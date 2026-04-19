# cedar — 产品说明（给 AI / 协作者）

面向 **公开展示** 的静态数据可视化站点，风格偏清晰、克制（Apple 系排版与配色），中文叙事为主。

**线上地址**：https://zhangs-cedar.github.io/cedar/  
**源码**：`https://github.com/zhangs-cedar/cedar`，默认分支 **`main`**。

---

## 1. 产品目标（Why）

| 维度 | 说明 |
|------|------|
| **用户价值** | 用一张可分享的公开链接，展示宏观经济/房价类图表，降低「数据在哪、怎么看」的认知成本。 |
| **体验目标** | 叙事清晰、加载稳定、移动端可读；避免重后台与复杂登录。 |
| **交付目标** | 改动可审计（Git 历史）、部署可预期（推 `main` 即发布）。 |

---

## 2. 受众与场景

- **主要读者**：需要快速浏览「70 城房价定基走势」「黄金储备」「苏州成交均价」的访客；可能来自分享链接或书签。
- **非目标**：实时交易、个性化账户、强交互后台管理。

---

## 3. 信息架构（当前）

| 入口 | 路径 / 说明 |
|------|-------------|
| 首页 | `index.html` — **由脚本生成**；图表目录、GitHub/联系、页脚 **`main` 提交时间**（浏览器请求 GitHub API）。 |
| 70 城总览 | `viz/cities.html` — **由脚本生成**；拼音分组、检索；链到各城单页。 |
| 单城房价 | `viz/city-<slug>-house-price.html` + `viz/embed/city-*-house-price-trend.html` — **由脚本生成**。 |
| 苏州（元/㎡） | `viz/city-suzhou-house-price.html` 等 — **由脚本生成**，指标为成交均价。 |
| 黄金储备 | `viz/gold-reserves.html` + `viz/embed/gold-reserves-trend.html` — **由脚本生成**。 |

城市列表与元数据：`viz/cities.json`（**由脚本生成**）。

**样式** `css/` 仍手维护；**其余上表所列 HTML（含首页）均由 `generate_city_pages.py` 写出**。

---

## 4. 体验与设计原则（给改 UI 的约束）

- **一致性**：单城页、embed、首页共用同一套视觉语言（`css/style.css`；图表侧与「苏州」embed 对齐的规范见 `scripts/generate_city_pages.py` 内注释）。
- **可读性**：关键说明放在页眉 `viz-note` / 卡片 `entry-sub`；数据缺口用「—」，勿静默省略。
- **诚信表述**：指数类页面注明口径（如定基 2014-01=100、数据来源说明）；避免暗示「预测」或「投资建议」除非产品明确需要。
- **无障碍**：保留合理标题层级、`aria`、跳过链接等现有习惯。

---

## 5. 技术现实（边界条件）

| 项 | 说明 |
|----|------|
| **形态** | 以 **静态 HTML/CSS/JS** 为主；图表多为 **ECharts**（iframe embed）。无应用级后端。 |
| **构建** | 仓库 **不设打包构建**；GitHub Actions 将仓库根目录 **原样** 部署为 Pages（见 `.github/workflows/deploy.yml`）。 |
| **发布** | 合并/推送到 **`main`** → Workflow 部署 → 数分钟内站点更新。 |
| **本地再生** | 在仓库根执行：`python3 scripts/generate_city_pages.py`。数据路径见脚本顶部（默认同 skill 数据目录）。 |

### 5.1 生成规范（给 AI / 协作者，建议当作硬约束）

- **禁止**直接批量手改、或用对话 AI 改下列已生成文件后提交：`index.html`、`viz/embed/city-*-house-price-trend.html`、`viz/city-*-house-price.html`、`viz/cities.html`、`viz/cities.json`、`viz/gold-reserves.html`、`viz/embed/gold-reserves-trend.html`、苏州相关页及脚本写入的其它产物。
- **正确做法**：只改 `scripts/generate_city_pages.py`（及数据 JSON），再运行 `python3 scripts/generate_city_pages.py`，用 Git diff 审阅生成结果后提交。
- **原因**：避免「脚本与磁盘 HTML 分叉」，否则下次跑脚本会覆盖手改，或线上与仓库不一致。

---

## 6. 产品经理向「验收清单」（新需求时自测）

- [ ] 新入口是否在首页或上级总览中有**可发现**的链接与一句话说明？
- [ ] 图表与表格是否**同源**、口径是否在首屏可读位置写明？
- [ ] 移动端窄屏下图表与表是否仍可滚动/阅读？
- [ ] 推 `main` 后线上是否与预期一致（含 CDN 延迟）？
- [ ] 若依赖外网 API（如首页更新时间），失败时是否有**降级文案**？

---

## 7. AI 协作提示（浓缩）

1. **默认假设**：优先在 **本仓库** 内完成可视化与文案；对外演示链接以 **GitHub Pages** 为准。  
2. **房价类页面**：一律通过 **`scripts/generate_city_pages.py` 规范生成**，不要直接改 `viz/` 下由该脚本产出的 HTML。改模板、文案、图表选项 → 改脚本 → 运行脚本 → 提交脚本 + 生成文件。  
3. **不要做**：引入必须服务端才能跑的功能、或依赖桌面 GUI 的说明（部署环境无图形界面）。  
4. **提交习惯**：小而可读的 commit message；图表相关改动必须 **脚本变更 + 再生成的静态文件** 同提交，避免只改一侧。

---

## 8. 联系与仓库

- 首页「联系」邮箱见 `index.html`。  
- 问题与版本以 **GitHub `main`** 为单一事实来源。
