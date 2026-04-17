#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

BASE_MONTH = "2014-01"
SKILL_FANGJIA_DIR = Path("/home/coder/.cursor/skills/cn-gold-house-price/data/fangjia")
REPO_ROOT = Path(__file__).resolve().parent.parent
VIZ_DIR = REPO_ROOT / "viz"
EMBED_DIR = VIZ_DIR / "embed"
CITY_JSON = VIZ_DIR / "cities.json"

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
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{city}房价定基指数</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
      html, body {{ margin: 0; background: #fff; color: #1d1d1f; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif; }}
      .wrap {{ padding: 18px 18px 6px; }}
      .meta {{ margin: 0 0 12px; color: #6e6e73; font-size: 13px; }}
      #chart {{ width: 100%; height: 640px; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <p class="meta">{city} · 定基指数（2014-01=100） · 数据源：东财70城月度</p>
      <div id="chart"></div>
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
          valueFormatter: (v) => Number(v).toFixed(2)
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
            data: secondData.map((d) => d.value),
            lineStyle: {{ width: 2, color: "#0066cc" }}
          }},
          {{
            name: "新建商品住宅",
            type: "line",
            smooth: true,
            showSymbol: false,
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


def render_city_page(city: str, slug: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{city}新房与二手房定基指数趋势。" />
    <title>{city}房价 · cedar</title>
    <link rel="stylesheet" href="../css/style.css" />
  </head>
  <body class="viz-page">
    <a class="skip" href="#chart">跳到图表</a>
    <div class="wrap--chart">
      <header class="viz-top">
        <a class="viz-back" href="../index.html" aria-label="返回 cedar 首页">‹ cedar</a>
        <h1 class="viz-title">{city}房价变化</h1>
        <p class="viz-note">东财 70 城月度环比指数折算定基（2014-01=100）。</p>
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

    print(f"cities_total={len(cities)} generated={len(metadata)} missing={len(missing)}")
    if missing:
        print("missing:", ",".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
