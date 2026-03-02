"""
股票数据 API Skill for OpenClaw

该 skill 提供了访问股票数据的完整功能，包括：
- 股票列表查询
- 日K线数据
- 历史分时数据
- 财务数据
- 实时数据（竞价、收盘快照）
- 股票估值数据

使用前请确保：
1. 已在 https://data.diemeng.chat/ 注册账号
2. 已获取 API Key
3. 设置环境变量 STOCK_API_KEY 或在代码中配置
"""

import os
import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta


# API 基础配置
BASE_URL = "https://data.diemeng.chat/api"
API_KEY_ENV = "STOCK_API_KEY"


def get_api_key() -> Optional[str]:
    """获取 API Key，优先从环境变量读取"""
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"未找到 API Key！请设置环境变量 {API_KEY_ENV}，"
            f"或访问 https://data.diemeng.chat/ 注册并获取 API Key"
        )
    return api_key


def _make_request(
    method: str,
    endpoint: str,
    headers: Optional[Dict] = None,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    发送 HTTP 请求的通用方法
    
    Args:
        method: HTTP 方法 (GET, POST)
        endpoint: API 端点路径
        headers: 请求头
        params: URL 参数（GET 请求）
        json_data: JSON 数据（POST 请求）
    
    Returns:
        API 响应数据
    """
    api_key = get_api_key()
    
    url = f"{BASE_URL}{endpoint}"
    request_headers = {
        "apiKey": api_key,
        "Content-Type": "application/json"
    }
    if headers:
        request_headers.update(headers)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=request_headers, json=json_data, timeout=30)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") != 200:
            raise Exception(f"API 错误: {result.get('msg', '未知错误')}")
        
        return result.get("data", {})
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"请求失败: {str(e)}")


# ==================== 股票列表相关 ====================

def get_stock_list(
    stock_code: Optional[str] = None,
    page: int = 0,
    page_size: int = 20000
) -> Dict[str, Any]:
    """
    获取股票列表
    
    Args:
        stock_code: 股票代码（可选，用于筛选）
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    params = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        params["stock_code"] = stock_code
    
    return _make_request("GET", "/stock/list", params=params)


# ==================== 行情数据相关 ====================

def get_daily_data(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取日K线数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表，例如 "600000.SH" 或 ["600000.SH", "000001.SZ"]
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        # 默认查询最近30天
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/daily", json_data=payload)


def get_history_data(
    stock_code: Optional[Union[str, List[str]]] = None,
    level: str = "5min",
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取历史分时数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表
        level: 时间级别，可选值: "1min", "5min", "15min", "30min", "60min"
        start_time: 开始时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        # 默认查询今天
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
    
    payload = {
        "level": level,
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/history", json_data=payload)


# ==================== 财务数据相关 ====================

def get_finance_data(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取每日财务数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典，包含 PE、PB、PS、市值等财务指标
    """
    if not start_time or not end_time:
        # 默认查询最近30天
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/finance", json_data=payload)


def get_stock_valuation(
    sort_by: str = "pe_ttm",
    sort_order: str = "asc",
    industry: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    获取股票估值列表
    
    Args:
        sort_by: 排序字段，可选值: "pe_ttm", "pe_percentile", "dividend_yield_ttm", "industry_pe_rank"
        sort_order: 排序方向，可选值: "asc", "desc"
        industry: 行业筛选（可选）
        limit: 返回数量限制
        offset: 偏移量
    
    Returns:
        股票估值数据列表
    """
    params = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "limit": limit,
        "offset": offset
    }
    
    if industry:
        params["industry"] = industry
    
    return _make_request("GET", "/stock/valuation/list", params=params)


# ==================== 实时数据相关 ====================

def get_call_auction(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取集合竞价数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表
        start_time: 开始时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        # 默认查询今天
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
    
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/call_auction", json_data=payload)


def get_closing_snapshot(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取收盘快照数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表
        start_time: 开始时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        # 默认查询今天
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
    
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/closing_snapshot", json_data=payload)


# ==================== 基础数据相关 ====================

def get_trade_calendar(
    start_time: str,
    end_time: str
) -> List[Dict[str, Any]]:
    """
    获取交易日历
    
    Args:
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
    
    Returns:
        交易日历列表，包含 date 和 is_open 字段
    """
    params = {
        "start_time": start_time,
        "end_time": end_time
    }
    
    return _make_request("GET", "/basic/calendar", params=params)


# ==================== 辅助函数 ====================

def search_stock_by_name(name: str) -> List[Dict[str, Any]]:
    """
    根据股票名称搜索股票
    
    Args:
        name: 股票名称（支持模糊匹配）
    
    Returns:
        匹配的股票列表
    """
    result = get_stock_list(page_size=20000)
    stocks = result.get("list", [])
    
    # 简单模糊匹配
    matched = [
        stock for stock in stocks
        if name.lower() in stock.get("name", "").lower()
    ]
    
    return matched


def get_stock_info(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取单个股票的详细信息
    
    Args:
        stock_code: 股票代码，例如 "600000.SH"
    
    Returns:
        股票信息字典，如果未找到返回 None
    """
    result = get_stock_list(stock_code=stock_code, page_size=1)
    stocks = result.get("list", [])
    
    if stocks:
        return stocks[0]
    return None
