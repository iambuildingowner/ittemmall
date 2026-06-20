(function () {
  var siteOrigin = window.location.origin || "https://ittemmall.com";
  window.ITTEMMALL_NAVER_PAY_CONFIG = {
    mode: "development",
    applicationType: "order",
    reviewButtonPlacement: "product_detail",
    clientId: "",
    chainId: "",
    openType: "page",
    returnUrl: siteOrigin + "/payment/return.html",
    orderEndpoint: siteOrigin + "/payment/order-store.php",
  };
})();
