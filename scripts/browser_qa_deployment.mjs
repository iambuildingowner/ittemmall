import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const args = new Map();
for (let index = 2; index < process.argv.length; index += 1) {
  const arg = process.argv[index];
  if (arg.startsWith("--")) {
    const next = process.argv[index + 1];
    args.set(arg, next && !next.startsWith("--") ? next : "true");
    if (next && !next.startsWith("--")) index += 1;
  }
}

const baseUrl = (args.get("--base-url") || "http://127.0.0.1:8124").replace(/\/$/, "");
const executablePath = args.get("--chrome-path") || undefined;
const staticLocal = args.get("--static-local") === "true";

const requiredTexts = {
  desktopHome: ["ITTEMMALL", "SHOP", "네이버페이"],
  productDetail: ["잇템몰 스위트 피클볼 패들", "바로 구매하기", "pay 구매"],
  cart: ["장바구니", "주문서 작성", "pay 준비"],
  order: ["주문 정보 입력", "N pay 결제 준비하기"],
  admin: ["Orders Admin", "주문 관리"],
  ops: ["운영 점검", "JSON 열기", "공개 런칭 점검", "메일 알림 테스트"],
  orderLookup: ["ITTEMMALL", "주문 조회", "조회하기"],
  mobileHome: ["ITTEMMALL", "피클볼 패들"],
  legal: ["ITTEMMALL", "사업자 정보", "개인정보처리방침", "환불 안내"],
  notFound: ["ITTEMMALL", "페이지를 찾을 수 없습니다", "상품 보기"],
};

const visits = [
  {
    label: "desktop home",
    url: `${baseUrl}/`,
    viewport: { width: 1440, height: 1100 },
    texts: requiredTexts.desktopHome,
  },
  {
    label: "desktop product detail",
    url: `${baseUrl}/#/product/pink`,
    viewport: { width: 1440, height: 1100 },
    texts: requiredTexts.productDetail,
  },
  {
    label: "desktop cart",
    url: `${baseUrl}/#/product/pink`,
    viewport: { width: 1440, height: 1100 },
    texts: requiredTexts.cart,
    setup: async (page) => {
      await page.click('button[data-action="add-to-cart"][data-cart-source="product_detail"]');
      await page.waitForFunction(() => location.hash === "#/cart", null, { timeout: 10000 });
      await page.reload({ waitUntil: "networkidle" });
      await page.waitForFunction(() => location.hash === "#/cart", null, { timeout: 10000 });
    },
  },
  {
    label: "desktop order",
    url: `${baseUrl}/#/product/pink`,
    viewport: { width: 1440, height: 1100 },
    texts: requiredTexts.order,
    setup: async (page) => {
      await page.click('button[data-action="apply"][data-checkout-source="npay"]');
      await page.waitForFunction(() => location.hash === "#/apply", null, { timeout: 10000 });
    },
  },
  {
    label: "mobile home",
    url: `${baseUrl}/`,
    viewport: { width: 390, height: 844 },
    texts: requiredTexts.mobileHome,
  },
  {
    label: "admin dashboard",
    url: `${baseUrl}/payment/admin.html`,
    viewport: { width: 1440, height: 1000 },
    texts: requiredTexts.admin,
  },
  {
    label: "ops readiness",
    url: `${baseUrl}/payment/ops.html`,
    viewport: { width: 1440, height: 1000 },
    texts: requiredTexts.ops,
  },
  {
    label: "customer order lookup",
    url: `${baseUrl}/payment/order-lookup.html`,
    viewport: { width: 1440, height: 1000 },
    texts: requiredTexts.orderLookup,
  },
  {
    label: "legal navigation",
    url: `${baseUrl}/legal/business.html`,
    viewport: { width: 1440, height: 1000 },
    texts: requiredTexts.legal,
    setup: async (page) => {
      await page.click('a[href="./privacy.html"]');
      await page.waitForURL("**/legal/privacy.html", { timeout: 10000 });
      await page.click('a[href="./refund.html"]');
      await page.waitForURL("**/legal/refund.html", { timeout: 10000 });
      await page.click('a[href="./business.html"]');
      await page.waitForURL("**/legal/business.html", { timeout: 10000 });
    },
  },
  {
    label: "404 page",
    url: `${baseUrl}/404.html`,
    viewport: { width: 390, height: 844 },
    texts: requiredTexts.notFound,
  },
];

