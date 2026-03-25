---
name: openclaw-stock-skill
description: 使用 data.diemeng.chat 提供的接口查询股票日线、分钟线、财务指标等数据，支持 A 股等市场。
user-invocable: true
metadata: {
  "openclaw": {
    "emoji": "📈",
    "skillKey": "openclaw-stock-skill",
    "requires": { "env": ["STOCK_API_KEY"] },
    "primaryEnv": "STOCK_API_KEY"
  }
}
---

## � 核心能力

本技能提供强大的股票数据查询与分析能力，主要包含：

1. **实时数据**：提供实时股票快照、实时分时行情。
2. **历史数据**：支持查询股票、可转债、ETF、指数等品种的历史数据（日线、分钟线、财务指标等）。
3. **自定义通知**（开发中）：支持涨停、炸板、放量大涨、涨停大额成交等异动信号的自定义消息通知。

## �📥 安装方法

```bash
npx skills add https://github.com/1018466411/openclaw-stock-data-skill
```

安装时按提示选择：
1. 选择 **openclaw**
2. 选择 **global** 应用于所有 Agent
3. Copy to all agents: **yes**

本技能教会代理如何使用你自建的股票数据服务（注册账号 `https://data.diemeng.chat`），通过 **API Key** 进行鉴权，查询股票的日线、分钟线、财务指标等数据。

