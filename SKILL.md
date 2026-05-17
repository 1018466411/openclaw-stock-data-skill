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
> - OpenClaw 会按照 [`skills.entries.<key>`](https://docs.openclaw.ai/tools/skills-config) [配置](https://docs.openclaw.ai/tools/skills-config) 把 API Key 和自定义配置注入到进程环境变量中。
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
请务必访问官网 <https://data.diemeng.chat/>（海外请访问 `https://mg.diemeng.chat/`），在个人中心开通所需权限（如股票行情、实时快照、可转债等）。

### 2. 接口类型区分

- **实时接口**：
  - `get_stock_snapshot_daily`（不传日期或传今日）：获取最新实时快照（价格、成交量、五档盘口等）。
  - `get_stock_snapshot_push_history`：获取实时推送的历史记录。
  - `get_call_auction`：获取集合竞价数据。
- **历史接口**：
  - `get_daily_data`：获取历史日 K 线。
  - `get_kline_data`：获取历史周期K线（周K、月K）。
  - `get_kline_adj_data`：获取复权历史周期K线（周K、月K）。
  - `get_history_data`：获取历史分钟线。
  - `get_finance_data`：获取历史财务指标。
  - `get_financial_indicator`：获取财务指标报表数据（stock\_financial\_indicator）。
  - `get_income_statement`：获取利润表数据（stock\_income）。
  - `get_balancesheet`：获取资产负债表数据（stock\_balancesheet）。
  - `get_cashflow_statement`：获取现金流量表数据（stock\_cashflow）。
  - `get_main_fund_flow`：获取大小单资金金流向。
  - `get_main_fund_flow_overview`：获取主力资金流向总览。
  - `get_cyq_chips`：获取筹码峰分布。
  - `get_holder_number`：获取股东人数数据。
  - `get_pledge_stat`：获取股票质押统计数据。
  - `get_margin_detail`：获取融资融券明细数据。
  - `get_stock_snapshot_daily`（传历史日期）：获取历史快照。
- **指数与板块接口**：
  - `get_index_history`：获取指数分钟级历史数据。
  - `get_index_realtime_history`：获取指数当天实时 1 分钟级别分时数据。
  - `get_index_weight`：获取指数月度成分和权重数据（index_code 必传，可按 stock_code 和 trade_date 筛选）。
  - `get_ths_sector_categories`：获取同花顺板块分类数据。
  - `get_ths_constituent_stocks`：获取同花顺成分股数据。
  - `get_dc_blocks`：获取东方财富板块列表。
  - `get_dc_daily`：获取东方财富板块日K（按交易日或板块代码）。
  - `get_dc_block_stocks`：获取东方财富板块成分股（支持板块/日期/股票筛选，空参默认最新日期）。
  - `get_tdx_block_stocks`：获取通达信板块成分股，返回分页结构 `data.total/page/page_size/list`，其中 `list` 项包含 `block_code`、`block_name`、`block_type`、`stock_code`。

## 总体说明

- **获取正确的 API Key 并验证**：
  - **一定要获取到正确的 apiKey 才可以调用接口。**
  - **获取途径**：优先从环境变量 `STOCK_API_KEY` 读取，或从当前目录的 `config.json` 获取。如果在 Skill 面板配置了也会注入到环境变量中。
- **基础域名**：默认接口的域名是 `data.diemeng.chat`，**如果是海外 IP 则访问 `mg.diemeng.chat`**。
- **鉴权方式**：所有需要权限的接口都必须带上 API Key，并且**必须放到 HTTP Header 里面**：
  - `apiKey: <STOCK_API_KEY>`（强制要求）
  - `Content-Type: application/json`
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

- **get\_stock\_daily\_bars**：查询指定股票在某一时间区间内的日线 K 线数据。
- **get\_stock\_intraday\_bars**：查询分钟级（1/5/15/30/60 分钟）历史数据。
- **get\_stock\_finance\_factors**：查询日度财务因子（PE、PB、换手率等）。
- **get\_stock\_main\_fund\_flow**：查询主力资金流向明细（按时间范围/股票代码，支持仅传其一）。
- **get\_stock\_main\_fund\_flow\_overview**：查询主力资金流向总览（净流入率与分档统计）。
- **get\_stock\_limit\_up**：查询涨停明细数据（封单、连板、涨停原因等）。
- **get\_stock\_list**：查询股票基础信息列表，用于代码／名称搜索。
- **get\_stock\_calendar\_and\_snapshot**：查询交易日历和当日快照。
- **get\_stock\_search**：使用自然语言条件搜索符合条件的股票（如"PE<20 且换手率>3%"）。
- **get\_stock\_call\_auction**：查询集合竞价数据。
- **get\_stock\_closing\_snapshot**：查询收盘快照数据。
- **get\_stock\_snapshot\_daily**：查询实时或历史股票快照（含 Redis 缓存加速）。
- **get\_stock\_suspension**：查询股票停牌信息。
- **get\_stock\_adj\_factor**：查询复权因子。
- **get\_bond\_daily**：查询可转债日线数据。
- **get\_bond\_indicator\_daily**：查询可转债日指标数据。
- **get\_bond\_list**：查询可转债列表信息。
- **get\_index\_realtime\_history**：查询指数当天实时 1 分钟级别分时数据。
- **get\_index\_weight**：查询指数月度成分和权重数据（可选按成分股过滤）。

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
  "volType": "share",
  "page": 0,
  "page_size": 1000
}
```

- 说明：
  - `stock_code` 可以是单个字符串，也可以是字符串数组。
  - `start_time`、`end_time` 格式为 `YYYY-MM-DD`。
  - `volType` 可选：`share`（默认，按股返回）或 `lot`（按手返回，`1手=100股`）。
  - 支持分页，`page` 从 0 开始。
- 响应字段：
  - `data.total`：总记录数
  - `data.list`：每条记录包含 `stock_code`, `stock_name`, `trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount` 等字段，价格与成交量已在后端统一保留 2 位小数，`vol` 单位由 `volType` 决定。
- 响应主体（简化）：
  - `data.total`：总记录数
  - `data.list`：每条记录包含 `stock_code`, `trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount` 等字段，价格与成交量已在后端统一保留 2 位小数。

### 1.1 复权日线：`POST /api/stock/daily_adj`

- 请求参数与 `POST /api/stock/daily` 基本一致，额外支持 `algo`（`recursive`/`factor`）。
- 新增 `volType` 可选参数：`share`（默认，按股）或 `lot`（按手）。
- 为兼容历史调用，未传 `volType` 时保持旧行为（按股返回）。

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
  - `stock_code`：仅支持单个股票代码字符串（不支持数组）
  - `level`：`"1min" | "5min" | "15min" | "30min" | "60min"`
  - `start_time` / `end_time`：
    - 允许仅日期（自动补全 00:00:00 和 23:59:59）
    - 或完整时间戳 `YYYY-MM-DD HH:MM:SS`
- 响应主体（简化）单位手：
  - `data.list` 中每条包含：`stock_code`, `trade_time`, `open`, `high`, `low`, `close`, `vol`, `amount`。

> 用于用户询问“某天/某段时间内的分钟级行情、分时数据”等场景。

### 3. 实时分时数据(支持最近7天内)：`POST /api/realtime/history` 及 `/api/index/realtime/history`

- **URL**：`{baseUrl}/api/realtime/history` 或 `{baseUrl}/api/index/realtime/history`
- **方法**：`POST`
- **Headers**：同上
- **请求体 JSON**：

```json
{
  "stock_code": "000001.SZ",
  "trade_time": "2026-03-15 09:31:00",
  "date": "2026-03-15"
}
```

*(对于指数接口，参数名为* *`index_code`)*

- 说明：
  - 获取实时 1 分钟级别分时数据，支持最近7天内，支持全市场或指定股票/指数。
  - `stock_code`/`index_code` 或 `trade_time` 至少提供一个。
  - 返回数据会根据代码 + `trade_time` 进行去重。

> **调用建议（定时任务拉取全市场数据）**：
>
> - 建议使用时间 (`trade_time`) 来获取实时分时，一次可以获取某一分钟的全市场数据。
> - 使用定时任务来获取数据，每分钟获取上一分钟的数据。
> - 建议在每分钟的 2 到 5 秒后开始获取。
> - 如果获取不到，建议暂停 1 秒后继续获取，最多重试不要超过 60 次，避免陷入死循环。
> - 建议在每分钟 15 秒之后再调用接口更新一次数据，确保数据的准确性。

### 3.1 指数成分与权重：`POST /api/index/weight`

- **URL**：`{baseUrl}/api/index/weight`
- **方法**：`POST`
- **Headers**：同上
- **请求体 JSON**：

```json
{
  "index_code": "000300.SH",
  "stock_code": "600519.SH",
  "trade_date": "2026-03-31",
  "page": 0,
  "page_size": 2000
}
```

- 字段说明：
  - `index_code`（必填）：指数代码
  - `stock_code`（可选）：成分股代码，支持字符串或数组（后端按 `con_code` 过滤）
  - `trade_date`（可选）：支持 `YYYY-MM` 或 `YYYY-MM-DD`，查询时仅按年和月过滤
  - `trade_date` 不传时默认返回该指数最新月份数据
- 返回字段：
  - `index_code`, `stock_code`, `trade_date`, `weight`

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

### 4.0 财务指标报表数据：`POST /api/stock/financial_indicator`

- **URL**：`{baseUrl}/api/stock/financial_indicator`
- **方法**：`POST`
- **请求体 JSON**：

```json
{
  "stock_code": "600000.SH",
  "end_date": "2025-12-31",
  "ann_date": "2026-03-28",
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `stock_code`：股票代码，支持字符串或数组
  - `end_date`：报告期最后日期，格式 `YYYY-MM-DD`
  - `ann_date`：公告日期，格式 `YYYY-MM-DD`
  - `stock_code` / `end_date` / `ann_date` 三选一至少提供一个
  - `page` 从 0 开始，`page_size` 最大 10000
- 主要返回字段（实际会返回 `stock_financial_indicator` 全字段）：
  - 基础标识：`stock_code`, `ann_date`, `end_date`, `update_flag`, `create_time`
  - 盈利能力：`eps`, `dt_eps`, `profit_dedt`, `op_income`, `ebit`, `ebitda`, `gross_margin`, `grossprofit_margin`, `netprofit_margin`
  - 资产收益：`roe`, `roe_dt`, `roe_yearly`, `roa`, `roa_yearly`, `roic`, `roic_yearly`
  - 现金与每股：`bps`, `ocfps`, `cfps`
  - 偿债能力：`current_ratio`, `quick_ratio`, `debt_to_assets`
  - 增长能力：`basic_eps_yoy`, `netprofit_yoy`, `dt_netprofit_yoy`, `tr_yoy`, `or_yoy`, `q_sales_yoy`, `q_netprofit_yoy`
  - 研发投入：`rd_exp`
- 完整返回字段：返回 `stock_financial_indicator` 全字段（除 `update_flag`、`create_time`）。

### 4.0.1 利润表数据：`POST /api/stock/income`

- **URL**：`{baseUrl}/api/stock/income`
- **方法**：`POST`
- **请求体 JSON**：

```json
{
  "stock_code": "600000.SH",
  "end_date": "2025-12-31",
  "ann_date": "2026-03-28",
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `stock_code`：股票代码，支持字符串或数组
  - `end_date`：报告期最后日期，格式 `YYYY-MM-DD`
  - `ann_date`：公告日期，格式 `YYYY-MM-DD`
  - `stock_code` / `end_date` / `ann_date` 三选一至少提供一个
  - `page` 从 0 开始，`page_size` 最大 10000
- 完整返回字段：返回 `stock_income` 全字段（除 `update_flag`、`create_time`）。

### 4.0.2 资产负债表数据：`POST /api/stock/balancesheet`

- **URL**：`{baseUrl}/api/stock/balancesheet`
- **方法**：`POST`
- 请求参数与 `/api/stock/income` 完全一致（`stock_code` / `end_date` / `ann_date` 三选一至少传一个）。
- 完整返回字段：返回 `stock_balancesheet` 全字段（除 `update_flag`、`create_time`）。

### 4.0.3 现金流量表数据：`POST /api/stock/cashflow`

- **URL**：`{baseUrl}/api/stock/cashflow`
- **方法**：`POST`
- 请求参数与 `/api/stock/income` 完全一致（`stock_code` / `end_date` / `ann_date` 三选一至少传一个）。
- 完整返回字段：返回 `stock_cashflow` 全字段（除 `update_flag`、`create_time`）。

### 4.1 主力资金流向明细：`POST /api/stock/main_fund_flow`

- **URL**：`{baseUrl}/api/stock/main_fund_flow`
- **方法**：`POST`
- **请求体 JSON**：

```json
{
  "start_time": "2026-04-03",
  "end_time": "2026-04-03",
  "stock_code": ["600000.SH", "000001.SZ"],
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `start_time` / `end_time`：交易日期范围，格式 `YYYY-MM-DD`，闭区间；当 `start_time = end_time` 时可查询当天数据
  - `stock_code`：股票代码，支持字符串或数组
  - `stock_code` 和 (`start_time` + `end_time`) 至少提供其一
  - `page` 从 0 开始，`page_size` 最大 10000
- 分档口径：
  - 小单：成交额 < 5万
  - 中单：成交额 5万 \~ 20万
  - 大单：成交额 20万 \~ 100万
  - 特大单：成交额 >= 100万
- 主要返回字段：
  - `trade_date`, `stock_code`
  - `buy_sm_vol`, `buy_sm_amount`, `sell_sm_vol`, `sell_sm_amount`
  - `buy_md_vol`, `buy_md_amount`, `sell_md_vol`, `sell_md_amount`
  - `buy_lg_vol`, `buy_lg_amount`, `sell_lg_vol`, `sell_lg_amount`
  - `buy_elg_vol`, `buy_elg_amount`, `sell_elg_vol`, `sell_elg_amount`
  - `net_mf_vol`, `net_mf_amount`

### 4.2 主力资金流向总览：`POST /api/stock/main_fund_flow_overview`

- **URL**：`{baseUrl}/api/stock/main_fund_flow_overview`
- **方法**：`POST`
- **请求体 JSON**：

```json
{
  "start_time": "2026-04-03",
  "end_time": "2026-04-03",
  "stock_code": "600000.SH",
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `start_time` / `end_time`：交易日期范围，格式 `YYYY-MM-DD`，闭区间；当 `start_time = end_time` 时可查询当天数据
  - `stock_code`：股票代码，支持字符串或数组
  - `stock_code` 和 (`start_time` + `end_time`) 至少提供其一
  - `page` 从 0 开始，`page_size` 最大 10000
- 分档口径：
  - 小单：成交额 < 5万
  - 中单：成交额 5万 \~ 20万
  - 大单：成交额 20万 \~ 100万
  - 特大单：成交额 >= 100万
- 主要返回字段：
  - `trade_date`, `stock_code`, `name`, `close`, `pct_change`
  - `net_amount`, `net_amount_rate`
  - `buy_elg_amount`, `buy_elg_amount_rate`
  - `buy_lg_amount`, `buy_lg_amount_rate`
  - `buy_md_amount`, `buy_md_amount_rate`
  - `buy_sm_amount`, `buy_sm_amount_rate`

### 4.3 筹码峰分布：`POST /api/stock/cyq_chips`

- **URL**：`{baseUrl}/api/stock/cyq_chips`
- **方法**：`POST`
- **请求体 JSON**：

```json
{
  "start_time": "2026-04-03",
  "end_time": "2026-04-03",
  "stock_code": "600000.SH",
  "page": 0,
  "page_size": 1000
}
```

- 字段说明：
  - `start_time` / `end_time`：交易日期范围，格式 `YYYY-MM-DD`，闭区间；当 `start_time = end_time` 时可查询当天数据
  - `stock_code`：股票代码，支持字符串或数组
  - `stock_code` 和 (`start_time` + `end_time`) 至少提供其一
  - `page` 从 0 开始，`page_size` 最大 10000
- 主要返回字段：
  - `trade_date`, `stock_code`, `price`, `percent`

### 4.4 股票基础信息列表：`GET /api/stock/list`

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

### 5. 交易日历：`GET/POST /api/basic/calendar`

- **URL**：`{baseUrl}/api/basic/calendar`
- **方法**：`GET` / `POST`
- **请求参数**：
  - `start_time`: `YYYY-MM-DD`
  - `end_time`: `YYYY-MM-DD`
- 响应：
  - `data` 为数组，每条含 `date`, `is_open`（1 为交易日，0 为休市）。

> 当用户问“某段时间哪些是交易日”“下一个交易日是什么时候”等，可使用此接口。


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

### 7. 期货数据

*   **获取合约基础信息 (`get_future_basic`)**：获取期货合约的基础信息数据，包括乘数、交割方式、上市日期等。
*   **获取主连合约映射 (`get_future_mapping`)**：获取期货主连或连续合约与实际月合约的映射关系。
*   **获取分钟K线数据 (`get_future_minute`)**：获取期货合约的历史分钟K线数据。

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
- **说明**：查询 WebSocket 推送历史，返回快照数组

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
  - 数据量较大，每个用户每个日期每天最多下载 **10 次**，超过后会被禁止下载该日期三天，请联系客服解封
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

### 18. 涨停明细数据：`POST /api/stock/limit_up`

- **URL**：`{baseUrl}/api/stock/limit_up`
- **方法**：`POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **请求体 JSON**：

```json
{
  "stock_code": ["603716.SH", "000001.SZ"],
  "start_time": "2026-04-10",
  "end_time": "2026-04-10",
  "page": 0,
  "page_size": 10000
}
```

- 字段说明：
  - `stock_code`（可选）：股票代码，支持字符串或数组
  - `start_time`、`end_time`（必填）：日期范围，格式 `YYYY-MM-DD`
  - `page`：页码，从 0 开始
  - `page_size`：每页数量，最大 10000
- 返回字段：
  - 基础信息：`trade_date`, `stock_code`, `stock_name`, `price`, `change_percent`
  - 封单信息：`sealed_volume`, `sealed_amount`, `sealed_turnover_ratio`, `sealed_flow_ratio`
  - 涨停过程：`first_limit_time`, `final_limit_time`, `open_count`, `consecutive_days`, `boards`
  - 业务标签：`limit_type`, `is_limit_up`, `reason_text`

### 19. 同花顺热度榜：`GET /api/ths/hot` / `POST /api/ths/hot`

- **URL**：`{baseUrl}/api/ths/hot`
- **方法**：`GET` / `POST`
- **Headers**：`apiKey: <STOCK_API_KEY>`
- **参数**：
  - `market`（可选）：热榜类型 (默认：热股)。可选值：`热股`, `ETF`, `可转债`, `行业板块`, `概念板块`, `期货`
  - `trade_date`（可选）：指定交易日期，支持 `YYYY-MM-DD` 或 `YYYYMMDD`；不传默认返回最新交易日
  - `GET` 使用 Query 参数，`POST` 使用 JSON Body
- **返回字段**：
  - `trade_date`: 交易日期
  - `update_time`: 排行榜更新时间
  - `list`: 热榜数据列表，包含 `name` (名称), `code` (代码), `rank` (排名), `pct_change` (涨跌幅%), `hot` (热度值)

### 20. 涨跌停推送 WS 订阅：`GET {{WS_BASE_URL}}/ws/stream`

- **URL**：`{{WS_BASE_URL}}/ws/stream?token=<STOCK_API_KEY>&types=...`
- **协议**：WebSocket
- **鉴权**：Query 参数 `token`（使用 API Key）
- **订阅参数**：`types`（逗号分隔，支持多选）

- **六类推送与订阅值**：
  - 涨停推送：`limit_up`
  - 涨停炸板：`limit_up_broken`
  - 涨停股数据推送（聚合）：`stock_limit_up`（包含 `limit_up` + `limit_up_broken`）
  - 跌停推送：`limit_down`
  - 跌停炸板：`limit_down_broken`
  - 跌停股数据推送（聚合）：`stock_limit_down`（包含 `limit_down` + `limit_down_broken`）

- **连接示例**：
  - `{{WS_BASE_URL}}/ws/stream?token=<STOCK_API_KEY>&types=stock_limit_up,stock_limit_down`

- **动态订阅示例**：

```json
{"action":"subscribe","types":["stock_limit_up","stock_limit_down"]}
```

- **推送消息示例**：

```json
{
  "type": "stock_limit_event",
  "data": {
    "type": "limit_up",
    "stock_code": "600000.SH",
    "stock_name": "浦发银行",
    "change_rate": 10.0,
    "source": "fast",
    "timestamp": "2026-04-17 11:23:45"
  }
}
```

- **字段说明**：
  - 外层 `type` 固定为 `stock_limit_event`
  - `data.type` 可能值：`limit_up` / `limit_up_broken` / `limit_down` / `limit_down_broken`
  - 常见字段：`stock_code`, `stock_name`, `change_rate`, `source`, `timestamp`

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
  1. 根据当前日期计算一周范围，调用 `GET/POST /api/basic/calendar`。
  2. 将 `is_open = 1` 的日期列出，说明哪些是交易日。

本技能不包含额外可执行脚本，完全通过指导代理调用现有 HTTP 接口工作。所有请求都应优先使用 `STOCK_API_KEY` 环境变量，并遵守上述限流与安全约定。
