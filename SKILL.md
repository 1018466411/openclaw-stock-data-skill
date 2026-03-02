---
name: stock_data_api
description: >
  股票数据 API Skill，提供完整的 A 股市场数据访问功能，包括股票列表、行情 K 线、
  分时、财务指标、估值、集合竞价、收盘快照和交易日历等。适合作为量化分析、
  投资研究和策略回测的数据来源。
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["STOCK_API_KEY"] },
        "primaryEnv": "STOCK_API_KEY",
        "emoji": "📈"
      }
  }
---

# 股票数据 API Skill（stock_data_api）

本 Skill 为 OpenClaw / ClaudeClaw / KimiClaw 等支持 AgentSkills 规范的客户端提供
统一的 A 股市场数据访问接口。

## 功能概览

- 股票列表与搜索
- 日 K 线与历史分时数据
- 财务指标（PE、PB、PS、市值等）
- 估值排行与百分位
- 集合竞价与收盘快照
- 交易日历查询

## API Key 配置

- 在 OpenClaw 等客户端安装本 Skill 后，会在 Skill 配置页面自动出现一个
  `api_key` 输入框（来源于 `skill.json` 中的 `configuration.api_key` 字段）。
- 将从 `https://data.diemeng.chat/` 获取到的 API Key 填入该输入框，客户端会在
  运行时注入为环境变量 `STOCK_API_KEY`。
- 代码内部统一从 `STOCK_API_KEY` 环境变量中读取密钥，不会在日志和提示词中明文输出。

