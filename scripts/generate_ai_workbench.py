#!/usr/bin/env python3
"""Generate the Cedar AI workflow display page.

Source data stays in content/ai_workbench.json. The generated HTML is an
artifact under viz/ and can be regenerated at any time.
"""
import html
import json
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = REPO_ROOT / "content" / "ai_workbench.json"
OUTPUT_PATH = REPO_ROOT / "viz" / "ai-workbench.html"


def escape_text(value: Any) -> str:
    return html.escape(str(value), quote=False)


def escape_attr(value: Any) -> str:
    return html.escape(str(value), quote=True)


def load_payload() -> Dict[str, Any]:
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


def render_principles(items: List[Dict[str, str]]) -> str:
    rows = []
    for item in items:
        rows.append(
            """
          <article class="principle-card">
            <h3>{title}</h3>
            <p>{body}</p>
          </article>""".format(
                title=escape_text(item["title"]),
                body=escape_text(item["body"]),
            )
        )
    return "".join(rows)


def render_architecture(rows: List[Dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append(
            """
              <tr>
                <td>{layer}</td>
                <td><code>{path}</code></td>
                <td>{formats}</td>
                <td>{purpose}</td>
              </tr>""".format(
                layer=escape_text(row["layer"]),
                path=escape_text(row["path"]),
                formats=escape_text(row["formats"]),
                purpose=escape_text(row["purpose"]),
            )
        )
    return "".join(body)


def render_use_cases(items: List[Dict[str, Any]]) -> str:
    cards = []
    for item in items:
        tags = "".join(
            '<span class="tag">{}</span>'.format(escape_text(tag)) for tag in item.get("tags", [])
        )
        cards.append(
            """
          <article class="case-card" data-search="{search}" data-tags="{tag_text}">
            <div class="case-head">
              <h3>{name}</h3>
              <div class="tag-row">{tags}</div>
            </div>
            <p>{description}</p>
            <dl>
              <dt>Source</dt><dd><code>{source}</code></dd>
              <dt>Artifact</dt><dd><code>{artifact}</code></dd>
            </dl>
          </article>""".format(
                search=escape_attr(
                    " ".join(
                        [
                            item["name"],
                            item["description"],
                            item["source"],
                            item["artifact"],
                            " ".join(item.get("tags", [])),
                        ]
                    ).lower()
                ),
                tag_text=escape_attr(" ".join(item.get("tags", []))),
                name=escape_text(item["name"]),
                tags=tags,
                description=escape_text(item["description"]),
                source=escape_text(item["source"]),
                artifact=escape_text(item["artifact"]),
            )
        )
    return "".join(cards)


def render_standards(items: List[str]) -> str:
    return "".join("<li>{}</li>".format(escape_text(item)) for item in items)


def render_prompts(items: List[Dict[str, str]]) -> str:
    blocks = []
    for idx, item in enumerate(items):
        prompt_id = "prompt-{}".format(idx + 1)
        blocks.append(
            """
          <article class="prompt-card">
            <h3>{title}</h3>
            <pre id="{prompt_id}">{text}</pre>
            <button type="button" data-copy="{prompt_id}">复制提示词</button>
          </article>""".format(
                title=escape_text(item["title"]),
                prompt_id=escape_attr(prompt_id),
                text=escape_text(item["text"]),
            )
        )
    return "".join(blocks)


def render_page(payload: Dict[str, Any]) -> str:
    meta = payload["meta"]
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{summary_attr}" />
    <meta name="theme-color" content="#111827" />
    <title>{title} · cedar</title>
    <link rel="icon" href="../favicon.svg" type="image/svg+xml" sizes="any" />
    <style>
      :root {{ color-scheme: dark; --bg: #0b1020; --panel: rgba(17, 24, 39, 0.78); --text: #f8fafc; --muted: #a7b0c0; --line: rgba(148, 163, 184, 0.22); --accent: #60a5fa; --accent-2: #a78bfa; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif; }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; min-height: 100vh; color: var(--text); background: radial-gradient(circle at 14% 8%, rgba(96, 165, 250, 0.22), transparent 30%), radial-gradient(circle at 88% 12%, rgba(167, 139, 250, 0.2), transparent 28%), linear-gradient(180deg, #0b1020 0%, #111827 100%); }}
      a {{ color: inherit; }} .wrap {{ width: min(74rem, calc(100% - 2rem)); margin: 0 auto; }}
      header {{ padding: clamp(2.6rem, 7vw, 5.6rem) 0 1.6rem; }} .back {{ color: var(--accent); text-decoration: none; font-size: 0.95rem; }}
      .eyebrow {{ margin: 1.5rem 0 0; color: var(--accent); letter-spacing: 0.18em; text-transform: uppercase; font-size: 0.78rem; }}
      h1 {{ max-width: 12ch; margin: 0.55rem 0 0; font-size: clamp(2.5rem, 7vw, 5.5rem); line-height: 0.98; letter-spacing: -0.055em; }}
      .summary {{ max-width: 47rem; color: var(--muted); font-size: clamp(1rem, 2vw, 1.18rem); }}
      .hero-grid {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 1rem; margin-top: 1.5rem; }}
      .hero-card, section {{ border: 1px solid var(--line); border-radius: 24px; background: linear-gradient(145deg, var(--panel), rgba(15, 23, 42, 0.72)); box-shadow: 0 24px 80px rgba(0, 0, 0, 0.24); backdrop-filter: blur(16px); }}
      .hero-card {{ padding: clamp(1.1rem, 2vw, 1.6rem); }} .flow {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.7rem; align-items: center; }}
      .flow-node {{ min-height: 7rem; padding: 1rem; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.04); }}
      .flow-node span {{ color: var(--accent); font-size: 0.78rem; letter-spacing: 0.1em; text-transform: uppercase; }} .flow-node strong {{ display: block; margin-top: 0.45rem; font-size: 1.15rem; }}
      main {{ padding: 0 0 4rem; display: grid; gap: 1rem; }} section {{ padding: clamp(1rem, 2.2vw, 1.6rem); }}
      h2 {{ margin: 0 0 1rem; font-size: 0.85rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); }} h3 {{ margin: 0 0 0.45rem; font-size: 1.02rem; }} p {{ color: var(--muted); }}
      .principle-grid, .case-grid, .prompt-grid {{ display: grid; gap: 0.85rem; }} .principle-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }} .case-grid, .prompt-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .principle-card, .case-card, .prompt-card {{ border: 1px solid var(--line); border-radius: 18px; padding: 1rem; background: rgba(255,255,255,0.045); }}
      .toolbar {{ display: flex; gap: 0.7rem; margin-bottom: 0.9rem; flex-wrap: wrap; }} input, select, button {{ border: 1px solid var(--line); border-radius: 999px; color: var(--text); background: rgba(15,23,42,0.72); padding: 0.68rem 0.9rem; font: inherit; }} input {{ flex: 1 1 18rem; }}
      button {{ cursor: pointer; color: #08111f; background: linear-gradient(135deg, var(--accent), var(--accent-2)); border: 0; font-weight: 700; }}
      .tag-row {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }} .tag {{ border: 1px solid rgba(96,165,250,0.34); border-radius: 999px; padding: 0.18rem 0.48rem; color: #bfdbfe; font-size: 0.76rem; }}
      dl {{ display: grid; grid-template-columns: 5.4rem minmax(0, 1fr); gap: 0.35rem 0.7rem; margin: 0.85rem 0 0; color: var(--muted); }} dt {{ color: var(--text); }} code {{ color: #dbeafe; overflow-wrap: anywhere; }}
      table {{ width: 100%; border-collapse: collapse; font-size: 0.94rem; }} th, td {{ padding: 0.75rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }} th {{ color: var(--muted); font-weight: 600; cursor: pointer; }}
      details {{ border: 1px solid var(--line); border-radius: 18px; padding: 1rem; background: rgba(255,255,255,0.04); }} summary {{ cursor: pointer; font-weight: 700; }} li {{ margin: 0.45rem 0; color: var(--muted); }}
      pre {{ white-space: pre-wrap; color: #dbeafe; background: rgba(2,6,23,0.55); border-radius: 14px; padding: 0.9rem; overflow: auto; }} .source-note, .empty {{ color: var(--muted); font-size: 0.86rem; }} .empty {{ display: none; }} .case-card[hidden] {{ display: none; }}
      @media (max-width: 62rem) {{ .hero-grid, .principle-grid, .case-grid, .prompt-grid {{ grid-template-columns: 1fr; }} .flow {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <header class="wrap">
      <a class="back" href="../index.html">← 返回 cedar 首页</a>
      <p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="summary">{summary}</p>
      <div class="hero-grid"><div class="hero-card flow" aria-label="工作流"><div class="flow-node"><span>source</span><strong>Markdown / JSON</strong><p>工程底稿，可 diff、可复用。</p></div><div class="flow-node"><span>generator</span><strong>Python</strong><p>读取源数据，生成静态产物。</p></div><div class="flow-node"><span>artifact</span><strong>Cedar HTML</strong><p>网页查看、搜索、筛选和展示。</p></div></div><div class="hero-card"><h2>当前规则</h2><p>Markdown 不退场；它变成底稿。HTML 也不变成源文件；它变成可再生展示面板。</p><p class="source-note">{source_note}</p></div></div>
    </header>
    <main class="wrap">
      <section><h2>原则</h2><div class="principle-grid">{principles}</div></section>
      <section><h2>分层架构</h2><table id="architecture-table"><thead><tr><th>Layer</th><th>Path</th><th>Formats</th><th>Purpose</th></tr></thead><tbody>{architecture}</tbody></table></section>
      <section><h2>落地场景</h2><div class="toolbar"><input id="case-search" type="search" placeholder="搜索场景、标签、产物路径..." aria-label="搜索场景" /><select id="tag-filter" aria-label="按标签筛选"><option value="">全部标签</option></select></div><div class="case-grid" id="case-grid">{use_cases}</div><p class="empty" id="case-empty">没有匹配的场景。</p></section>
      <section><h2>HTML 产物标准</h2><details open><summary>生成约束</summary><ul>{standards}</ul></details></section>
      <section><h2>可复制提示词</h2><div class="prompt-grid">{prompts}</div></section>
    </main>
    <script id="report-data" type="application/json">{payload_json}</script>
    <script>
      (function () {{
        var payload = JSON.parse(document.getElementById("report-data").textContent);
        var search = document.getElementById("case-search"); var filter = document.getElementById("tag-filter"); var cards = Array.prototype.slice.call(document.querySelectorAll(".case-card")); var empty = document.getElementById("case-empty"); var tags = [];
        payload.use_cases.forEach(function (item) {{ (item.tags || []).forEach(function (tag) {{ if (tags.indexOf(tag) === -1) tags.push(tag); }}); }});
        tags.sort().forEach(function (tag) {{ var option = document.createElement("option"); option.value = tag; option.textContent = tag; filter.appendChild(option); }});
        function applyFilter() {{ var q = (search.value || "").trim().toLowerCase(); var tag = filter.value; var shown = 0; cards.forEach(function (card) {{ var hitText = !q || card.dataset.search.indexOf(q) !== -1; var hitTag = !tag || card.dataset.tags.split(" ").indexOf(tag) !== -1; var hit = hitText && hitTag; card.hidden = !hit; if (hit) shown += 1; }}); empty.style.display = shown ? "none" : "block"; }}
        search.addEventListener("input", applyFilter); filter.addEventListener("change", applyFilter);
        document.querySelectorAll("[data-copy]").forEach(function (button) {{ button.addEventListener("click", function () {{ var target = document.getElementById(button.dataset.copy); navigator.clipboard.writeText(target.textContent).then(function () {{ var old = button.textContent; button.textContent = "已复制"; setTimeout(function () {{ button.textContent = old; }}, 1200); }}); }}); }});
        document.querySelectorAll("th").forEach(function (th, index) {{ th.addEventListener("click", function () {{ var tbody = th.closest("table").querySelector("tbody"); var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr")); rows.sort(function (a, b) {{ return a.children[index].textContent.localeCompare(b.children[index].textContent, "zh-CN"); }}); rows.forEach(function (row) {{ tbody.appendChild(row); }}); }}); }});
      }})();
    </script>
  </body>
</html>
""".format(
        title=escape_text(meta["title"]),
        eyebrow=escape_text(meta["eyebrow"]),
        summary=escape_text(meta["summary"]),
        summary_attr=escape_attr(meta["summary"]),
        source_note=escape_text(meta["source_note"]),
        principles=render_principles(payload["principles"]),
        architecture=render_architecture(payload["architecture"]),
        use_cases=render_use_cases(payload["use_cases"]),
        standards=render_standards(payload["standards"]),
        prompts=render_prompts(payload["prompts"]),
        payload_json=escape_text(payload_json),
    )


def main() -> int:
    payload = load_payload()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_page(payload), encoding="utf-8")
    print("generated {}".format(OUTPUT_PATH.relative_to(REPO_ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
