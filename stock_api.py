"""
股票数据 API Skill for OpenClaw

该 skill 提供了访问股票数据的完整功能，包括：
- 股票列表查询
- 日K线数据
- 历史分时数据
- 财务数据
- 实时数据（竞价、收盘快照）

使用前请确保：
1. 已在 https://data.diemeng.chat/ 注册账号
2. 已获取 API Key
3. 设置环境变量 STOCK_API_KEY 或在代码中配置
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta


# API 基础配置
API_DOMAIN = os.getenv("STOCK_API_DOMAIN", "data.diemeng.chat")
# 如果是海外 IP，建议设置环境变量 STOCK_API_DOMAIN="mg.diemeng.chat"
BASE_URL = f"https://{API_DOMAIN}/api"
API_KEY_ENV = "STOCK_API_KEY"
CONFIG_FILE = "config.json"


def get_api_key() -> str:
    """
    获取 API Key
    优先级：
    1. 配置的参数获取（如果在 Skill 初始化或函数调用时直接传入，暂不在此处理）
    2. 环境变量 STOCK_API_KEY
    3. 当前目录下的 config.json 文件中的 api_key 字段
    
    一定要获取到正确的 apiKey 才可以调用接口。
    接口的域名是 data.diemeng.chat，如果是海外 IP 则访问 mg.diemeng.chat。
    apiKey 需要放到 header 里面:
    headers = { 
         "apiKey": "YOUR_API_KEY", 
         "Content-Type": "application/json" 
    }
    """
    # 1. 尝试从环境变量读取
    api_key = os.getenv(API_KEY_ENV)
    if api_key:
        return api_key

    # 2. 尝试从配置文件读取
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('api_key')
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Warning: 读取配置文件 {CONFIG_FILE} 失败: {e}")

    # 3. 未找到，抛出异常，强调必须获取正确的 apiKey
    raise ValueError(
        f"【错误】一定要获取到正确的 apiKey 才可以调用接口！\n"
        f"获取 apiKey 途径：\n"
        f"1. 配置环境变量 {API_KEY_ENV}\n"
        f"2. 在同级目录下创建 {CONFIG_FILE} 文件，内容为: {{\"api_key\": \"YOUR_API_KEY\"}}\n"
        f"3. 访问 https://data.diemeng.chat/ 注册并获取 API Key\n\n"
        f"请注意：接口的域名是 data.diemeng.chat，如果是海外 IP 则访问 mg.diemeng.chat。\n"
        f"apiKey 会被放到 header 里面: {{\"apiKey\": \"YOUR_API_KEY\", \"Content-Type\": \"application/json\"}}"
    )


def _make_request(
    method: str,
    endpoint: str,
    headers: Optional[Dict] = None,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    发送 HTTP 请求的通用方法
    
    必须获取到正确的 apiKey 才可以调用接口，
    接口的域名是 data.diemeng.chat，如果是海外 IP 则访问 mg.diemeng.chat，
    apiKey 放到 header 里面:
    headers = {
        "apiKey": "YOUR_API_KEY",
        "Content-Type": "application/json"
    }

    Args:
        method: HTTP 方法 (GET, POST)
        endpoint: API 端点路径
        headers: 请求头
        params: URL 参数（GET 请求）
        json_data: JSON 数据（POST 请求）
    
    Returns:
        API 响应数据
    """
    # 一定要获取到正确的 apiKey 才可以调用接口
    api_key = get_api_key()
    if not api_key:
        raise ValueError("一定要获取到正确的 apiKey 才可以调用接口！")
    
    url = f"{BASE_URL}{endpoint}"
    # apikey放到header里面
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
            msg = result.get('msg', '未知错误')
            if result.get("code") == 403:
                msg += " (权限不足，请访问 https://data.diemeng.chat/ 开通对应权限)"
            raise Exception(f"API 错误: {msg}")
        
        return result.get("data", {})
    
    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 403:
            raise Exception("权限不足 (HTTP 403): 请访问 https://data.diemeng.chat/ 开通对应权限")
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
    vol_type: str = "share",
    page: int = 0,
    page_size: int = 60000
) -> Dict[str, Any]:
    """
    获取日K线数据
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表，例如 "600000.SH" 或 ["600000.SH", "000001.SZ"]
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        vol_type: 成交量单位，share(股，默认) 或 lot(手)
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
        "volType": vol_type,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/daily", json_data=payload)

def get_hk_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    vol_type: str = "share",
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取港股日K线数据
    """
    if not start_time or not end_time:
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "volType": vol_type,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/hk/daily", json_data=payload)

