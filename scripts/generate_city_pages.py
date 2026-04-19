#!/usr/bin/env python3
"""批量生成房价相关静态页（70 城 embed/shell、cities 总览、苏州、黄金）。

本仓库中下列产物必须由本脚本写入，禁止手改 HTML 后再提交（应改本文件并重跑）：
  index.html, viz/embed/city-*-house-price-trend.html, viz/city-*-house-price.html,
  viz/cities.html, viz/cities.json, 苏州与黄金相关页。
例外：css/ 等样式仍手维护。

用法：python3 scripts/generate_city_pages.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

BASE_MONTH = "2014-01"
SKILL_DATA_DIR = Path("/home/coder/.cursor/skills/cn-gold-house-price/data")
SKILL_FANGJIA_DIR = SKILL_DATA_DIR / "fangjia"
REPO_ROOT = Path(__file__).resolve().parent.parent
VIZ_DIR = REPO_ROOT / "viz"
EMBED_DIR = VIZ_DIR / "embed"
CITY_JSON = VIZ_DIR / "cities.json"

# viz/cities.html 文案（与单城页口径一致，仅在此维护）
CITIES_PAGE_META_DESCRIPTION = (
    "东财70城新房与二手房价格走势（定基指数）城市总览，支持检索与拼音分组。"
)
CITIES_PAGE_VIZ_NOTE = (
    "单城页展示二手房与新建商品住宅价格水平变化趋势（定基 2014-01=100）；悬停可看环比涨跌。"
)

# index.html 文案（仅在此维护）
INDEX_META_DESCRIPTION = "cedar · Apple 风静态可视化入口。"
INDEX_THEME_COLOR = "#f5f5f7"
INDEX_EYEBROW = "cedar data showcase"
INDEX_BRAND = "Discover Data, Simply."
INDEX_HERO_TAGLINE = "面向公开展示的静态可视化入口，聚焦清晰叙事、轻交互与稳定交付。"
INDEX_PANEL_CHARTS_TITLE = "可视化图表"
INDEX_CARD_CITIES = (
    "viz/cities.html",
    "Chart 00",
    "70城房价总览",
    "按拼音分组；单城页为二手房与新房价格走势（定基折线）、月度表与环比",
    "70 城单页入口",
)
INDEX_CARD_GOLD = (
    "viz/gold-reserves.html",
    "Chart 01",
    "黄金储备变化",
    "央行储备总量与月度增减趋势",
    "静态 iframe 图表",
)
INDEX_CARD_SUZHOU = (
    "viz/city-suzhou-house-price.html",
    "Chart 02",
    "苏州房价变化",
    "二手房与新房成交价格走势（元/㎡），含月度表与悬停环比",
    "与 70 城同套 ECharts 生成",
)
INDEX_PANEL_MORE_TITLE = "更多入口"
INDEX_LINK_GITHUB = (
    "https://github.com/zhangs-cedar/cedar",
    "Resource",
    "GitHub",
    "查看仓库与发布流程",
)
INDEX_LINK_MAIL = (
    "mailto:s.zhang.cedar@gmail.com",
    "Resource",
    "联系",
    "s.zhang.cedar@gmail.com",
)
INDEX_FOOTER_LINE = "Built for GitHub Pages. Zero build, focused delivery."
INDEX_FOOTER_LOADING = "内容更新：加载中…"
INDEX_GITHUB_REPO = "zhangs-cedar/cedar"

# 与苏州 embed 对齐：字体、留白、图例位置、tooltip、折线样式（定基页 y 轴语义不同）
_EMBED_BASE_STYLE = """    <style>
      html, body { margin: 0; background: #fff; color: #1d1d1f; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif; }
      .wrap { padding: 18px 18px 6px; }
      .meta { margin: 0 0 12px; color: #6e6e73; font-size: 13px; }
      #chart { width: 100%; height: 640px; }
    </style>"""

_TOOLTIP_NUMBER = """valueFormatter: (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN"))"""

_CITY_EMBED_TABLE_STYLE = """    <style>
      .table-block { margin-top: 16px; padding-bottom: 12px; }
      .table-caption { margin: 0 0 8px; font-size: 13px; color: #6e6e73; }
      .table-scroll { max-height: min(360px, 42vh); overflow: auto; border: 1px solid rgba(29,29,31,0.12); border-radius: 10px; background: #fff; }
      .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
      .data-table thead th { position: sticky; top: 0; background: #f5f5f7; color: #6e6e73; font-weight: 600; z-index: 1; box-shadow: 0 1px 0 rgba(29,29,31,0.08); }
      .data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid rgba(29,29,31,0.08); }
      .data-table tbody tr:hover { background: rgba(0,102,204,0.04); }
      .data-table td.num { text-align: right; font-variant-numeric: tabular-nums; }
      .data-table td:nth-child(2) { color: #34a853; }
      .data-table td:nth-child(3) { color: #0066cc; }
    </style>"""


def _html_index_table_rows(
    first: list[tuple[str, float]], second: list[tuple[str, float]]
) -> str:
    """与图表同源：按二手序列月份对齐，新房缺月显示 —。"""
    fmap = {m: v for m, v in first}
    lines: list[str] = []
    for m, sv in second:
        fv = fmap.get(m)
        cell_new = "—" if fv is None else f"{fv:.2f}"
        cell_sec = f"{sv:.2f}"
        lines.append(
            "          <tr>"
            f"<td>{m}</td>"
            f'<td class="num">{cell_new}</td>'
            f'<td class="num">{cell_sec}</td>'
            "</tr>"
        )
    return "\n".join(lines)


def _html_yuan_table_rows(payload: list[dict]) -> str:
    """苏州成交均价表：与图同源，缺数显示 —。"""
    lines: list[str] = []
    for r in payload:
        m = r["month"]
        nv, sv = r.get("new"), r.get("second")

        def cell_yuan(v: float | None) -> str:
            if v is None:
                return "—"
            x = float(v)
            if abs(x - round(x)) < 1e-6:
                return f"{int(round(x)):,}"
            return f"{x:,.2f}"

        lines.append(
            "          <tr>"
            f"<td>{m}</td>"
            f'<td class="num">{cell_yuan(nv)}</td>'
            f'<td class="num">{cell_yuan(sv)}</td>'
            "</tr>"
        )
    return "\n".join(lines)


# 定基指数轴：十字准线 + 悬停数值 + 相对上月涨跌幅（链式指数相邻两点推算）
_TOOLTIP_AXIS_MOM_INDEX = """axisPointer: { type: "cross" },
          formatter: function (params) {
          const fmt = (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
          const lineFor = (p) => {
            const arr = p.seriesName === "新建商品住宅" ? firstData : secondData;
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
        }"""


CITY_SLUG = {
    "三亚": "sanya",
    "上海": "shanghai",
    "丹东": "dandong",
    "乌鲁木齐": "urumqi",
    "九江": "jiujiang",
    "兰州": "lanzhou",
    "包头": "baotou",
    "北京": "beijing",
    "北海": "beihai",
    "南京": "nanjing",
    "南充": "nanchong",
    "南宁": "nanning",
    "南昌": "nanchang",
    "厦门": "xiamen",
    "合肥": "hefei",
    "吉林": "jilin",
    "呼和浩特": "hohhot",
    "哈尔滨": "harbin",
    "唐山": "tangshan",
    "大理": "dali",
    "大连": "dalian",
    "天津": "tianjin",
    "太原": "taiyuan",
    "宁波": "ningbo",
    "安庆": "anqing",
    "宜昌": "yichang",
    "岳阳": "yueyang",
    "常德": "changde",
    "平顶山": "pingdingshan",
    "广州": "guangzhou",
    "徐州": "xuzhou",
    "惠州": "huizhou",
    "成都": "chengdu",
    "扬州": "yangzhou",
    "无锡": "wuxi",
    "昆明": "kunming",
    "杭州": "hangzhou",
    "桂林": "guilin",
    "武汉": "wuhan",
    "沈阳": "shenyang",
    "泉州": "quanzhou",
    "泸州": "luzhou",
    "洛阳": "luoyang",
    "济南": "jinan",
    "济宁": "jining",
    "海口": "haikou",
    "深圳": "shenzhen",
    "温州": "wenzhou",
    "湛江": "zhanjiang",
    "烟台": "yantai",
    "牡丹江": "mudanjiang",
    "石家庄": "shijiazhuang",
    "福州": "fuzhou",
    "秦皇岛": "qinhuangdao",
    "蚌埠": "bengbu",
    "襄阳": "xiangyang",
    "西宁": "xining",
    "西安": "xian",
    "贵阳": "guiyang",
    "赣州": "ganzhou",
    "遵义": "zunyi",
    "郑州": "zhengzhou",
    "重庆": "chongqing",
    "金华": "jinhua",
    "银川": "yinchuan",
    "锦州": "jinzhou",
    "长春": "changchun",
    "长沙": "changsha",
    "青岛": "qingdao",
    "韶关": "shaoguan",
}


def load_rows() -> list[dict]:
    rows: list[dict] = []
    for fp in sorted(SKILL_FANGJIA_DIR.glob("*.json")):
        month = fp.stem
        data = json.loads(fp.read_text(encoding="utf-8"))
        for item in data:
            row = dict(item)
            row["MONTH"] = month
            rows.append(row)
    return rows


def build_index(rows: list[dict], city: str, key: str) -> list[tuple[str, float]]:
    month_seq: dict[str, float] = {}
    for row in rows:
        if row.get("CITY") != city:
            continue
        seq = row.get(key)
        if seq:
            month_seq[row["MONTH"]] = float(seq)
    months = sorted(month_seq.keys())
    if BASE_MONTH not in months:
        return []
    start_idx = months.index(BASE_MONTH)
    value = 100.0
    out = [(BASE_MONTH, 100.0)]
    for m in months[start_idx + 1 :]:
        seq = month_seq[m]
        if seq > 0:
            value = value * seq / 100.0
        out.append((m, value))
    return out


def render_embed(city: str, first: list[tuple[str, float]], second: list[tuple[str, float]]) -> str:
    first_json = json.dumps([{"month": m, "value": round(v, 4)} for m, v in first], ensure_ascii=False)
    second_json = json.dumps([{"month": m, "value": round(v, 4)} for m, v in second], ensure_ascii=False)
    table_body = _html_index_table_rows(first, second)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{city}二手房与新房价格趋势</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
{_EMBED_BASE_STYLE}
{_CITY_EMBED_TABLE_STYLE}
  </head>
  <body>
    <div class="wrap">
      <p class="meta">{city} · 二手房与新房价格水平变化趋势 · 定基指数（2014-01=100） · 东财70城月度</p>
      <div id="chart"></div>
      <section class="table-block" aria-label="月度定基指数数据表">
        <p class="table-caption">月度定基指数（与折线一致；指数刻画新房、二手房各自价格走势）</p>
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th scope="col">月份</th>
                <th scope="col">新建商品住宅</th>
                <th scope="col">二手住宅</th>
              </tr>
            </thead>
            <tbody>
{table_body}
            </tbody>
          </table>
        </div>
      </section>
    </div>
    <script>
      const firstData = {first_json};
      const secondData = {second_json};
      const chart = echarts.init(document.getElementById("chart"));
      chart.setOption({{
        animationDuration: 300,
        legend: {{ top: 4, data: ["二手住宅", "新建商品住宅"] }},
        tooltip: {{
          trigger: "axis",
          {_TOOLTIP_AXIS_MOM_INDEX}
        }},
        grid: {{ left: 56, right: 26, top: 42, bottom: 56 }},
        xAxis: {{
          type: "category",
          data: secondData.map((d) => d.month),
          axisLabel: {{ color: "#6e6e73", interval: 8 }}
        }},
        yAxis: {{
          type: "value",
          name: "定基指数（价格走势）",
          axisLabel: {{ color: "#6e6e73" }},
          splitLine: {{ lineStyle: {{ color: "rgba(29,29,31,0.12)" }} }}
        }},
        series: [
          {{
            name: "二手住宅",
            type: "line",
            smooth: true,
            showSymbol: false,
            connectNulls: false,
            data: secondData.map((d) => d.value),
            lineStyle: {{ width: 2, color: "#0066cc" }}
          }},
          {{
            name: "新建商品住宅",
            type: "line",
            smooth: true,
            showSymbol: false,
            connectNulls: false,
            data: firstData.map((d) => d.value),
            lineStyle: {{ width: 2, color: "#34a853" }}
          }}
        ]
      }});
      window.addEventListener("resize", () => chart.resize());
    </script>
  </body>
</html>
"""


def render_city_page(
    city: str,
    slug: str,
    *,
    description: str | None = None,
    note: str | None = None,
) -> str:
    desc = description or f"{city}二手房与新建商品住宅价格水平变化趋势（东财70城定基指数）。"
    note_txt = note or (
        "下图展示二手与新房两条价格走势；定基口径 2014-01=100。悬停可看环比涨跌。"
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{desc}" />
    <title>{city}房价 · cedar</title>
    <link rel="stylesheet" href="../css/style.css" />
  </head>
  <body class="viz-page">
    <a class="skip" href="#chart">跳到图表</a>
    <div class="wrap--chart">
      <header class="viz-top">
        <a class="viz-back" href="../index.html" aria-label="返回 cedar 首页">‹ cedar</a>
        <h1 class="viz-title">{city}房价变化</h1>
        <p class="viz-note">{note_txt}</p>
      </header>
      <iframe
        id="chart"
        class="viz-frame"
        title="{city}房价"
        src="embed/city-{slug}-house-price-trend.html"
        loading="lazy"
      ></iframe>
    </div>
  </body>
</html>
"""


def render_gold_embed(months: list[str], amounts: list[float], deltas: list[float | None]) -> str:
    months_j = json.dumps(months, ensure_ascii=False)
    amounts_j = json.dumps(amounts, ensure_ascii=False)
    deltas_j = json.dumps(deltas, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>央行黄金储备</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
      html, body {{ margin: 0; background: #fff; color: #1d1d1f; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif; }}
      .wrap {{ padding: 18px 18px 6px; }}
      .meta {{ margin: 0 0 12px; color: #6e6e73; font-size: 13px; }}
      #chart {{ width: 100%; height: 720px; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <p class="meta">中国人民银行 · 黄金储备（万盎司）与月度变化 · 数据源：cn-gold-house-price/gold_reserves.json</p>
      <div id="chart"></div>
    </div>
    <script>
      const months = {months_j};
      const amounts = {amounts_j};
      const deltas = {deltas_j};
      const chart = echarts.init(document.getElementById("chart"));
      chart.setOption({{
        animationDuration: 300,
        tooltip: {{
          trigger: "axis",
          axisPointer: {{ type: "cross" }},
          {_TOOLTIP_NUMBER}
        }},
        axisPointer: {{ link: [{{ xAxisIndex: "all" }}] }},
        grid: [
          {{ left: 56, right: 26, top: 42, height: 260 }},
          {{ left: 56, right: 26, top: 374, height: 260 }}
        ],
        xAxis: [
          {{ type: "category", data: months, axisLabel: {{ color: "#6e6e73", interval: 4 }}, gridIndex: 0 }},
          {{ type: "category", data: months, axisLabel: {{ color: "#6e6e73", interval: 4 }}, gridIndex: 1 }}
        ],
        yAxis: [
          {{
            type: "value",
            name: "万盎司",
            gridIndex: 0,
            axisLabel: {{ color: "#6e6e73" }},
            splitLine: {{ lineStyle: {{ color: "rgba(29,29,31,0.12)" }} }}
          }},
          {{
            type: "value",
            name: "月度变化",
            gridIndex: 1,
            axisLabel: {{ color: "#6e6e73" }},
            splitLine: {{ lineStyle: {{ color: "rgba(29,29,31,0.12)" }} }}
          }}
        ],
        series: [
          {{
            name: "黄金储备",
            type: "line",
            xAxisIndex: 0,
            yAxisIndex: 0,
            smooth: true,
            showSymbol: false,
            data: amounts,
            lineStyle: {{ width: 2, color: "#b8860b" }}
          }},
          {{
            name: "月度变化",
            type: "bar",
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: deltas.map((v, i) => ({{
              value: v,
              itemStyle: {{
                color: v == null ? "transparent" : v > 0 ? "#34a853" : v < 0 ? "#ea4335" : "#6e6e73"
              }}
            }})),
            barMaxWidth: 16
          }}
        ]
      }});
      window.addEventListener("resize", () => chart.resize());
    </script>
  </body>
</html>
"""


def render_gold_shell() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta
      name="description"
      content="中国人民银行黄金储备月度趋势与购金变化量。"
    />
    <title>黄金储备 · cedar</title>
    <link rel="stylesheet" href="../css/style.css" />
  </head>
  <body class="viz-page">
    <a class="skip" href="#chart">跳到图表</a>
    <div class="wrap--chart">
      <header class="viz-top">
        <a class="viz-back" href="../index.html" aria-label="返回 cedar 首页">‹ cedar</a>
        <h1 class="viz-title">黄金储备变化</h1>
        <p class="viz-note">月度库存（万盎司）与相邻月差值；双图布局，样式与苏州、70 城房价 embed 一致。</p>
      </header>
      <iframe
        id="chart"
        class="viz-frame"
        title="央行黄金储备"
        src="embed/gold-reserves-trend.html"
        loading="lazy"
      ></iframe>
    </div>
  </body>
</html>
"""


def load_gold_series() -> tuple[list[str], list[float], list[float | None]]:
    path = SKILL_DATA_DIR / "gold_reserves.json"
    data = json.loads(path.read_text(encoding="utf-8"))["gold_reserves"]["data"]
    months: list[str] = []
    amounts: list[float] = []
    for d in data:
        months.append(f"{d['year']}-{d['month']:02d}")
        amounts.append(float(d["amount"]))
    deltas: list[float | None] = [None]
    for i in range(1, len(amounts)):
        deltas.append(round(amounts[i] - amounts[i - 1], 4))
    return months, amounts, deltas


def render_suzhou_yuan_embed(
    months: list[str],
    new_yuan: list[float | None],
    second_yuan: list[float | None],
) -> str:
    payload = [
        {"month": m, "new": nv, "second": sv}
        for m, nv, sv in zip(months, new_yuan, second_yuan, strict=True)
    ]
    data_j = json.dumps(payload, ensure_ascii=False)
    table_body = _html_yuan_table_rows(payload)
    _suzhou_tooltip = """axisPointer: { type: "cross" },
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
        }"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>苏州二手房与新房价格趋势</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
{_EMBED_BASE_STYLE}
{_CITY_EMBED_TABLE_STYLE}
  </head>
  <body>
    <div class="wrap">
      <p class="meta">苏州 · 二手房与新房成交价格变化趋势（元/㎡） · cn-gold-house-price/suzhou_house_price.json</p>
      <div id="chart"></div>
      <section class="table-block" aria-label="月度成交均价数据表">
        <p class="table-caption">月度成交均价元/㎡（与折线一致：新房、二手房两条走势）</p>
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th scope="col">月份</th>
                <th scope="col">新建商品住宅</th>
                <th scope="col">二手住宅</th>
              </tr>
            </thead>
            <tbody>
{table_body}
            </tbody>
          </table>
        </div>
      </section>
    </div>
    <script>
      const rows = {data_j};
      const chart = echarts.init(document.getElementById("chart"));
      chart.setOption({{
        animationDuration: 300,
        legend: {{ top: 4, data: ["二手住宅", "新建商品住宅"] }},
        tooltip: {{
          trigger: "axis",
          {_suzhou_tooltip}
        }},
        grid: {{ left: 56, right: 26, top: 42, bottom: 56 }},
        xAxis: {{
          type: "category",
          data: rows.map((d) => d.month),
          axisLabel: {{ color: "#6e6e73", interval: 8 }}
        }},
        yAxis: {{
          type: "value",
          name: "成交均价（元/㎡）",
          axisLabel: {{ color: "#6e6e73" }},
          splitLine: {{ lineStyle: {{ color: "rgba(29,29,31,0.12)" }} }}
        }},
        series: [
          {{
            name: "二手住宅",
            type: "line",
            smooth: true,
            showSymbol: false,
            connectNulls: false,
            data: rows.map((d) => d.second),
            lineStyle: {{ width: 2, color: "#0066cc" }}
          }},
          {{
            name: "新建商品住宅",
            type: "line",
            smooth: true,
            showSymbol: false,
            connectNulls: false,
            data: rows.map((d) => d.new),
            lineStyle: {{ width: 2, color: "#34a853" }}
          }}
        ]
      }});
      window.addEventListener("resize", () => chart.resize());
    </script>
  </body>
</html>
"""


def load_suzhou_yuan_rows() -> tuple[list[str], list[float | None], list[float | None]]:
    path = SKILL_DATA_DIR / "suzhou_house_price.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    months: list[str] = []
    new_y: list[float | None] = []
    sec_y: list[float | None] = []
    for r in raw:
        months.append(f"{r['year']}-{r['month']:02d}")
        nv = r.get("new_house_price")
        sv = r.get("second_hand_price")
        new_y.append(float(nv) if nv is not None else None)
        sec_y.append(float(sv) if sv is not None else None)
    return months, new_y, sec_y


def write_gold_pages() -> None:
    months, amounts, deltas = load_gold_series()
    (EMBED_DIR / "gold-reserves-trend.html").write_text(
        render_gold_embed(months, amounts, deltas), encoding="utf-8"
    )
    (VIZ_DIR / "gold-reserves.html").write_text(render_gold_shell(), encoding="utf-8")


def render_cities_html(metadata: list[dict]) -> str:
    """70 城总览：城市列表与文案均由本脚本生成，勿手改 viz/cities.html。"""
    rows = [[m["slug"], m["name"]] for m in metadata]
    cities_js = json.dumps(rows, ensure_ascii=False)
    meta_esc = html.escape(CITIES_PAGE_META_DESCRIPTION, quote=True)
    note_esc = html.escape(CITIES_PAGE_VIZ_NOTE, quote=False)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{meta_esc}" />
    <title>70城房价总览 · cedar</title>
    <link rel="stylesheet" href="../css/style.css" />
  </head>
  <body class="viz-page cities-page">
    <a class="skip" href="#cities">跳到城市列表</a>
    <div class="wrap--chart">
      <header class="viz-top">
        <a class="viz-back" href="../index.html" aria-label="返回 cedar 首页">‹ cedar</a>
        <h1 class="viz-title">70城房价总览</h1>
        <p class="viz-note">{note_esc}</p>
      </header>
      <section class="cities-toolbar" aria-label="检索与分组导航">
        <label for="city-search" class="visually-hidden">搜索城市</label>
        <input id="city-search" class="city-search" type="search" placeholder="搜索城市，如：上海 / shanghai / beijing" autocomplete="off" />
        <nav id="alpha-nav" class="alpha-nav" aria-label="按拼音首字母分组"></nav>
      </section>
      <p id="cities-empty" class="cities-empty" hidden>未找到匹配城市，请尝试中文名或拼音。</p>
      <main id="cities" class="city-groups" aria-label="70城列表"></main>
    </div>
    <script>
      const cities = {cities_js};

      const groups = new Map();
      cities.forEach(([pinyin, name]) => {{
        const letter = pinyin.charAt(0).toUpperCase();
        if (!groups.has(letter)) groups.set(letter, []);
        groups.get(letter).push({{ pinyin, name }});
      }});

      const nav = document.getElementById("alpha-nav");
      const list = document.getElementById("cities");
      const search = document.getElementById("city-search");
      const empty = document.getElementById("cities-empty");

      Array.from(groups.keys()).sort().forEach((letter) => {{
        const navLink = document.createElement("a");
        navLink.className = "alpha-link";
        navLink.href = `#group-${{letter}}`;
        navLink.textContent = letter;
        const count = document.createElement("span");
        count.textContent = groups.get(letter).length;
        navLink.appendChild(count);
        nav.appendChild(navLink);

        const section = document.createElement("section");
        section.className = "city-group";
        section.id = `group-${{letter}}`;
        section.dataset.group = letter;
        section.innerHTML = `<h2 class="city-group-title">${{letter}}</h2><div class="city-grid"></div>`;
        const grid = section.querySelector(".city-grid");

        groups.get(letter).forEach(({{ pinyin, name }}) => {{
          const link = document.createElement("a");
          link.className = "city-card";
          link.href = `city-${{pinyin}}-house-price.html`;
          link.dataset.pinyin = pinyin;
          link.dataset.city = name;
          link.textContent = name;
          grid.appendChild(link);
        }});
        list.appendChild(section);
      }});

      search.addEventListener("input", () => {{
        const keyword = search.value.trim().toLowerCase();
        let visibleGroupCount = 0;
        document.querySelectorAll(".city-group").forEach((groupEl) => {{
          let visibleCards = 0;
          groupEl.querySelectorAll(".city-card").forEach((card) => {{
            const hit = !keyword || card.dataset.city.includes(keyword) || card.dataset.pinyin.includes(keyword);
            card.hidden = !hit;
            if (hit) visibleCards += 1;
          }});
          groupEl.hidden = visibleCards === 0;
          if (visibleCards > 0) visibleGroupCount += 1;
        }});
        empty.hidden = visibleGroupCount !== 0;
      }});
    </script>
  </body>
</html>
"""


def render_index_html() -> str:
    """站点首页：文案在此常量区维护，勿手改 index.html。"""

    def ea(s: str) -> str:
        return html.escape(s, quote=True)

    def et(s: str) -> str:
        return html.escape(s, quote=False)

    hc, k0, t0, s0, m0 = INDEX_CARD_CITIES
    hg, k1, t1, s1, m1 = INDEX_CARD_GOLD
    hs, k2, t2, s2, m2 = INDEX_CARD_SUZHOU
    g_h, g_k, g_t, g_s = INDEX_LINK_GITHUB
    m_h, m_k, m_t, m_s = INDEX_LINK_MAIL

    footer_script = f"""    <script>
      (function () {{
        var el = document.getElementById("site-updated");
        if (!el) return;
        var repo = "{ea(INDEX_GITHUB_REPO)}";
        fetch("https://api.github.com/repos/" + repo + "/commits/main", {{
          headers: {{ Accept: "application/vnd.github+json" }},
        }})
          .then(function (r) {{
            if (!r.ok) throw new Error("github");
            return r.json();
          }})
          .then(function (data) {{
            var raw = data && data.commit && data.commit.committer && data.commit.committer.date;
            if (!raw) throw new Error("date");
            var dt = new Date(raw);
            var fmt = new Intl.DateTimeFormat("zh-CN", {{
              timeZone: "Asia/Shanghai",
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              hour12: false,
            }});
            el.textContent = "内容更新：" + fmt.format(dt) + "（上海，main 最新提交）";
          }})
          .catch(function () {{
            el.textContent = "内容更新：暂无法获取（可刷新重试）";
          }});
      }})();
    </script>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{ea(INDEX_META_DESCRIPTION)}" />
    <meta name="theme-color" content="{ea(INDEX_THEME_COLOR)}" />
    <title>cedar</title>
    <link rel="stylesheet" href="css/style.css" />
  </head>
  <body class="home-page">
    <a class="skip" href="#content">跳到正文</a>

    <header class="site-header">
      <p class="eyebrow">{et(INDEX_EYEBROW)}</p>
      <h1 class="brand">{et(INDEX_BRAND)}</h1>
      <p class="hero-tagline">
        {et(INDEX_HERO_TAGLINE)}
      </p>
    </header>

    <main id="content" class="site-main">
      <section class="panel panel--primary">
        <h2 class="panel-title">{et(INDEX_PANEL_CHARTS_TITLE)}</h2>
        <div class="card-grid" aria-label="图表目录">
          <a class="entry-card" href="{ea(hc)}">
            <span class="entry-kicker">{et(k0)}</span>
            <span class="entry-title">{et(t0)}</span>
            <span class="entry-sub">{et(s0)}</span>
            <span class="entry-meta">{et(m0)}</span>
          </a>
          <a class="entry-card" href="{ea(hg)}">
            <span class="entry-kicker">{et(k1)}</span>
            <span class="entry-title">{et(t1)}</span>
            <span class="entry-sub">{et(s1)}</span>
            <span class="entry-meta">{et(m1)}</span>
          </a>
          <a class="entry-card" href="{ea(hs)}">
            <span class="entry-kicker">{et(k2)}</span>
            <span class="entry-title">{et(t2)}</span>
            <span class="entry-sub">{et(s2)}</span>
            <span class="entry-meta">{et(m2)}</span>
          </a>
        </div>
      </section>

      <section class="panel panel--minor">
        <h2 class="panel-title">{et(INDEX_PANEL_MORE_TITLE)}</h2>
        <div class="card-grid card-grid--minor">
          <a
            class="entry-card entry-card--minor"
            href="{ea(g_h)}"
            rel="noopener noreferrer"
          >
            <span class="entry-kicker">{et(g_k)}</span>
            <span class="entry-title">{et(g_t)}</span>
            <span class="entry-sub">{et(g_s)}</span>
          </a>
          <a class="entry-card entry-card--minor" href="{ea(m_h)}">
            <span class="entry-kicker">{et(m_k)}</span>
            <span class="entry-title">{et(m_t)}</span>
            <span class="entry-sub">{et(m_s)}</span>
          </a>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <p class="footer-line">{et(INDEX_FOOTER_LINE)}</p>
      <p class="footer-updated" id="site-updated" aria-live="polite">{et(INDEX_FOOTER_LOADING)}</p>
    </footer>
{footer_script}
  </body>
</html>
"""


def write_suzhou_pages() -> None:
    months, new_y, sec_y = load_suzhou_yuan_rows()
    slug = "suzhou"
    embed = render_suzhou_yuan_embed(months, new_y, sec_y)
    shell = render_city_page(
        "苏州",
        slug,
        description="苏州二手房与新建商品住宅成交价格变化趋势（元/㎡）。",
        note=(
            "与 70 城定基页不同：本页为元/㎡绝对价；折线展示二手与新房两条价格走势，表与悬停可对照环比。"
        ),
    )
    (EMBED_DIR / f"city-{slug}-house-price-trend.html").write_text(embed, encoding="utf-8")
    (VIZ_DIR / f"city-{slug}-house-price.html").write_text(shell, encoding="utf-8")
    redirect = """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0; url=city-suzhou-house-price.html" />
    <title>苏州房价 · cedar</title>
    <link rel="canonical" href="city-suzhou-house-price.html" />
  </head>
  <body>
    <p>已迁移至 <a href="city-suzhou-house-price.html">city-suzhou-house-price.html</a>。</p>
  </body>
</html>
"""
    (VIZ_DIR / "suzhou-house-price.html").write_text(redirect, encoding="utf-8")
    legacy_embed = EMBED_DIR / "suzhou-house-price-trend.html"
    if legacy_embed.exists():
        legacy_embed.unlink()


def main() -> int:
    rows = load_rows()
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

    cities = sorted({r.get("CITY") for r in rows if r.get("CITY")})
    metadata = []
    missing = []
    for city in cities:
        slug = CITY_SLUG.get(city)
        if not slug:
            missing.append(city)
            continue
        first = build_index(rows, city, "FIRST_COMHOUSE_SEQUENTIAL")
        second = build_index(rows, city, "SECOND_HOUSE_SEQUENTIAL")
        if not first or not second:
            missing.append(city)
            continue

        embed_html = render_embed(city, first, second)
        city_html = render_city_page(city, slug)
        (EMBED_DIR / f"city-{slug}-house-price-trend.html").write_text(embed_html, encoding="utf-8")
        (VIZ_DIR / f"city-{slug}-house-price.html").write_text(city_html, encoding="utf-8")
        metadata.append({"name": city, "slug": slug})

    metadata = sorted(metadata, key=lambda x: x["slug"])
    CITY_JSON.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (VIZ_DIR / "cities.html").write_text(render_cities_html(metadata), encoding="utf-8")

    write_suzhou_pages()
    write_gold_pages()

    (REPO_ROOT / "index.html").write_text(render_index_html(), encoding="utf-8")

    print(f"cities_total={len(cities)} generated={len(metadata)} missing={len(missing)}")
    if missing:
        print("missing:", ",".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
