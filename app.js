(function () {
  const STORAGE_KEY = "runnerwin_state_v2";
  const TRACKING_KEY = "ittemmall_tracking_events_v1";
  const ATTRIBUTION_KEY = "ittemmall_attribution_v1";
  const BRAND = {
    name: "ITTEMMALL",
    kr: "잇템몰",
    domain: "ittemmall.com"
  };
  const TRACKING = {
    metaPixelId: "1288524852852406",
    serverEndpoint: "/track.php",
    serverLoggedEvents: ["ViewContent", "AddToCart", "CheckoutStartClick", "CheckoutPageView", "NpayClick", "CheckoutFormStart", "PaymentGatewayClick", "PaymentPageView", "OptionSelect"],
    dailyBudgetKrw: 50000,
    currency: "KRW",
    primaryLandingPath: "/headband/",
    primaryCreativeImage: "assets/images/runnerwin-wide-headband-main.png"
  };
  const WON = new Intl.NumberFormat("ko-KR", { style: "currency", currency: "KRW", maximumFractionDigits: 0 });
  const app = document.getElementById("app");
  const PRIMARY_PRODUCT_PATH = "/headband/";
  const LEGACY_PRODUCT_PATH = "/product/coolfit-wide-headband/50/category/25/display/1/";
  const ROUTE_ALIASES = {
    "/home": PRIMARY_PRODUCT_PATH,
    "/index.html": PRIMARY_PRODUCT_PATH,
    "/product/search.html": "/search/",
    "/order/basket.html": "/cart/",
    "/order/checkout.html": "/checkout/",
    "/myshop/index.html": "/account/",
    "/myshop/order/list.html": "/orders/",
    "/myshop//order/list.html": "/orders/",
    "/myshop/order/detail.html": "/orders/detail/",
    "/myshop/order/edit.html": "/orders/edit/"
  };
  const IS_FILE_MODE = window.location.protocol === "file:";
  const APP_BASE_PATH = !IS_FILE_MODE && window.location.hostname.endsWith("github.io") ? "/ittemmall" : "";

  initMetaPixel();
  captureAttribution();

  const heroSlides = [
    {
      href: PRIMARY_PRODUCT_PATH,
      tone: "band",
      title: "WIDE SWEAT CONTROL",
      copy: "넓게 감싸고 빠르게 말리는 와이드 헤드밴드 셋업.",
      alt: "와이드 헤드밴드 캠페인"
    }
  ];

  const products = [
    {
      id: "coolfit-wide-headband",
      cafeId: 50,
      name: "러너윈 테크니컬 헤드밴드",
      price: 7900,
      category: "acc",
      cateNo: 25,
      subCateNo: 68,
      tags: ["best", "new", "all", "acc"],
      visual: "headband-wide",
      image: "/assets/images/runnerwin-wide-headband-main.png",
      desc: "이마를 넓게 감싸 땀 흐름을 줄이고, 부드러운 신축 원단으로 장시간 착용 부담을 낮춘 와이드 밴드입니다.",
      sizes: ["FREE"],
      colors: ["BLACK", "WHITE"],
      detailType: "Segmented product detail",
      detailMode: "wide-headband",
      bullets: ["넓은 커버 폭", "부드러운 텐션", "빠른 건조감"],
      sections: [
        { title: "넓게 받쳐주는 앞면 폭", body: "눈가로 내려오는 땀을 한 번 더 잡아주도록 앞면 커버 면적을 넓혔습니다.", role: "상품 단독컷", mediaRole: "product-only" },
        { title: "압박보다 안정감", body: "머리를 조이는 느낌을 줄이고, 달리는 동안 밀림을 줄이는 탄성 밸런스를 기준으로 정리했습니다.", role: "사람 착용컷", mediaRole: "human-wearing" },
        { title: "운동 후에도 가볍게 관리", body: "손세탁 후 빠르게 마르는 얇은 원단감으로 매일 훈련 루틴에 맞췄습니다.", role: "소재 클로즈업", mediaRole: "feature-detail" }
      ],
      reviews: [
        { name: "김*영", date: "2026.05.18", text: "앞머리 쪽 땀이 눈으로 바로 내려오지 않아 인터벌 때 확인하기 좋았습니다." },
        { name: "박*주", date: "2026.05.18", text: "넓은데 답답하지 않고, 모자 안에 같이 써도 들뜨는 느낌이 적었습니다." }
      ]
    }
  ];

  const categories = {
    new: { title: "ALL", cateNo: 44, match: (p) => p.tags.includes("all") || p.tags.includes("new") },
    acc: { title: "ACC", cateNo: 25, match: (p) => p.category === "acc" }
  };

  const subCategories = {
    64: { title: "T-SHIRTS", match: (p) => p.subCateNo === 64 },
    65: { title: "SLEEVELESS", match: (p) => p.subCateNo === 65 },
    66: { title: "PANTS", match: (p) => p.subCateNo === 66 },
    67: { title: "SHORTS", match: (p) => p.subCateNo === 67 },
    68: { title: "CAP & HEADWEAR", match: (p) => p.subCateNo === 68 },
    69: { title: "NECKGAITER", match: (p) => p.subCateNo === 69 },
    70: { title: "BAG", match: (p) => p.subCateNo === 70 },
    71: { title: "SLEEVE", match: (p) => p.subCateNo === 71 },
    73: { title: "SOCKS", match: (p) => p.subCateNo === 73 },
    75: { title: "TOWEL", match: (p) => p.subCateNo === 75 },
    87: { title: "JACKET", match: (p) => p.subCateNo === 87 },
    89: { title: "LEGGINGS", match: (p) => p.subCateNo === 89 }
  };

  const races = [
    { date: "5월 23일 (토)", name: "새벽 페이스 10K", info: "10km, 5km", url: "/about/contents.html" },
    { date: "5월 30일 (토)", name: "도심 릴레이 러닝", info: "20km relay", url: "/about/contents.html" },
    { date: "5월 30일 (토)", name: "강변 하프 챌린지", info: "half, 10km", url: "/about/contents.html" },
    { date: "5월 30일 (토)", name: "주말 이지런 모임", info: "10km, 5km", url: "/about/contents.html" },
    { date: "5월 31일 (일)", name: "트랙 템포 세션", info: "track, 5km", url: "/about/contents.html" },
    { date: "5월 31일 (일)", name: "나이트 조깅 클럽", info: "10km, 5km", url: "/about/contents.html" }
  ];

  const boards = {
    1: { title: "NOTICE", items: ["Runnerwin 검증 스토어 오픈", "배송 및 교환 안내", "러닝 액세서리 셀렉션 안내"] },
    3: { title: "FAQ", items: ["사이즈 선택 기준", "세탁 및 관리 방법", "멤버십 적립금 안내"] },
    4: { title: "REVIEW", items: ["와이드 헤드밴드 착용감 확인", "땀 흡수감 샘플 후기", "색상 선택 기준"] },
    5: { title: "BOARD", items: ["러닝 크루 소식", "입고 예정 제품", "오프라인 팝업 공지"] },
    6: { title: "Q&A", items: ["상품 사이즈 문의", "배송 일정 문의", "교환 가능 여부"] }
  };

  const defaultCheckoutForm = {
    name: "",
    phone: "",
    email: "",
    zipcode: "",
    address: "",
    addressDetail: "",
    memo: "",
    agreeNotice: false,
    agreeContact: false
  };

  const defaultState = {
    cart: [],
    orders: [],
    checkoutForm: { ...defaultCheckoutForm },
    routeState: {},
    origin: { path: "/index.html", label: "HOME" },
    lastPath: "/index.html",
    searchHistory: [],
    recentProducts: [],
    trackingTest: false
  };

  let heroTimer = null;
  let state = loadState();

  function loadState() {
    try {
      return { ...defaultState, ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") };
    } catch (error) {
      return { ...defaultState };
    }
  }

  function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    updateCartCount();
  }

  function appHref(path) {
    if (!path || path.startsWith("http")) return path;
    const cleanPath = canonicalizePath(path);
    if (!IS_FILE_MODE) return cleanPath.startsWith("/") ? `${APP_BASE_PATH}${cleanPath}` : cleanPath;
    const route = cleanPath.startsWith("#/") ? cleanPath.slice(1) : cleanPath;
    if (!route.startsWith("/")) return path;
    return `index.html?route=${encodeURIComponent(route)}#${route}`;
  }

  function stripBasePath(path) {
    if (!APP_BASE_PATH || !path.startsWith(`${APP_BASE_PATH}/`)) return path;
    return path.slice(APP_BASE_PATH.length) || "/index.html";
  }

  function routeFromHref(rawHref) {
    if (!rawHref) return PRIMARY_PRODUCT_PATH;
    if (rawHref.startsWith("#/")) return canonicalizePath(rawHref.slice(1));
    const hashIndex = rawHref.indexOf("#/");
    if (hashIndex >= 0) return canonicalizePath(rawHref.slice(hashIndex + 1));
    if (rawHref.startsWith("/")) return canonicalizePath(stripBasePath(rawHref));
    try {
      const url = new URL(rawHref, window.location.href);
      const hashPath = decodeURIComponent(url.hash.replace(/^#/, ""));
      if (hashPath.startsWith("/")) return canonicalizePath(hashPath);
      const routePath = url.searchParams.get("route");
      if (routePath?.startsWith("/")) {
        const params = new URLSearchParams(url.search);
        params.delete("route");
        const query = params.toString();
        return canonicalizePath(query ? `${routePath}${routePath.includes("?") ? "&" : "?"}${query}` : routePath);
      }
      const cleanPath = stripBasePath(url.pathname);
      if (cleanPath.endsWith("/index.html")) return canonicalizePath(cleanPath);
      return canonicalizePath(cleanPath + url.search);
    } catch (error) {
      return canonicalizePath(rawHref);
    }
  }

  function routeParams(path = getPath()) {
    const [, routeQuery = ""] = path.split("?");
    return new URLSearchParams(routeQuery);
  }

  function assetUrl(path) {
    if (IS_FILE_MODE && path.startsWith("/assets/")) return path.slice(1);
    if (!IS_FILE_MODE && path.startsWith("/assets/")) return `${APP_BASE_PATH}${path}`;
    return path;
  }

  function getPath() {
    const hashPath = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (hashPath === "/home" || hashPath === "home") return PRIMARY_PRODUCT_PATH;
    if (hashPath.startsWith("/")) return canonicalizePath(hashPath);
    const routeParams = new URLSearchParams(window.location.search);
    const routePath = routeParams.get("route");
    if (routePath === "/home" || routePath === "home") return PRIMARY_PRODUCT_PATH;
    if (routePath?.startsWith("/")) {
      routeParams.delete("route");
      const query = routeParams.toString();
      return canonicalizePath(query ? `${routePath}${routePath.includes("?") ? "&" : "?"}${query}` : routePath);
    }
    if (IS_FILE_MODE) {
      return PRIMARY_PRODUCT_PATH;
    }
    return canonicalizePath(stripBasePath(window.location.pathname) + window.location.search);
  }

  function routeKey(path = getPath()) {
    return canonicalizePath(path).replace(/([?&])state=(loading|empty|error|success)/, "").replace(/\/$/, "") || PRIMARY_PRODUCT_PATH;
  }

  function normalizePath(path) {
    return canonicalizePath(path);
  }

  function canonicalizePath(path) {
    if (!path || path === "/" || path === "home" || path === "/home") return PRIMARY_PRODUCT_PATH;
    let next = String(path).trim();
    const queryIndex = next.indexOf("?");
    let base = queryIndex >= 0 ? next.slice(0, queryIndex) : next;
    const query = queryIndex >= 0 ? next.slice(queryIndex) : "";
    try {
      base = decodeURIComponent(base);
    } catch (error) {
      // Keep the original path if it is not valid percent-encoded text.
    }
    if (base.startsWith(APP_BASE_PATH + "/")) base = stripBasePath(base);
    if (!base.startsWith("/")) base = `/${base}`;
    base = base.replace(/\/{2,}/g, "/");
    if (base.endsWith("/index.html")) base = base.replace(/index\.html$/, "");
    if (base !== "/" && !base.includes(".") && !base.endsWith("/")) base = `${base}/`;
    if (base === "/" || base === "/index.html") base = PRIMARY_PRODUCT_PATH;
    if (base === LEGACY_PRODUCT_PATH || base.startsWith("/product/coolfit-wide-headband/")) base = PRIMARY_PRODUCT_PATH;
    else if (base === "/category/new/44/" || base.startsWith("/category/new/")) base = "/all/";
    else if (base === "/category/acc/25/" || base.startsWith("/category/acc/")) base = "/acc/";
    else if (ROUTE_ALIASES[base]) base = ROUTE_ALIASES[base];
    return `${base}${query}`;
  }

  function writeHistory(path, replace = false) {
    const nextPath = normalizePath(path);
    if (IS_FILE_MODE) {
      const url = new URL(window.location.href);
      url.search = "";
      url.searchParams.set("route", nextPath);
      url.hash = nextPath;
      history[replace ? "replaceState" : "pushState"]({}, "", url);
      return;
    }
    history[replace ? "replaceState" : "pushState"]({}, "", `${APP_BASE_PATH}${nextPath}`);
  }

  function syncCanonicalUrl(path) {
    if (IS_FILE_MODE) return;
    const target = normalizePath(path);
    const visible = stripBasePath(window.location.pathname) + window.location.search;
    if (visible !== target) writeHistory(target, true);
  }

  function beforeLeave() {
    state.routeState[routeKey()] = {
      ...(state.routeState[routeKey()] || {}),
      scrollY: window.scrollY
    };
    state.lastPath = getPath();
    saveState();
  }

  function navigate(path, options = {}) {
    beforeLeave();
    const nextPath = normalizePath(path);
    if (options.origin !== false) {
      state.origin = {
        path: getPath(),
        label: getOriginLabel()
      };
    }
    saveState();
    writeHistory(nextPath);
    render({ restoreScroll: options.restoreScroll === true });
  }

  function getOriginLabel() {
    const path = getPath();
    if (path.includes("/all/") || path.includes("/acc/") || path.includes("/category/")) return "CATEGORY";
    if (path.includes("/headband/") || path.includes("/product/")) return "PRODUCT";
    if (path.includes("/cart/") || path.includes("/order/basket")) return "CART";
    if (path.includes("/board/")) return "COMMUNITY";
    if (path.includes("/about/")) return "ABOUT";
    return "HOME";
  }

  function resumeButton(light = false) {
    const origin = state.origin || defaultState.origin;
    const cls = light ? "outline_btn" : "ghost_btn";
    return `<button class="${cls}" type="button" data-resume>BACK TO ${escapeHtml(origin.label || "ORIGIN")}</button>`;
  }

  function delay(ms = 180) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function getProductList(filter = {}) {
    const params = routeParams();
    if (params.get("state") === "error") {
      throw new Error("상품 정보를 불러오지 못했습니다.");
    }
    const forced = params.get("state");
    if (forced === "empty") return [];
    let result = products.slice();
    if (filter.category && categories[filter.category]) result = result.filter(categories[filter.category].match);
    if (filter.subCateNo && subCategories[filter.subCateNo]) result = result.filter(subCategories[filter.subCateNo].match);
    if (filter.keyword) {
      const q = filter.keyword.trim().toLowerCase();
      result = result.filter((p) => `${p.name} ${p.desc} ${p.category}`.toLowerCase().includes(q));
    }
    if (filter.sort === "price-asc") result.sort((a, b) => a.price - b.price);
    if (filter.sort === "price-desc") result.sort((a, b) => b.price - a.price);
    if (filter.sort === "new") result.sort((a, b) => b.cafeId - a.cafeId);
    return result;
  }

  const repo = {
    async listProducts(filter = {}) {
      return getProductList(filter);
    },
    async getProduct(id) {
      return products.find((p) => p.id === id || String(p.cafeId) === String(id));
    },
    async getCart() {
      return state.cart.map((item) => ({ ...item, product: products.find((p) => p.id === item.productId) })).filter((item) => item.product);
    }
  };

  function productUrl(product) {
    if (product.id === "coolfit-wide-headband") return PRIMARY_PRODUCT_PATH;
    return `/product/${product.id}/${product.cafeId}/category/${product.cateNo}/display/1/`;
  }

  function categoryUrl(slug) {
    const cat = categories[slug];
    if (!cat) return PRIMARY_PRODUCT_PATH;
    if (slug === "new") return "/all/";
    if (slug === "acc") return "/acc/";
    return `/category/${slug}/${cat.cateNo}/`;
  }

  async function render({ restoreScroll = true } = {}) {
    clearInterval(heroTimer);
    closeMenu();
    closeSearch();
    const currentPath = getPath();
    const [routePath, routeQuery = ""] = currentPath.split("?");
    const path = normalizePath(routePath);
    const params = new URLSearchParams(routeQuery);
    syncCanonicalUrl(currentPath);
    const isHome = path === "/index.html" || path === "/";
    document.body.classList.toggle("st-home", isHome);
    document.body.classList.toggle("st-hero", isHome && window.scrollY < 80);
    document.body.classList.toggle("header_solid", !isHome);
    if (path === PRIMARY_PRODUCT_PATH) await renderProduct(LEGACY_PRODUCT_PATH);
    else if (path === "/all/") await renderCategory("new");
    else if (path === "/acc/") await renderCategory("acc");
    else if (path === "/cart/") await renderCart();
    else if (path === "/checkout-start/") await renderCheckoutStart(params);
    else if (path === "/checkout/") await renderCheckout();
    else if (path === "/orders/") renderOrders();
    else if (path === "/orders/detail/") renderOrderDetail(params.get("order_id"));
    else if (path === "/orders/edit/") renderOrderEdit(params.get("order_id"));
    else if (path === "/account/") renderAccount();
    else if (path === "/search/") await renderSearchPage(params.get("keyword") || "");
    else if (path.startsWith("/category/")) await renderCategory(path.split("/")[2]);
    else if (path === "/product/list.html") await renderSubCategory(params.get("cate_no"));
    else if (path.startsWith("/product/search.html")) await renderSearchPage(params.get("keyword") || "");
    else if (path.startsWith("/product/")) await renderProduct(path);
    else if (path.startsWith("/order/complete.html")) renderOrderComplete(params.get("order_id"));
    else if (path.startsWith("/order/checkout.html")) await renderCheckout();
    else if (path.startsWith("/order/basket.html")) await renderCart();
    else if (path.startsWith("/myshop/order/detail.html")) renderOrderDetail(params.get("order_id"));
    else if (path.startsWith("/myshop/order/edit.html")) renderOrderEdit(params.get("order_id"));
    else if (path.startsWith("/myshop/order/list.html") || path.startsWith("/myshop//order/list.html")) renderOrders();
    else if (path.startsWith("/myshop/index.html")) renderAccount();
    else if (path.startsWith("/board/")) renderBoard(params.get("board_no") || "1");
    else if (path.startsWith("/about/about.html")) renderAbout();
    else if (path.startsWith("/collection/index.html")) renderCollection();
    else if (path.startsWith("/about/contents.html")) renderContents();
    else if (path.startsWith("/member/agreement.html")) renderPolicy("TERMS&CONDITIONS");
    else if (path.startsWith("/member/privacy.html")) renderPolicy("PRIVACY POLICY");
    else if (path.startsWith("/shopinfo/guide.html")) renderPolicy("GUIDE");
    else renderNotFound();

    updateCartCount();
    queueMicrotask(() => {
      bindPageControls();
      if (restoreScroll) restoreScrollPosition();
      else window.scrollTo({ top: 0, behavior: "instant" });
    });
  }

  function restoreScrollPosition() {
    const saved = state.routeState[routeKey()]?.scrollY;
    window.scrollTo({ top: Number(saved || 0), behavior: "instant" });
  }

  function renderHome() {
    app.innerHTML = `
      <section class="home_hero" aria-label="Runnerwin 메인 캠페인">
        ${heroSlides.map((slide, index) => `
          <div class="hero_slide hero_tone_${slide.tone} ${index === 0 ? "is_active" : ""}" data-hero-slide>
            <a href="${appHref(slide.href)}" data-link aria-label="${escapeHtml(slide.alt)}"></a>
            <div class="hero_art" role="img" aria-label="${escapeHtml(slide.alt)}">
              <span class="hero_line"></span>
              <span class="hero_product_mark">${escapeHtml(slide.tone.toUpperCase())}</span>
            </div>
            <div class="hero_copy">
              <p>${escapeHtml(BRAND.name)}</p>
              <h2>${escapeHtml(slide.title)}</h2>
              <span>${escapeHtml(slide.copy)}</span>
            </div>
          </div>
        `).join("")}
        <button class="hero_arrow prev" type="button" data-hero-prev aria-label="이전 캠페인">‹</button>
        <button class="hero_arrow next" type="button" data-hero-next aria-label="다음 캠페인">›</button>
        <div class="hero_pagination"><span data-hero-current>1</span> / ${heroSlides.length}</div>
      </section>

      <section class="st-brand-section band">
        <div class="st-brand-inner">
          <p class="st-brand-tagline">Built to <em>disappear</em><br>while you run</p>
          <p class="st-brand-desc">
            우리는 러너의 흐름을 방해하는 요소를 덜어냅니다.<br>
            땀, 햇빛, 머리카락처럼 작은 불편을 줄이는 액세서리만 선별했습니다.<br>
            ${BRAND.name}는 훈련 중 사라지는 착용감과 남는 기능을 기준으로 검증합니다.
          </p>
          <a href="${appHref("/about/about.html")}" class="outline_btn" data-link>DISCOVER MORE</a>
        </div>
      </section>

      <section class="st-new-section band">
        <h2 class="section_title">ALL PRODUCTS</h2>
        <div class="st-new-grid">
          ${products.filter((p) => p.tags.includes("new")).slice(0, 4).map((p) => productTile(p, "st-new")).join("")}
        </div>
        <a class="outline_btn st-new-viewall" href="${appHref("/category/new/44/")}" data-link>VIEW ALL</a>
      </section>

      <section class="st-cat-section band">
        <h2 class="section_title">SHOP BY CATEGORY</h2>
        <div class="st-cat-grid">
          ${categoryCard("acc", "러너윈 테크니컬 헤드밴드")}
        </div>
      </section>

      <section class="st-race-section band">
        <h2 class="section_title">UPCOMING RACES</h2>
        <div class="st-race-grid">
          ${races.map((race) => raceCard(race)).join("")}
          <div class="race_more_wrap"><a class="outline_btn" href="${appHref("/about/contents.html")}" data-link>더보기</a></div>
        </div>
      </section>
      ${footer()}
    `;
    initHero();
  }

  function renderCategory(slug) {
    const cat = categories[slug] || categories.acc;
    const safeSlug = categories[slug] ? slug : "acc";
    renderProductListShell(cat.title, "CATEGORY", categoryUrl(safeSlug));
    hydrateProductList({ category: safeSlug }, cat.title);
  }

  function renderSubCategory(cateNo) {
    const sub = subCategories[cateNo] || { title: "PRODUCT", match: () => true };
    renderProductListShell(sub.title, "SHOP", `/product/list.html?cate_no=${encodeURIComponent(cateNo || "")}`);
    hydrateProductList({ subCateNo: cateNo }, sub.title);
  }

  function renderSearchPage(keyword) {
    if (keyword && !state.searchHistory.includes(keyword)) {
      state.searchHistory = [keyword, ...state.searchHistory].slice(0, 5);
      saveState();
    }
    renderProductListShell(keyword ? `SEARCH: ${keyword}` : "SEARCH", "PRODUCT SEARCH", `/product/search.html?keyword=${encodeURIComponent(keyword)}`);
    hydrateProductList({ keyword }, "SEARCH");
  }

  function renderProductListShell(title, kicker, selfPath) {
    const saved = state.routeState[routeKey()] || {};
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">${escapeHtml(kicker)}</p>
              <h2 class="page_title">${escapeHtml(title)}</h2>
              <p class="origin_note">ORIGIN: ${escapeHtml(state.origin?.label || "HOME")}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref("/category/acc/25/")}" data-link>ACC</a>
            </div>
          </div>
          <div class="toolbar">
            <label>
              <span class="page_kicker">SORT</span>
              <select data-list-sort>
                <option value="new" ${saved.sort === "new" ? "selected" : ""}>NEW</option>
                <option value="price-asc" ${saved.sort === "price-asc" ? "selected" : ""}>LOW PRICE</option>
                <option value="price-desc" ${saved.sort === "price-desc" ? "selected" : ""}>HIGH PRICE</option>
              </select>
            </label>
          </div>
          <div data-list-root><div class="product_grid">${products.map(productCard).join("")}</div></div>
        </div>
      </section>
      ${footer()}
    `;
  }

  function hydrateProductList(filter, title) {
    const root = app.querySelector("[data-list-root]");
    const saved = state.routeState[routeKey()] || {};
    const sort = app.querySelector("[data-list-sort]")?.value || saved.sort || "new";
    state.routeState[routeKey()] = { ...saved, sort };
    saveState();
    try {
      const result = getProductList({ ...filter, sort });
      if (!result.length) {
        root.innerHTML = emptyState(
          `${title} 상품이 없습니다.`,
          "지금은 표시할 상품이 없습니다. 상품 상세로 이동해 흐름을 이어갈 수 있습니다.",
          [
            ["상품 보기", PRIMARY_PRODUCT_PATH],
            ["ACC", "/category/acc/25/"]
          ]
        );
        return;
      }
      root.innerHTML = `<div class="product_grid">${result.map(productCard).join("")}</div>`;
    } catch (error) {
      root.innerHTML = errorState(
        "상품 목록을 불러오지 못했습니다.",
        "네트워크나 저장소 상태를 다시 확인한 뒤 재시도할 수 있습니다.",
        [
          ["RETRY", getPath().replace(/([?&])state=error/, "")],
          ["HOME", "/index.html"]
        ]
      );
    }
  }

  async function renderProduct(path) {
    const parts = path.split("/").filter(Boolean);
    const id = parts[1] || parts[2];
    const product = await repo.getProduct(id);
    if (!product) {
      renderNotFound();
      return;
    }
    state.recentProducts = [product.id, ...state.recentProducts.filter((item) => item !== product.id)].slice(0, 6);
    saveState();
    trackEvent("ViewContent", {
      content_ids: [product.id],
      content_name: product.name,
      content_type: "product",
      value: product.price,
      currency: TRACKING.currency,
      landing_path: productUrl(product)
    });
    const savedDetail = state.routeState[routeKey()]?.detail || {};
    const selectedColor = savedDetail.color || product.colors[0];
    const selectedSize = savedDetail.size || product.sizes[0];
    const selectedQty = Math.max(1, Number(savedDetail.qty || 1));
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">PRODUCT DETAIL</p>
              <h2 class="page_title">${escapeHtml(product.category)}</h2>
              <p class="origin_note">ORIGIN: ${escapeHtml(state.origin?.label || "HOME")}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref(categoryUrl(product.category))}" data-link>RELATED CATEGORY</a>
            </div>
          </div>
          <div class="detail_grid">
            <div class="detail_media">
              ${productVisual(product, "detail")}
              <div class="image_status">
                <strong>${product.image ? "PRODUCT IMAGE" : "DETAIL IMAGE"}</strong>
                <span>${product.image ? "Runnerwin 상품 상세에 맞춘 대표 이미지입니다." : "Runnerwin 상세 이미지가 들어갈 영역입니다."}</span>
              </div>
            </div>
            <form class="detail_info" data-add-cart="${product.id}">
              <h2 class="detail_name">${escapeHtml(product.name)}</h2>
              <p class="detail_price">${WON.format(product.price)}</p>
              <p class="detail_desc">${escapeHtml(product.desc)}</p>
              <div class="detail_badges">
                ${product.bullets.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
              </div>
              <div class="option_group">
                <label>COLOR</label>
                <div class="color_row">
                  ${product.colors.map((color, index) => `
                    <label class="color_option color_option_${escapeHtml(color.toLowerCase())}">
                      <input name="color" type="radio" value="${escapeHtml(color)}" ${color === selectedColor || (!savedDetail.color && index === 0) ? "checked" : ""}>
                      <span>${escapeHtml(color)}</span>
                    </label>
                  `).join("")}
                </div>
              </div>
              <div class="option_group">
                <label>SIZE</label>
                <div class="size_row">
                  ${product.sizes.map((size, index) => `
                    <label><input name="size" type="radio" value="${size}" ${size === selectedSize || (!savedDetail.size && index === 0) ? "checked" : ""}><span>${size}</span></label>
                  `).join("")}
                </div>
              </div>
              <div class="option_group">
                <label>QTY</label>
                ${qtyControl(selectedQty)}
              </div>
              <div class="detail_actions">
                <button class="outline_btn direct_buy_btn" type="button" data-direct-buy>비회원으로 구매하기</button>
                <button class="solid_btn" type="submit">장바구니에 담기</button>
                <button class="npay_btn" type="button" data-npay-buy><span>N</span> pay 구매</button>
              </div>
            </form>
          </div>
          ${productDetailSections(product)}
          ${sampleReviews(product)}
          ${commonGuide()}
        </div>
      </section>
      ${footer()}
    `;
  }

  async function renderCart() {
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">CART</p>
              <h2 class="page_title">장바구니</h2>
              <p class="origin_note">ORIGIN: ${escapeHtml(state.origin?.label || "HOME")}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref(PRIMARY_PRODUCT_PATH)}" data-link>상품으로 돌아가기</a>
            </div>
          </div>
          <div data-cart-root>${loadingState("장바구니를 불러오는 중입니다.")}</div>
        </div>
      </section>
      ${footer()}
    `;
    const root = app.querySelector("[data-cart-root]");
    try {
      const cart = await repo.getCart();
      if (!cart.length) {
        root.innerHTML = emptyState(
          "장바구니가 비어 있습니다.",
          "상품 상세에서 장바구니에 담기를 누르거나 비회원 구매로 주문서를 작성할 수 있습니다.",
          [
            ["상품 보기", PRIMARY_PRODUCT_PATH],
            ["ACC", "/category/acc/25/"]
          ]
        );
        return;
      }
      const total = cart.reduce((sum, item) => sum + item.product.price * item.qty, 0);
      root.innerHTML = `
        <div class="cart_list">
          ${cart.map(cartItem).join("")}
        </div>
        <div class="cart_total"><span>주문 금액</span><span>${WON.format(total)}</span></div>
        <div class="cart_actions" style="margin-top:24px">
          <button class="solid_btn" type="button" data-checkout>구매하기</button>
          <a class="outline_btn" href="${appHref("/myshop/order/list.html")}" data-link>주문 내역</a>
        </div>
      `;
    } catch (error) {
      root.innerHTML = errorState("장바구니 상품을 불러오지 못했습니다.", "저장된 장바구니 상태를 다시 확인해 주세요.", [["RETRY", "/order/basket.html"], ["상품 보기", PRIMARY_PRODUCT_PATH]]);
    }
  }

  async function renderCheckout() {
    const cart = await repo.getCart();
    if (!cart.length) {
      app.innerHTML = `
        <section class="page_shell">
          <div class="page_inner">
            ${emptyState("주문서에 담긴 상품이 없습니다.", "상품을 선택하거나 장바구니로 돌아가 구매 흐름을 이어갈 수 있습니다.", [["상품 보기", PRIMARY_PRODUCT_PATH], ["장바구니", "/order/basket.html"]])}
          </div>
        </section>
        ${footer()}
      `;
      return;
    }
    const form = getCheckoutForm();
    const total = cart.reduce((sum, item) => sum + item.product.price * item.qty, 0);
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">CHECKOUT</p>
              <h2 class="page_title">주문서 작성</h2>
              <p class="origin_note">ORIGIN: ${escapeHtml(state.origin?.label || "CART")}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref("/order/basket.html")}" data-link>장바구니</a>
            </div>
          </div>

          <div class="checkout_layout">
            <aside class="checkout_summary" aria-label="주문 상품 요약">
              <h3>주문 상품</h3>
              <div class="cart_list">${cart.map(orderLineItem).join("")}</div>
              <div class="cart_total"><span>주문 금액</span><span>${WON.format(total)}</span></div>
            </aside>

            <form class="checkout_form" data-checkout-form>
              <h3>배송 정보</h3>
              ${checkoutInput("이름", "name", "홍길동", form.name, true)}
              ${checkoutInput("휴대폰 번호", "phone", "01012345678", form.phone, true)}
              ${checkoutInput("이메일", "email", "이메일 주소를 입력해주세요", form.email, true)}
              <div class="checkout_zip_row">
                ${checkoutInput("우편번호", "zipcode", "12345", form.zipcode, true)}
                <div class="checkout_address_group">
                  ${checkoutInput("기본 주소", "address", "도로명 주소", form.address, true)}
                  <button class="outline_btn checkout_address_btn" type="button" data-fill-address>주소 찾기</button>
                </div>
              </div>
              ${checkoutInput("상세 주소", "addressDetail", "동/호수 등 상세 주소", form.addressDetail, true)}
              <label class="checkout_field">
                <span>배송 요청사항</span>
                <textarea data-checkout-field="memo" rows="4" placeholder="요청사항이 있으면 입력해주세요">${escapeHtml(form.memo)}</textarea>
              </label>
              ${checkoutNotice()}
              <div class="checkout_checks">
                <label>
                  <input type="checkbox" data-checkout-field="agreeNotice" ${form.agreeNotice ? "checked" : ""} required>
                  <span>주문 접수 안내를 확인했습니다. <strong>필수</strong></span>
                </label>
                <label>
                  <input type="checkbox" data-checkout-field="agreeContact" ${form.agreeContact ? "checked" : ""}>
                  <span>구매 가능 일정 및 결제 안내 연락에 동의합니다. 선택</span>
                </label>
              </div>
              <div class="cart_actions checkout_actions">
                <button class="solid_btn" type="button" data-payment-gateway>결제 페이지로 이동하기</button>
                <a class="outline_btn" href="${appHref("/order/basket.html")}" data-link>장바구니로 돌아가기</a>
              </div>
            </form>
          </div>
        </div>
      </section>
      ${footer()}
    `;
  }

  async function renderCheckoutStart(params = new URLSearchParams()) {
    const productId = params.get("product") || "coolfit-wide-headband";
    const product = products.find((item) => item.id === productId) || products[0];
    const requestedColor = (params.get("color") || "BLACK").toUpperCase();
    const requestedSize = (params.get("size") || "FREE").toUpperCase();
    const color = product.colors.includes(requestedColor) ? requestedColor : product.colors[0];
    const size = product.sizes.includes(requestedSize) ? requestedSize : product.sizes[0];
    const qty = Math.max(1, Number(params.get("qty") || 1));
    const isTest = params.get("test") === "1";
    const marker = `checkout-start:${product.id}:${color}:${size}:${qty}:${isTest}`;

    state.origin = { path: PRIMARY_PRODUCT_PATH, label: "PRODUCT" };
    state.cart = [{ productId: product.id, color, size, qty }];
    state.trackingTest = isTest;
    saveState();

    try {
      if (!sessionStorage.getItem(marker)) {
        trackProductIntent("CheckoutPageView", product.id, color, size, qty, {
          source: "checkout_start_url",
          __test: isTest
        });
        sessionStorage.setItem(marker, "1");
      }
    } catch (error) {
      trackProductIntent("CheckoutPageView", product.id, color, size, qty, {
        source: "checkout_start_url",
        __test: isTest
      });
    }

    await renderCheckout();
  }

  function renderOrders() {
    const orders = state.orders || [];
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">MYSHOP</p>
              <h2 class="page_title">주문 내역</h2>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref(PRIMARY_PRODUCT_PATH)}" data-link>상품 보기</a>
            </div>
          </div>
          ${orders.length ? `
            <div class="order_list">
              ${orders.map((order) => `
                <a class="order_item" href="${appHref(`/myshop/order/detail.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>
                  <h3>${escapeHtml(order.id)}</h3>
                  <p>${escapeHtml(order.date)} / ${order.items.length} items / ${WON.format(order.total)}</p>
                  <span>상세 확인</span>
                </a>
              `).join("")}
            </div>
          ` : emptyState("주문 내역이 없습니다.", "상품 상세에서 구매를 완료하면 이곳에 기록됩니다.", [["상품 보기", PRIMARY_PRODUCT_PATH], ["ACC", "/category/acc/25/"]])}
        </div>
      </section>
      ${footer()}
    `;
  }

  function findOrder(orderId) {
    return (state.orders || []).find((order) => order.id === orderId);
  }

  function orderItems(order) {
    return (order?.items || []).map((item) => ({ ...item, product: products.find((product) => product.id === item.productId) })).filter((item) => item.product);
  }

  function orderTotal(items) {
    return items.reduce((sum, item) => sum + item.product.price * Number(item.qty || 1), 0);
  }

  function getCheckoutForm() {
    return { ...defaultCheckoutForm, ...(state.checkoutForm || {}) };
  }

  function checkoutInput(label, field, placeholder, value, required = false, scope = "checkout") {
    const dataAttr = scope === "edit" ? "data-edit-buyer-field" : "data-checkout-field";
    return `
      <label class="checkout_field">
        <span>${escapeHtml(label)}${required ? "<em>필수</em>" : ""}</span>
        <input ${dataAttr}="${escapeHtml(field)}" value="${escapeHtml(value || "")}" placeholder="${escapeHtml(placeholder)}" ${required ? "required" : ""}>
      </label>
    `;
  }

  function readCheckoutForm(form, scope = "checkout") {
    const selector = scope === "edit" ? "[data-edit-buyer-field]" : "[data-checkout-field]";
    const buyer = { ...defaultCheckoutForm };
    form.querySelectorAll(selector).forEach((field) => {
      const key = scope === "edit" ? field.dataset.editBuyerField : field.dataset.checkoutField;
      buyer[key] = field.type === "checkbox" ? field.checked : field.value.trim();
    });
    return buyer;
  }

  function checkoutNotice() {
    return `
      <section class="checkout_notice">
        <h3>주문 접수 안내</h3>
        <ul>
          <li>현재 주문 접수 단계이며 실제 결제는 진행되지 않습니다.</li>
          <li>주문 접수 후 구매 가능 일정과 결제 안내를 입력하신 연락처로 안내드립니다.</li>
          <li>N pay 구매 버튼은 추후 픽셀 연결 전까지 동작하지 않습니다.</li>
        </ul>
      </section>
    `;
  }

  function createOrder(cart, buyer) {
    const total = cart.reduce((sum, item) => sum + item.product.price * item.qty, 0);
    return {
      id: `TN-${Date.now().toString().slice(-8)}`,
      date: new Date().toLocaleDateString("ko-KR"),
      buyer,
      items: cart.map((item) => ({
        productId: item.productId,
        color: item.color || item.product.colors?.[0] || "BLACK",
        size: item.size,
        qty: item.qty
      })),
      total
    };
  }

  function buyerSummary(buyer = {}) {
    const info = { ...defaultCheckoutForm, ...buyer };
    if (!info.name && !info.phone && !info.address) return "";
    return `
      <section class="buyer_summary">
        <h3>배송 정보</h3>
        <dl>
          <div><dt>받는 분</dt><dd>${escapeHtml(info.name || "-")}</dd></div>
          <div><dt>연락처</dt><dd>${escapeHtml(info.phone || "-")}</dd></div>
          <div><dt>이메일</dt><dd>${escapeHtml(info.email || "-")}</dd></div>
          <div><dt>주소</dt><dd>${escapeHtml(`${info.zipcode ? `[${info.zipcode}] ` : ""}${info.address} ${info.addressDetail}`.trim() || "-")}</dd></div>
          <div><dt>요청사항</dt><dd>${escapeHtml(info.memo || "-")}</dd></div>
        </dl>
      </section>
    `;
  }

  function renderOrderComplete(orderId) {
    const order = findOrder(orderId);
    if (!order) {
      app.innerHTML = `<section class="page_shell"><div class="page_inner">${errorState("주문 완료 내역을 찾을 수 없습니다.", "내역으로 이동하거나 상품 상세에서 다시 구매할 수 있습니다.", [["주문 내역", "/myshop/order/list.html"], ["상품 보기", PRIMARY_PRODUCT_PATH]])}</div></section>${footer()}`;
      return;
    }
    const items = orderItems(order);
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="state_panel order_complete_panel">
            <div>
              <p class="page_kicker">ORDER COMPLETE</p>
              <h2>주문이 완료되었습니다.</h2>
              <p>${escapeHtml(order.id)} / ${escapeHtml(order.date)} / ${WON.format(order.total)}</p>
              <div class="state_actions">
                <a class="ghost_btn" href="${appHref(`/myshop/order/detail.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>주문 상세</a>
                <a class="ghost_btn" href="${appHref(`/myshop/order/edit.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>수정하기</a>
                ${resumeButton()}
              </div>
            </div>
          </div>
          <div class="cart_list">${items.map(orderLineItem).join("")}</div>
          ${buyerSummary(order.buyer)}
        </div>
      </section>
      ${footer()}
    `;
  }

  function renderOrderDetail(orderId) {
    const order = findOrder(orderId);
    if (!order) {
      app.innerHTML = `<section class="page_shell"><div class="page_inner">${errorState("주문 내역을 찾을 수 없습니다.", "내역 목록이나 상품 상세로 이동해 흐름을 이어갈 수 있습니다.", [["주문 내역", "/myshop/order/list.html"], ["상품 보기", PRIMARY_PRODUCT_PATH]])}</div></section>${footer()}`;
      return;
    }
    const items = orderItems(order);
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">ORDER DETAIL</p>
              <h2 class="page_title">주문 상세</h2>
              <p class="origin_note">${escapeHtml(order.id)} / ${escapeHtml(order.date)}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref("/myshop/order/list.html")}" data-link>주문 내역</a>
              <a class="ghost_btn" href="${appHref(`/myshop/order/edit.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>수정</a>
            </div>
          </div>
          <div class="cart_list">${items.map(orderLineItem).join("")}</div>
          <div class="cart_total"><span>주문 금액</span><span>${WON.format(order.total)}</span></div>
          ${buyerSummary(order.buyer)}
          <div class="cart_actions" style="margin-top:24px">
            <a class="outline_btn" href="${appHref(PRIMARY_PRODUCT_PATH)}" data-link>상품으로 복귀</a>
            <a class="solid_btn" href="${appHref("/myshop/order/list.html")}" data-link>주문 내역</a>
          </div>
        </div>
      </section>
      ${footer()}
    `;
  }

  function renderOrderEdit(orderId) {
    const order = findOrder(orderId);
    if (!order) {
      app.innerHTML = `<section class="page_shell"><div class="page_inner">${errorState("수정할 주문 내역을 찾을 수 없습니다.", "내역 목록으로 돌아가거나 상품 상세에서 다시 구매할 수 있습니다.", [["주문 내역", "/myshop/order/list.html"], ["상품 보기", PRIMARY_PRODUCT_PATH]])}</div></section>${footer()}`;
      return;
    }
    const items = orderItems(order);
    const buyer = { ...defaultCheckoutForm, ...(order.buyer || state.checkoutForm || {}) };
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">ORDER EDIT</p>
              <h2 class="page_title">주문 수정</h2>
              <p class="origin_note">${escapeHtml(order.id)} / ${escapeHtml(order.date)}</p>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref(`/myshop/order/detail.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>상세로 복귀</a>
            </div>
          </div>
          <form data-edit-order="${escapeHtml(order.id)}">
            <div class="cart_list">
              ${items.map((item) => `
                <article class="cart_item" data-edit-item="${escapeHtml(item.productId)}" data-color="${escapeHtml(item.color || item.product.colors?.[0] || "BLACK")}" data-size="${escapeHtml(item.size)}">
                  <a href="${appHref(productUrl(item.product))}" data-link>${productVisual(item.product, "cart")}</a>
                  <div>
                    <h3>${escapeHtml(item.product.name)}</h3>
                    <p>COLOR ${escapeHtml(item.color || item.product.colors?.[0] || "BLACK")} / SIZE ${escapeHtml(item.size)} / ${WON.format(item.product.price)}</p>
                    <label class="edit_qty_label">수량 <input type="number" min="1" value="${Number(item.qty || 1)}" data-edit-qty></label>
                  </div>
                </article>
              `).join("")}
            </div>
            <section class="checkout_form order_edit_form">
              <h3>배송 정보</h3>
              ${checkoutInput("이름", "name", "홍길동", buyer.name, true, "edit")}
              ${checkoutInput("휴대폰 번호", "phone", "01012345678", buyer.phone, true, "edit")}
              ${checkoutInput("이메일", "email", "이메일 주소를 입력해주세요", buyer.email, true, "edit")}
              <div class="checkout_zip_row">
                ${checkoutInput("우편번호", "zipcode", "12345", buyer.zipcode, true, "edit")}
                ${checkoutInput("기본 주소", "address", "도로명 주소", buyer.address, true, "edit")}
              </div>
              ${checkoutInput("상세 주소", "addressDetail", "동/호수 등 상세 주소", buyer.addressDetail, true, "edit")}
              <label class="checkout_field">
                <span>배송 요청사항</span>
                <textarea data-edit-buyer-field="memo" rows="4" placeholder="요청사항이 있으면 입력해주세요">${escapeHtml(buyer.memo)}</textarea>
              </label>
              <div class="checkout_checks">
                <label>
                  <input type="checkbox" data-edit-buyer-field="agreeNotice" ${buyer.agreeNotice ? "checked" : ""} required>
                  <span>주문 접수 안내를 확인했습니다. <strong>필수</strong></span>
                </label>
                <label>
                  <input type="checkbox" data-edit-buyer-field="agreeContact" ${buyer.agreeContact ? "checked" : ""}>
                  <span>구매 가능 일정 및 결제 안내 연락에 동의합니다. 선택</span>
                </label>
              </div>
            </section>
            <div class="cart_actions" style="margin-top:24px">
              <button class="solid_btn" type="submit">수정 저장</button>
              <a class="outline_btn" href="${appHref(`/myshop/order/detail.html?order_id=${encodeURIComponent(order.id)}`)}" data-link>취소</a>
            </div>
          </form>
        </div>
      </section>
      ${footer()}
    `;
  }

  function renderAccount() {
    const recent = state.recentProducts.map((id) => products.find((p) => p.id === id)).filter(Boolean);
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">MYSHOP</p>
              <h2 class="page_title">ACCOUNT</h2>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref("/myshop/order/list.html")}" data-link>ORDER</a>
            </div>
          </div>
          <div class="board_list">
            <article class="content_card">
              <h3>${escapeHtml(BRAND.name)} MEMBER</h3>
              <p>최근 본 상품, 주문 내역, 장바구니 상태가 이 브라우저에 저장됩니다.</p>
            </article>
          </div>
          <h3 class="section_title" style="margin-top:54px;text-align:left;font-size:28px">RECENTLY VIEWED</h3>
          ${recent.length ? `<div class="product_grid">${recent.map(productCard).join("")}</div>` : emptyState("최근 본 상품이 없습니다.", "상품 상세를 열면 최근 본 상품으로 남습니다.", [["ALL", "/category/new/44/"], ["상품 보기", PRIMARY_PRODUCT_PATH]])}
        </div>
      </section>
      ${footer()}
    `;
  }

  function renderBoard(boardNo) {
    const board = boards[boardNo] || boards[1];
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">COMMUNITY</p>
              <h2 class="page_title">${escapeHtml(board.title)}</h2>
            </div>
            <div class="page_actions">
              ${resumeButton()}
              <a class="ghost_btn" href="${appHref("/about/contents.html")}" data-link>CONTENTS</a>
            </div>
          </div>
          ${board.items.length ? `
            <div class="board_list">
              ${board.items.map((title, index) => `
                <a class="board_item" href="${appHref(`/board/free/read.html?board_no=${boardNo}&no=${index + 1}`)}" data-link>
                  <h3>${escapeHtml(title)}</h3>
                  <p>${escapeHtml(BRAND.name)} / 2026.05.${String(18 + index).padStart(2, "0")}</p>
                </a>
              `).join("")}
            </div>
          ` : emptyState("게시글이 없습니다.", "다른 커뮤니티 게시판이나 홈으로 이동할 수 있습니다.", [["NOTICE", "/board/free/list.html?board_no=1"], ["HOME", "/index.html"]])}
        </div>
      </section>
      ${footer()}
    `;
  }

  function renderAbout() {
    app.innerHTML = staticPage("ABOUT", "Built for serious distance runners.", `
      <div class="editorial_grid">
        <article class="editorial_card"><h3>LESS SWEAT,<br>MORE PACE</h3><p>흐르는 땀과 흔들리는 착용감을 줄여 훈련의 리듬을 지키는 액세서리를 선별합니다.</p></article>
        <article class="editorial_card"><h3>BUILT TO<br>STAY LIGHT</h3><p>착용했다는 감각보다 페이스와 호흡에 집중하게 만드는 낮은 무게감을 지향합니다.</p></article>
        <article class="editorial_card"><h3>SEOUL,<br>KOREA</h3><p>러너의 반복 훈련에서 불편했던 작은 지점을 제품 설명과 구매 흐름에 반영합니다.</p></article>
      </div>
    `, [["상품 보기", PRIMARY_PRODUCT_PATH], ["CONTENTS", "/about/contents.html"]]);
  }

  function renderCollection() {
    app.innerHTML = staticPage("COLLECTIONS", "Seasonal edits for training and race day.", `
      <div class="product_grid">${products.slice(0, 6).map(productCard).join("")}</div>
    `, [["ALL", "/category/new/44/"], ["ABOUT", "/about/about.html"]]);
  }

  function renderContents() {
    app.innerHTML = staticPage("CONTENTS", "Stories, races, and running notes.", `
      <div class="board_list">
        <article class="content_card"><h3>러너를 위한 액세서리 기준</h3><p>러닝 중 거슬리는 감각은 줄이고 필요한 기능만 남긴다.</p></article>
        <article class="content_card"><h3>UPCOMING RACES</h3><p>이번 주말 달릴 곳과 훈련 목표를 함께 확인한다.</p></article>
        <article class="content_card"><h3>RUN LOG</h3><p>꾸준히 달린 기록들이 다음 구매와 다음 훈련의 맥락이 된다.</p></article>
      </div>
    `, [["상품 보기", PRIMARY_PRODUCT_PATH], ["ALL", "/category/new/44/"]]);
  }

  function renderPolicy(title) {
    app.innerHTML = staticPage(title, `${BRAND.name} store information.`, `
      <div class="board_list">
        <article class="content_card"><h3>${escapeHtml(title)}</h3><p>운영 정책, 개인정보 처리, 배송 및 교환 기준을 확인할 수 있습니다.</p></article>
      </div>
    `, [["GUIDE", "/shopinfo/guide.html"], ["상품 보기", PRIMARY_PRODUCT_PATH]]);
  }

  function renderNotFound() {
    app.innerHTML = `
      <section class="page_shell">
        <div class="page_inner">
          ${errorState("페이지를 찾을 수 없습니다.", "등록되지 않은 주소입니다. 상품 상세로 이동할 수 있습니다.", [["상품 보기", PRIMARY_PRODUCT_PATH], ["ACC", "/category/acc/25/"]])}
        </div>
      </section>
      ${footer()}
    `;
  }

  function staticPage(title, lead, content, actions) {
    return `
      <section class="page_shell dark_shell">
        <div class="page_inner">
          <div class="page_head">
            <div>
              <p class="page_kicker">${escapeHtml(BRAND.name)}</p>
              <h2 class="page_title">${escapeHtml(title)}</h2>
              <p class="origin_note">${escapeHtml(lead)}</p>
            </div>
            <div class="page_actions">
              ${resumeButton(true)}
              ${actions.map(([label, href]) => href.startsWith("http") ? `<a class="outline_btn" href="${href}" target="_blank" rel="noreferrer">${label}</a>` : `<a class="outline_btn" href="${appHref(href)}" data-link>${label}</a>`).join("")}
            </div>
          </div>
          ${content}
        </div>
      </section>
      ${footer()}
    `;
  }

  function productVisual(product, size = "card") {
    if (product.image) {
      return `
        <div class="product_visual product_visual_${size} visual_${product.visual} has_image">
          <img class="product_image" src="${escapeHtml(assetUrl(product.image))}" alt="${escapeHtml(product.name)} 상품 이미지">
        </div>
      `;
    }
    return `
      <div class="product_visual product_visual_${size} visual_${product.visual}" role="img" aria-label="${escapeHtml(product.name)} 이미지 대체 슬롯">
        <span class="visual_shadow"></span>
        <span class="visual_shape"></span>
        <span class="visual_trim"></span>
        <span class="visual_label">${escapeHtml(product.visualLabel || product.name)}</span>
      </div>
    `;
  }

  function sectionVisual(product, section) {
    if (section.image) {
      const fitClass = section.imageFit ? ` image_fit_${escapeHtml(section.imageFit)}` : "";
      return `
        <div class="product_visual product_visual_section visual_${product.visual} has_image media_role_${escapeHtml(section.mediaRole || "detail")}${fitClass}">
          <img class="product_image" src="${escapeHtml(assetUrl(section.image))}" alt="${escapeHtml(product.name)} ${escapeHtml(section.role)}">
        </div>
      `;
    }
    if (section.mediaRole === "product-only" && product.image) {
      return productVisual(product, "section");
    }
    const label = {
      "human-wearing": "HUMAN WEARING SHOT",
      "product-only": "PRODUCT ONLY SHOT",
      "product-use": "PRODUCT USE SHOT",
      "feature-detail": "MATERIAL / DETAIL SHOT",
      "color-option": "COLOR OPTION SHOT",
      "review-guide": "REVIEW GUIDE BLOCK"
    }[section.mediaRole] || "DETAIL IMAGE";
    return `
      <div class="product_visual product_visual_section section_visual_role media_role_${escapeHtml(section.mediaRole || "detail")}" role="img" aria-label="${escapeHtml(product.name)} ${escapeHtml(section.role)} 생성 이미지 슬롯">
        <span class="role_scene"></span>
        <span class="role_product"></span>
        <span class="visual_label">${escapeHtml(label)}</span>
      </div>
    `;
  }

  function productDetailSections(product) {
    if (product.detailMode === "wide-headband") {
      return wideHeadbandDetail(product);
    }
    if (product.pilotSections) {
      return productPilotDetail(product);
    }
    return `
      <section class="detail_story" aria-label="상품 상세 정보">
        <div class="detail_story_head">
          <div>
            <p class="page_kicker">PRODUCT STORY</p>
            <h3>${escapeHtml(product.detailType)}</h3>
          </div>
          <p>${escapeHtml(product.detailLead || "러닝 중 필요한 기능을 이미지와 문구로 확인할 수 있습니다.")}</p>
        </div>
        <div class="detail_section_grid">
          ${product.sections.map((section, index) => `
            <article class="detail_section_card">
              ${sectionVisual(product, section)}
              <p class="page_kicker">${String(index + 1).padStart(2, "0")} / ${escapeHtml(section.role)}</p>
              <h4>${escapeHtml(section.title)}</h4>
              <p>${escapeHtml(section.body)}</p>
            </article>
          `).join("")}
        </div>
      </section>
    `;
  }

  function imageNeed(product, label, mediaRole = "feature-detail") {
    return sectionVisual(product, { role: label, mediaRole });
  }

  function wideHeadbandDetail(product) {
    const assets = {
      wearing: "/assets/images/runnerwin-wide-headband-main.png",
      stretch: "/assets/images/runnerwin-wide-headband-stretch.png",
      white: "/assets/images/runnerwin-wide-headband-white-product.jpg",
      black: "/assets/images/runnerwin-wide-headband-black-product.jpg"
    };
    const wideImage = (role, image, mediaRole = "feature-detail", imageFit = "contain") => sectionVisual(product, { role, mediaRole, image, imageFit });
    const keyPoints = [
      ["와이드 커버", "헤어라인과 이마를 넓게 감싸 흐르는 땀을 먼저 받아줍니다."],
      ["빠른 흡수감", "넓은 면적의 원단이 땀을 분산시켜 눈가로 바로 흐르는 불편을 줄입니다."],
      ["부드러운 텐션", "머리 둘레에 맞게 늘어나고 오래 착용해도 조임 부담을 낮춥니다."],
      ["야외 커버", "햇빛이 강한 러닝에서도 이마 주변 노출 부담을 줄이는 폭감입니다."],
      ["쉬운 관리", "운동 후 손세탁하고 가볍게 말려 반복 훈련에 다시 사용할 수 있습니다."]
    ];
    const benefits = [
      "운동이나 야외 활동 중 이마를 넓게 커버",
      "땀이 눈으로 바로 흐르는 불편 감소",
      "부드러운 안감으로 피부 자극 부담 완화",
      "땀과 수분을 빠르게 받아주는 넓은 흡수 면적",
      "머리카락을 눌러 정리해주는 안정적인 착용감",
      "반복 착용을 고려한 손쉬운 세탁 관리"
    ];
    const faq = [
      ["땀이 많은 사람도 사용할 수 있나요?", "넓은 면적으로 땀을 받아주도록 설계했습니다. 장시간 고강도 운동으로 충분히 젖었을 때는 한 번 짜서 다시 착용하는 방식이 좋습니다."],
      ["머리가 작거나 큰 편이어도 괜찮나요?", "FREE 사이즈 기준의 신축 원단입니다. 처음 착용할 때는 머리 둘레에 맞게 가볍게 늘려 텐션을 맞춘 뒤 사용하는 편이 좋습니다."],
      ["어떤 운동에 쓰기 좋나요?", "러닝, 헬스, 테니스, 등산처럼 땀이 얼굴 쪽으로 흐르기 쉬운 운동에 잘 맞습니다. 모자 안에 함께 착용해도 부담이 적은 편입니다."]
    ];
    const productInfo = [
      ["상품명", "러너윈 테크니컬 헤드밴드"],
      ["모델명", "RWHB-W01"],
      ["소재", "겉감 폴리에스터/스판덱스 혼방, 안감 나일론/스판덱스 혼방"],
      ["색상", "블랙, 화이트"],
      ["사이즈", "FREE / 약 23.5cm, 넓은 폭 약 12cm, 좁은 폭 약 4.5cm"],
      ["제조국", "중국 OEM"],
      ["관리법", "중성세제 단독 손세탁, 그늘 건조, 표백제/건조기 사용 금지"]
    ];

    return `
      <section class="wide_detail" aria-label="${escapeHtml(product.name)} 상세페이지">
        <div class="wide_intro">
          <p class="page_kicker">RUNNERWIN DETAIL</p>
          <h3>땀은 넓게 받고, 착용감은 가볍게</h3>
          <p>이마와 헤어라인을 넓게 감싸고, 부드러운 신축 원단으로 러닝 중 흔들림과 압박감을 줄이는 와이드 헤드밴드입니다.</p>
        </div>

        <article class="wide_image_band wide_hero_band">
          ${wideImage("파란 배경 사람 착용컷", assets.wearing, "human-wearing", "cover")}
          <div class="wide_copy">
            <p class="page_kicker">01 / WIDE FIT</p>
            <h4>이마와 헤어라인을 넓게 감싸는 테크니컬 폭</h4>
            <p>좁은 밴드처럼 한 줄로 누르는 느낌보다 넓은 면으로 안정감 있게 감싸주는 구조입니다. 머리카락이 내려오는 불편과 땀이 눈가로 흐르는 상황을 줄이는 방향으로 설계된 와이드 헤드밴드입니다.</p>
            <ul class="wide_inline_list">
              <li>러닝 중 땀 흐름 완화</li>
              <li>앞머리·잔머리 정리</li>
              <li>얼굴 라인에 과하지 않은 폭감</li>
            </ul>
          </div>
        </article>

        <section class="wide_key_points" aria-label="핵심 기능">
          ${keyPoints.map(([title, body], index) => `
            <article>
              <span>${String(index + 1).padStart(2, "0")}</span>
              <h4>${escapeHtml(title)}</h4>
              <p>${escapeHtml(body)}</p>
            </article>
          `).join("")}
        </section>

        <article class="wide_text_block">
          <p class="page_kicker">02 / SWEAT CONTROL</p>
          <h4>땀이 얼굴로 흐르기 전에 넓은 면적으로 먼저 흡수</h4>
          <p>와이드 헤드밴드의 핵심은 땀을 완전히 없애는 것이 아니라, 얼굴로 흘러내리기 전 넓은 원단 면적이 한 번 받아주는 데 있습니다. 빠른 페이스, 실내 웨이트, 더운 날 야외 러닝처럼 땀이 집중되는 상황에서 시야 방해를 줄여줍니다.</p>
          <div class="wide_specs">
            <span>SWEAT CONTROL</span>
            <span>WIDE COVER</span>
            <span>QUICK CARE</span>
            <span>FREE SIZE</span>
          </div>
        </article>

        <div class="wide_feature_stack">
          <article class="wide_feature_row is_reverse">
            <div class="wide_copy">
              <p class="page_kicker">03 / ELASTIC FIT</p>
              <h4>양손으로 당겼을 때 확인되는 부드러운 신축성</h4>
              <p>스트레치 사진은 이 상품의 착용감을 설명하는 핵심 컷입니다. 머리를 강하게 조이는 방식이 아니라, 원단이 늘어나며 둘레에 맞춰지는 구조라 오래 착용해도 부담을 줄여줍니다.</p>
            </div>
            ${wideImage("스트레치 사진", assets.stretch, "feature-detail", "cover")}
          </article>

          <article class="wide_feature_row">
            <div class="wide_copy">
              <p class="page_kicker">04 / OUTDOOR COVER</p>
              <h4>러닝, 헬스, 야외 활동까지 이어지는 착용 장면</h4>
              <p>얼굴 라인을 과하게 덮지 않으면서 이마를 안정적으로 감싸줍니다. 러닝 전후 이동이나 가벼운 야외 활동에도 자연스럽게 이어지는 실루엣입니다.</p>
            </div>
            ${wideImage("화이트 제품 단독컷", assets.white, "product-only")}
          </article>
        </div>

        <section class="wide_check_panel">
          <div>
            <p class="page_kicker">05 / DAILY BENEFIT</p>
            <h4>Runnerwin 와이드 헤드밴드가 필요한 순간</h4>
          </div>
          <ul>
            ${benefits.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>

        <section class="wide_colors" aria-label="색상 옵션">
          <div class="wide_section_head">
            <p class="page_kicker">06 / COLOR</p>
            <h4>블랙과 화이트, 가장 기본적인 두 가지 선택</h4>
          </div>
          <div class="wide_color_grid">
            <article>
              ${wideImage("블랙 색상 옵션컷", assets.black, "color-option")}
              <h5>블랙</h5>
              <p>운동복과 가장 쉽게 맞는 기본 컬러입니다.</p>
            </article>
            <article>
              ${wideImage("화이트 색상 옵션컷", assets.white, "color-option")}
              <h5>화이트</h5>
              <p>밝은 러닝웨어나 여름 야외 활동에 잘 어울립니다.</p>
            </article>
          </div>
        </section>

        <article class="wide_text_block">
          <p class="page_kicker">07 / WIDTH CONTROL</p>
          <h4>넓게 펼쳐 쓰고, 필요하면 접어서 조절</h4>
          <p>와이드 폭을 그대로 사용하면 이마를 넓게 덮을 수 있고, 코디나 운동 강도에 따라 접어 쓰면 더 단정한 폭으로 착용할 수 있습니다. 하나의 제품으로 커버감과 스타일을 조절하는 구조입니다.</p>
        </article>

        <section class="wide_size_care">
          <article>
            <p class="page_kicker">08 / SIZE INFO</p>
            <h4>사이즈 정보</h4>
            <div class="size_diagram" aria-label="와이드 헤드밴드 사이즈 도식">
              <span class="size_shape"></span>
              <span class="size_w">23.5cm</span>
              <span class="size_h">12cm</span>
              <span class="size_s">4.5cm</span>
            </div>
          </article>
          <article>
            <p class="page_kicker">09 / CARE</p>
            <h4>세탁 주의사항</h4>
            <ul>
              <li>첫 세탁은 단독 세탁을 권장합니다.</li>
              <li>중성세제로 가볍게 손세탁해 주세요.</li>
              <li>표백제와 드라이클리닝은 피해주세요.</li>
              <li>형태 유지를 위해 그늘에서 자연 건조해 주세요.</li>
            </ul>
          </article>
        </section>

        <section class="wide_faq">
          <p class="page_kicker">10 / FAQ</p>
          <h4>자주 묻는 질문</h4>
          ${faq.map(([question, answer]) => `
            <article>
              <h5>${escapeHtml(question)}</h5>
              <p>${escapeHtml(answer)}</p>
            </article>
          `).join("")}
        </section>

        <section class="wide_product_info">
          <p class="page_kicker">11 / PRODUCT INFO</p>
          <h4>제품 정보</h4>
          <table>
            <tbody>
              ${productInfo.map(([label, value]) => `
                <tr>
                  <th scope="row">${escapeHtml(label)}</th>
                  <td>${escapeHtml(value)}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </section>
      </section>
    `;
  }

  function productPilotDetail(product) {
    const featureItems = [
      ["통기성", "열이 머무는 시간을 줄이는 가벼운 패널"],
      ["시야 안정", "챙은 낮게, 움직임은 가볍게"],
      ["조절식 핏", "후면 스트랩으로 맞추는 밀착감"]
    ];
    return `
      <section class="pilot_detail" aria-label="${escapeHtml(product.name)} 상세 정보">
        <div class="pilot_intro">
          <p class="page_kicker">RUNNERWIN PILOT DETAIL</p>
          <h3>낮게 쓰고 오래 달리는 올라운드 캡</h3>
          <p>가볍게 눌러 쓰는 실루엣, 달릴 때의 시야, 운동 후 관리까지 러너가 실제로 확인하는 순서로 정리했습니다.</p>
        </div>

        <article class="pilot_hero_section">
          ${sectionVisual(product, product.pilotSections[0])}
          <div>
            <p class="page_kicker">RUNNING FIT</p>
            <h4>${escapeHtml(product.pilotSections[0].title)}</h4>
            <p>${escapeHtml(product.pilotSections[0].body)}</p>
          </div>
        </article>

        <div class="pilot_feature_strip">
          ${featureItems.map(([title, body]) => `
            <article>
              <h4>${escapeHtml(title)}</h4>
              <p>${escapeHtml(body)}</p>
            </article>
          `).join("")}
        </div>

        <div class="pilot_section_stack">
          ${product.pilotSections.slice(1, 7).map((section, index) => `
            <article class="pilot_story_row ${index % 2 ? "is_reverse" : ""}">
              ${sectionVisual(product, section)}
              <div class="pilot_story_copy">
                <p class="page_kicker">${escapeHtml(section.role)}</p>
                <h4>${escapeHtml(section.title)}</h4>
                <p>${escapeHtml(section.body)}</p>
              </div>
            </article>
          `).join("")}
        </div>

        <article class="pilot_review_summary">
          <div>
            <p class="page_kicker">SAMPLE REVIEW GUIDE</p>
            <h4>${escapeHtml(product.pilotSections[7].title)}</h4>
            <p>${escapeHtml(product.pilotSections[7].body)}</p>
          </div>
          <ul>
            <li>가볍고 오래 써도 답답하지 않다는 반응</li>
            <li>챙 각도가 러닝 중 시야를 크게 막지 않는다는 반응</li>
            <li>후면 조절이 쉬워 머리 둘레에 맞추기 편하다는 반응</li>
          </ul>
        </article>
      </section>
    `;
  }

  function sampleReviews(product) {
    return `
      <section class="review_section" aria-label="검증용 샘플 후기">
        <div class="review_head">
          <div>
            <p class="page_kicker">SAMPLE REVIEW</p>
            <h3>검증용 샘플 후기</h3>
            <p>실제 고객 후기가 아닌 전환 구조 확인용 샘플 데이터입니다.</p>
          </div>
          <button class="ghost_btn" type="button">REVIEW BOARD</button>
        </div>
        <div class="review_grid">
          ${product.reviews.map((review) => `
            <article class="review_card">
              <div class="stars" aria-label="별점 5점">★★★★★</div>
              <p>${escapeHtml(review.text)}</p>
              <span>${escapeHtml(review.name)} / ${escapeHtml(review.date)}</span>
            </article>
          `).join("")}
        </div>
      </section>
    `;
  }

  function commonGuide() {
    return `
      <section class="common_guide" aria-label="공통 구매 안내">
        <div class="guide_grid">
          <article>
            <p class="page_kicker">DELIVERY</p>
            <h3>배송 안내</h3>
            <p>평일 기준 결제 다음 영업일부터 순차 출고됩니다. 도서산간 지역은 추가 기간이 필요할 수 있습니다.</p>
          </article>
          <article>
            <p class="page_kicker">EXCHANGE</p>
            <h3>교환/반품</h3>
            <p>착용 흔적, 세탁, 패키지 훼손이 없는 상품은 수령 후 7일 이내 접수할 수 있습니다.</p>
          </article>
          <article>
            <p class="page_kicker">CARE</p>
            <h3>세탁/관리</h3>
            <p>미지근한 물에 단독 손세탁 후 그늘에서 말려주세요. 건조기와 표백제 사용은 피해주세요.</p>
          </article>
          <article>
            <p class="page_kicker">FAQ</p>
            <h3>자주 묻는 질문</h3>
            <p>헤드웨어는 FREE 사이즈 기준이며, 착용 전 스트랩과 원단 텐션을 먼저 맞춘 뒤 사용해 주세요.</p>
          </article>
        </div>
      </section>
    `;
  }

  function productTile(product) {
    return `
      <a href="${appHref(productUrl(product))}" class="st-new-item">
        <div class="st-new-img-wrap">${productVisual(product, "tile")}</div>
        <p class="st-new-name">${escapeHtml(product.name)}</p>
      </a>
    `;
  }

  function productCard(product) {
    return `
      <article class="product_card_wrap">
        <a class="product_card" href="${appHref(productUrl(product))}">
          <div class="product_thumb">${productVisual(product, "card")}</div>
          <div class="product_meta">
            <h3 class="product_name">${escapeHtml(product.name)}</h3>
            <p class="product_price">${WON.format(product.price)}</p>
          </div>
        </a>
      </article>
    `;
  }

  function categoryCard(slug, desc) {
    const cat = categories[slug];
    return `
      <a class="st-cat-item" href="${appHref(categoryUrl(slug))}" data-link>
        <div class="st-cat-img-wrap">
          <div class="category_visual category_${slug}" role="img" aria-label="${cat.title} 카테고리 이미지 슬롯">
            <span>${cat.title}</span>
          </div>
        </div>
        <p class="st-cat-name">${cat.title}</p>
        <p class="st-cat-desc">${escapeHtml(desc)}</p>
      </a>
    `;
  }

  function raceCard(race) {
    const attrs = race.url.startsWith("http") ? `href="${race.url}" target="_blank" rel="noreferrer"` : `href="${appHref(race.url)}" data-link`;
    return `
      <a class="st-race-card" ${attrs}>
        <span class="st-race-date">${escapeHtml(race.date)}</span>
        <h3 class="st-race-name">${escapeHtml(race.name)}</h3>
        <div class="st-race-info">${escapeHtml(race.info)}</div>
      </a>
    `;
  }

  function cartItem(item) {
    const color = item.color || item.product.colors?.[0] || "BLACK";
    return `
      <article class="cart_item" data-cart-item="${item.productId}" data-color="${escapeHtml(color)}" data-size="${item.size}">
        <a href="${appHref(productUrl(item.product))}" data-link>${productVisual(item.product, "cart")}</a>
        <div>
          <h3>${escapeHtml(item.product.name)}</h3>
          <p>COLOR ${escapeHtml(color)} / SIZE ${escapeHtml(item.size)} / ${WON.format(item.product.price)}</p>
          ${qtyControl(item.qty)}
        </div>
        <div class="cart_actions">
          <button class="ghost_btn" type="button" data-remove-cart>REMOVE</button>
        </div>
      </article>
    `;
  }

  function orderLineItem(item) {
    const color = item.color || item.product.colors?.[0] || "BLACK";
    return `
      <article class="cart_item">
        <a href="${appHref(productUrl(item.product))}" data-link>${productVisual(item.product, "cart")}</a>
        <div>
          <h3>${escapeHtml(item.product.name)}</h3>
          <p>COLOR ${escapeHtml(color)} / SIZE ${escapeHtml(item.size)} / QTY ${Number(item.qty || 1)} / ${WON.format(item.product.price * Number(item.qty || 1))}</p>
        </div>
      </article>
    `;
  }

  function qtyControl(value) {
    return `
      <div class="qty_control">
        <button type="button" data-qty-dec aria-label="수량 감소">-</button>
        <input type="number" min="1" value="${Number(value) || 1}" data-qty-input aria-label="수량">
        <button type="button" data-qty-inc aria-label="수량 증가">+</button>
      </div>
    `;
  }

  function loadingState(message) {
    return `<div class="state_panel"><div><h2>LOADING</h2><p>${escapeHtml(message)}</p></div></div>`;
  }

  function emptyState(title, message, actions) {
    return `
      <div class="state_panel">
        <div>
          <h2>${escapeHtml(title)}</h2>
          <p>${escapeHtml(message)}</p>
          <div class="state_actions">
            ${actions.map(([label, href]) => `<a class="ghost_btn" href="${appHref(href)}" data-link>${label}</a>`).join("")}
          </div>
        </div>
      </div>
    `;
  }

  function errorState(title, message, actions) {
    return `
      <div class="state_panel">
        <div>
          <h2>${escapeHtml(title)}</h2>
          <p>${escapeHtml(message)}</p>
          <div class="state_actions">
            ${actions.map(([label, href]) => `<a class="ghost_btn" href="${appHref(href)}" data-link>${label}</a>`).join("")}
          </div>
        </div>
      </div>
    `;
  }

  function footer() {
    return `
      <footer id="footer" class="band">
        <div class="inner">
          <div class="company_info">
            <p>회사명 : 잇템몰(ITTEMMALL)</p>
            <nav class="footer_menu" aria-label="하단 메뉴">
              <span>회사소개</span>
              <span>이용약관</span>
              <span>개인정보처리방침</span>
              <span>고객센터</span>
            </nav>
            <p>@2026 ITTEMMALL All rights reserved.</p>
          </div>
        </div>
      </footer>
    `;
  }

  function initHero() {
    let index = 0;
    const slides = [...document.querySelectorAll("[data-hero-slide]")];
    const current = document.querySelector("[data-hero-current]");
    const show = (next) => {
      index = (next + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => slide.classList.toggle("is_active", slideIndex === index));
      if (current) current.textContent = String(index + 1);
    };
    document.querySelector("[data-hero-prev]")?.addEventListener("click", () => show(index - 1));
    document.querySelector("[data-hero-next]")?.addEventListener("click", () => show(index + 1));
    heroTimer = window.setInterval(() => show(index + 1), 5200);
  }

  function bindPageControls() {
    app.querySelectorAll("[data-list-sort]").forEach((select) => {
      select.addEventListener("change", () => {
        state.routeState[routeKey()] = { ...(state.routeState[routeKey()] || {}), sort: select.value, scrollY: window.scrollY };
        saveState();
        render({ restoreScroll: true });
      });
    });

    app.querySelectorAll("[data-add-cart]").forEach((form) => {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        saveDetailForm(form);
        const productId = form.getAttribute("data-add-cart");
        const color = form.querySelector("input[name=color]:checked")?.value || "BLACK";
        const size = form.querySelector("input[name=size]:checked")?.value || "FREE";
        const qty = Math.max(1, Number(form.querySelector("[data-qty-input]")?.value || 1));
        addCart(productId, color, size, qty);
        trackProductIntent("AddToCart", productId, color, size, qty);
        toast("장바구니에 담았습니다.");
      });
      form.querySelectorAll("input[name=color]").forEach((input) => {
        input.addEventListener("change", () => saveDetailForm(form));
      });
      form.querySelectorAll("input[name=size]").forEach((input) => {
        input.addEventListener("change", () => saveDetailForm(form));
      });
    });

    app.querySelectorAll("[data-direct-buy]").forEach((button) => {
      button.addEventListener("click", () => {
        const form = button.closest("[data-add-cart]");
        if (!form) return;
        saveDetailForm(form);
        const productId = form.getAttribute("data-add-cart");
        const color = form.querySelector("input[name=color]:checked")?.value || "BLACK";
        const size = form.querySelector("input[name=size]:checked")?.value || "FREE";
        const qty = Math.max(1, Number(form.querySelector("[data-qty-input]")?.value || 1));
        trackProductIntent("CheckoutStartClick", productId, color, size, qty, {
          source: "direct_buy_button"
        });
        startGuestCheckout(productId, color, size, qty, { origin: false });
      });
    });

    app.querySelectorAll("[data-npay-buy]").forEach((button) => {
      button.addEventListener("click", () => {
        const form = button.closest("[data-add-cart]");
        if (!form) return;
        saveDetailForm(form);
        const productId = form.getAttribute("data-add-cart");
        const color = form.querySelector("input[name=color]:checked")?.value || "BLACK";
        const size = form.querySelector("input[name=size]:checked")?.value || "FREE";
        const qty = Math.max(1, Number(form.querySelector("[data-qty-input]")?.value || 1));
        trackProductIntent("NpayClick", productId, color, size, qty);
      });
    });

    app.querySelectorAll("[data-qty-inc]").forEach((button) => {
      button.addEventListener("click", () => {
        const input = button.parentElement.querySelector("[data-qty-input]");
        input.value = Number(input.value || 1) + 1;
        updateCartQtyFromControl(button);
        const form = button.closest("[data-add-cart]");
        if (form) saveDetailForm(form);
      });
    });

    app.querySelectorAll("[data-qty-dec]").forEach((button) => {
      button.addEventListener("click", () => {
        const input = button.parentElement.querySelector("[data-qty-input]");
        input.value = Math.max(1, Number(input.value || 1) - 1);
        updateCartQtyFromControl(button);
        const form = button.closest("[data-add-cart]");
        if (form) saveDetailForm(form);
      });
    });

    app.querySelectorAll("[data-qty-input]").forEach((input) => {
      input.addEventListener("change", () => {
        input.value = Math.max(1, Number(input.value || 1));
        updateCartQtyFromControl(input);
        const form = input.closest("[data-add-cart]");
        if (form) saveDetailForm(form);
      });
    });

    app.querySelectorAll("[data-remove-cart]").forEach((button) => {
      button.addEventListener("click", () => {
        const item = button.closest("[data-cart-item]");
        state.cart = state.cart.filter((cartItem) => !(cartItem.productId === item.dataset.cartItem && (cartItem.color || "BLACK") === (item.dataset.color || "BLACK") && cartItem.size === item.dataset.size));
        saveState();
        render({ restoreScroll: true });
      });
    });

    app.querySelector("[data-checkout]")?.addEventListener("click", () => {
      repo.getCart().then((cart) => {
        if (!cart.length) return;
        const value = cart.reduce((sum, item) => sum + item.product.price * item.qty, 0);
        trackEvent("CheckoutStartClick", {
          content_ids: cart.map((item) => item.productId),
          content_name: "Cart checkout",
          content_type: "product_group",
          value,
          currency: TRACKING.currency,
          source: "cart"
        });
        navigate("/order/checkout.html", { origin: false });
      });
    });

    app.querySelector("[data-checkout-form]")?.addEventListener("input", (event) => {
      const field = event.target.closest("[data-checkout-field]");
      if (!field) return;
      const value = field.type === "checkbox" ? field.checked : field.value;
      const previous = state.checkoutForm || {};
      state.checkoutForm = { ...getCheckoutForm(), [field.dataset.checkoutField]: value };
      saveState();
      if (!previous.__formStarted && String(value).trim()) {
        state.checkoutForm.__formStarted = true;
        saveState();
        trackEvent("CheckoutFormStart", {
          field: field.dataset.checkoutField,
          content_name: "Runnerwin checkout form",
          currency: TRACKING.currency
        });
      }
    });

    app.querySelector("[data-fill-address]")?.addEventListener("click", () => {
      state.checkoutForm = {
        ...getCheckoutForm(),
        zipcode: "06134",
        address: "서울특별시 강남구 테헤란로 123"
      };
      saveState();
      render({ restoreScroll: true });
    });

    app.querySelector("[data-payment-gateway]")?.addEventListener("click", () => {
      const form = app.querySelector("[data-checkout-form]");
      if (form && !form.checkValidity()) {
        form.reportValidity();
        return;
      }
      if (form) state.checkoutForm = readCheckoutForm(form, "checkout");
      saveState();
      repo.getCart().then((cart) => {
        const value = cart.reduce((sum, item) => sum + item.product.price * item.qty, 0);
        const paymentPayload = {
          content_ids: cart.map((item) => item.productId),
          content_name: "Headband payment page button",
          content_type: "product_group",
          value,
          currency: TRACKING.currency,
          source: "payment_gateway_button",
          __test: state.trackingTest === true
        };
        trackEvent("PaymentGatewayClick", {
          content_ids: paymentPayload.content_ids,
          content_name: "Payment gateway placeholder",
          content_type: "product_group",
          value,
          currency: TRACKING.currency,
          source: "payment_gateway_button",
          __test: state.trackingTest === true
        });
        const primaryPaymentItem = cart.find((item) => item.productId === "coolfit-wide-headband") || cart[0];
        const productPaymentPath = primaryPaymentItem?.productId === "coolfit-wide-headband"
          ? "/payment/headband/"
          : `/payment/${primaryPaymentItem?.productId || "headband"}/`;
        const paymentPath = `${productPaymentPath}${state.trackingTest === true ? "?test=1" : ""}`;
        window.setTimeout(() => {
          window.location.href = appHref(paymentPath);
        }, 280);
      });
    });

    app.querySelector("[data-checkout-form]")?.addEventListener("submit", (event) => {
      event.preventDefault();
      state.checkoutForm = readCheckoutForm(event.currentTarget, "checkout");
      saveState();
    });

    app.querySelector("[data-edit-order]")?.addEventListener("submit", (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      const orderId = form.getAttribute("data-edit-order");
      const order = findOrder(orderId);
      if (!order) return;
      const items = [...form.querySelectorAll("[data-edit-item]")].map((row) => ({
        productId: row.getAttribute("data-edit-item"),
        color: row.getAttribute("data-color") || "BLACK",
        size: row.getAttribute("data-size") || "FREE",
        qty: Math.max(1, Number(row.querySelector("[data-edit-qty]")?.value || 1))
      }));
      const buyer = readCheckoutForm(form, "edit");
      const hydrated = items.map((item) => ({ ...item, product: products.find((product) => product.id === item.productId) })).filter((item) => item.product);
      order.items = items;
      order.buyer = buyer;
      order.total = orderTotal(hydrated);
      order.updatedAt = new Date().toLocaleDateString("ko-KR");
      saveState();
      navigate(`/myshop/order/detail.html?order_id=${encodeURIComponent(order.id)}`, { origin: false });
    });
  }

  function updateCartQtyFromControl(control) {
    const item = control.closest("[data-cart-item]");
    if (!item) return;
    const input = item.querySelector("[data-qty-input]");
    state.cart = state.cart.map((cartItem) => {
      if (cartItem.productId === item.dataset.cartItem && (cartItem.color || "BLACK") === (item.dataset.color || "BLACK") && cartItem.size === item.dataset.size) {
        return { ...cartItem, qty: Math.max(1, Number(input.value || 1)) };
      }
      return cartItem;
    });
    saveState();
    render({ restoreScroll: true });
  }

  function saveDetailForm(form) {
    const key = routeKey();
    state.routeState[key] = {
      ...(state.routeState[key] || {}),
      detail: {
        color: form.querySelector("input[name=color]:checked")?.value || "BLACK",
        size: form.querySelector("input[name=size]:checked")?.value || "FREE",
        qty: Math.max(1, Number(form.querySelector("[data-qty-input]")?.value || 1))
      }
    };
    saveState();
    const productId = form.getAttribute("data-add-cart");
    const color = form.querySelector("input[name=color]:checked")?.value || "BLACK";
    const size = form.querySelector("input[name=size]:checked")?.value || "FREE";
    const qty = Math.max(1, Number(form.querySelector("[data-qty-input]")?.value || 1));
    trackProductIntent("OptionSelect", productId, color, size, qty);
  }

  function addCart(productId, color, size, qty) {
    const found = state.cart.find((item) => item.productId === productId && (item.color || "BLACK") === color && item.size === size);
    if (found) found.qty += qty;
    else state.cart.push({ productId, color, size, qty });
    saveState();
  }

  function startGuestCheckout(productId, color = "BLACK", size = "FREE", qty = 1, options = {}) {
    state.cart = [{ productId, color, size, qty: Math.max(1, Number(qty || 1)) }];
    saveState();
    navigate("/order/checkout.html", options);
  }

  function trackingPayloadForProduct(productId, color = "BLACK", size = "FREE", qty = 1, extra = {}) {
    const product = products.find((item) => item.id === productId);
    return {
      content_ids: [productId],
      content_name: product?.name || productId,
      content_type: "product",
      color,
      size,
      quantity: qty,
      value: product ? product.price * qty : 0,
      currency: TRACKING.currency,
      ...extra
    };
  }

  function trackProductIntent(eventName, productId, color, size, qty, extra = {}) {
    trackEvent(eventName, trackingPayloadForProduct(productId, color, size, qty, extra));
  }

  function trackEvent(eventName, payload = {}) {
    const event = {
      event: eventName,
      payload,
      path: getPath(),
      url: window.location.href,
      referrer: document.referrer || "",
      attribution: getAttribution(),
      timestamp: new Date().toISOString()
    };
    try {
      const current = JSON.parse(localStorage.getItem(TRACKING_KEY) || "[]");
      localStorage.setItem(TRACKING_KEY, JSON.stringify([event, ...current].slice(0, 120)));
    } catch (error) {
      // Tracking must never break the checkout path.
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(event);
    sendServerTrackingEvent(event);
    if (typeof window.fbq === "function") {
      const standard = ["ViewContent", "AddToCart"].includes(eventName);
      window.fbq(standard ? "track" : "trackCustom", eventName, payload);
    }
  }

  function sendServerTrackingEvent(event) {
    if (IS_FILE_MODE || !TRACKING.serverEndpoint || !TRACKING.serverLoggedEvents.includes(event.event)) return;
    try {
      const body = JSON.stringify({
        ...event,
        meta_pixel_id: TRACKING.metaPixelId,
        brand: BRAND.name,
        product_focus: "runnerwin-wide-headband"
      });
      if (navigator.sendBeacon) {
        const blob = new Blob([body], { type: "application/json" });
        if (navigator.sendBeacon(TRACKING.serverEndpoint, blob)) return;
      }
      fetch(TRACKING.serverEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        credentials: "same-origin",
        keepalive: true
      }).catch(() => {});
    } catch (error) {
      // Server logging must never block the shopping flow.
    }
  }

  function captureAttribution() {
    if (IS_FILE_MODE) return;
    const params = new URLSearchParams(window.location.search);
    const keys = ["fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
    const values = {};
    keys.forEach((key) => {
      const value = params.get(key);
      if (value) values[key] = value.slice(0, 300);
    });
    const looksLikePaidSocial = values.fbclid || /(^|\.)facebook\.com$|(^|\.)instagram\.com$|l\.facebook\.com|lm\.facebook\.com/i.test(document.referrer || "");
    if (!Object.keys(values).length && !looksLikePaidSocial) return;
    const previous = getAttribution();
    const attribution = {
      ...previous,
      ...values,
      referrer: document.referrer || previous.referrer || "",
      landing_url: previous.landing_url || window.location.href,
      first_seen: previous.first_seen || new Date().toISOString(),
      last_seen: new Date().toISOString()
    };
    try {
      localStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(attribution));
    } catch (error) {
      // Attribution is helpful, but not required for checkout.
    }
  }

  function getAttribution() {
    try {
      return JSON.parse(localStorage.getItem(ATTRIBUTION_KEY) || "{}") || {};
    } catch (error) {
      return {};
    }
  }

  function initMetaPixel() {
    if (!TRACKING.metaPixelId || typeof window.fbq === "function") return;
    (function (f, b, e, v, n, t, s) {
      if (f.fbq) return;
      n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n;
      n.push = n;
      n.loaded = true;
      n.version = "2.0";
      n.queue = [];
      t = b.createElement(e);
      t.async = true;
      t.src = v;
      s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", TRACKING.metaPixelId);
    window.fbq("track", "PageView");
  }

  function updateCartCount() {
    const count = (state.cart || []).reduce((sum, item) => sum + Number(item.qty || 0), 0);
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(count);
      el.classList.toggle("is_empty", count === 0 && el.classList.contains("cart_count"));
    });
  }

  function openMenu() {
    document.body.classList.add("menu_open");
    document.getElementById("menu").setAttribute("aria-hidden", "false");
    document.getElementById("nav_toggle").setAttribute("aria-expanded", "true");
    document.querySelector(".page_cover").hidden = false;
  }

  function closeMenu() {
    document.body.classList.remove("menu_open");
    document.getElementById("menu").setAttribute("aria-hidden", "true");
    document.getElementById("nav_toggle").setAttribute("aria-expanded", "false");
    document.querySelector(".page_cover").hidden = true;
  }

  function openSearch() {
    document.body.classList.add("search_open");
    const wrap = document.querySelector(".search_wrap");
    wrap.setAttribute("aria-hidden", "false");
    const input = document.getElementById("keyword");
    input.value = state.routeState.searchInput || "";
    renderSuggestions(input.value);
    window.setTimeout(() => input.focus(), 50);
  }

  function closeSearch() {
    document.body.classList.remove("search_open");
    document.querySelector(".search_wrap").setAttribute("aria-hidden", "true");
  }

  function renderSuggestions(value) {
    const root = document.querySelector("[data-search-suggestions]");
    const q = value.trim().toLowerCase();
    const matched = products.filter((p) => !q || p.name.toLowerCase().includes(q)).slice(0, 4);
    const history = state.searchHistory.filter((item) => item.toLowerCase().includes(q)).slice(0, 3);
    root.innerHTML = [
      ...history.map((term) => `<a href="${appHref(`/product/search.html?keyword=${encodeURIComponent(term)}`)}" data-link>${escapeHtml(term)}</a>`),
      ...matched.map((p) => `<a href="${appHref(productUrl(p))}" data-link>${escapeHtml(p.name)}</a>`)
    ].join("");
  }

  function toast(message) {
    document.querySelector(".toast")?.remove();
    const el = document.createElement("div");
    el.className = "toast";
    el.textContent = message;
    document.body.appendChild(el);
    window.setTimeout(() => el.remove(), 1800);
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;" }[char]));
  }

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-resume]")) {
      event.preventDefault();
      const target = normalizePath(state.origin?.path || "/index.html");
      beforeLeave();
      navigate(target, { origin: false, restoreScroll: true });
      return;
    }

    const link = event.target.closest("a[data-link], a.product_card, a.st-new-item");
    if (link) {
      const rawHref = link.getAttribute("href") || "";
      if (rawHref.startsWith("http")) return;
      const target = routeFromHref(rawHref);
      if (IS_FILE_MODE) {
        event.preventDefault();
        beforeLeave();
        state.origin = {
          path: getPath(),
          label: getOriginLabel()
        };
        saveState();
        navigate(target || PRIMARY_PRODUCT_PATH);
        return;
      }
      const url = new URL(link.href, window.location.href);
      if (url.origin === window.location.origin) {
        event.preventDefault();
        navigate(target || url.pathname + url.search);
      }
    }
  });

  document.getElementById("nav_toggle").addEventListener("click", () => {
    document.body.classList.contains("menu_open") ? closeMenu() : openMenu();
  });

  document.querySelector("[data-menu-close]").addEventListener("click", closeMenu);

  document.querySelectorAll(".down_btn").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".down_nav");
      item.classList.toggle("is_open");
      button.setAttribute("aria-expanded", item.classList.contains("is_open") ? "true" : "false");
    });
  });

  document.querySelectorAll("[data-search-open]").forEach((button) => button.addEventListener("click", openSearch));
  document.querySelectorAll("[data-search-close]").forEach((button) => button.addEventListener("click", closeSearch));

  document.getElementById("keyword").addEventListener("input", (event) => {
    state.routeState.searchInput = event.target.value;
    saveState();
    renderSuggestions(event.target.value);
  });

  document.getElementById("searchBarForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const keyword = document.getElementById("keyword").value.trim();
    if (!keyword) return;
    navigate(`/product/search.html?keyword=${encodeURIComponent(keyword)}`);
  });

  window.addEventListener("popstate", () => render({ restoreScroll: true }));
  window.addEventListener("hashchange", () => render({ restoreScroll: true }));

  window.addEventListener("scroll", () => {
    const isHome = document.body.classList.contains("st-home");
    document.body.classList.toggle("st-hero", isHome && window.scrollY < 80);
    document.body.classList.toggle("header_solid", !isHome || window.scrollY >= 80);
  }, { passive: true });

  window.addEventListener("beforeunload", beforeLeave);

  render({ restoreScroll: true });
})();
