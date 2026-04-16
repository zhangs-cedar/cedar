(function () {
  var stamp = document.getElementById("stamp");
  var btn = document.getElementById("ping");
  if (stamp) {
    stamp.textContent =
      "加载时间（本地时钟）：" + new Date().toLocaleString("zh-CN", { hour12: false });
  }
  if (btn) {
    btn.addEventListener("click", function () {
      if (stamp) {
        stamp.textContent =
          "JS 正常 · 点击于 " + new Date().toLocaleTimeString("zh-CN", { hour12: false });
      }
    });
  }
})();