> ⚙️ **API Key 配置约定**
>
> - OpenClaw 会按照 [`skills.entries.<key>` 配置](https://docs.openclaw.ai/tools/skills-config) 把 API Key 和自定义配置注入到进程环境变量中。
> - 本技能约定使用环境变量 **`STOCK_API_KEY`** 作为主密钥，并在 `metadata.openclaw.primaryEnv` 中声明，以便通过 `skills.entries.openclaw-stock-skill.apiKey` 统一配置。
> - 推荐的 OpenClaw 配置示例（`~/.openclaw/openclaw.json`）：
>
> ```json5
> {
>   skills: {
>     entries: {
>       "openclaw-stock-skill": {
>         enabled: true,
>         // 建议在 OpenClaw UI 的 Skill 参数面板里填写 apiKey，
>         // Gateway 会自动将其写入 STOCK_API_KEY 环境变量
>         apiKey: { source: "env", provider: "default", id: "STOCK_API_KEY" },
>         env: {
>           // 可在这里直接写死，或通过系统环境变量覆盖
>           STOCK_API_KEY: "YOUR_REAL_STOCK_API_KEY"
>         },
>         config: {
>           // 可选：覆盖默认域名
>           baseUrl: "https://data.diemeng.chat"
>         }
>       }
>     }
>   }
> }
> ```
>
> 参考文档：[Skills Config](https://docs.openclaw.ai/tools/skills-config)、[Skills](https://docs.openclaw.ai/tools/skills)

## ⚠️ 重要说明

### 1. 权限开通与 403 错误
如果 API 返回 **403 错误**，说明您的账号没有开通对应接口的权限。
请务必访问官网 [https://data.diemeng.chat/](https://data.diemeng.chat/)，在个人中心开通所需权限（如股票行情、实时快照、可转债等）。

### 2. 接口类型区分
- **实时接口**：
  - `get_stock_snapshot_daily`（不传日期或传今日）：获取最新实时快照（价格、成交量、五档盘口等）。
  - `get_stock_snapshot_push_history`：获取实时推送的历史记录。
  - `get_call_auction`：获取集合竞价数据。
- **历史接口**：
  - `get_daily_data`：获取历史日 K 线。
  - `get_history_data`：获取历史分钟线。
  - `get_finance_data`：获取历史财务指标。
  - `get_stock_snapshot_daily`（传历史日期）：获取历史快照。
- **指数与板块接口**：
  - `get_index_history`：获取指数分钟级历史数据。
  - `get_ths_sector_categories`：获取同花顺板块分类数据。
  - `get_ths_constituent_stocks`：获取同花顺成分股数据。

## 总体说明

- **基础域名**：默认使用 `https://data.diemeng.chat`，如存在 `skills.entries.openclaw-stock-skill.config.baseUrl` 则优先使用配置中的 `baseUrl`。
- **鉴权方式**：所有需要权限的接口都必须带上 API Key：
  - 首选 HTTP Header：`apiKey: <STOCK_API_KEY>`（推荐）
  - 兼容 Header：`X-API-Key: <STOCK_API_KEY>`
  - 后端也支持在 JSON body 中携带 `apiKey` 字段，但为了安全与规范，本技能**统一通过 Header 传递**。
- **返回结构**：
  - 大多数接口返回：`{ "code": 200, "msg": "成功", "data": { ... } }`
  - 少数列表类接口直接返回数组或简单结构，实际响应以 JSON 为准。
- **限流与黑名单**：
  - API Key 及 IP 都有严格限流与黑名单逻辑：
    - 无效 API Key 多次尝试会触发封禁（参见后端 `DataAccessVerifier` 实现）。
    - 需优先缓存和复用同一 API Key，不要在循环中频繁切换。
- **⚠️ 数据量限制**：除特别说明外，**大多数列表类接口单次请求最多返回 10000 条数据**。如需获取更多数据，请使用分页参数。

## 能力概览（建议的工具意图）

代理应将本技能视作一组 HTTP 能力，而不是单一接口：

- **get_stock_daily_bars**：查询指定股票在某一时间区间内的日线 K 线数据。
- **get_stock_intraday_bars**：查询分钟级（1/5/15/30/60 分钟）历史数据。
- **get_stock_finance_factors**：查询日度财务因子（PE、PB、换手率等）。
- **get_stock_list**：查询股票基础信息列表，用于代码／名称搜索。
- **get_stock_calendar_and_snapshot**：查询交易日历和当日快照。
- **get_stock_search**：使用自然语言条件搜索符合条件的股票（如"PE<20 且换手率>3%"）。
- **get_stock_call_auction**：查询集合竞价数据。
- **get_stock_closing_snapshot**：查询收盘快照数据。
- **get_stock_snapshot_daily**：查询实时或历史股票快照（含 Redis 缓存加速）。
- **get_stock_suspension**：查询股票停牌信息。
- **get_stock_adj_factor**：查询复权因子。
- **get_bond_daily**：查询可转债日线数据。
- **get_bond_indicator_daily**：查询可转债日指标数据。
- **get_bond_list**：查询可转债列表信息。

代理在规划调用时，应根据用户自然语言意图，选择以上能力并组合使用。

## 接口详情与调用规范

### 1. 日线数据：`POST /api/stock/daily`

- **URL**：`{baseUrl}/api/stock/daily`
- **方法**：`POST`
- **Headers**：
  - `Content-Type: application/json`
  - `apiKey: <STOCK_API_KEY>`
- **请求体 JSON**（后端 `DailyDataRequest`）：

```json
{
  "stock_code": "000001.SZ",
  "start_time": "2024-01-01",
  "end_time": "2024-01-31",
  "page": 0,
  "page_size": 1000
}
```

- 说明：
  - `stock_code` 可以是单个字符串，也可以是字符串数组。
  - `start_time`、`end_time` 格式为 `YYYY-MM-DD`。
  - 支持分页，`page` 从 0 开始。
- 响应字段：
  - `data.total`：总记录数
  - `data.list`：每条记录包含 `stock_code`, `stock_name`, `trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount` 等字段，价格与成交量已在后端统一保留 2 位小数。
- 响应主体（简化）：
  - `data.total`：总记录数
  - `data.list`：每条记录包含 `stock_code`, `trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount` 等字段，价格与成交量已在后端统一保留 2 位小数。

> 代理在需要“某股某段时间的日 K 线”时，应优先选择该接口。

### 2. 分钟级历史数据：`POST /api/stock/history`

- **URL**：`{baseUrl}/api/stock/history`
- **方法**：`POST`
- **Headers**：同上
- **请求体 JSON**（后端 `HistoryDataRequest`）：

```json
{
  "stock_code": "000001.SZ",
  "level": "5min",
  "start_time": "2024-01-01 09:30:00",
  "end_time": "2024-01-01 15:00:00",
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `level`：`"1min" | "5min" | "15min" | "30min" | "60min"`
  - `start_time` / `end_time`：
    - 允许仅日期（自动补全 00:00:00 和 23:59:59）
    - 或完整时间戳 `YYYY-MM-DD HH:MM:SS`
- 响应主体（简化）：
  - `data.list` 中每条包含：`stock_code`, `trade_time`, `open`, `high`, `low`, `close`, `vol`, `amount`。

> 用于用户询问“某天/某段时间内的分钟级行情、分时数据”等场景。

### 3. 当天分时数据：`POST /api/realtime/history`

- **URL**：`{baseUrl}/api/realtime/history`
- **方法**：`POST`
- **Headers**：同上
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "trade_time": "2026-03-15 09:31:00"
}
```

- 说明：
  - 获取当天分时数据 (实时 1 分钟级别分时数据)，支持全市场或指定股票。
  - `stock_code` 或 `trade_time` 至少提供一个。
  - 返回数据会根据 `stock_code` + `trade_time` 进行去重。

> **调用建议（定时任务拉取全市场数据）**：
> - 建议使用时间 (`trade_time`) 来获取实时分时，一次可以获取某一分钟的全市场数据。
> - 使用定时任务来获取数据，每分钟获取上一分钟的数据。
> - 建议在每分钟的 2 到 5 秒后开始获取。
> - 如果获取不到，建议暂停 1 秒后继续获取，最多重试不要超过 60 次，避免陷入死循环。
> - 建议在每分钟 15 秒之后再调用接口更新一次数据，确保数据的准确性。

### 4. 财务与因子（行情因子）：`POST /api/stock/finance`

- **URL**：`{baseUrl}/api/stock/finance`
- **方法**：`POST`
- **请求体 JSON**（后端 `FinanceDataRequest`）：

```json
{
  "stock_code": "000001.SZ",
  "start_time": "2024-01-01",
  "end_time": "2024-03-31",
  "page": 0,
  "page_size": 1000
}
```

- 主要返回字段（列表中每条）：
  - `stock_code`, `stock_name`, `trade_date`, `close`, `turnover_rate`, `turnover_rate_f`, `volume_ratio`, `pe`, `pe_ttm`, `pb`, `ps`, `ps_ttm`, `dv_ratio`, `dv_ttm`, `total_share`, `float_share`, `free_share`, `total_mv`, `circ_mv` 等。

> 适合估值分析、换手率、成交金额、市值等相关问题。

### 4. 股票基础信息列表：`GET /api/stock/list`

- **URL**：`{baseUrl}/api/stock/list`
- **方法**：`GET`
- **Query 参数**：
  - `stock_code`（可选）：精确股票代码筛选
  - `page`：默认 0
  - `page_size`：默认 20000
- 响应（封装在统一 `success` 结构中）：
  - `data.total`
  - `data.list`：包含 `stock_code`, `name`, `area`, `industry`, `list_date`, `symbol`, `list_status`, `delist_date`, `is_hs` 等。

> 当用户只给出股票名称、地区、行业等描述时，可先通过该接口获取匹配列表，再提示用户选择具体代码。

### 5. 交易日历与快照：`GET /api/basic/calendar` & `GET /api/basic/snapshot`

#### 5.1 交易日历：`GET /api/basic/calendar`

- **URL**：`{baseUrl}/api/basic/calendar`
- **方法**：`GET`
- **Query 参数**：
  - `start_time`: `YYYY-MM-DD`
  - `end_time`: `YYYY-MM-DD`
- 响应：
  - `data` 为数组，每条含 `date`, `is_open`（1 为交易日，0 为休市）。

> 当用户问“某段时间哪些是交易日”“下一个交易日是什么时候”等，可使用此接口。

#### 5.2 快照：`GET /api/basic/snapshot`

- **URL**：`{baseUrl}/api/basic/snapshot`
- **方法**：`GET`
- **Query 参数**：
  - `stock_code`（可选）
  - `page`, `page_size`
- 返回最新一笔集合竞价数据的汇总，字段包括价格、成交量、买卖盘等。

> 当用户需要“当前（最近一次）盘口快照”或大盘扫描时，可使用此接口。

### 6. 股票条件搜索：`POST /api/stock/search`

- **URL**：`{baseUrl}/api/stock/search`
- **方法**：`POST`
- **Headers**：
  - `Content-Type: application/json`
  - `apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "query": "pe_ttm < 20 且 turnover_rate > 3%",
  "stock_code": "000001.SZ",
  "date": "2024-01-01",
  "page": 0,
  "page_size": 100,
  "sort_by": "pe_ttm",
  "sort_order": "asc"
}
```

- 字段说明：
  - `query`（**必填**）：搜索条件，支持自然语言或表达式
    - 支持格式：`pe_ttm < 20`、`turnover_rate > 3%`、`pe_ttm < 20 且 turnover_rate > 3%`
    - 支持中文：`市盈率小于20`、`换手率大于3%`
    - 支持单位：`circ_mv > 100亿`、`volume > 1000万`
  - `stock_code`（可选）：精确股票代码筛选
  - `date`（可选）：日期，格式 `YYYY-MM-DD` 或 `MM-DD`（默认为当年）
    - **不提供日期**：查询 `stock_snapshot_daily`（最新实时数据）
    - **提供日期**：查询 `stock_finance_daily`（历史财务数据）
  - `page`：页码，从 0 开始
  - `page_size`：每页数量，**最大 1000**
  - `sort_by`（可选）：排序字段，如 `pe_ttm`、`turnover_rate`
  - `sort_order`（可选）：排序方向 `asc` 或 `desc`（默认 desc）

- **支持的字段**：
  - `price` / `close`：股价/收盘价
  - `pct_chg`：涨跌幅
  - `turnover_rate`：换手率
  - `pe` / `pe_ttm`：市盈率
  - `pb`：市净率
  - `total_mv` / `circ_mv`：总市值/流通市值
  - `total_share` / `float_share`：总股本/流通股本
  - `volume` / `turnover`：成交量/成交额
  - `dividend_ratio`：股息率

- 响应主体：
  - `data.total`：总记录数
  - `data.list`：符合条件的股票列表

> **重要提醒**：该接口单次请求**最多返回 1000 条数据**。如需获取更多结果，请使用分页功能。

> **适用场景**：用户需要根据财务指标筛选股票，如"帮我找出 PE<20 的股票"、"换手率大于 5% 的股票有哪些"。


### 8. 集合竞价数据：`POST /api/stock/call_auction`

- **URL**：`{baseUrl}/api/stock/call_auction`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "start_time": "2024-01-01 09:15:00",
  "end_time": "2024-01-01 09:25:00",
  "page": 0,
  "page_size": 100
}
```

- 字段说明：
  - `start_time` / `end_time`：时间范围，支持仅日期（自动补全时间）
  - `page_size`：**最大 10000**
- 返回字段：`stock_code`, `name`, `trade_time`, `close`, `open`, `high`, `low`, `pre_close`, `vol`, `amount`, `turnover_rate`, `pe`, `pb`, `pe_ttm`, `dv_ttm` 等

> **重要提醒**：单次请求**最多返回 10000 条数据**。

### 9. 收盘快照数据：`POST /api/stock/closing_snapshot`

- **URL**：`{baseUrl}/api/stock/closing_snapshot`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "start_time": "2024-01-01 15:00:00",
  "end_time": "2024-01-01 15:05:00",
  "page": 0,
  "page_size": 100
}
```

- 返回字段：包含价格、成交量、买卖盘、涨跌幅等完整快照数据

> **重要提醒**：单次请求**最多返回 10000 条数据**。

### 10. 股票快照数据（实时/历史）：`POST /api/stock/snapshot_daily`

- **URL**：`{baseUrl}/api/stock/snapshot_daily`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "date": "2024-01-01",
  "page": 0,
  "page_size": 10000
}
```

- 特性：
  - **实时快照**：如果不提供 `date` 或提供今日日期，系统优先从 Redis 缓存读取最新的实时快照数据。
  - **历史快照**：如果提供历史日期，系统返回当天的历史快照数据。
  - 返回字段包含 40+ 个指标：价格、成交量、市值、PE、PB、买卖盘等。
  - `page_size`：**最大 10000**。

> **重要提醒**：这是获取实时行情快照的主要接口。

### 11. 推送历史数据：`POST /api/stock/snapshot_push_history`

- **URL**：`{baseUrl}/api/stock/snapshot_push_history`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **说明**：查询 WebSocket 推送历史，按推送批次分组返回

### 12. 停牌信息：`GET /api/stock/suspension`

- **URL**：`{baseUrl}/api/stock/suspension`
- **方法**：`GET`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **Query 参数**：
  - `stock_code`（可选）
  - `trade_date`（可选）
  - `page`, `page_size`

### 13. 复权因子：`POST /api/stock/adj_factor`

- **URL**：`{baseUrl}/api/stock/adj_factor`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "start_time": "2024-01-01",
  "end_time": "2024-01-31",
  "page": 0,
  "page_size": 10000
}
```

- 返回字段：`stock_code`, `stock_name`, `trade_date`, `factor_a`, `factor_b`（自定义复权因子）

> **重要提醒**：单次请求**最多返回 10000 条数据**。

### 14. 数据下载（整日行情）：`POST /api/stock/daily_dump`

- **URL**：`{baseUrl}/api/stock/daily_dump`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "date": "2024-01-01",
  "level": "daily"
}
```

- `level` 参数：`daily` | `1min` | `5min` | `15min` | `30min` | `60min`
- 返回：gzip 压缩的 JSON 文件（通过 Nginx 高性能下载）
- 限制：
  - 只能下载**最近 90 天**的数据
  - 每个用户每个日期每天最多下载 **10 次**，超过后限制 3 天
  - 当日数据需收盘后（15:05 后）才能下载

### 15. 可转债日线数据：`POST /api/bond/daily`

- **URL**：`{baseUrl}/api/bond/daily`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "128136.SZ",
  "start_time": "2024-01-01",
  "end_time": "2024-01-31",
  "page": 0,
  "page_size": 10000
}
```

