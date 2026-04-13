<?php
/**
 * Plugin Name: Returns Sync for WooCommerce
 * Description: Demo sync plugin for WooCommerce refunds, returns and RMA workflow.
 * Version: 0.1.0
 * Author: Portfolio Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class ReturnsSyncForWooCommerce
{
    private const OPTION_WEBHOOK = 'rsfw_webhook_url';
    private const OPTION_SYNC_PROFILE = 'rsfw_sync_profile';
    private const OPTION_RETRY_QUEUE = 'rsfw_retry_queue';

    public function boot(): void
    {
        add_action('admin_menu', [$this, 'register_admin_page']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('woocommerce_order_refunded', [$this, 'handle_refund'], 10, 2);
    }

    public function register_admin_page(): void
    {
        add_options_page('Returns Sync', 'Returns Sync', 'manage_options', 'returns-sync', [$this, 'render_admin_page']);
    }

    public function register_settings(): void
    {
        register_setting('returns_sync_options', self::OPTION_WEBHOOK, ['sanitize_callback' => 'esc_url_raw', 'default' => '']);
        register_setting('returns_sync_options', self::OPTION_SYNC_PROFILE, ['sanitize_callback' => 'sanitize_text_field', 'default' => 'default']);
    }

    public function render_admin_page(): void
    {
        ?>
        <div class="wrap">
            <h1>Returns Sync for WooCommerce</h1>
            <form method="post" action="options.php">
                <?php settings_fields('returns_sync_options'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="rsfw_webhook_url">Webhook URL</label></th>
                        <td><input class="regular-text" type="url" id="rsfw_webhook_url" name="<?php echo esc_attr(self::OPTION_WEBHOOK); ?>" value="<?php echo esc_attr(get_option(self::OPTION_WEBHOOK, '')); ?>"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="rsfw_sync_profile">Sync profile</label></th>
                        <td><input class="regular-text" type="text" id="rsfw_sync_profile" name="<?php echo esc_attr(self::OPTION_SYNC_PROFILE); ?>" value="<?php echo esc_attr(get_option(self::OPTION_SYNC_PROFILE, 'default')); ?>"></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    public function handle_refund(int $order_id, int $refund_id): void
    {
        $payload = [
            'order_id' => $order_id,
            'refund_id' => $refund_id,
            'sync_profile' => get_option(self::OPTION_SYNC_PROFILE, 'default'),
            'idempotency_key' => hash('sha256', implode('|', [$order_id, $refund_id])),
            'created_at' => current_time('mysql'),
        ];

        $response = wp_remote_post(get_option(self::OPTION_WEBHOOK, ''), [
            'timeout' => 8,
            'headers' => ['Content-Type' => 'application/json'],
            'body' => wp_json_encode($payload),
        ]);

        if (is_wp_error($response)) {
            $queue = get_option(self::OPTION_RETRY_QUEUE, []);
            if (!is_array($queue)) {
                $queue = [];
            }
            $queue[] = $payload;
            update_option(self::OPTION_RETRY_QUEUE, $queue, false);
        }
    }
}

$returns_sync_for_woocommerce = new ReturnsSyncForWooCommerce();
$returns_sync_for_woocommerce->boot();
