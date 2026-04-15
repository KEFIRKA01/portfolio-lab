import { chromium } from "playwright";

const waits = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function shot(page, url, path, options = {}) {
  await page.goto(url, { waitUntil: "networkidle" });
  if (options.onReady) {
    await options.onReady(page);
  }
  await waits(500);
  await page.screenshot({ path, fullPage: true });
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });

  await shot(
    page,
    "http://127.0.0.1:4173",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/conversion-landing-kit/assets/conversion-landing-kit-01-cover.png"
  );

  await shot(
    page,
    "http://127.0.0.1:4173",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/conversion-landing-kit/assets/conversion-landing-kit-03-flow.png",
    {
      onReady: async (page) => {
        await page.getByRole("button", { name: "Форма + CRM" }).click();
        await page.getByPlaceholder("Ваше имя").fill("Алексей");
        await page.getByPlaceholder("Telegram или email").fill("@alexey_dev");
        await page.getByPlaceholder("Коротко опишите задачу").fill(
          "Нужен лендинг с формой, отправкой в CRM и уведомлением в Telegram."
        );
      },
    }
  );

  await shot(
    page,
    "http://127.0.0.1:4174",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/quote-configurator-studio/assets/quote-configurator-studio-01-cover.png"
  );

  await shot(
    page,
    "http://127.0.0.1:4174",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/quote-configurator-studio/assets/quote-configurator-studio-03-flow.png",
    {
      onReady: async (page) => {
        await page.getByRole("button", { name: "Интеграции" }).click();
        await page.locator('input[value="crm"]').check();
        await page.locator('input[value="telegram"]').check();
        await page.locator('input[value="payments"]').check();
        await page.locator("#complexity").fill("4");
      },
    }
  );

  await shot(
    page,
    "http://127.0.0.1:8011/docs",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/flowdesk-crm-hub/assets/flowdesk-crm-hub-02-main.png"
  );

  await shot(
    page,
    "http://127.0.0.1:8012/docs",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/opsportal-b2b-cabinet/assets/opsportal-b2b-cabinet-02-main.png"
  );

  await shot(
    page,
    "http://127.0.0.1:8013/docs",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/eventmesh-booking-router/assets/eventmesh-booking-router-02-main.png"
  );

  await shot(
    page,
    "http://127.0.0.1:8014/docs",
    "C:/Users/KIFER/Desktop/ТГ фриланс бот/portfolio_lab/projects/vendorhub-compliance-portal/assets/vendorhub-compliance-portal-02-main.png"
  );

  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