- 字段说明：
  - `stock_code`（可选）：可转债代码，如 `128136.SZ`，支持数组
  - `start_time`、`end_time`：格式为 `YYYY-MM-DD`
- 返回字段：`stock_code`, `stock_name`, `trade_date`, `open`, `high`, `low`, `close`, `prev_close`, `change`, `pct_chg`, `factor`, `vol`, `amount`

> 单次请求**最多返回 10000 条数据**。

### 16. 可转债日指标数据：`POST /api/bond/indicator_daily`

- **URL**：`{baseUrl}/api/bond/indicator_daily`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": "128136.SZ",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "page": 0,
  "page_size": 10000
}
```

- 字段说明：
  - `stock_code`（可选）：可转债代码，支持数组
  - `start_date`、`end_date`（可选）：日期范围，至少提供一个
- 返回字段：`stock_code`, `stock_name`, `trade_date`, `name`, `pre_close`, `open`, `high`, `low`, `close`, `change`, `pct_chg`, `vol`, `amount`, `remain_size`, `pure_bond`, `pure_premium`, `conv_value`, `conv_premium` 等

> 单次请求**最多返回 10000 条数据**。

### 17. 可转债列表：`POST /api/bond/list`

- **URL**：`{baseUrl}/api/bond/list`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "bond_code": "128136.SZ",
  "stock_code": "000001.SZ",
  "exchange": "SZSE",
  "page": 0,
  "page_size": 10000
}
```

