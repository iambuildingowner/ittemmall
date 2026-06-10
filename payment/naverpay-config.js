(function () {
  var siteOrigin = window.location.origin || "https://ittemmall.com";
  window.ITTEMMALL_NAVER_PAY_CONFIG = {
    mode: "development",
    clientId: "",
    chainId: "",
    openType: "page",
    returnUrl: siteOrigin + "/payment/return.html",
    orderEndpoint: siteOrigin + "/payment/order-store.php",
  };
})();
