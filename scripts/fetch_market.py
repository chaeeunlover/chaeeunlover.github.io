# -*- coding: utf-8 -*-
"""
시장 전체 요약(지수 레벨 + 오늘 하루 인트라데이 흐름 + 섹터 등락 + 금/환율/VIX)을
실제 야후 파이낸스 데이터로 받아 market_dump.json에 저장합니다.
"""
import json

import yfinance as yf

INDICES = [
    {"code": "SPX", "label": "S&P 500", "ticker": "^GSPC"},
    {"code": "NDX", "label": "나스닥", "ticker": "^IXIC"},
    {"code": "DJI", "label": "다우", "ticker": "^DJI"},
]
SECTORS = [
    {"sector": "tech", "label": "기술", "ticker": "XLK"},
    {"sector": "fin", "label": "금융", "ticker": "XLF"},
    {"sector": "health", "label": "헬스케어", "ticker": "XLV"},
    {"sector": "cons", "label": "소비재", "ticker": "XLY"},
    {"sector": "ind", "label": "산업재·에너지", "ticker": "XLI"},
    {"sector": "comm", "label": "커뮤니케이션", "ticker": "XLC"},
]


def intraday_series(ticker):
    """오늘(가장 최근 거래일) 하루치 인트라데이 가격 흐름."""
    try:
        hist = yf.Ticker(ticker).history(period="5d", interval="15m")
        if hist is None or hist.empty:
            return []
        last_day = hist.index[-1].date()
        day_rows = hist[hist.index.map(lambda x: x.date()) == last_day]
        closes = day_rows["Close"].dropna().tolist()
        return [round(float(c), 4) for c in closes]
    except Exception as e:
        print(f"  인트라데이 실패: {ticker} ({e})")
        return []


def fetch_index(spec):
    t = yf.Ticker(spec["ticker"])
    hist = t.history(period="5d")
    hist = hist.dropna(subset=["Close"])
    last_close = float(hist["Close"].iloc[-1])
    prev_close = float(hist["Close"].iloc[-2])
    chg_pct = round((last_close / prev_close - 1) * 100, 2)
    return {
        "code": spec["code"], "label": spec["label"],
        "price": round(last_close, 2), "chg_pct": chg_pct,
        "intraday": intraday_series(spec["ticker"]),
    }


def fetch_sector(spec):
    t = yf.Ticker(spec["ticker"])
    hist = t.history(period="5d").dropna(subset=["Close"])
    last_close = float(hist["Close"].iloc[-1])
    prev_close = float(hist["Close"].iloc[-2])
    chg_pct = round((last_close / prev_close - 1) * 100, 2)
    return {"sector": spec["sector"], "label": spec["label"], "chg_pct": chg_pct}


def fetch_extra(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="5d").dropna(subset=["Close"])
    last_close = float(hist["Close"].iloc[-1])
    prev_close = float(hist["Close"].iloc[-2])
    chg_pct = round((last_close / prev_close - 1) * 100, 2)
    return {"price": round(last_close, 2), "chg": chg_pct}


if __name__ == "__main__":
    indices = [fetch_index(s) for s in INDICES]
    print("지수 완료:", [i["code"] for i in indices])
    sector_perf = sorted((fetch_sector(s) for s in SECTORS), key=lambda x: -x["chg_pct"])
    print("섹터 완료")
    extras = {
        "GOLD": fetch_extra("GC=F"),
        "KRW": fetch_extra("KRW=X"),
        "VIX": fetch_extra("^VIX"),
    }
    print("환율/금/VIX 완료")
    out = {"indices": indices, "sector_perf": sector_perf, "extras": extras}
    with open("market_dump.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("market_dump.json 작성 완료")
