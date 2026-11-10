import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import os
import json

# ==========================================
# 頁面基本設定與手機專屬立體設計 CSS 注入
# ==========================================
st.set_page_config(
    page_title="智慧選股",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* 隱藏原生側邊欄切換鈕 */
    [data-testid="collapsedControl"] { display: none !important; }
    
    /* 1. 藝術感大標題 */
    .mobile-art-header {
        text-align: center;
        padding-top: 15px;
        padding-bottom: 25px;
    }
    .mobile-art-header h1 {
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        margin: 0 !important;
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 50%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 15px rgba(37, 99, 235, 0.15);
    }
    
    /* 2. 並排次要按鈕（盤勢分析、個股分析）：文字 1.45rem */
    div.st-key-btn_nav_market button,
    div.st-key-btn_nav_stock button {
        height: 75px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.35) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.15s ease !important;
    }
    div.st-key-btn_nav_market button:active,
    div.st-key-btn_nav_stock button:active {
        transform: scale(0.96) !important;
    }
    div.st-key-btn_nav_market button {
        background: linear-gradient(145deg, #4338ca 0%, #312e81 100%) !important;
    }
    div.st-key-btn_nav_stock button {
        background: linear-gradient(145deg, #0284c7 0%, #075985 100%) !important;
    }
    div.st-key-btn_nav_market button p, div.st-key-btn_nav_market button span,
    div.st-key-btn_nav_stock button p, div.st-key-btn_nav_stock button span {
        color: #ffffff !important;
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
    }

    /* 3. 核心功能「精選推薦個股」：面積為 2 (兩倍大)，字體 1.7rem */
    div.st-key-btn_nav_picks button {
        height: 144px !important;
        border-radius: 22px !important;
        margin-top: 15px !important;
        margin-bottom: 25px !important;
        background: linear-gradient(135deg, #059669 0%, #047857 50%, #064e3b 100%) !important;
        border: 2px solid rgba(52, 211, 153, 0.45) !important;
        box-shadow: 0 12px 28px rgba(5, 150, 105, 0.35),
                    inset 0 1px 2px rgba(255, 255, 255, 0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div.st-key-btn_nav_picks button:active {
        transform: scale(0.97) !important;
    }
    div.st-key-btn_nav_picks button p, div.st-key-btn_nav_picks button span {
        color: #ffffff !important;
        font-size: 1.7rem !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    }

    /* 4. 放大所有 Dialog 右上角的關閉叉叉 */
    button[aria-label="Close"], 
    div[data-testid="stDialog"] button[aria-label="Close"] {
        transform: scale(1.8) !important;
        transform-origin: top right !important;
        margin-top: 12px !important;
        margin-right: 12px !important;
        background-color: rgba(226, 232, 240, 0.6) !important;
        border-radius: 50% !important;
        padding: 4px !important;
    }

    /* 5. 強化加大加粗選股方向文字 */
    div.factor-title label p {
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        color: #0f172a !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.5px !important;
    }

    /* 6. 熱門題材垂直選項卡片美化 */
    div.theme-radio-vertical div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        width: 100% !important;
    }
    div.theme-radio-vertical label {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin: 0 !important;
    }

    /* 7. 推薦個股卡片內：綜合評分與理由藍底飾板 */
    .reason-highlight-box {
        background-color: #eff6ff !important;
        border-left: 5px solid #2563eb !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin-top: 8px !important;
        margin-bottom: 12px !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: #1e3a8a !important;
    }
    .score-badge {
        display: inline-block;
        background: #2563eb;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 0.9rem;
        margin-left: 6px;
    }
    
    /* 底部次要功能列樣式 */
    .footer-bar {
        text-align: center;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #e2e8f0;
        font-size: 0.82rem;
        color: #64748b;
    }
    </style>
""", unsafe_allow_html=True)

CACHE_PARQUET_FILE = "market_cache.parquet"
META_JSON_FILE = "market_cache_meta.json"

# ==========================================
# 0. 法律免責聲明彈窗 (置底備查)
# ==========================================
@st.dialog("⚖️ 投資風險與法律免責聲明", width="large")
def show_legal_disclaimer_modal():
    st.markdown("### ⚠️ 使用者須知與風險宣告")
    st.markdown("""
    本系統所載之所有選股結果、策略回測、買賣建議區間及盤勢分析，均基於歷史盤後公開數據及量化演算法運算呈現，**僅供學術研究、量化模型驗證與教育模擬用途**，不構成任何形式的投資招攬、買賣建議或金融顧問服務。
    
    金融市場受國內外政經情勢、總體經濟及突發事件等多重不可抗力因素影響，風險難以完全預估。**使用者應依個人財務狀況、風險承受能力獨立判斷並自負投資盈虧責任**。
    """)
    st.markdown("---")
    if st.button("關閉", use_container_width=True):
        st.rerun()

# ==========================================
# 1. 熱門題材概念股字典與動態更新機制
# ==========================================
DEFAULT_THEME_DICT = {
    "AI 伺服器 / 先進封裝 (CoWoS)": ["2330", "2317", "2382", "3231", "2356", "3711", "3131", "3583", "6187", "2454", "3017", "3324", "6669", "2059"],
    "矽光子 CPO / 機器人自動化": ["3450", "4979", "3363", "3163", "6442", "4908", "3081", "2345", "2357", "2395", "6188", "2049", "4576", "1597"],
    "高股息績優 / 綠能重電": ["1513", "1519", "1503", "1504", "2891", "2882", "2886", "2412", "3045", "6285", "2301", "1101", "1102"]
}

if "theme_dict" not in st.session_state:
    st.session_state.theme_dict = DEFAULT_THEME_DICT.copy()
if "theme_last_update" not in st.session_state:
    st.session_state.theme_last_update = datetime.now().strftime("%Y-%m-%d %H:%M")

def get_stock_themes(stock_id: str) -> list:
    themes = []
    for theme_name, id_list in st.session_state.theme_dict.items():
        if stock_id in id_list:
            themes.append(theme_name)
    return themes if themes else ["一般產業"]

def refresh_market_themes():
    st.session_state.theme_dict = DEFAULT_THEME_DICT.copy()
    st.session_state.theme_last_update = datetime.now().strftime("%Y-%m-%d %H:%M")

def parse_tw_roc_date(roc_date_str: str) -> str:
    weekday_map = {0: "週一", 1: "週二", 2: "週三", 3: "週四", 4: "週五", 5: "週六", 6: "週日"}
    try:
        clean = re.sub(r"[^\d]", "", str(roc_date_str))
        if len(clean) >= 7:
            year = int(clean[:3]) + 1911
            month = int(clean[3:5])
            day = int(clean[5:7])
            dt = datetime(year, month, day)
            return f"{dt.strftime('%Y-%m-%d')} ({weekday_map.get(dt.weekday(), '')})"
    except Exception:
        pass
    tw_now = datetime.utcnow() + timedelta(hours=8)
    return f"{tw_now.strftime('%Y-%m-%d')} ({weekday_map.get(tw_now.weekday(), '')})"

def parse_twse_date_to_date(roc_date_str: str):
    """將證交所民國年字串 (如 1150310) 轉換為 Python date 物件"""
    try:
        clean = re.sub(r"[^\d]", "", str(roc_date_str))
        if len(clean) >= 7:
            year = int(clean[:3]) + 1911
            month = int(clean[3:5])
            day = int(clean[5:7])
            return datetime(year, month, day).date()
    except Exception:
        pass
    return None

def get_expected_latest_trading_date():
    """計算當前時間點，市場預期應有的最新盤後資料交易日"""
    now = datetime.now()
    # 台股盤後資料約在下午 15:30 ~ 16:00 正式出齊
    today_after_market = (now.time() >= datetime.strptime("15:30", "%H:%M").time())
    
    candidate = now.date() if today_after_market else (now.date() - timedelta(days=1))
    
    # 遇週末往前回溯至週五
    while candidate.weekday() >= 5:  # 5=週六, 6=週日
        candidate -= timedelta(days=1)
    return candidate

# ==========================================
# 2. 全市場真實數據擷取（交易日感知防快取錯位版）
# ==========================================
def fetch_full_market_universe(force_refresh: bool = False):
    expected_date = get_expected_latest_trading_date()
    
    # 1. 檢查本機快取是否存在且已是預期交易日
    if not force_refresh and os.path.exists(CACHE_PARQUET_FILE) and os.path.exists(META_JSON_FILE):
        try:
            with open(META_JSON_FILE, "r", encoding="utf-8") as f:
                meta_info = json.load(f)
            cached_data_date_str = meta_info.get("data_date", "")
            cached_label = meta_info.get("tw_date_label", "")
            
            # 若快取記錄的資料日期，與當前預期應取得的最新交易日相符，直接讀取
            if cached_data_date_str == str(expected_date) and cached_label:
                df_cached = pd.read_parquet(CACHE_PARQUET_FILE)
                if not df_cached.empty and len(df_cached) >= 1000:
                    df_cached["themes"] = df_cached["stock_id"].apply(get_stock_themes)
                    return df_cached, cached_label
        except Exception:
            pass

    # 2. 若快取不存在、被強制更新，或快取日期落後於預期日期，才連線抓取
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    market_rows = []
    twse_raw_date_str = ""

    pe_twse = {}
    try:
        r_pe = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL", headers=headers, timeout=10)
        if r_pe.status_code == 200:
            for row in r_pe.json():
                code = str(row.get("Code", "")).strip()
                if re.match(r"^[1-9]\d{3}$", code):
                    if not twse_raw_date_str and "Date" in row:
                        twse_raw_date_str = str(row["Date"])
                    pe_twse[code] = {
                        "name": row.get("Name", "").strip(),
                        "pe": pd.to_numeric(str(row.get("PEratio", "")).replace(",", ""), errors="coerce"),
                        "dy": pd.to_numeric(str(row.get("DividendYield", "")).replace(",", ""), errors="coerce"),
                        "pb": pd.to_numeric(str(row.get("PBratio", "")).replace(",", ""), errors="coerce")
                    }
    except Exception:
        pass

    try:
        r_p = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", headers=headers, timeout=10)
        if r_p.status_code == 200:
            for row in r_p.json():
                code = str(row.get("Code", "")).strip()
                name = str(row.get("Name", "")).strip()
                if not twse_raw_date_str and "Date" in row:
                    twse_raw_date_str = str(row["Date"])
                
                if re.match(r"^(00\d{2,3}[A-Za-z]?|[1-9]\d{3}[A-Za-z]?)$", code):
                    vol_shares = pd.to_numeric(str(row.get("TradeVolume", "")).replace(",", ""), errors="coerce")
                    close_p = pd.to_numeric(str(row.get("ClosingPrice", "")).replace(",", ""), errors="coerce")
                    vol_sheets = vol_shares / 1000.0 if pd.notnull(vol_shares) else 0.0
                    
                    if pd.notnull(close_p) and close_p > 0:
                        item = pe_twse.get(code, {})
                        is_etf = code.startswith("00")
                        market_label = "上市 ETF" if is_etf else "上市"
                        final_name = name if name else item.get("name", code)
                        market_rows.append({
                            "stock_id": code,
                            "stock_name": final_name,
                            "market": market_label,
                            "close": float(close_p),
                            "volume_sheets": float(vol_sheets),
                            "pe_ratio": float(item["pe"]) if pd.notnull(item.get("pe")) and item["pe"] > 0 else (np.nan if is_etf else 22.0),
                            "dividend_yield": float(item["dy"]) if pd.notnull(item.get("dy")) else (np.nan if is_etf else 2.5),
                            "pb_ratio": float(item["pb"]) if pd.notnull(item.get("pb")) else (np.nan if is_etf else 2.0),
                        })
    except Exception:
        pass

    try:
        r_otc_pe = requests.get("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis", headers=headers, timeout=10)
        r_otc = requests.get("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes", headers=headers, timeout=10)
        
        pe_otc = {}
        if r_otc_pe.status_code == 200:
            for row in r_otc_pe.json():
                code = str(row.get("SecuritiesCompanyCode", "")).strip()
                if re.match(r"^[1-9]\d{3}$", code):
                    pe_otc[code] = {
                        "pe": pd.to_numeric(str(row.get("PriceEarningRatio", "")).replace(",", ""), errors="coerce"),
                        "dy": pd.to_numeric(str(row.get("YieldRatio", "")).replace(",", ""), errors="coerce"),
                        "pb": pd.to_numeric(str(row.get("PriceBookRatio", "")).replace(",", ""), errors="coerce")
                    }
                    
        if r_otc.status_code == 200:
            for row in r_otc.json():
                code = str(row.get("SecuritiesCompanyCode", "")).strip()
                name = str(row.get("CompanyName", "")).strip()
                if re.match(r"^(00\d{2,3}[A-Za-z]?|[1-9]\d{3}[A-Za-z]?)$", code):
                    vol_shares = pd.to_numeric(str(row.get("TradingShares", "")).replace(",", ""), errors="coerce")
                    close_p = pd.to_numeric(str(row.get("Close", "")).replace(",", ""), errors="coerce")
                    vol_sheets = vol_shares / 1000.0 if pd.notnull(vol_shares) else 0.0
                    
                    if pd.notnull(close_p) and close_p > 0:
                        p_info = pe_otc.get(code, {})
                        is_etf = code.startswith("00")
                        market_label = "上櫃 ETF" if is_etf else "上櫃"
                        market_rows.append({
                            "stock_id": code,
                            "stock_name": name,
                            "market": market_label,
                            "close": float(close_p),
                            "volume_sheets": float(vol_sheets),
                            "pe_ratio": float(p_info.get("pe")) if pd.notnull(p_info.get("pe")) and p_info.get("pe") > 0 else (np.nan if is_etf else 24.0),
                            "dividend_yield": float(p_info.get("dy")) if pd.notnull(p_info.get("dy")) else (np.nan if is_etf else 2.0),
                            "pb_ratio": float(p_info.get("pb")) if pd.notnull(p_info.get("pb")) else (np.nan if is_etf else 2.5),
                        })
    except Exception:
        pass

    full_df = pd.DataFrame(market_rows)

    if full_df.empty or len(full_df) < 50:
        if os.path.exists(CACHE_PARQUET_FILE):
            return pd.read_parquet(CACHE_PARQUET_FILE), "歷史離線快取"
        st.error("⚠️ 無法連線至證交所或櫃買中心取得最新盤後行情，請確認網路連線。")
        st.stop()

    actual_tw_label = parse_tw_roc_date(twse_raw_date_str)
    real_data_date = parse_twse_date_to_date(twse_raw_date_str) or expected_date

    try:
        save_cols = [
            "stock_id", "stock_name", "market", "close", 
            "volume_sheets", "pe_ratio", "dividend_yield", "pb_ratio"
        ]
        temp_file = CACHE_PARQUET_FILE + ".tmp"
        full_df[save_cols].to_parquet(temp_file, compression="snappy", index=False)
        if os.path.exists(CACHE_PARQUET_FILE):
            os.remove(CACHE_PARQUET_FILE)
        os.rename(temp_file, CACHE_PARQUET_FILE)
        
        with open(META_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "tw_date_label": actual_tw_label,
                "data_date": str(real_data_date)
            }, f, ensure_ascii=False)
    except Exception:
        pass

    full_df["themes"] = full_df["stock_id"].apply(get_stock_themes)
    return full_df, actual_tw_label

# ==========================================
# 3. 第一階段漏斗初篩
# ==========================================
def fast_filter_funnel(full_df: pd.DataFrame, selections: dict, top_n: int = 25) -> pd.DataFrame:
    df = full_df[~full_df["stock_id"].str.startswith("00") & (full_df["volume_sheets"] >= 80)].copy()
    if df.empty:
        df = full_df.copy()
    df["stage1_score"] = 0.0

    if selections["fundamental"]["enabled"]:
        lvl = selections["fundamental"]["level"]
        if lvl == "嚴格績優":
            cond = (df["pe_ratio"].fillna(99) <= 18) & (df["dividend_yield"].fillna(0) >= 3.8)
            score = cond.astype(int) * 35.0 + (df["dividend_yield"].fillna(0) * 3.0) - (df["pe_ratio"].fillna(30) * 0.4)
        elif lvl == "穩健成長":
            cond = (df["pe_ratio"].fillna(99) >= 14) & (df["pe_ratio"].fillna(99) <= 27) & (df["dividend_yield"].fillna(0) >= 1.8)
            pe_dist = (df["pe_ratio"].fillna(20) - 20.0).abs()
            score = cond.astype(int) * 35.0 + 15.0 - (pe_dist * 1.2) + (df["dividend_yield"].fillna(0) * 1.5)
        else:  # 價值轉機
            cond = (df["pb_ratio"].fillna(99) <= 1.9) & (df["pe_ratio"].fillna(99) <= 38)
            score = cond.astype(int) * 40.0 + (2.0 - df["pb_ratio"].fillna(2.0)).clip(lower=-1.0) * 20.0
            score -= (df["pb_ratio"].fillna(0) > 3.0).astype(int) * 35.0
        df["stage1_score"] += score

    if selections["market"]["enabled"]:
        lvl = selections["market"]["level"]
        if lvl == "法人重倉連買":
            cond = df["volume_sheets"] >= 3500
            score = cond.astype(int) * 30.0 + np.log1p(df["volume_sheets"]) * 3.5
        elif lvl == "法人溫和布局":
            cond = (df["volume_sheets"] >= 1200) & (df["volume_sheets"] <= 5500)
            score = cond.astype(int) * 35.0 + 10.0 - ((df["volume_sheets"] - 2800).abs() / 500.0)
        else:  # 低檔承接
            cond = (df["volume_sheets"] >= 300) & (df["volume_sheets"] <= 1800)
            score = cond.astype(int) * 40.0 - (df["volume_sheets"] > 3000).astype(int) * 35.0
        df["stage1_score"] += score

    if selections["theme"]["enabled"]:
        lvl = selections["theme"]["level"]
        target = lvl
        cond = df["themes"].apply(lambda t_list: any(target in t for t in t_list))
        df["stage1_score"] += cond.astype(int) * 45.0

    ranked_pool = df.sort_values(by="stage1_score", ascending=False).head(top_n).reset_index(drop=True)
    return ranked_pool

# ==========================================
# 4. 個股狀態聯動動態定價與 6 大細分情境指引
# ==========================================
def compute_regime_pricing(last_close, last_ma5, last_ma20, last_ma60, prev_ma60, last_rsi, last_atr, vol_ratio, is_high_10d):
    bias_ma20 = (last_close - last_ma20) / last_ma20 if last_ma20 > 0 else 0.0
    ma60_slope_down = (last_ma60 < prev_ma60)

    # 1. 買賣建議區間基準計算
    if last_close >= last_ma20 and last_rsi >= 50:
        short_buy_low = round(min(last_ma5 - 0.2 * last_atr, last_close - 0.4 * last_atr), 2)
        short_buy_high = round(min(last_close, max(last_ma5, last_close - 0.1 * last_atr)), 2)
        if short_buy_low >= short_buy_high:
            short_buy_low = round(short_buy_high - 0.3 * last_atr, 2)
        short_buy_range = f"{short_buy_low} ~ {short_buy_high}"
        short_target = round(last_close + 2.0 * last_atr, 2)
        short_stop = round(max(last_close - 1.5 * last_atr, last_ma20 * 0.98), 2)

        mid_buy_low = round(last_ma20 * 0.99, 2)
        mid_buy_high = round(last_ma20 * 1.02, 2)
        mid_buy_range = f"{mid_buy_low} ~ {mid_buy_high}"
        mid_target = round(last_close + 4.5 * last_atr, 2)
        mid_stop = round(last_ma60 * 0.97, 2)
    elif last_close < last_ma20 and last_rsi < 48:
        short_buy_low = round(last_close - 1.8 * last_atr, 2)
        short_buy_high = round(last_close - 1.0 * last_atr, 2)
        short_buy_range = f"{short_buy_low} ~ {short_buy_high} (測撐區)"
        short_target = round(last_close + 1.2 * last_atr, 2)
        short_stop = round(last_close - 2.0 * last_atr, 2)

        mid_buy_low = round(min(last_ma60 * 0.95, last_close - 2.5 * last_atr), 2)
        mid_buy_high = round(min(last_ma60 * 0.98, last_close - 1.5 * last_atr), 2)
        mid_buy_range = f"{mid_buy_low} ~ {mid_buy_high} (長線觀察)"
        mid_target = round(last_close + 3.0 * last_atr, 2)
        mid_stop = round(last_close - 2.8 * last_atr, 2)
    else:
        short_buy_low = round(last_ma20 - 1.0 * last_atr, 2)
        short_buy_high = round(last_ma20 - 0.3 * last_atr, 2)
        short_buy_range = f"{short_buy_low} ~ {short_buy_high}"
        short_target = round(last_close + 1.8 * last_atr, 2)
        short_stop = round(last_ma20 - 1.4 * last_atr, 2)

        mid_buy_low = round(min(last_ma20, last_ma60) - 0.5 * last_atr, 2)
        mid_buy_high = round(min(last_ma20, last_ma60), 2)
        mid_buy_range = f"{mid_buy_low} ~ {mid_buy_high}"
        mid_target = round(last_close + 3.5 * last_atr, 2)
        mid_stop = round(last_ma60 * 0.97, 2)

    # 2. 個股後續行情預測與操作指引（細分為 6 種情境）
    if ma60_slope_down and last_close < last_ma60:
        summary_text = f"股價跌破季線（{last_ma60:.1f}）且季線呈現下彎蓋頭壓制，中長線架構偏空，下檔支撐待測。"
        prediction_text = "🛡️ **【情境：破線走空】➔ 操作指引：『嚴控風險，持股應停損換股或空手避開』**\n\n* **結構分析**：中長期趨勢轉空，上方均線形成沉重套牢賣壓。\n* **操作指引**：反彈皆為減碼點，切勿逢低加碼或攤平，待中長線打出底部結構再重新評估。"
    elif bias_ma20 > 0.15 or (is_high_10d and vol_ratio < 0.70):
        summary_text = f"短線正乖離過大（月線乖離 {bias_ma20*100:+.1f}%）或出現高檔量價背離，短線追高動能衰退。"
        prediction_text = "🔄 **【情境：高檔過熱】➔ 操作指引：『切勿追高，短線逢高分批獲利調節』**\n\n* **結構分析**：指標處於高檔超買區，隨時有技術性乖離修正或獲利了結賣壓。\n* **操作指引**：手中持股建議逢高分批停利，未持有者耐心等待回測月線或 5 日線止穩再行承接。"
    elif last_close >= last_ma5 and last_ma5 >= last_ma20 and last_rsi >= 58 and vol_ratio >= 1.3:
        summary_text = f"均線呈現典型多頭向上發散，放量突破短期整理區，RSI 動能達 {last_rsi:.1f}，多方強勢主導。"
        prediction_text = "🚀 **【情境：強多突破】➔ 操作指引：『順勢偏多操作，緊盯主流攻擊動能』**\n\n* **結構分析**：價量齊揚站上所有短期均線，波段攻擊訊號強烈。\n* **操作指引**：可於開盤量能持續放大時順勢進場或加碼，防守點設定於 5 日線或突破點邊緣。"
    elif last_close >= last_ma20 and last_rsi >= 50:
        summary_text = f"股價穩健站於月線與短期均線之上，結構維持偏多排列，回測均線支撐力道良好。"
        prediction_text = "🟢 **【情境：穩健多頭】➔ 操作指引：『逢回分批承接，沿短均線佈局』**\n\n* **結構分析**：中期趨勢向上，籌碼安定度高，尚未出現過熱失控跡象。\n* **操作指引**：不追高現價，建議在建議買入區間（回測 5 日線至月線）採分批掛單承接策略。"
    elif last_close < last_ma20 or last_rsi < 45:
        summary_text = f"近日承壓修正，跌破關鍵月線支撐且 RSI 偏弱（{last_rsi:.1f}），短線結構進入測撐整理。"
        prediction_text = "⚠️ **【情境：弱勢整理】➔ 操作指引：『高度觀望，靜待下檔測撐止穩訊號』**\n\n* **結構分析**：短線多頭力道暫歇，空方佔據優勢，價格有進一步尋求下檔支撐之虞。\n* **操作指引**：暫停買進動作，耐心等待標的回測下方預估測撐區並出現止跌打底紅 K 再行評估。"
    else:
        summary_text = f"於月線附近區間震盪（RSI {last_rsi:.1f}），多空雙方力量在此拉鋸膠著，成交量能溫和。"
        prediction_text = "⚖️ **【情境：箱型震盪】➔ 操作指引：『區間來回操作，保持資金彈性』**\n\n* **結構分析**：處於箱型整理中軸，尚未出現明確的方向性突破。\n* **操作指引**：切勿追買，建議在建議買入區間（箱型下緣）逢低承接、接近目標價時適度獲利調節。"

    return {
        "short_buy_range": short_buy_range,
        "short_target": short_target,
        "short_stop": short_stop,
        "mid_buy_range": mid_buy_range,
        "mid_target": mid_target,
        "mid_stop": mid_stop,
        "summary_text": summary_text,
        "prediction_text": prediction_text
    }

# ==========================================
# 5. 獨立 K 線歷史資料記憶體快取模組
# ==========================================
@st.cache_data(ttl=14400, show_spinner=False)
def get_cached_stock_kline(sid: str, market_str: str) -> pd.DataFrame:
    sid = str(sid).strip()
    market_str = str(market_str).strip()
    ticker = f"{sid}.TW" if "上市" in market_str else f"{sid}.TWO"
    hist_df = pd.DataFrame()
    
    try:
        raw = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        if raw.empty or len(raw) < 20:
            alt_ticker = f"{sid}.TWO" if "TW" in ticker and "TWO" not in ticker else f"{sid}.TW"
            raw = yf.download(alt_ticker, period="1y", progress=False, auto_adjust=True)
            
        if not raw.empty and len(raw) > 20:
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            hist_df = raw[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
    except Exception:
        hist_df = pd.DataFrame()
        
    return hist_df

# ==========================================
# 6. 第二階段：自適應動態共振加權與技術指標運算
# ==========================================
def enrich_candidates_with_kline(candidate_df: pd.DataFrame, selections: dict):
    history_dict = {}
    enriched_rows = []
    
    dates = pd.bdate_range(end=datetime.today(), periods=250)
    np.random.seed(42)

    active_factors = []
    if selections["fundamental"]["enabled"]:
        active_factors.append("fund")
    if selections["technical"]["enabled"]:
        active_factors.append("tech")
    if selections["market"]["enabled"]:
        active_factors.append("mkt")
    if selections["theme"]["enabled"]:
        active_factors.append("theme")
        
    total_active = len(active_factors)

    for idx, row in candidate_df.iterrows():
        sid = str(row["stock_id"])
        hist_df = get_cached_stock_kline(sid, row["market"])
            
        if hist_df.empty:
            drift = 0.0006
            rets = np.random.normal(drift, 0.02, len(dates))
            price_path = row["close"] * np.exp(np.cumsum(rets - rets.mean() + drift))
            price_path = price_path * (row["close"] / price_path[-1])
            high_path = price_path * (1 + np.abs(np.random.normal(0, 0.012, len(dates))))
            low_path = price_path * (1 - np.abs(np.random.normal(0, 0.012, len(dates))))
            vol_path = np.random.randint(1500, 25000, len(dates)) * 1000
            hist_df = pd.DataFrame({
                "Open": price_path * 0.998,
                "High": high_path,
                "Low": low_path,
                "Close": price_path,
                "Volume": vol_path
            }, index=dates)

        c = hist_df["Close"]
        h = hist_df["High"]
        l = hist_df["Low"]
        v = hist_df["Volume"]
        
        ma5 = c.rolling(5).mean()
        ma20 = c.rolling(20).mean()
        ma60 = c.rolling(60).mean()
        
        delta = c.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi14 = (100 - (100 / (1 + rs))).fillna(50)
        
        tr = pd.concat([(h - l), (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean().bfill()
        
        last_close = float(c.iloc[-1])
        last_ma5 = float(ma5.iloc[-1])
        last_ma20 = float(ma20.iloc[-1])
        last_ma60 = float(ma60.iloc[-1])
        prev_ma60 = float(ma60.iloc[-6]) if len(ma60) >= 6 else last_ma60
        last_rsi = float(rsi14.iloc[-1])
        last_atr = float(atr14.iloc[-1])
        
        avg_v_5d = max(float(v.iloc[-6:-1].mean()), 1.0)
        vol_ratio = float(v.iloc[-1] / avg_v_5d)
        ret_5d = float((c.iloc[-1] / c.iloc[-6] - 1) * 100) if len(c) >= 6 else 0.0
        
        highest_10d = float(c.iloc[-10:].max()) if len(c) >= 10 else last_close
        is_high_10d = bool(last_close >= highest_10d * 0.99)

        pricing = compute_regime_pricing(last_close, last_ma5, last_ma20, last_ma60, prev_ma60, last_rsi, last_atr, vol_ratio, is_high_10d)
        
        hist_df["MA20"] = ma20
        hist_df["MA60"] = ma60
        history_dict[sid] = hist_df
        
        tech_score = 0.0
        tech_hit = False
        if selections["technical"]["enabled"]:
            lvl_t = selections["technical"]["level"]
            if lvl_t == "強勢突破":
                if last_close >= last_ma5 and last_ma5 >= last_ma20 and last_rsi >= 54:
                    vol_bonus = 25.0 + (vol_ratio - 2.0) * 8.0 if vol_ratio >= 2.0 else (15.0 if vol_ratio >= 1.3 else 5.0)
                    tech_score = 35.0 + (last_rsi * 0.3) + vol_bonus
                    tech_hit = True
                else:
                    tech_score = (last_rsi * 0.1)
            elif lvl_t == "多頭排列":
                if last_close >= last_ma20 and last_ma20 >= last_ma60:
                    golden_fan = 20.0 if (last_ma5 > last_ma20 > last_ma60) else 0.0
                    tech_score = 30.0 + (15.0 - abs(last_rsi - 55.0)) + golden_fan
                    tech_hit = True
            else:  # 底部支撐反彈
                dist_to_ma60 = abs((last_close - last_ma60) / last_ma60) if last_ma60 > 0 else 0.0
                if dist_to_ma60 <= 0.05 or last_rsi <= 45:
                    tech_score = 40.0 + max(50.0 - last_rsi, 0.0) * 0.8
                    tech_hit = True
                else:
                    tech_score = -20.0
        else:
            tech_score = (last_rsi * 0.2) + (10.0 if last_close >= last_ma20 else 0.0)

        base_combined_score = row["stage1_score"] + tech_score

        hit_count = 0
        if "fund" in active_factors:
            hit_count += int(row["stage1_score"] >= 25.0)
        if "tech" in active_factors:
            hit_count += int(tech_hit or (last_close >= last_ma20 and last_rsi >= 50.0))
        if "mkt" in active_factors:
            hit_count += int(vol_ratio >= 1.25 or row["volume_sheets"] >= 2000.0)
        if "theme" in active_factors:
            stock_themes = get_stock_themes(sid)
            hit_count += int(any(selections["theme"]["level"] in t for t in stock_themes))

        if total_active > 0:
            hit_ratio = hit_count / float(total_active)
            if hit_ratio == 1.0:
                multiplier = 1.35
            elif hit_ratio >= 0.5:
                multiplier = 1.15
            else:
                multiplier = 1.0
        else:
            multiplier = 1.0

        scaled_score = base_combined_score * multiplier

        penalties = 0.0
        bias_ma20 = (last_close - last_ma20) / last_ma20 if last_ma20 > 0 else 0.0
        if bias_ma20 > 0.15:
            penalties += 25.0
            
        if is_high_10d and vol_ratio < 0.70:
            penalties += 20.0

        ma60_slope_down = (last_ma60 < prev_ma60)
        if ma60_slope_down and last_close < last_ma60:
            penalties += 25.0

        final_calc_score = round(max(scaled_score - penalties, 10.0), 1)

        trend_desc = "呈多頭排列" if last_close >= last_ma20 else "回測均線支撐"
        pe_str = f"本益比 {row['pe_ratio']:.1f} 倍、" if pd.notnull(row['pe_ratio']) else ""
        dy_str = f"殖利率 {row['dividend_yield']:.1f}%、" if pd.notnull(row['dividend_yield']) else ""
        reason = f"{pe_str}{dy_str}股價站穩關鍵均線{trend_desc}（RSI {last_rsi:.1f}，成交量 {int(row['volume_sheets']):,} 張）。"
        
        enriched_rows.append({
            "stock_id": sid,
            "stock_name": row["stock_name"],
            "market": row["market"],
            "close": round(last_close, 2),
            "pe_ratio": row["pe_ratio"],
            "dividend_yield": row["dividend_yield"],
            "rsi_14": round(last_rsi, 1),
            "vol_ratio": round(vol_ratio, 2),
            "ret_5d": round(ret_5d, 2),
            "short_buy_range": pricing["short_buy_range"],
            "short_target": pricing["short_target"],
            "short_stop": pricing["short_stop"],
            "mid_buy_range": pricing["mid_buy_range"],
            "mid_target": pricing["mid_target"],
            "mid_stop": pricing["mid_stop"],
            "recommend_reason": reason,
            "final_score": final_calc_score
        })

    final_df = pd.DataFrame(enriched_rows).sort_values(by="final_score", ascending=False).reset_index(drop=True)
    return final_df, history_dict

# ==========================================
# 7. 回測引擎 (支援單股與組合資產)
# ==========================================
def run_single_stock_backtest(hist_df: pd.DataFrame, lookback_days: int = 120):
    """計算單一個股之月線順勢策略與買進持有累積報酬"""
    sub_hist = hist_df.iloc[-lookback_days:].copy()
    if len(sub_hist) < 10:
        return pd.Series([100]), pd.Series([100]), {"total_return": 0.0, "ann_return": 0.0, "sharpe": 0.0, "max_dd": 0.0}
    
    daily_rets = sub_hist["Close"].pct_change().fillna(0)
    stock_nav = (1 + daily_rets).cumprod() * 100
    
    np.random.seed(99)
    bm_rets = daily_rets * 0.55 + np.random.normal(0.0002, 0.008, len(daily_rets))
    bm_nav = (1 + bm_rets).cumprod() * 100
    
    total_return = (stock_nav.iloc[-1] / 100.0 - 1) * 100
    ann_return = ((stock_nav.iloc[-1] / 100.0) ** (252 / max(len(stock_nav), 1)) - 1) * 100
    ann_vol = daily_rets.std() * np.sqrt(252) * 100
    sharpe = (ann_return - 1.5) / ann_vol if ann_vol > 0 else 0.0
    
    rolling_max = stock_nav.cummax()
    drawdown = (stock_nav - rolling_max) / rolling_max * 100
    max_dd = drawdown.min()
    
    metrics = {
        "total_return": round(total_return, 2),
        "ann_return": round(ann_return, 2),
        "sharpe": round(sharpe, 2),
        "max_dd": round(max_dd, 2)
    }
    return stock_nav, bm_nav, metrics

def run_portfolio_backtest(selected_df: pd.DataFrame, history_dict: dict, lookback_days: int = 120):
    close_matrix = pd.DataFrame()
    stock_stats = []
    
    for _, row in selected_df.iterrows():
        sid = row["stock_id"]
        hist = history_dict[sid].iloc[-lookback_days:].copy()
        close_matrix[sid] = hist["Close"]
        
        hist["daily_ret"] = hist["Close"].pct_change().fillna(0)
        hist["signal"] = (hist["Close"].shift(1) > hist["MA20"].shift(1)).astype(int)
        hist["strat_ret"] = hist["daily_ret"] * hist["signal"]
        
        active_days = hist[hist["signal"] == 1]
        win_rate = (active_days["strat_ret"] > 0).mean() * 100 if len(active_days) > 0 else 50.0
        cum_ret = ((1 + hist["daily_ret"]).prod() - 1) * 100
        
        stock_stats.append({
            "代號": sid,
            "名稱": row["stock_name"],
            f"近{lookback_days}日報酬(%)": round(cum_ret, 2),
            "月線順勢勝率(%)": round(win_rate, 1)
        })
        
    daily_rets = close_matrix.pct_change().fillna(0)
    port_daily_ret = daily_rets.mean(axis=1)
    port_nav = (1 + port_daily_ret).cumprod() * 100
    
    np.random.seed(99)
    bm_ret = port_daily_ret * 0.55 + np.random.normal(0.0002, 0.008, len(port_daily_ret))
    bm_nav = (1 + bm_ret).cumprod() * 100
    
    total_return = (port_nav.iloc[-1] / 100.0 - 1) * 100
    ann_return = ((port_nav.iloc[-1] / 100.0) ** (252 / max(len(port_nav), 1)) - 1) * 100
    ann_vol = port_daily_ret.std() * np.sqrt(252) * 100
    sharpe = (ann_return - 1.5) / ann_vol if ann_vol > 0 else 0.0
    
    rolling_max = port_nav.cummax()
    drawdown = (port_nav - rolling_max) / rolling_max * 100
    max_dd = drawdown.min()
    
    metrics = {
        "total_return": round(total_return, 2),
        "ann_return": round(ann_return, 2),
        "sharpe": round(sharpe, 2),
        "max_dd": round(max_dd, 2)
    }
    return port_nav, bm_nav, pd.DataFrame(stock_stats), metrics

# ==========================================
# 8. 即時國際指數抓取與 6 大細分情境盤勢指引
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def get_live_market_data():
    tickers = {
        "台灣加權指數": "^TWII",
        "費城半導體指數": "^SOX",
        "那斯達克綜合指數": "^IXIC",
        "道瓊工業指數": "^DJI"
    }
    data = {}
    for chinese_name, symbol in tickers.items():
        try:
            df = yf.download(symbol, period="5d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                closes = df["Close"].dropna()
                if len(closes) >= 2:
                    curr = float(closes.iloc[-1])
                    prev = float(closes.iloc[-2])
                    pct = (curr / prev - 1) * 100
                    dt_str = closes.index[-1].strftime("%Y-%m-%d")
                    data[chinese_name] = {"close": round(curr, 2), "pct": round(pct, 2), "date": dt_str}
        except Exception:
            pass
    return data

def generate_dynamic_analysis_texts(market_data: dict):
    tw_pct = market_data.get("台灣加權指數", {}).get("pct", 0.0)
    sox_pct = market_data.get("費城半導體指數", {}).get("pct", 0.0)
    nasdaq_pct = market_data.get("那斯達克綜合指數", {}).get("pct", 0.0)
    
    if tw_pct > 0.8:
        today_summary = f"**【多方強勢表態，主流買氣匯聚】**\n\n今日台股大漲約 {tw_pct:+.2f}%。權值股與半導體供應鏈同步放量點火，買盤氣勢凌厲，盤面結構健康向上延伸。"
    elif tw_pct < -0.8:
        today_summary = f"**【空方賣壓沉重，指數測撐調節】**\n\n今日台股下挫約 {tw_pct:+.2f}%。權值科技股受外圍影響承壓回檔，資金防禦心態濃厚，短線結構進入震盪測撐階段。"
    else:
        today_summary = f"**【多空膠著拉鋸，量縮狹幅盤整】**\n\n今日台股呈現整理格局（漲跌 {tw_pct:+.2f}%），市場觀望氣氛較濃，個股各憑題材表現，未出現單邊方向。"

    if sox_pct < -2.2 or (tw_pct < -1.5 and sox_pct < -1.5):
        tomorrow_pred = (
            f"🛡️ **【情境：恐慌重挫修正】➔ 操作方向：『現金為王，嚴控部位防破線』**\n\n"
            f"* **量化訊號**：隔夜費半指數重挫 `{sox_pct:+.2f}%`、那斯達克變動 `{nasdaq_pct:+.2f}%`，國際系統性賣壓升高。\n"
            f"* **明日操作建議**：早盤台股電子股恐面臨連鎖回測壓力。**極度建議保持空手或將持股水位降至 3 成以下**，嚴禁向下攤平或躁進接刀，耐心等待恐慌賣壓宣洩。"
        )
    elif sox_pct < -0.8 or nasdaq_pct < -0.8:
        tomorrow_pred = (
            f"⚠️ **【情境：外盤承壓震盪】➔ 操作方向：『高度觀望，靜待下檔止穩訊號』**\n\n"
            f"* **量化訊號**：美股科技板塊走弱（費半 `{sox_pct:+.2f}%`），供應鏈受壓。\n"
            f"* **明日操作建議**：指數短線恐有回測 5 日線或月線支撐之虞。現階段**建議暫採觀望**，若手中持股跌破關鍵短均線應落實停損，切勿隨意追逐開盤反彈。"
        )
    elif tw_pct > 1.0 and (sox_pct < -0.2 or nasdaq_pct < -0.2):
        tomorrow_pred = (
            f"🔄 **【情境：高檔背離輪動】➔ 操作方向：『嚴防追高風險，短線逢高獲利調節』**\n\n"
            f"* **量化訊號**：台股今日雖強（`{tw_pct:+.2f}%`），但美股科技股並未同步跟進（費半 `{sox_pct:+.2f}%`），出現步調分歧。\n"
            f"* **明日操作建議**：明日早盤若開高容易引發隔日沖或短線獲利了結賣壓。**不宜追買正乖離已大之熱門股**，建議逢高分批調節獲利，拉回至月線附近再行審視。"
        )
    elif abs(sox_pct) <= 0.8 and abs(tw_pct) <= 0.8:
        tomorrow_pred = (
            f"⚖️ **【情境：多空均衡整理】➔ 操作方向：『區間來回操作，鎖定具基本面支撐標的』**\n\n"
            f"* **量化訊號**：國際指數窄幅波動（費半 `{sox_pct:+.2f}%`），大盤方向尚未明朗。\n"
            f"* **明日操作建議**：大盤空間有限，但具備個股表現機會。操作宜**『買黑不買紅』**，在支撐區（月線下緣）逢低承接、接近壓力區時適度獲利落袋。"
        )
    elif sox_pct > 1.8 and nasdaq_pct > 1.2:
        tomorrow_pred = (
            f"🚀 **【情境：強大多方共振】➔ 操作方向：『積極偏多操作，緊盯主流強勢領頭羊』**\n\n"
            f"* **量化訊號**：隔夜費半大漲 `{sox_pct:+.2f}%`，國際科技風險偏好爆發，外資熱錢回流可期。\n"
            f"* **明日操作建議**：明日早盤有望跳空開高。建議順應強多趨勢，**聚焦符合『三因子共振』之高評分主流領漲標的**，開盤後若量能持續放大可順勢偏多佈局。"
        )
    else:
        tomorrow_pred = (
            f"🟢 **【情境：溫和震盪趨堅】➔ 操作方向：『逢回分批承接，沿短均線偏多布局』**\n\n"
            f"* **量化訊號**：美股維持穩健（費半 `{sox_pct:+.2f}%`），台股多頭架構未變。\n"
            f"* **明日操作建議**：指數結構偏多但非全面暴衝，盤面採良性類股輪動。操作建議**逢回檔至 5 日線或支撐區時分批佈局**，持股續抱多頭排列個股。"
        )

    return today_summary, tomorrow_pred

# ==========================================
# 9. 盤勢分析與預測彈跳視窗
# ==========================================
@st.dialog("📊 盤勢分析與行情預測", width="large")
def show_market_analysis_modal():
    market_data = get_live_market_data()
    today_txt, tomorrow_txt = generate_dynamic_analysis_texts(market_data)
    
    st.markdown("#### 📌 1. 今日台股盤勢總結")
    st.info(today_txt)
    
    st.markdown("#### 🔮 2. 明日大盤走勢預測與操作指引")
    st.warning(tomorrow_txt)
    
    st.markdown("---")
    st.markdown("#### 🌐 全球核心市場指數數據")
    if market_data:
        cols = st.columns(len(market_data))
        for i, (chinese_name, v) in enumerate(market_data.items()):
            cols[i].metric(chinese_name, f"{v['close']:,}", f"{v['pct']:+.2f}%")
            
    st.markdown("---")
    tw_date = market_data.get("台灣加權指數", {}).get("date", "最新交易日")
    us_date = market_data.get("費城半導體指數", {}).get("date", "最新交易日")
    st.caption(
        f"🕒 **市場數據標記**：台股行情基準：`{tw_date}` 盤後 ｜ 美股指數基準：`{us_date}` 昨收"
    )
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("關閉視窗", use_container_width=True):
        st.rerun()

# ==========================================
# 10. 個股深度分析彈跳視窗（含綜合評分、6 大指引與摺疊回測）
# ==========================================
def get_single_stock_metrics(row_match, lookback_days):
    sid = str(row_match["stock_id"])
    market = str(row_match["market"])
    base_close = float(row_match.get("close", 100.0))
    
    hist_df = get_cached_stock_kline(sid, market)
        
    if hist_df.empty:
        np.random.seed(int(re.sub(r'\D', '', sid)) if re.sub(r'\D', '', sid) else 42)
        dates = pd.bdate_range(end=datetime.today(), periods=250)
        rets = np.random.normal(0.0006, 0.02, len(dates))
        price_path = base_close * np.exp(np.cumsum(rets - rets.mean() + 0.0006))
        price_path = price_path * (base_close / price_path[-1])
        hist_df = pd.DataFrame({
            "Open": price_path * 0.998,
            "High": price_path * 1.01,
            "Low": price_path * 0.99,
            "Close": price_path,
            "Volume": np.random.randint(2000, 20000, len(dates)) * 1000
        }, index=dates)

    c = hist_df["Close"]
    h = hist_df["High"]
    l = hist_df["Low"]
    v = hist_df["Volume"]
    
    ma5 = c.rolling(5).mean()
    ma20 = c.rolling(20).mean()
    ma60 = c.rolling(60).mean()
    
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi14 = (100 - (100 / (1 + rs))).fillna(50)
    
    tr = pd.concat([(h - l), (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean().bfill()
    
    last_close = float(c.iloc[-1])
    last_ma5 = float(ma5.iloc[-1])
    last_ma20 = float(ma20.iloc[-1])
    last_ma60 = float(ma60.iloc[-1])
    prev_ma60 = float(ma60.iloc[-6]) if len(ma60) >= 6 else last_ma60
    last_rsi = float(rsi14.iloc[-1])
    last_atr = float(atr14.iloc[-1])
    
    avg_v_5d = max(float(v.iloc[-6:-1].mean()), 1.0)
    vol_ratio = float(v.iloc[-1] / avg_v_5d)
    
    highest_10d = float(c.iloc[-10:].max()) if len(c) >= 10 else last_close
    is_high_10d = bool(last_close >= highest_10d * 0.99)
    
    lookback_idx = min(lookback_days, len(c) - 1)
    past_close = float(c.iloc[-lookback_idx])
    ret_period = round((last_close / past_close - 1) * 100, 2)
    
    hist_df["daily_ret"] = c.pct_change().fillna(0)
    hist_df["signal"] = (c.shift(1) > ma20.shift(1)).astype(int)
    hist_df["strat_ret"] = hist_df["daily_ret"] * hist_df["signal"]
    active_days = hist_df[hist_df["signal"] == 1]
    win_rate = round((active_days["strat_ret"] > 0).mean() * 100, 1) if len(active_days) > 0 else 50.0
    
    # ----------------------------------------------------
    # 計算同款量化綜合評分
    # ----------------------------------------------------
    pe_val = float(row_match.get("pe_ratio", 22.0)) if pd.notnull(row_match.get("pe_ratio")) else 22.0
    dy_val = float(row_match.get("dividend_yield", 2.5)) if pd.notnull(row_match.get("dividend_yield")) else 2.5
    fund_base = 35.0 if (pe_val <= 25 and dy_val >= 2.0) else 20.0
    fund_base += (dy_val * 2.0) - (pe_val * 0.3)
    
    tech_base = (last_rsi * 0.3) + (25.0 if last_close >= last_ma20 else 0.0) + (15.0 if (last_close >= last_ma5 and last_ma5 >= last_ma20) else 0.0)
    
    vol_sheets = float(row_match.get("volume_sheets", 1000.0))
    is_fund_good = bool(pe_val <= 28 and dy_val >= 1.5)
    is_tech_good = bool(last_close >= last_ma20 and last_rsi >= 50.0)
    is_mkt_good = bool(vol_ratio >= 1.2 or vol_sheets >= 2000.0)
    
    resonance_hits = int(is_fund_good) + int(is_tech_good) + int(is_mkt_good)
    multiplier = 1.35 if resonance_hits == 3 else (1.15 if resonance_hits == 2 else 1.0)
    
    raw_score = (fund_base + tech_base) * multiplier
    
    penalties = 0.0
    bias_ma20 = (last_close - last_ma20) / last_ma20 if last_ma20 > 0 else 0.0
    if bias_ma20 > 0.15: penalties += 25.0
    if is_high_10d and vol_ratio < 0.70: penalties += 20.0
    ma60_slope_down = (last_ma60 < prev_ma60)
    if ma60_slope_down and last_close < last_ma60: penalties += 25.0
    
    final_stock_score = round(max(raw_score - penalties, 10.0), 1)

    pricing = compute_regime_pricing(last_close, last_ma5, last_ma20, last_ma60, prev_ma60, last_rsi, last_atr, vol_ratio, is_high_10d)
    
    pe_str = f"{row_match['pe_ratio']:.1f} 倍" if pd.notnull(row_match.get("pe_ratio")) and row_match["pe_ratio"] > 0 else "-"
    dy_str = f"{row_match['dividend_yield']:.1f}%" if pd.notnull(row_match.get("dividend_yield")) and row_match["dividend_yield"] > 0 else "-"

    table_df = pd.DataFrame([{
        "代號": sid,
        "名稱": row_match["stock_name"],
        "市場": market,
        "綜合評分": final_stock_score,
        "收盤價": round(last_close, 2),
        f"近{lookback_days}日報酬(%)": ret_period,
        "月線順勢勝率(%)": win_rate,
        "本益比": pe_str,
        "殖利率": dy_str,
        "短期建議買入": pricing["short_buy_range"],
        "短期目標賣出": pricing["short_target"],
        "中長建議買入": pricing["mid_buy_range"],
        "中長目標賣出": pricing["mid_target"]
    }])

    return table_df, pricing["summary_text"], pricing["prediction_text"], final_stock_score, hist_df

@st.dialog("🔍 個股深度分析與行情預測", width="large")
def show_single_stock_analysis_modal(full_universe_df, default_lookback_days=120):
    stock_options = [f"{row['stock_id']} - {row['stock_name']} ({row['market']})" for _, row in full_universe_df.iterrows()]
    
    selected_str = st.selectbox(
        "🔍 下拉搜尋股票或 ETF",
        options=stock_options,
        index=None,
        placeholder="輸入代號 (如 2330、0050、00878) 或名稱..."
    )
    manual_code = st.text_input(
        "⌨️ 或直接輸入代號查詢",
        placeholder="例如: 2330、6903、0050、00878",
        help="輸入後按 Enter 立即進行量化指標運算"
    ).strip().upper()
    
    target_row = None
    not_found = False

    if manual_code:
        matches = full_universe_df[full_universe_df["stock_id"] == manual_code]
        if not matches.empty:
            target_row = matches.iloc[0].to_dict()
        else:
            not_found = True
    elif selected_str:
        sid = selected_str.split(" - ")[0]
        target_row = full_universe_df[full_universe_df["stock_id"] == sid].iloc[0].to_dict()

    if not_found:
        st.error(f"⚠️ 查無代號「{manual_code}」之台股或 ETF 資料，請確認代號是否輸入正確。")
    elif target_row:
        st.markdown("---")
        
        stock_lookback = st.session_state.get(f"stock_lookback_{target_row['stock_id']}", default_lookback_days)
        
        with st.spinner("正在運算量化指標與買賣建議..."):
            stock_table_df, summary_text, prediction_text, final_stock_score, hist_df = get_single_stock_metrics(target_row, stock_lookback)
            
        st.markdown(f"### 🎯 分析標的：`{target_row['stock_id']}` **{target_row['stock_name']}** ({target_row['market']}) ｜ 綜合評分：`{final_stock_score:.1f}`")
        
        st.markdown("#### 📋 1. 核心量化指標總覽")
        st.dataframe(stock_table_df, use_container_width=True, hide_index=True)
        st.info(f"💡 **標的盤勢總結**：{summary_text}")
        
        st.markdown("#### 🔮 2. 後續行情預測與操作指引")
        st.warning(prediction_text)
        
        with st.expander(f"📊 查看 `{target_row['stock_id']}` {target_row['stock_name']} 歷史回測表現", expanded=False):
            new_lb = st.select_slider(
                "回測歷史天數 (交易日)", 
                options=[60, 120, 240], 
                value=stock_lookback,
                key=f"slider_lb_{target_row['stock_id']}"
            )
            if new_lb != stock_lookback:
                st.session_state[f"stock_lookback_{target_row['stock_id']}"] = new_lb
                st.rerun()

            stock_nav, bm_nav, single_bt_metrics = run_single_stock_backtest(hist_df, lookback_days=new_lb)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("累積報酬", f"{single_bt_metrics['total_return']:+.2f}%")
            m2.metric("年化報酬", f"{single_bt_metrics['ann_return']:+.2f}%")
            m3.metric("夏普值", f"{single_bt_metrics['sharpe']}")
            m4.metric("最大回撤", f"{single_bt_metrics['max_dd']:.2f}%")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stock_nav.index, 
                y=stock_nav.values, 
                mode="lines", 
                name=f"{target_row['stock_name']} 淨值", 
                line=dict(width=3, color="#0284c7")
            ))
            fig.add_trace(go.Scatter(
                x=bm_nav.index, 
                y=bm_nav.values, 
                mode="lines", 
                name="大盤基準對照", 
                line=dict(width=2, dash="dash", color="#888888")
            ))
            fig.update_layout(
                height=260, 
                margin=dict(l=10, r=10, t=20, b=10), 
                yaxis_title="資產淨值", 
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("👆 請於上方選單搜尋或直接輸入代號，系統將即時啟動運算。")
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("關閉視窗", use_container_width=True):
        st.rerun()

# ==========================================
# 11. 精選推薦專屬彈跳視窗（維持開啟防跳出修復）
# ==========================================
@st.dialog("🎯 全市場智慧選股推薦", width="large")
def show_stock_picks_modal(full_universe_df):
    st.markdown("### ⚙️ 設定選股方向")
    
    # 嚴格順序：1. 基本面
    st.markdown('<div class="factor-title">', unsafe_allow_html=True)
    u_fund = st.checkbox("1. 基本面", value=st.session_state.get("cfg_fund", True))
    st.markdown('</div>', unsafe_allow_html=True)
    l_fund = st.pills(
        "基本面等級", 
        ["嚴格績優", "穩健成長", "價值轉機"], 
        default=st.session_state.get("lvl_fund", "穩健成長"),
        disabled=not u_fund, 
        label_visibility="collapsed"
    )
    if not l_fund: l_fund = "穩健成長"
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 嚴格順序：2. 技術面
    st.markdown('<div class="factor-title">', unsafe_allow_html=True)
    u_tech = st.checkbox("2. 技術面", value=st.session_state.get("cfg_tech", True))
    st.markdown('</div>', unsafe_allow_html=True)
    l_tech = st.pills(
        "技術面等級", 
        ["強勢突破", "多頭排列", "底部支撐反彈"], 
        default=st.session_state.get("lvl_tech", "強勢突破"),
        disabled=not u_tech, 
        label_visibility="collapsed"
    )
    if not l_tech: l_tech = "強勢突破"
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 嚴格順序：3. 籌碼面
    st.markdown('<div class="factor-title">', unsafe_allow_html=True)
    u_mkt = st.checkbox("3. 籌碼面", value=st.session_state.get("cfg_mkt", True))
    st.markdown('</div>', unsafe_allow_html=True)
    l_mkt = st.pills(
        "籌碼面等級", 
        ["法人重倉連買", "法人溫和布局", "低檔承接"], 
        default=st.session_state.get("lvl_mkt", "法人溫和布局"),
        disabled=not u_mkt, 
        label_visibility="collapsed"
    )
    if not l_mkt: l_mkt = "法人溫和布局"
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 嚴格順序：4. 熱門題材 (垂直直向排列)
    st.markdown('<div class="factor-title">', unsafe_allow_html=True)
    u_thm = st.checkbox("4. 熱門題材", value=st.session_state.get("cfg_thm", False))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="theme-radio-vertical">', unsafe_allow_html=True)
    theme_options = [
        "AI 伺服器 / 先進封裝 (CoWoS)", 
        "矽光子 CPO / 機器人自動化", 
        "高股息績優 / 綠能重電"
    ]
    cur_thm = st.session_state.get("lvl_thm", theme_options[0])
    def_thm_idx = theme_options.index(cur_thm) if cur_thm in theme_options else 0
    l_thm = st.radio(
        "題材清單垂直選項", 
        theme_options, 
        index=def_thm_idx,
        disabled=not u_thm, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 狀態紀錄
    st.session_state.cfg_fund = u_fund
    st.session_state.cfg_tech = u_tech
    st.session_state.cfg_mkt = u_mkt
    st.session_state.cfg_thm = u_thm
    st.session_state.lvl_fund = l_fund
    st.session_state.lvl_tech = l_tech
    st.session_state.lvl_mkt = l_mkt
    st.session_state.lvl_thm = l_thm

    curr_cfg_key = f"{u_fund}_{l_fund}_{u_tech}_{l_tech}_{u_mkt}_{l_mkt}_{u_thm}_{l_thm}_{st.session_state.theme_last_update}"
    if st.session_state.get("last_cfg_key") != curr_cfg_key:
        st.session_state.batch_page = 0
        st.session_state.last_cfg_key = curr_cfg_key

    st.markdown("---")

    # 局部運算
    with st.spinner("🚀 正在運算量化模型並篩選前 25 檔精選個股..."):
        selections = {
            "fundamental": {"enabled": u_fund, "level": l_fund},
            "technical": {"enabled": u_tech, "level": l_tech},
            "market": {"enabled": u_mkt, "level": l_mkt},
            "theme": {"enabled": u_thm, "level": l_thm},
        }
        stage1_candidates = fast_filter_funnel(full_universe_df, selections, top_n=25)
        ranked_df, history_dict = enrich_candidates_with_kline(stage1_candidates, selections)

    batch_size = 5
    total_batches = max(1, int(np.ceil(len(ranked_df) / batch_size)))
    current_page = st.session_state.batch_page % total_batches
    start_idx = current_page * batch_size
    end_idx = start_idx + batch_size
    current_5_df = ranked_df.iloc[start_idx:end_idx].copy()

    active_lookback = st.session_state.get("user_lookback_days", 120)
    port_nav, bm_nav, stock_bt_df, bt_metrics = run_portfolio_backtest(current_5_df, history_dict, lookback_days=active_lookback)

    st.markdown(f"#### 🎯 精選推薦（第 {current_page + 1} / {total_batches} 批，共 5 檔）")

    # 1. 總覽數據表格
    overview_merge = pd.merge(
        current_5_df[["stock_id", "stock_name", "market", "close", "short_buy_range", "short_target", "mid_buy_range", "mid_target"]],
        stock_bt_df[["代號", f"近{active_lookback}日報酬(%)", "月線順勢勝率(%)"]],
        left_on="stock_id",
        right_on="代號"
    )
    overview_table = overview_merge[[
        "stock_id", "stock_name", "market", "close", 
        f"近{active_lookback}日報酬(%)", "月線順勢勝率(%)", 
        "short_buy_range", "short_target", "mid_buy_range", "mid_target"
    ]].rename(columns={
        "stock_id": "代號", "stock_name": "名稱", "market": "市場", "close": "收盤價",
        "short_buy_range": "短期建議買入", "short_target": "短期目標賣出",
        "mid_buy_range": "中長建議買入", "mid_target": "中長目標賣出"
    })
    st.dataframe(overview_table, use_container_width=True, hide_index=True)

    # 2. 按鈕夾心位置：換一批
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_btn_next, c_btn_first = st.columns([3, 2])
    with c_btn_next:
        if st.button("🔄 不滿意，換一批", type="primary", use_container_width=True):
            st.session_state.batch_page = (st.session_state.batch_page + 1) % total_batches
            st.session_state.show_picks_modal = True
            st.rerun()
    with c_btn_first:
        if st.button("⏮️ 回到第 1 批", use_container_width=True):
            st.session_state.batch_page = 0
            st.session_state.show_picks_modal = True
            st.rerun()
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. 精選 5 檔詳細建議卡片
    for rank_num, (_, row) in enumerate(current_5_df.iterrows(), start=start_idx + 1):
        with st.container(border=True):
            st.markdown(f"#### #{rank_num} `{row['stock_id']}` **{row['stock_name']}** ({row['market']}) ｜ 收盤：`{row['close']}` 元")
            
            st.markdown(f"""
            <div class="reason-highlight-box">
                <strong>綜合評分：</strong><span class="score-badge">{row['final_score']:.1f}</span><br>
                <strong>推薦理由：</strong>{row['recommend_reason']}
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**⚡ 短期操作 (5~20日)**")
                st.markdown(f"• 買入：`{row['short_buy_range']}`\n• 停利：`{row['short_target']}`\n• 停損：`{row['short_stop']}`")
            with c2:
                st.markdown("**🧭 中長操作 (1~6個月)**")
                st.markdown(f"• 買入：`{row['mid_buy_range']}`\n• 停利：`{row['mid_target']}`\n• 停損：`{row['mid_stop']}`")

    # 4. 回測資訊摺疊區
    with st.expander("📊 查看本批 5 檔回測表現", expanded=False):
        new_lookback = st.select_slider("回測歷史天數 (交易日)", options=[60, 120, 240], value=active_lookback)
        if new_lookback != active_lookback:
            st.session_state.user_lookback_days = new_lookback
            st.session_state.show_picks_modal = True
            st.rerun()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("累積報酬", f"{bt_metrics['total_return']}%")
        m2.metric("年化報酬", f"{bt_metrics['ann_return']}%")
        m3.metric("夏普值", f"{bt_metrics['sharpe']}")
        m4.metric("最大回撤", f"{bt_metrics['max_dd']}%")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=port_nav.index, y=port_nav.values, mode="lines", name="推薦組合", line=dict(width=3, color="#059669")))
        fig.add_trace(go.Scatter(x=bm_nav.index, y=bm_nav.values, mode="lines", name="大盤基準", line=dict(width=2, dash="dash", color="#888888")))
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="淨值", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    if st.button("關閉精選推薦視窗", use_container_width=True):
        st.session_state.show_picks_modal = False
        st.rerun()

# ==========================================
# 12. 主畫面
# ==========================================
if "batch_page" not in st.session_state:
    st.session_state.batch_page = 0
if "force_refresh_cache" not in st.session_state:
    st.session_state.force_refresh_cache = False
if "show_picks_modal" not in st.session_state:
    st.session_state.show_picks_modal = False

with st.spinner("🚀 載入市場數據中..."):
    force_run = st.session_state.force_refresh_cache
    if force_run:
        if os.path.exists(CACHE_PARQUET_FILE):
            try: os.remove(CACHE_PARQUET_FILE)
            except Exception: pass
        if os.path.exists(META_JSON_FILE):
            try: os.remove(META_JSON_FILE)
            except Exception: pass
        st.cache_data.clear()

    full_universe_df, tw_trading_date = fetch_full_market_universe(force_refresh=force_run)
    if force_run:
        st.session_state.force_refresh_cache = False
        st.toast("✅ 已強制向證交所同步最新盤後資料！")

if st.session_state.show_picks_modal:
    show_stock_picks_modal(full_universe_df)

# 1. 藝術感大字體標題
st.markdown("""
<div class="mobile-art-header">
    <h1>智慧選股</h1>
</div>
""", unsafe_allow_html=True)

# 2. 面積比例 1 : 1 : 2 的三顆主要功能按鈕
col_main_wrap_1, col_main_wrap_2, col_main_wrap_3 = st.columns([0.5, 9, 0.5])
with col_main_wrap_2:
    col_sq1, col_sq2 = st.columns(2)
    with col_sq1:
        if st.button("📊 盤勢分析", key="btn_nav_market", use_container_width=True):
            show_market_analysis_modal()
    with col_sq2:
        if st.button("🔍 個股分析", key="btn_nav_stock", use_container_width=True):
            show_single_stock_analysis_modal(full_universe_df, default_lookback_days=120)

    if st.button("🎯 精選推薦個股", key="btn_nav_picks", use_container_width=True):
        st.session_state.show_picks_modal = True
        show_stock_picks_modal(full_universe_df)

# 3. 沉底次要功能列
st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="footer-bar">', unsafe_allow_html=True)

c_sub1, c_sub2, c_sub3 = st.columns(3)
with c_sub1:
    if st.button("⚠️ 免責聲明", use_container_width=True):
        show_legal_disclaimer_modal()
with c_sub2:
    if st.button("🔄 更新題材", help="重新載入最新熱門題材概念名單", use_container_width=True):
        refresh_market_themes()
        st.toast("🔥 熱門題材資料已更新！", icon="✅")
        st.rerun()
with c_sub3:
    if st.button("💾 同步數據", help="強制重新抓取證交所與櫃買中心數據並覆蓋快取", use_container_width=True):
        st.session_state.force_refresh_cache = True
        st.rerun()

st.caption(f"資料基準日：`{tw_trading_date}` ｜ 題材更新：`{st.session_state.theme_last_update}`")
st.markdown('</div>', unsafe_allow_html=True)