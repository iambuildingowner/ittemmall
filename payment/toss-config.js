(function () {
  var siteOrigin = window.location.origin || "https://ittemmall.com";
  window.ITTEMMALL_TOSS_PAYMENTS_CONFIG = {
    enabled: false,
    mode: "development",
    clientKey: "",
    customerKeyPrefix: "ittemmall-customer",
    paymentWidgetVariantKey: "DEFAULT",
    successUrl: siteOrigin + "/payment/toss-success.html",
    failUrl: siteOrigin + "/payment/toss-fail.html",
    orderEndpoint: siteOrigin + "/payment/order-store.php",
  };
})();