def get_kline_data(
    period: str,
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取周期K线数据 (周K、月K)
    
    Args:
        period: 周期，可选值: "weekly", "monthly"
        stock_code: 股票代码，支持单个字符串或列表，例如 "600000.SH" 或 ["600000.SH", "000001.SZ"]
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        end_time = datetime.now().strftime("%Y-%m-%d")
        if period == "monthly":
            start_time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            start_time = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    payload = {
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/kline", json_data=payload)

def get_kline_adj_data(
    period: str,
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = None,
    end_time: str = None,
    algo: str = "recursive",
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取复权周期K线数据 (周K、月K)
    
    Args:
        period: 周期，可选值: "weekly", "monthly"
        stock_code: 股票代码，支持单个字符串或列表
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        algo: 复权算法，可选值: "recursive", "factor"
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    if not start_time or not end_time:
        end_time = datetime.now().strftime("%Y-%m-%d")
        if period == "monthly":
            start_time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            start_time = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    payload = {
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "algo": algo,
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    
    return _make_request("POST", "/stock/kline_adj", json_data=payload)




def get_history_data(
    stock_code: Optional[str] = None,
    level: str = "5min",
    start_time: str = None,
    end_time: str = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取历史分时数据
    
    Args:
        stock_code: 股票代码，仅支持单个字符串
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


def get_market_technical_indicator(
    market: str,
    indicator: str,
    stock_code: Union[str, List[str]],
    level: str = "daily",
    start_time: str = None,
    end_time: str = None,
    adjust: str = "none",
    vol_type: str = "share",
    page: int = 0,
    page_size: int = 10000,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    kdj_period: int = 9,
    k_period: int = 3,
    d_period: int = 3,
    rsi_period: int = 6,
    boll_period: int = 20,
    boll_std: float = 2.0,
    ma_periods: Optional[Union[str, List[int]]] = None,
    mavol_periods: Optional[Union[str, List[int]]] = None,
) -> Dict[str, Any]:
    """获取股票、ETF、可转债或指数的技术指标；指数不支持MAVOL。"""
    market = market.lower()
    indicator = indicator.lower()
    if market not in {"stock", "etf", "bond", "index"}:
        raise ValueError("market must be one of: stock, etf, bond, index")
    if indicator not in {"macd", "mavol", "kdj", "rsi", "boll", "ma"}:
        raise ValueError("indicator must be one of: macd, mavol, kdj, rsi, boll, ma")
    if market == "index" and indicator == "mavol":
        raise ValueError("index technical indicators do not support mavol")
    if not stock_code:
        raise ValueError("stock_code is required")
    if market != "stock" and adjust != "none":
        raise ValueError("ETF, bond and index technical indicators currently support adjust='none' only")
    if not start_time or not end_time:
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

    payload: Dict[str, Any] = {
        "index_code" if market == "index" else "stock_code": stock_code,
        "level": level,
        "start_time": start_time,
        "end_time": end_time,
        "adjust": adjust,
        "volType": vol_type,
        "page": page,
        "page_size": page_size,
    }
    if indicator == "macd":
        payload.update({
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period,
        })
    elif indicator == "mavol" and mavol_periods is not None:
        payload["mavol_periods"] = mavol_periods
    elif indicator == "kdj":
        payload.update({
            "kdj_period": kdj_period,
            "k_period": k_period,
            "d_period": d_period,
        })
    elif indicator == "rsi":
        payload["rsi_period"] = rsi_period
    elif indicator == "boll":
        payload.update({
            "boll_period": boll_period,
            "boll_std": boll_std,
        })
    elif indicator == "ma" and ma_periods is not None:
        payload["ma_periods"] = ma_periods

    return _make_request("POST", f"/{market}/{indicator}", json_data=payload)


def get_stock_indicator(indicator: str, **kwargs) -> Dict[str, Any]:
    return get_market_technical_indicator("stock", indicator, **kwargs)


def get_etf_indicator(indicator: str, **kwargs) -> Dict[str, Any]:
    return get_market_technical_indicator("etf", indicator, **kwargs)


def get_bond_technical_indicator(indicator: str, **kwargs) -> Dict[str, Any]:
    return get_market_technical_indicator("bond", indicator, **kwargs)


def get_index_indicator(indicator: str, index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_market_technical_indicator("index", indicator, stock_code=index_code, **kwargs)


def get_stock_macd(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("macd", **kwargs)


def get_stock_mavol(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("mavol", **kwargs)


def get_stock_kdj(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("kdj", **kwargs)


def get_stock_rsi(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("rsi", **kwargs)


def get_stock_boll(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("boll", **kwargs)


def get_stock_ma(**kwargs) -> Dict[str, Any]:
    return get_stock_indicator("ma", **kwargs)


def get_market_realtime_indicator(
    market: str,
    indicator: str,
    stock_code: Union[str, List[str]],
    level: str = "1min",
    start_time: str = None,
    end_time: str = None,
    adjust: Optional[str] = None,
    vol_type: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    fast_period: Optional[int] = None,
    slow_period: Optional[int] = None,
    signal_period: Optional[int] = None,
    kdj_period: Optional[int] = None,
    k_period: Optional[int] = None,
    d_period: Optional[int] = None,
    rsi_period: Optional[int] = None,
    boll_period: Optional[int] = None,
    boll_std: Optional[float] = None,
    ma_periods: Optional[Union[str, List[int]]] = None,
    mavol_periods: Optional[Union[str, List[int]]] = None,
) -> Dict[str, Any]:
    """Get one Redis-cached realtime 1-minute indicator for stock, bond, or index."""
    market = market.lower()
    indicator = indicator.lower()
    if market not in {"stock", "bond", "index"}:
        raise ValueError("market must be one of: stock, bond, index")
    if indicator not in {"macd", "mavol", "kdj", "rsi", "boll", "ma"}:
        raise ValueError("indicator must be one of: macd, mavol, kdj, rsi, boll, ma")
    if market == "index" and indicator == "mavol":
        raise ValueError("index realtime indicators do not support mavol")
    codes = [stock_code] if isinstance(stock_code, str) else list(stock_code)
    if not codes or len(set(codes)) > 100:
        raise ValueError("stock_code must contain between 1 and 100 unique codes")

    if level != "1min":
        raise ValueError("realtime indicators always use 1min; omit level")
    payload: Dict[str, Any] = {
        "index_code" if market == "index" else "stock_code": codes if len(codes) > 1 else codes[0],
    }
    if start_time is not None:
        payload["start_time"] = start_time
    if end_time is not None:
        payload["end_time"] = end_time
    if adjust is not None:
        payload["adjust"] = adjust
    if vol_type is not None:
        payload["volType"] = vol_type
    if page is not None:
        payload["page"] = page
    if page_size is not None:
        payload["page_size"] = page_size
    if indicator == "macd":
        if fast_period is not None:
            payload["fast_period"] = fast_period
        if slow_period is not None:
            payload["slow_period"] = slow_period
        if signal_period is not None:
            payload["signal_period"] = signal_period
    elif indicator == "mavol" and mavol_periods is not None:
        payload["mavol_periods"] = mavol_periods
    elif indicator == "kdj":
        if kdj_period is not None:
            payload["kdj_period"] = kdj_period
        if k_period is not None:
            payload["k_period"] = k_period
        if d_period is not None:
            payload["d_period"] = d_period
    elif indicator == "rsi":
        if rsi_period is not None:
            payload["rsi_period"] = rsi_period
    elif indicator == "boll":
        if boll_period is not None:
            payload["boll_period"] = boll_period
        if boll_std is not None:
            payload["boll_std"] = boll_std
    elif indicator == "ma" and ma_periods is not None:
        payload["ma_periods"] = ma_periods
    return _make_request("POST", f"/{market}/realtime/{indicator}", json_data=payload)


def get_stock_realtime_indicator(indicator: str, **kwargs) -> Dict[str, Any]:
    return get_market_realtime_indicator("stock", indicator, **kwargs)


def get_bond_realtime_indicator(indicator: str, **kwargs) -> Dict[str, Any]:
    return get_market_realtime_indicator("bond", indicator, **kwargs)


def get_index_realtime_indicator(indicator: str, index_code, **kwargs) -> Dict[str, Any]:
    return get_market_realtime_indicator(
        "index", indicator, stock_code=index_code, **kwargs
    )


def get_stock_realtime_macd(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("macd", **kwargs)


def get_stock_realtime_mavol(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("mavol", **kwargs)


def get_stock_realtime_kdj(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("kdj", **kwargs)


def get_stock_realtime_rsi(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("rsi", **kwargs)


def get_stock_realtime_boll(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("boll", **kwargs)


def get_stock_realtime_ma(**kwargs) -> Dict[str, Any]:
    return get_stock_realtime_indicator("ma", **kwargs)


def get_bond_realtime_macd(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("macd", **kwargs)


def get_bond_realtime_mavol(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("mavol", **kwargs)


def get_bond_realtime_kdj(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("kdj", **kwargs)


def get_bond_realtime_rsi(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("rsi", **kwargs)


def get_bond_realtime_boll(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("boll", **kwargs)


def get_bond_realtime_ma(**kwargs) -> Dict[str, Any]:
    return get_bond_realtime_indicator("ma", **kwargs)


def get_index_realtime_macd(index_code, **kwargs) -> Dict[str, Any]:
    return get_index_realtime_indicator("macd", index_code, **kwargs)


def get_index_realtime_kdj(index_code, **kwargs) -> Dict[str, Any]:
    return get_index_realtime_indicator("kdj", index_code, **kwargs)


def get_index_realtime_rsi(index_code, **kwargs) -> Dict[str, Any]:
    return get_index_realtime_indicator("rsi", index_code, **kwargs)


def get_index_realtime_boll(index_code, **kwargs) -> Dict[str, Any]:
    return get_index_realtime_indicator("boll", index_code, **kwargs)


def get_index_realtime_ma(index_code, **kwargs) -> Dict[str, Any]:
    return get_index_realtime_indicator("ma", index_code, **kwargs)


def get_etf_macd(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("macd", **kwargs)


def get_etf_mavol(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("mavol", **kwargs)


def get_etf_kdj(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("kdj", **kwargs)


def get_etf_rsi(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("rsi", **kwargs)


def get_etf_boll(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("boll", **kwargs)


def get_etf_ma(**kwargs) -> Dict[str, Any]:
    return get_etf_indicator("ma", **kwargs)


def get_bond_macd(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("macd", **kwargs)


def get_bond_mavol(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("mavol", **kwargs)


def get_bond_kdj(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("kdj", **kwargs)


def get_bond_rsi(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("rsi", **kwargs)


def get_bond_boll(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("boll", **kwargs)


def get_bond_ma(**kwargs) -> Dict[str, Any]:
    return get_bond_technical_indicator("ma", **kwargs)


def get_index_macd(index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_index_indicator("macd", index_code, **kwargs)


def get_index_kdj(index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_index_indicator("kdj", index_code, **kwargs)


def get_index_rsi(index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_index_indicator("rsi", index_code, **kwargs)


def get_index_boll(index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_index_indicator("boll", index_code, **kwargs)


def get_index_ma(index_code: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    return get_index_indicator("ma", index_code, **kwargs)


def get_realtime_history(
    stock_code: Optional[str] = None,
    trade_time: Optional[str] = None,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取实时分时数据 (实时 1 分钟级别分时数据，支持最近7天内)。
    返回数据会根据 stock_code + trade_time 进行去重。注意：stock_code 或 trade_time 至少提供一个。
    
    调用建议（定时任务拉取全市场数据）：
    1. 建议使用时间 (trade_time) 来获取实时分时，一次可以获取某一分钟的全市场数据。
    2. 使用定时任务来获取数据，每分钟获取上一分钟的数据。
    3. 建议在每分钟的 2 到 5 秒后开始获取。
    4. 如果获取不到，建议暂停 1 秒后继续获取，最多重试不要超过 60 次，避免陷入死循环。
    5. 建议在每分钟 15 秒之后再调用接口更新一次数据，确保数据的准确性。

    Args:
        stock_code: 股票代码，如 600000.SH (必须提供 stock_code 或 trade_time 之一)
        trade_time: 交易时间，如 2026-03-15 09:31:00 (必须提供 stock_code 或 trade_time 之一)
        date: 日期，格式 YYYY-MM-DD，默认今天，支持查询最近7天内的数据
    """
    if not stock_code and not trade_time:
        raise ValueError("必须提供 stock_code 或 trade_time 之一")

    payload = {}
    if stock_code:
        payload["stock_code"] = stock_code
    if trade_time:
        payload["trade_time"] = trade_time
    if date:
        payload["date"] = date

    return _make_request("POST", "/realtime/history", json_data=payload)


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
        包含 total 和 list 的字典，包含 PE、PB、PS、市值、PE百分位等财务指标
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

def get_financial_indicator(
    stock_code: Optional[Union[str, List[str]]] = None,
    end_date: Optional[str] = None,
    ann_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not end_date and not ann_date:
        raise ValueError("必须提供 stock_code 或 end_date 或 ann_date 之一")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }

    if stock_code:
        payload["stock_code"] = stock_code
    if end_date:
        payload["end_date"] = end_date
    if ann_date:
        payload["ann_date"] = ann_date

    return _make_request("POST", "/stock/financial_indicator", json_data=payload)


def get_income_statement(
    stock_code: Optional[Union[str, List[str]]] = None,
    end_date: Optional[str] = None,
    ann_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not end_date and not ann_date:
        raise ValueError("必须提供 stock_code 或 end_date 或 ann_date 之一")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if end_date:
        payload["end_date"] = end_date
    if ann_date:
        payload["ann_date"] = ann_date

    return _make_request("POST", "/stock/income", json_data=payload)


def get_balancesheet(
    stock_code: Optional[Union[str, List[str]]] = None,
    end_date: Optional[str] = None,
    ann_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not end_date and not ann_date:
        raise ValueError("必须提供 stock_code 或 end_date 或 ann_date 之一")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if end_date:
        payload["end_date"] = end_date
    if ann_date:
        payload["ann_date"] = ann_date

    return _make_request("POST", "/stock/balancesheet", json_data=payload)


def get_cashflow_statement(
    stock_code: Optional[Union[str, List[str]]] = None,
    end_date: Optional[str] = None,
    ann_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not end_date and not ann_date:
        raise ValueError("必须提供 stock_code 或 end_date 或 ann_date 之一")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if end_date:
        payload["end_date"] = end_date
    if ann_date:
        payload["ann_date"] = ann_date

    return _make_request("POST", "/stock/cashflow", json_data=payload)

def get_main_fund_flow(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/main_fund_flow", json_data=payload)

def get_main_fund_flow_overview(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/main_fund_flow_overview", json_data=payload)

def get_cyq_chips(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/cyq_chips", json_data=payload)


def get_report_rc(
    stock_code: Optional[str] = None,
    report_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取券商盈利预测数据。
    """
    if (start_date and not end_date) or (end_date and not start_date):
        raise ValueError("start_date 和 end_date 需要同时传入")
    if not stock_code and not report_date and not (start_date and end_date):
        raise ValueError("stock_code、report_date、(start_date+end_date) 至少传一个条件")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if report_date:
        payload["report_date"] = report_date
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    return _make_request("POST", "/stock/report_rc", json_data=payload)


def get_holder_number(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取股东人数数据。
    """
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if isinstance(stock_code, list):
        raise ValueError("get_history_data 的 stock_code 仅支持单个字符串，不支持数组")

    if stock_code:
        payload["stock_code"] = stock_code
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time

    return _make_request("POST", "/stock/holder_number", json_data=payload)


def get_pledge_stat(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取股票质押统计数据。
    """
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time

    return _make_request("POST", "/stock/pledge_stat", json_data=payload)


def get_margin_detail(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取融资融券明细数据。
    """
    if not stock_code and not (start_time and end_time):
        raise ValueError("必须提供 stock_code 或 (start_time + end_time) 至少一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if start_time and end_time:
        payload["start_time"] = start_time
        payload["end_time"] = end_time

    return _make_request("POST", "/stock/margin_detail", json_data=payload)

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


# ==================== 复权与复权因子相关 ====================

def get_daily_adj_data(
    stock_code: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    algo: str = "recursive",
    vol_type: str = "share",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取复权日K线数据（前复权）。

    注意：后端要求必须至少提供 `stock_code` 或 (`start_time` 与 `end_time`) 之一。
    """
    payload: Dict[str, Any] = {
        "algo": algo,
        "volType": vol_type,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    return _make_request("POST", "/stock/daily_adj", json_data=payload)


def get_adj_factor(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取自定义复权因子（递归算法因子），用于本地自行复权处理。

    Args:
        stock_code: 单个股票代码或股票代码列表
        start_time: 开始日期 YYYY-MM-DD（必填）
        end_time: 结束日期 YYYY-MM-DD（必填）
        page: 页码
        page_size: 每页数量，最大 10000
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/adj_factor", json_data=payload)


# ==================== 条件搜索相关 ====================

def search_stock_by_condition(
    query: str,
    stock_code: Optional[str] = None,
    date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> Dict[str, Any]:
    """
    按条件搜索股票（支持中文/英文条件，如“pe_ttm < 20 且 turnover_rate > 3%”）。

    Args:
        query: 条件表达式，支持中文描述与 AND/OR 组合
        stock_code: 可选，限制在某一只股票内筛选
        date: 可选，YYYY-MM-DD 或 MM-DD；为空时为最新快照
        page: 页码，从 0 开始
        page_size: 每页数量，默认 10，最大 1000
        sort_by: 排序字段
        sort_order: 排序方向 asc/desc
    """
    payload: Dict[str, Any] = {
        "query": query,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if date:
        payload["date"] = date
    if sort_by:
        payload["sort_by"] = sort_by
    if sort_order:
        payload["sort_order"] = sort_order

    return _make_request("POST", "/stock/search", json_data=payload)


def get_stock_search_fields() -> Dict[str, Any]:
    """
    获取条件搜索支持的字段列表和示例。
    """
    return _make_request("GET", "/stock/search/fields")


# ==================== 基础快照与停牌信息 ====================




def get_stock_suspension(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取股票停牌信息。
    """
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        params["stock_code"] = stock_code
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    return _make_request("GET", "/stock/suspension", params=params)


def upload_stock_suspension_token(
    data: List[Dict[str, Any]],
    admin_token: str
) -> Dict[str, Any]:
    """
    通过Token验证方式批量上传股票停牌数据，仅供后端或数据脚本使用。
    """
    payload: Dict[str, Any] = {
        "data": data
    }
    headers = {
        "X-Admin-Token": admin_token,
        "Content-Type": "application/json"
    }
    return _make_request("POST", "/data/suspension/import_token", json_data=payload, headers=headers)


def get_st_info(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000
) -> Dict[str, Any]:
    """
    获取ST信息
    
    Args:
        stock_code: 股票代码，支持单个字符串或列表
        start_time: 开始日期，格式 YYYY-MM-DD
        end_time: 结束日期，格式 YYYY-MM-DD
        page: 页码，从0开始
        page_size: 每页数量
    
    Returns:
        包含 total 和 list 的字典
    """
    payload = {
        "page": page,
        "page_size": page_size
    }
    
    if stock_code:
        payload["stock_code"] = stock_code
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time
        
    return _make_request("POST", "/stock/st_info", json_data=payload)

def get_stock_limit_list(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取股票涨跌停数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 和 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/limit_list", json_data=payload)


# ==================== 股票快照历史 ====================

def get_stock_snapshot_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取股票日度快照数据（实时/历史）。
    
    这是获取实时行情快照的主要接口。
    - 如果提供 `date` 为今日日期，则返回实时快照数据（优先读取 Redis 缓存）。
    - 如果提供 `date` 为历史日期，则返回历史快照数据。
    - 如果不提供 `date`，则返回指定股票的历史快照列表。

    Args:
        stock_code: 股票代码（可选，单个或列表）
        date: 交易日期 YYYY-MM-DD（可选，为空时返回历史列表）
        page: 页码
        page_size: 每页数量，最大 10000
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if date:
        payload["date"] = date

    return _make_request("POST", "/stock/snapshot_daily", json_data=payload)


def get_auction_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 60000,
) -> Dict[str, Any]:
    """
    获取当天竞价时间 (09:15-09:25) 的快照数据，包括开盘价、成交量等竞价信息。支持按时间区间查询历史快照序列。
    
    Args:
        stock_code: 股票代码（可选，单个或列表）
        date: 交易日期 YYYY-MM-DD（可选，为空时默认今天。如果不传 start_time/end_time，则返回该日期内每只股票最新的一条快照。）
        start_time: 开始时间 YYYY-MM-DD HH:MM:SS（可选，如果传了该参数，则查询指定时间区间的历史序列数据）
        end_time: 结束时间 YYYY-MM-DD HH:MM:SS（可选）
        page: 页码
        page_size: 每页数量，最大 60000
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if date:
        payload["date"] = date
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    return _make_request("POST", "/realtime/auction_daily", json_data=payload)


def get_limit_up_current(
    date: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    获取涨停股票快照数据。

    Args:
        date: 日期，格式 YYYY-MM-DD，默认今天
        stock_code: 股票代码（可选，单个或列表）。传入后返回该股票（或多只股票）当天全部数据。
        page: 页码，从0开始（可选，不传默认0）
        page_size: 每页数量（可选，不传默认10000，最大10000）

    Returns:
        包含涨停快照数据的字典
    """
    payload: Dict[str, Any] = {}
    if date:
        payload["date"] = date
    if stock_code:
        payload["stock_code"] = stock_code
    if page is not None:
        payload["page"] = page
    if page_size is not None:
        payload["page_size"] = page_size

    return _make_request("POST", "/realtime/limit_up", json_data=payload)


def get_stock_snapshot_push_history(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取推送通道中的快照历史记录（返回快照数组）。

    Args:
        stock_code: 股票代码（可选，单个或列表）
        start_time: 开始时间 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间 YYYY-MM-DD HH:MM:SS（可选）
        page: 页码
        page_size: 每页数量
    """
    if not start_time:
        raise ValueError("start_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if end_time:
        payload["end_time"] = end_time

    return _make_request("POST", "/stock/snapshot_push_history", json_data=payload)


# ==================== 可转债相关 ====================

def get_bond_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取可转债日线数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/bond/daily", json_data=payload)


def get_bond_history(
    stock_code: Optional[Union[str, List[str]]] = None,
    level: str = "5min",
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取可转债分钟级历史数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "level": level,
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/bond/history", json_data=payload)


def get_bond_indicator_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取可转债日度指标数据（纯债价值、转股溢价等）。

    注意：至少需要提供 `stock_code` 或 `start_date` / `end_date` 之一。
    """
    if not stock_code and not start_date and not end_date:
        raise ValueError("stock_code 与 start_date/end_date 至少需要提供一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    return _make_request("POST", "/bond/indicator_daily", json_data=payload)


def get_bond_closing_snapshot(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取可转债收盘快照数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/bond/closing_snapshot", json_data=payload)


def get_bond_list(
    bond_code: Optional[Union[str, List[str]]] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    exchange: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取可转债基础信息列表。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if bond_code:
        payload["bond_code"] = bond_code
    if stock_code:
        payload["stock_code"] = stock_code
    if exchange:
        payload["exchange"] = exchange

    return _make_request("POST", "/bond/list", json_data=payload)


# ==================== ETF 相关 ====================

def get_etf_list() -> Dict[str, Any]:
    """
    获取全市场ETF的基础信息列表
    """
    return _make_request("POST", "/etf/list", json_data={})


def get_etf_holdings(
    stock_code: str,
    mode: str = "latest",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取指定 ETF 的定期报告成分股。

    mode="latest" 返回最新报告期；mode="range" 按 report_date 查询闭区间。
    返回单位：holding_ratio_percent 为百分比，shares_10k 为万股，
    market_value_10k 为万元人民币。
    """
    if mode not in {"latest", "range"}:
        raise ValueError("mode must be 'latest' or 'range'")
    payload: Dict[str, Any] = {"stock_code": stock_code, "mode": mode}
    if mode == "range":
        if not start_date or not end_date:
            raise ValueError("range mode requires start_date and end_date")
        payload["start_date"] = start_date
        payload["end_date"] = end_date
    return _make_request("POST", "/etf/holdings", json_data=payload)


def get_etf_realtime_history(
    stock_code: Optional[str] = None,
    trade_time: Optional[str] = None,
    date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取ETF实时 1 分钟级别分时数据（支持查询最近7天内的数据）。返回数据会根据 stock_code + trade_time 进行去重。注意：stock_code 或 trade_time 至少提供一个。
    """
    if not stock_code and not trade_time:
        return {"code": 400, "msg": "必须提供 stock_code 或 trade_time 其中之一", "data": None}
        
    payload = {}
    if stock_code is not None:
        payload["stock_code"] = stock_code
    if trade_time is not None:
        payload["trade_time"] = trade_time
    if date is not None:
        payload["date"] = date

    return _make_request("POST", "/etf/realtime/history", json_data=payload)

def get_etf_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取 ETF 日线数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/etf/daily", json_data=payload)


def get_etf_history(
    stock_code: Optional[Union[str, List[str]]] = None,
    level: str = "5min",
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取 ETF 分钟级历史数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "level": level,
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/etf/history", json_data=payload)


# ==================== 指数相关 ====================

def get_index_history(
    index_code: Optional[Union[str, List[str]]] = None,
    level: str = "1min",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取指数分钟级历史数据。

    注意：后端要求 `index_code` 与 `start_time/end_time` 至少提供一类。
    """
    payload: Dict[str, Any] = {
        "level": level,
        "page": page,
        "page_size": page_size,
    }
    if index_code:
        payload["index_code"] = index_code
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    return _make_request("POST", "/index/history", json_data=payload)

def get_index_realtime_history(
    index_code: Optional[Union[str, List[str]]] = None,
    trade_time: Optional[str] = None,
    date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取指数实时 1 分钟级别分时数据（支持查询最近7天内的数据）
    注意: index_code 或 trade_time 至少提供一个
    """
    if not index_code and not trade_time:
        raise ValueError("index_code 和 trade_time 必须至少提供一个")
    
    payload = {}
    if index_code is not None:
        payload["index_code"] = index_code
    if trade_time is not None:
        payload["trade_time"] = trade_time
    if date is not None:
        payload["date"] = date
        
    return _make_request("POST", "/index/realtime/history", json_data=payload)

def get_index_yellow_line(
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取大盘黄白线分钟数据
    
    Args:
        date: 日期，格式 YYYY-MM-DD，默认今天
        
    Returns:
        包含大盘黄白线数据的字典
    """
    payload: Dict[str, Any] = {}
    if date:
        payload["date"] = date

    return _make_request("POST", "/index/yellow_line", json_data=payload)

def get_market_distribution(
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取全市场涨跌分布分钟数据
    
    Args:
        date: 日期，格式 YYYY-MM-DD，默认今天
        
    Returns:
        包含全市场涨跌分布数据的字典
    """
    payload: Dict[str, Any] = {}
    if date:
        payload["date"] = date

    return _make_request("POST", "/realtime/market_distribution", json_data=payload)

def get_ths_sector_categories(
    type: Optional[str] = None,
    page: int = 0,
    page_size: int = 1000,
) -> Dict[str, Any]:
    """
    获取同花顺板块分类数据。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if type:
        payload["type"] = type

    return _make_request("POST", "/index/ths_sector_categories", json_data=payload)

def get_ths_constituent_stocks(
    index_code: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: int = 0,
    page_size: int = 1000,
) -> Dict[str, Any]:
    """
    获取同花顺成分股数据。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if index_code:
        payload["index_code"] = index_code
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/index/ths_constituent_stocks", json_data=payload)


def get_ths_daily(
    ths_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取同花顺指数日线数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if ths_code:
        payload["ths_code"] = ths_code

    return _make_request("POST", "/index/ths_daily", json_data=payload)


def get_index_daily(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取指数每日行情。
    
    :param stock_code: 指数代码，如 "000001.SH"
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param page: 页码
    :param page_size: 每页数量
    """
    payload = {
        "page": page,
        "page_size": page_size
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    return _make_request("POST", "/index/daily", json_data=payload)

def get_index_weight(
    index_code: str,
    stock_code: Optional[Union[str, List[str]]] = None,
    trade_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取指数月度成分和权重数据。

    Args:
        index_code: 指数代码（必填），例如 000300.SH
        stock_code: 成分股代码（可选），支持字符串或数组
        trade_date: 交易日期（可选），支持 YYYY-MM 或 YYYY-MM-DD；查询时仅按年和月过滤，不传默认返回最新月份数据
        page: 页码，从0开始
        page_size: 每页数量，默认2000，最大10000
    """
    if not index_code:
        raise ValueError("index_code 为必填参数")

    payload: Dict[str, Any] = {
        "index_code": index_code,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code
    if trade_date:
        payload["trade_date"] = trade_date

    return _make_request("POST", "/index/weight", json_data=payload)


def get_dc_blocks(
    block_code: Optional[Union[str, List[str]]] = None,
    block_type: Optional[str] = None,
    block_name: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取东方财富板块列表。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if block_code:
        payload["block_code"] = block_code
    if block_type:
        payload["block_type"] = block_type
    if block_name:
        payload["block_name"] = block_name

    return _make_request("POST", "/dc/blocks", json_data=payload)


def get_dc_daily(
    block_code: Optional[Union[str, List[str]]] = None,
    trade_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取东方财富板块日K。block_code 与 trade_date 至少传一个。
    """
    if not block_code and not trade_date:
        raise ValueError("block_code 与 trade_date 至少需要传一个")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if block_code:
        payload["block_code"] = block_code
    if trade_date:
        payload["trade_date"] = trade_date

    return _make_request("POST", "/dc/daily", json_data=payload)


def get_dc_block_stocks(
    block_code: Optional[Union[str, List[str]]] = None,
    trade_date: Optional[str] = None,
    stock_code: Optional[Union[str, List[str]]] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取东方财富板块成分股。三个筛选条件均可选；全不传时默认返回最新交易日数据。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if block_code:
        payload["block_code"] = block_code
    if trade_date:
        payload["trade_date"] = trade_date
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/dc/block_stocks", json_data=payload)


def get_ths_hot(
    market: str = "热股",
    trade_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取同花顺热度榜
    
    :param market: 热榜类型 (默认：热股)。可选值：热股, ETF, 可转债, 行业板块, 概念板块, 期货
    :param trade_date: 指定交易日期，支持 YYYY-MM-DD 或 YYYYMMDD；不传默认最新交易日
    :return: 包含热榜数据的字典，包含 list、trade_date、update_time 等；list 内含 rank 字段
    """
    params: Dict[str, Any] = {"market": market}
    if trade_date:
        params["trade_date"] = trade_date
    return _make_request("GET", "/api/ths/hot", params=params)


# ==================== 港股相关 ====================

def get_hk_stock_list() -> List[Dict[str, Any]]:
    """
    获取港股基础信息列表。
    """
    return _make_request("GET", "/stock/hk/list")


def get_hk_finance_data(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取港股财务报表及财务指标数据。
    """
    if not start_date or not end_date:
        raise ValueError("start_date 与 end_date 为必填参数")

    payload: Dict[str, Any] = {
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/hk/finance", json_data=payload)


def get_hk_stock_valuation() -> Dict[str, Any]:
    """
    获取港股综合估值信息（含行业分布与 10 年成长指标）。
    """
    return _make_request("GET", "/stock/hk/valuation")


def get_hk_closing_snapshot(
    stock_code: Optional[Union[str, List[str]]] = None,
    start_time: str = "",
    end_time: str = "",
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取港股收盘快照数据。
    """
    if not start_time or not end_time:
        raise ValueError("start_time 与 end_time 为必填参数")

    payload: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "page": page,
        "page_size": page_size,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/hk/closing_snapshot", json_data=payload)


def get_hk_connect(
    type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    获取最新一日港股互联互通成分（沪深港通标的）。

    Args:
        type: 可选，HK_SZ / SZ_HK / HK_SH / SH_HK
    """
    params: Dict[str, Any] = {}
    if type:
        params["type"] = type

    return _make_request("GET", "/stock/hk/connect", params=params)

# ==================== 龙虎榜数据 ====================

def get_dragon_tiger(
    date: Optional[str] = None,
    stock_code: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    获取龙虎榜机构明细数据。
    date 和 stock_code 必须至少提供一个。
    """
    if not date and not stock_code:
        # 如果都没有提供，默认查询当天
        date = datetime.now().strftime("%Y-%m-%d")

    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if date:
        payload["date"] = date
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/dragon_tiger", json_data=payload)

def get_top_list(
    trade_date: str,
    stock_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取龙虎榜每日明细数据。
    """
    payload: Dict[str, Any] = {
        "trade_date": trade_date,
    }
    if stock_code:
        payload["stock_code"] = stock_code

    return _make_request("POST", "/stock/top_list", json_data=payload)


def get_tdx_daily(
    board_code: Optional[str] = None,
    trade_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    获取通达信板块日K线数据。
    支持按特定板块（查询历史）或特定日期（查询所有板块）进行筛选。如果 start_date 和 end_date 相同，将忽略分页返回当天所有板块数据。

    Args:
        board_code: 板块代码（可选，如 880471 或 880471.TDX）
        trade_date: 交易日期 YYYY-MM-DD（可选）
        start_date: 开始日期 YYYY-MM-DD（可选）
        end_date: 结束日期 YYYY-MM-DD（可选）
        page: 页码，从 0 开始
        page_size: 每页数量
    """
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if board_code:
        params["board_code"] = board_code
    if trade_date:
        params["trade_date"] = trade_date
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    return _make_request("GET", "/tdx/daily", params=params)


# ==================== 同花顺 数据相关 ====================

def get_tdx_blocks(
    block_type: int,
    block_name: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取通达信板块列表数据。block_type 为必填参数。

    Args:
        block_type: 板块类型（0:行业板块, 1:风格板块, 2:概念板块, 3:指数板块）
        block_name: 板块名称（可选，用于筛选，如 5G概念）
        page: 页码，从 0 开始
        page_size: 每页数量，默认 10000
    """
    params: Dict[str, Any] = {
        "block_type": block_type,
        "page": page,
        "page_size": page_size,
    }
    if block_name:
        params["block_name"] = block_name

    return _make_request("GET", "/tdx/blocks", params=params)


def get_tdx_block_stocks(
    block_code: Optional[str] = None,
    stock_code: Optional[str] = None,
    page: int = 0,
    page_size: int = 10000,
) -> Dict[str, Any]:
    """
    获取通达信板块成分股数据。支持按板块代码或股票代码筛选。
    返回分页结构 data.total / data.page / data.page_size / data.list，
    其中 data.list 的每项包含 block_code、block_name、block_type、stock_code。

    Args:
        block_code: 板块代码（可选，如 880506.TDX）
        stock_code: 股票代码（可选，如 000063.SZ）
        page: 页码，从 0 开始
        page_size: 每页数量，默认 10000
    """
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if block_code:
        params["block_code"] = block_code
    if stock_code:
        params["stock_code"] = stock_code

    return _make_request("GET", "/tdx/block_stocks", params=params)


def get_future_basic(
    contract_code: Optional[Union[str, List[str]]] = None,
    exchange: Optional[str] = None,
    fut_code: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取期货合约的基础信息数据，包括乘数、交割方式、上市日期等。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if contract_code:
        payload["contract_code"] = contract_code
    if exchange:
        payload["exchange"] = exchange
    if fut_code:
        payload["fut_code"] = fut_code

    return _make_request("POST", "/future/basic", json_data=payload)

def get_future_mapping(
    mapping_code: Optional[Union[str, List[str]]] = None,
    contract_code: Optional[Union[str, List[str]]] = None,
    trade_date: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取期货主连或连续合约与实际月合约的映射关系。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if mapping_code:
        payload["mapping_code"] = mapping_code
    if contract_code:
        payload["contract_code"] = contract_code
    if trade_date:
        payload["trade_date"] = trade_date

    return _make_request("POST", "/future/mapping", json_data=payload)

def get_future_minute(
    contract_code: Optional[Union[str, List[str]]] = None,
    freq: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 0,
    page_size: int = 2000,
) -> Dict[str, Any]:
    """
    获取期货合约的历史分钟K线数据。
    """
    payload: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
    }
    if contract_code:
        payload["contract_code"] = contract_code
    if freq:
        payload["freq"] = freq
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    return _make_request("POST", "/future/minute", json_data=payload)
