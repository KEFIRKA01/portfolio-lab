<?php
/**
 * Plugin Name: Checkout Bridge for WooCommerce
 * Description: Demo bridge for WooCommerce orders, webhook sync and Telegram notifications.
 * Version: 0.3.0
 * Author: Portfolio Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class CheckoutBridgeForWooCommerce
{
    private const OPTION_WEBHOOK = 'cbfw_webhook_url';
    private const OPTION_TELEGRAM = 'cbfw_telegram_url';
    private const OPTION_SYNC_PROFILE = 'cbfw_sync_profile';
    private const OPTION_RETRY_QUEUE = 'cbfw_retry_queue';
    private const RETRY_ACTION = 'cbfw_retry_failed_deliveries';

    public function boot(): void
    {
        add_action('admin_menu', [$this, 'register_admin_page']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('admin_post_' . self::RETRY_ACTION, [$this, 'retry_failed_deliveries']);
        add_action('woocommerce_checkout_order_processed', [$this, 'handle_order'], 10, 3);
    }

    public function register_admin_page(): void
    {
        add_options_page(
            'Checkout Bridge',
            'Checkout Bridge',
            'manage_options',
            'checkout-bridge',
            [$this, 'render_admin_page']
        );
    }

    public function register_settings(): void
    {
        register_setting('checkout_bridge_options', self::OPTION_WEBHOOK, [
            'sanitize_callback' => 'esc_url_raw',
            'default' => '',
        ]);
        register_setting('checkout_bridge_options', self::OPTION_TELEGRAM, [
            'sanitize_callback' => 'esc_url_raw',
            'default' => '',
        ]);
        register_setting('checkout_bridge_options', self::OPTION_SYNC_PROFILE, [
            'sanitize_callback' => 'sanitize_text_field',
            'default' => 'default',
        ]);
    }

    public function render_admin_page(): void
    {
        $retry_queue = $this->read_retry_queue();
        ?>
        <div class="wrap">
            <h1>Checkout Bridge for WooCommerce</h1>
            <form method="post" action="options.php">
                <?php settings_fields('checkout_bridge_options'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="cbfw_webhook_url">Webhook URL</label></th>
                        <td><input class="regular-text" type="url" id="cbfw_webhook_url" name="<?php echo esc_attr(self::OPTION_WEBHOOK); ?>" value="<?php echo esc_attr(get_option(self::OPTION_WEBHOOK, '')); ?>"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="cbfw_telegram_url">Telegram notifier URL</label></th>
                        <td><input class="regular-text" type="url" id="cbfw_telegram_url" name="<?php echo esc_attr(self::OPTION_TELEGRAM); ?>" value="<?php echo esc_attr(get_option(self::OPTION_TELEGRAM, '')); ?>"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="cbfw_sync_profile">Sync profile</label></th>
                        <td>
                            <select id="cbfw_sync_profile" name="<?php echo esc_attr(self::OPTION_SYNC_PROFILE); ?>">
                                <option value="default" <?php selected(get_option(self::OPTION_SYNC_PROFILE, 'default'), 'default'); ?>>Default</option>
                                <option value="b2b" <?php selected(get_option(self::OPTION_SYNC_PROFILE, 'default'), 'b2b'); ?>>B2B</option>
                                <option value="white_label" <?php selected(get_option(self::OPTION_SYNC_PROFILE, 'default'), 'white_label'); ?>>White-label</option>
                            </select>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>

            <hr>
            <h2>Retry queue</h2>
            <p>Pending failed deliveries: <strong><?php echo esc_html((string) count($retry_queue)); ?></strong></p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="<?php echo esc_attr(self::RETRY_ACTION); ?>">
                <?php wp_nonce_field(self::RETRY_ACTION); ?>
                <?php submit_button('Retry failed deliveries', 'secondary'); ?>
            </form>
        </div>
        <?php
    }

    public function handle_order(int $order_id, array $posted_data, $order): void
    {
        $payload = $this->build_payload($order_id, $order);
        $destinations = array_filter([
            get_option(self::OPTION_WEBHOOK, ''),
            get_option(self::OPTION_TELEGRAM, ''),
        ]);

        foreach ($destinations as $destination) {
            $delivered = $this->push_json($destination, $payload);
            if (!$delivered) {
                $this->queue_failed_delivery($destination, $payload);
            }
        }

        if (is_object($order) && method_exists($order, 'add_order_note')) {
            $order->add_order_note('Checkout Bridge processed integration payload.');
        }
    }

    public function retry_failed_deliveries(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die('Forbidden');
        }
        check_admin_referer(self::RETRY_ACTION);

        $queue = $this->read_retry_queue();
        $remaining = [];
        foreach ($queue as $entry) {
            $delivered = $this->push_json($entry['destination'], $entry['payload']);
            if (!$delivered) {
                $remaining[] = $entry;
            }
        }

        update_option(self::OPTION_RETRY_QUEUE, $remaining, false);
        wp_safe_redirect(admin_url('options-general.php?page=checkout-bridge'));
        exit;
    }

    private function build_payload(int $order_id, $order): array
    {
        $status = is_object($order) && method_exists($order, 'get_status') ? $order->get_status() : null;
        $total = is_object($order) && method_exists($order, 'get_total') ? $order->get_total() : null;
        $segment = $this->detect_order_segment($order, $total);
        return [
            'order_id' => $order_id,
            'total' => $total,
            'customer_email' => is_object($order) && method_exists($order, 'get_billing_email') ? $order->get_billing_email() : null,
            'created_at' => current_time('mysql'),
            'status' => $status,
            'segment' => $segment,
            'sync_profile' => get_option(self::OPTION_SYNC_PROFILE, 'default'),
            'idempotency_key' => $this->build_idempotency_key($order_id, $status, $total),
        ];
    }

    private function detect_order_segment($order, $total): string
    {
        if (is_numeric($total) && (float) $total >= 50000) {
            return 'high_value';
        }
        if (is_object($order) && method_exists($order, 'get_items')) {
            foreach ($order->get_items() as $item) {
                $product = method_exists($item, 'get_product') ? $item->get_product() : null;
                if ($product && method_exists($product, 'is_virtual') && $product->is_virtual()) {
                    return 'digital';
                }
            }
        }
        return 'standard';
    }

    private function build_idempotency_key(int $order_id, $status, $total): string
    {
        return hash('sha256', implode('|', [$order_id, (string) $status, (string) $total]));
    }

    private function read_retry_queue(): array
    {
        $queue = get_option(self::OPTION_RETRY_QUEUE, []);
        return is_array($queue) ? $queue : [];
    }

    private function queue_failed_delivery(string $destination, array $payload): void
    {
        $queue = $this->read_retry_queue();
        $queue[] = [
            'destination' => esc_url_raw($destination),
            'payload' => $payload,
        ];
        update_option(self::OPTION_RETRY_QUEUE, $queue, false);
    }

    private function push_json(string $url, array $payload): bool
    {
        if (empty($url)) {
            return true;
        }

        $response = wp_remote_post($url, [
            'timeout' => 8,
            'headers' => ['Content-Type' => 'application/json'],
            'body' => wp_json_encode($payload),
        ]);

        if (is_wp_error($response)) {
            return false;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        return $status_code >= 200 && $status_code < 300;
    }
}

$checkout_bridge_for_woocommerce = new CheckoutBridgeForWooCommerce();
$checkout_bridge_for_woocommerce->boot();