const failures = [];
const warnings = [];
const networkErrors = [];
const allowedNetworkErrors = [];
const consoleErrors = [];

function noteFailure(message) {
  failures.push(message);
  console.log(`FAIL ${message}`);
}

function noteWarning(message) {
  warnings.push(message);
  console.log(`WARN ${message}`);
}

function noteOk(message) {
  console.log(`OK   ${message}`);
}

const browser = await chromium.launch({
  headless: true,
  executablePath,
});

try {
  for (const visit of visits) {
    const page = await browser.newPage({ viewport: visit.viewport });
    page.on("response", (response) => {
      const status = response.status();
      const url = response.url();
      if (status >= 400) {
        if (staticLocal && (url.endsWith("/track.php") || url.endsWith("/payment/order-store.php"))) {
          allowedNetworkErrors.push(`${visit.label}: ${status} ${url}`);
          return;
        }
        networkErrors.push(`${visit.label}: ${status} ${url}`);
      }
    });
    page.on("console", (message) => {
      if (message.type() === "error") {
        consoleErrors.push(`${visit.label}: ${message.text()}`);
      }
    });

    try {
      await page.goto(visit.url, { waitUntil: "networkidle", timeout: 20000 });
      if (visit.setup) await visit.setup(page);
      noteOk(`${visit.label} loaded`);

      const bodyText = await page.locator("body").innerText({ timeout: 10000 });
      for (const text of visit.texts) {
        if (bodyText.includes(text)) {
          noteOk(`${visit.label} contains "${text}"`);
        } else {
          noteFailure(`${visit.label} missing "${text}"`);
        }
      }

      const brokenImages = await page.evaluate(() =>
        Array.from(document.images)
          .filter((image) => image.complete && image.naturalWidth === 0)
          .map((image) => image.currentSrc || image.src || image.alt)
      );
      if (brokenImages.length === 0) {
        noteOk(`${visit.label} images loaded`);
      } else {
        noteFailure(`${visit.label} broken images: ${brokenImages.join(", ")}`);
      }

      const metrics = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        bodyScrollWidth: document.body.scrollWidth,
        bodyClientWidth: document.body.clientWidth,
      }));
      const overflow = Math.max(metrics.scrollWidth - metrics.clientWidth, metrics.bodyScrollWidth - metrics.bodyClientWidth);
      if (overflow <= 2) {
        noteOk(`${visit.label} has no horizontal overflow`);
      } else {
        noteFailure(`${visit.label} horizontal overflow ${overflow}px`);
      }

      if (visit.label === "desktop order") {
        await page.fill('[data-field="name"]', "테스트 주문자");
        await page.fill('[data-field="phone"]', "01000000000");
        await page.fill('[data-field="email"]', "qa@example.com");
        await page.fill('[data-field="fulfillmentPrimary"]', "서울 테스트 주소");
        await page.check('[data-field="agreeNotice"]');
        await page.check('[data-field="agreeTermsPrivacy"]');
        await page.click('button[data-action="submit-apply"]');
        await page.waitForFunction(() => location.hash.startsWith("#/payment/"), null, { timeout: 10000 });
        const updatedText = await page.locator("body").innerText({ timeout: 10000 });
        if (updatedText.includes("서버 주문 저장소 연결 필요") || updatedText.includes("서버 주문 저장 완료")) {
          noteOk("desktop order Naver Pay guard/status rendered");
        } else {
          noteFailure("desktop order did not show server-sync payment status");
        }
      }
    } catch (error) {
      noteFailure(`${visit.label} threw ${error.message}`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

for (const error of networkErrors) noteFailure(`network ${error}`);
for (const error of allowedNetworkErrors) noteWarning(`static-local network ${error}`);
for (const error of consoleErrors) {
  if (staticLocal && error.includes("Failed to load resource") && error.includes("501")) {
    noteWarning(`static-local console ${error}`);
  } else if (error.includes("Failed to load resource")) {
    noteFailure(`console ${error}`);
  } else {
    noteWarning(`console ${error}`);
  }
}

if (warnings.length > 0) {
  console.log("\nWarnings:");
  for (const warning of warnings) console.log(`- ${warning}`);
}

if (failures.length > 0) {
  console.log("\nFailures:");
  for (const failure of failures) console.log(`- ${failure}`);
  process.exit(1);
}

console.log("\nBrowser QA passed.");
