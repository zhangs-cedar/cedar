#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

BASE_MONTH = "2014-01"
SKILL_DATA_DIR = Path("/home/coder/.cursor/skills/cn-gold-house-price/data")
SKILL_FANGJIA_DIR = SKILL_DATA_DIR / "fangjia"
REPO_ROOT = Path(__file__).resolve().parent.parent
VIZ_DIR = REPO_ROOT / "viz"
EMBED_DIR = VIZ_DIR / "embed"
CITY_JSON = VIZ_DIR / "cities.json"

# 与苏州 embed 对齐：字体、留白、图例位置、tooltip、折线样式（定基页 y 轴语义不同）
_EMBED_BASE_STYLE = """    <style>
      html, body {{ margin: 0; background: #fff; color: #1d1d1f; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif; }}
      .wrap {{ padding: 18px 18px 6px; }}
      .meta {{ margin: 0 0 12px; color: #6e6e73; font-size: 13px; }}
      #chart {{ width: 100%; height: 640px; }}
    </style>"""

_TOOLTIP_INDEX = """valueFormatter: (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }))"""

_TOOLTIP_NUMBER = """valueFormatter: (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toLocaleString("zh-CN"))"""

_CITY_EMBED_TABLE_STYLE = """    <style>
      .table-block {{ margin-top: 16px; padding-bottom: 12px; }}
      .table-caption {{ margin: 0 0 8px; font-size: 13px; color: #6e6e73; }}
      .table-scroll {{ max-height: min(360px, 42vh); overflow: auto; border: 1px solid rgba(29,29,31,0.12); border-radius: 10px; background: #fff; }}
      .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
      .data-table thead th {{ position: sticky; top: 0; background: #f5f5f7; color: #6e6e73; font-weight: 600; z-index: 1; box-shadow: 0 1px 0 rgba(29,29,31,0.08); }}
      .data-table th, .data-table td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid rgba(29,29,31,0.08); }}
      .data-table tbody tr:hover {{ background: rgba(0,102,204,0.04); }}
      .data-table td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
      .data-table td:nth-child(2) {{ color: #34a853; }}
      .data-table td:nth-child(3) {{ color: #0066cc; }}
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
    <title>{city}房价定基指数</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
{_EMBED_BASE_STYLE}
{_CITY_EMBED_TABLE_STYLE}
  </head>
  <body>
    <div class="wrap">
      <p class="meta">{city} · 定基指数（2014-01=100） · 数据源：东财70城月度</p>
      <div id="chart"></div>
      <section class="table-block" aria-label="月度定基指数数据表">
        <p class="table-caption">月度数据表（定基指数 2014-01=100，与上图一致）</p>
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
        legend: {{ top: 4, data: ["新建商品住宅", "二手住宅"] }},
        tooltip: {{
          trigger: "axis",
          {_TOOLTIP_INDEX}
        }},
        grid: {{ left: 56, right: 26, top: 42, bottom: 56 }},
        xAxis: {{
          type: "category",
          data: secondData.map((d) => d.month),
          axisLabel: {{ color: "#6e6e73", interval: 8 }}
        }},
        yAxis: {{
          type: "value",
          name: "2014-01=100",
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
    desc = description or f"{city}新房与二手房定基指数趋势。"
    note_txt = note or "东财 70 城月度环比指数折算定基（2014-01=100）。"
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
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>苏州房价成交均价</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
{_EMBED_BASE_STYLE}
  </head>
  <body>
    <div class="wrap">
      <p class="meta">苏州 · 成交均价（元/㎡） · 数据源：cn-gold-house-price/suzhou_house_price.json</p>
      <div id="chart"></div>
    </div>
    <script>
      const rows = {data_j};
      const chart = echarts.init(document.getElementById("chart"));
      chart.setOption({{
        animationDuration: 300,
        legend: {{ top: 4, data: ["新建商品住宅", "二手住宅"] }},
        tooltip: {{
          trigger: "axis",
          valueFormatter: (v) => (v == null || v === "" ? "—" : Number(v).toLocaleString("zh-CN"))
        }},
        grid: {{ left: 56, right: 26, top: 42, bottom: 56 }},
        xAxis: {{
          type: "category",
          data: rows.map((d) => d.month),
          axisLabel: {{ color: "#6e6e73", interval: 8 }}
        }},
        yAxis: {{
          type: "value",
          name: "元/㎡",
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


def write_suzhou_pages() -> None:
    months, new_y, sec_y = load_suzhou_yuan_rows()
    slug = "suzhou"
    embed = render_suzhou_yuan_embed(months, new_y, sec_y)
    shell = render_city_page(
        "苏州",
        slug,
        description="苏州新房与二手房成交均价（元/㎡）月度轨迹。",
        note="与 70 城页不同：本图为成交均价（元/㎡），非东财定基指数。",
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

    write_suzhou_pages()
    write_gold_pages()

    print(f"cities_total={len(cities)} generated={len(metadata)} missing={len(missing)}")
    if missing:
        print("missing:", ",".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