- 字段说明：
  - `bond_code`（可选）：可转债代码筛选
  - `stock_code`（可选）：正股代码筛选
  - `exchange`（可选）：交易所筛选（SZSE/SSE）
- 返回字段：包含 `bond_code`, `bond_name`, `bond_short_name`, `conv_code`, `stock_code`, `stock_name` 等完整可转债信息

## 调用策略与最佳实践

1. **API Key 获取与使用**
   - 优先从环境变量 `STOCK_API_KEY` 读取（由 OpenClaw 按 `skills.entries.openclaw-stock-skill.apiKey` 注入）。
   - 若环境变量缺失，可根据用户在 Skill 配置面板中输入的值（通常同样会映射到该环境变量）进行调用。
   - 不要在 URL Query 中传递 `apiKey` 或 `api_key`，后端会视为安全风险。

2. **错误处理**
   - `code = 401`：API Key 无效或缺失，应提示用户检查在 OpenClaw Skill 配置中的 API Key。
   - `code = 403`：权限不足或下载次数/访问次数限制，应向用户说明权限/限流约束。
   - `code = 429`：请求过于频繁，需减少调用频率或提示用户稍后再试。

3. **分页与大数据量**
   - 若 `data.total` 很大，代理应分批分页请求，并在回答中做汇总，而不是一次性获取全部数据。
   - 对于分钟级或 tick 级大数据量，应在对话中与用户确认时间范围和精度，避免无谓的海量下载。

4. **单位与精度**
   - 价格、成交量等字段在后端已经统一保留 2 位小数；如需展示给用户，可直接使用或再格式化。
   - 分红相关字段在估值接口中已做 10 年平均等处理，解释时注意说明口径（年化、近 10 年等）。

## 使用示例（给代理的思路）

- 当用户说：**“帮我查一下 000001.SZ 在 2024 年 1 月份的日 K 线”**
  1. 调用 `POST /api/stock/daily`，`stock_code = "000001.SZ"`，时间区间为 `2024-01-01` 至 `2024-01-31`。
  2. 对返回的 `data.list` 进行整理，总结涨跌幅、最大回撤、平均成交额等。

- 当用户说：**“这周哪些天是交易日？”**
  1. 根据当前日期计算一周范围，调用 `GET /api/basic/calendar`。
  2. 将 `is_open = 1` 的日期列出，说明哪些是交易日。

本技能不包含额外可执行脚本，完全通过指导代理调用现有 HTTP 接口工作。所有请求都应优先使用 `STOCK_API_KEY` 环境变量，并遵守上述限流与安全约定。

