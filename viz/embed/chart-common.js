function initCityChart(containerId, cityName, firstSeriesName, secondSeriesName, firstData, secondData) {
  const chart = echarts.init(document.getElementById(containerId));
  chart.setOption({
    animationDuration: 300,
    legend: { top: 4, data: [secondSeriesName, firstSeriesName] },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      formatter: function (params) {
        const fmt = (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
        const lineFor = (p) => {
          const arr = p.seriesName === firstSeriesName ? firstData : secondData;
          const i = p.dataIndex;
          const cur = arr[i].value;
          let extra = "";
          if (i > 0) {
            const prev = arr[i - 1].value;
            if (prev != null && prev !== 0 && cur != null && !Number.isNaN(Number(prev)) && !Number.isNaN(Number(cur))) {
              const pct = (cur / prev - 1) * 100;
              extra = " · 较上月 " + (pct > 0 ? "+" : "") + pct.toFixed(2) + "%";
            }
          }
          return p.marker + p.seriesName + ": " + fmt(cur) + extra;
        };
        return params[0].axisValue + "<br/>" + params.map(lineFor).join("<br/>");
      }
    },
    grid: { left: 56, right: 26, top: 42, bottom: 56 },
    xAxis: {
      type: "category",
      data: secondData.map((d) => d.month),
      axisLabel: { color: "#6e6e73", interval: 8 }
    },
    yAxis: {
      type: "value",
      name: "定基指数（价格走势）",
      axisLabel: { color: "#6e6e73" },
      splitLine: { lineStyle: { color: "rgba(29,29,31,0.12)" } }
    },
    series: [
      {
        name: secondSeriesName,
        type: "line",
        smooth: true,
        showSymbol: false,
        connectNulls: false,
        data: secondData.map((d) => d.value),
        lineStyle: { width: 2, color: "#0066cc" }
      },
      {
        name: firstSeriesName,
        type: "line",
        smooth: true,
        showSymbol: false,
        connectNulls: false,
        data: firstData.map((d) => d.value),
        lineStyle: { width: 2, color: "#34a853" }
      }
    ]
  });
  window.addEventListener("resize", () => chart.resize());
}

function initSuzhouChart(containerId, rows) {
  const chart = echarts.init(document.getElementById(containerId));
  chart.setOption({
    animationDuration: 300,
    legend: { top: 4, data: ["二手住宅", "新建商品住宅"] },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      formatter: function (params) {
        const fmt = (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN", { maximumFractionDigits: 0 }));
        const lineFor = (p) => {
          const i = p.dataIndex;
          const row = rows[i];
          const cur = p.seriesName === "新建商品住宅" ? row.new : row.second;
          let extra = "";
          if (i > 0) {
            const prevRow = rows[i - 1];
            const prev = p.seriesName === "新建商品住宅" ? prevRow.new : prevRow.second;
            if (prev != null && prev !== 0 && cur != null && !Number.isNaN(Number(prev)) && !Number.isNaN(Number(cur))) {
              const pct = (cur / prev - 1) * 100;
              extra = " · 较上月 " + (pct > 0 ? "+" : "") + pct.toFixed(2) + "%";
            }
          }
          return p.marker + p.seriesName + ": " + fmt(cur) + extra;
        };
        return params[0].axisValue + "<br/>" + params.map(lineFor).join("<br/>");
      }
    },
    grid: { left: 56, right: 26, top: 42, bottom: 56 },
    xAxis: {
      type: "category",
      data: rows.map((d) => d.month),
      axisLabel: { color: "#6e6e73", interval: 8 }
    },
    yAxis: {
      type: "value",
      name: "成交均价（元/㎡）",
      axisLabel: { color: "#6e6e73" },
      splitLine: { lineStyle: { color: "rgba(29,29,31,0.12)" } }
    },
    series: [
      {
        name: "二手住宅",
        type: "line",
        smooth: true,
        showSymbol: false,
        connectNulls: false,
        data: rows.map((d) => d.second),
        lineStyle: { width: 2, color: "#0066cc" }
      },
      {
        name: "新建商品住宅",
        type: "line",
        smooth: true,
        showSymbol: false,
        connectNulls: false,
        data: rows.map((d) => d.new),
        lineStyle: { width: 2, color: "#34a853" }
      }
    ]
  });
  window.addEventListener("resize", () => chart.resize());
}

function initGoldChart(containerId, months, amounts, deltas) {
  const chart = echarts.init(document.getElementById(containerId));
  chart.setOption({
    animationDuration: 300,
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      valueFormatter: (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN"))
    },
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    grid: [
      { left: 56, right: 26, top: 42, height: 260 },
      { left: 56, right: 26, top: 374, height: 260 }
    ],
    xAxis: [
      { type: "category", data: months, axisLabel: { color: "#6e6e73", interval: 4 }, gridIndex: 0 },
      { type: "category", data: months, axisLabel: { color: "#6e6e73", interval: 4 }, gridIndex: 1 }
    ],
    yAxis: [
      {
        type: "value",
        name: "万盎司",
        gridIndex: 0,
        axisLabel: { color: "#6e6e73" },
        splitLine: { lineStyle: { color: "rgba(29,29,31,0.12)" } }
      },
      {
        type: "value",
        name: "月度变化",
        gridIndex: 1,
        axisLabel: { color: "#6e6e73" },
        splitLine: { lineStyle: { color: "rgba(29,29,31,0.12)" } }
      }
    ],
    series: [
      {
        name: "黄金储备",
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: true,
        showSymbol: false,
        data: amounts,
        lineStyle: { width: 2, color: "#b8860b" }
      },
      {
        name: "月度变化",
        type: "bar",
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: deltas.map((v, i) => ({
          value: v,
          itemStyle: {
            color: v == null ? "transparent" : v > 0 ? "#34a853" : v < 0 ? "#ea4335" : "#6e6e73"
          }
        })),
        barMaxWidth: 16
      }
    ]
  });
  window.addEventListener("resize", () => chart.resize());
}
