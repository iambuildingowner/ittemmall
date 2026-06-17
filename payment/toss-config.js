(function () {
  var siteOrigin = window.location.origin || "https://ittemmall.com";
  window.ITTEMMALL_TOSS_PAYMENTS_CONFIG = {
    enabled: true,
    mode: "development",
    mid: "ittemmvfiq",
    clientKey: "test_gck_docs_Ovk5rk1EwkEbP0W43n07xlzm",
    usesDocumentTestKey: true,
    customerKeyPrefix: "ittemmall-customer",
    paymentWidgetVariantKey: "DEFAULT",
    agreementWidgetVariantKey: "DEFAULT",
    checkoutUrl: siteOrigin + "/payment/toss-checkout.html",
    successUrl: siteOrigin + "/payment/toss-success.html",
    failUrl: siteOrigin + "/payment/toss-fail.html",
    orderEndpoint: siteOrigin + "/payment/order-store.php",
  };
})();
