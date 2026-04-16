(function () {
  var stamp = document.getElementById("stamp");
  var printBtn = document.getElementById("print");
  var lang = document.documentElement.lang || "zh-CN";
  var locale = /^zh/i.test(lang) ? "zh-CN" : "en-US";

  if (stamp) {
    var prefix = /^zh/i.test(lang)
      ? "页面生成时间（本地）："
      : "Generated locally: ";
    stamp.textContent =
      prefix + new Date().toLocaleString(locale, { hour12: false });
  }

  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }
})();
