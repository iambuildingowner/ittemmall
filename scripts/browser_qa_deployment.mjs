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
  desktopHome: ["ITTEMMALL", "MARCE", "대표 상품 보기"],
  productDetail: ["MARCE 스위트 피클볼 패들", "바로 구매하기", "N pay 구매", "네이버페이 주문형 가맹 신청 준비", "USAPA"],
  paymentFlow: ["토스페이먼츠 안내 요청", "토스 결제창 열기", "주문 수정"],
  tossCheckout: ["토스페이먼츠 결제", "토스 결제하기", "주문 요약"],
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
    label: "desktop payment flow",
    url: `${baseUrl}/#/product/pink`,
    viewport: { width: 1440, height: 1100 },
    texts: requiredTexts.paymentFlow,
    setup: async (page) => {
      await page.click('button[data-action="apply"]');
      await page.waitForFunction(() => location.hash === "#/apply", null, { timeout: 10000 });
      await page.fill('[data-field="name"]', "안뜰에해듬");
      await page.fill('[data-field="phone"]', "01077008087");
      await page.fill('[data-field="email"]', "staysiaofficial@gmail.com");
      await page.fill('[data-field="postcode"]', "54533");
      await page.fill('[data-field="roadAddress"]', "전북특별자치도 익산시 황등면 황금로 73");
      await page.fill('[data-field="detailAddress"]', "브라우저 QA");
      await page.check('[data-field="agreeTermsPrivacy"]');
      await page.click('button[data-action="submit-apply"]');
      await page.waitForFunction(() => location.hash.startsWith("#/payment"), null, { timeout: 10000 });
    },
  },
  {
    label: "toss checkout",
    url: `${baseUrl}/payment/toss-checkout.html?orderId=IT-BROWSER-QA&amount=59000&orderName=MARCE%20%EC%8A%A4%EC%9C%84%ED%8A%B8%20%ED%94%BC%ED%81%B4%EB%B3%BC%20%ED%8C%A8%EB%93%A4&customerName=%EC%95%88%EB%9C%B0%EC%97%90%ED%95%B4%EB%93%AC&customerEmail=staysiaofficial%40gmail.com&customerMobilePhone=01077008087`,
    viewport: { width: 390, height: 900 },
    texts: requiredTexts.tossCheckout,
    setup: async (page) => {
      await page.waitForSelector("iframe", { timeout: 20000 });
      await page.waitForSelector("#payButton:not([disabled])", { timeout: 20000 });
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
        if (url.endsWith("/payment/order-store.php") && status === 501) {
          allowedNetworkErrors.push(`${visit.label}: ${status} ${url}`);
          return;
        }
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

      if (visit.label === "toss checkout") {
        const disabled = await page.locator("#payButton").evaluate((button) => button.disabled);
        if (!disabled) noteOk("toss checkout pay button enabled");
        else noteFailure("toss checkout pay button disabled");
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
  } else if (error.includes("Failed to load resource") && error.includes("501") && error.includes("order-store.php")) {
    noteWarning(`owner-gate console ${error}`);
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
