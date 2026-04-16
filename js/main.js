(function () {
  var stamp = document.getElementById("stamp");
  var printBtn = document.getElementById("print");

  if (stamp) {
    stamp.textContent =
      "页面生成时间（本地）：" +
      new Date().toLocaleString("zh-CN", { hour12: false });
  }

  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }
})();
