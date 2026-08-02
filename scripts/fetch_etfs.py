# -*- coding: utf-8 -*-
"""
ETF 허브용 실제 데이터를 받아옵니다: 가격/30일 등락/운용보수/배당수익률/AUM/
30일 스파크라인 + 실제 보유 종목(top holdings, 비중 포함).
"""
import json

import yfinance as yf

ETFS = [
    {"t": "SPY", "cat": "broad"},
    {"t": "VOO", "cat": "broad"},
    {"t": "QQQ", "cat": "broad"},
    {"t": "XLK", "cat": "sector"},
    {"t": "SOXX", "cat": "sector"},
    {"t": "XLF", "cat": "sector"},
    {"t": "SCHD", "cat": "dividend"},
    {"t": "VYM", "cat": "dividend"},
    {"t": "ARKK", "cat": "thematic"},
    {"t": "GLD", "cat": "commodity"},
    {"t": "AGG", "cat": "bond"},
    {"t": "TLT", "cat": "bond"},
]


def fetch_holdings(ticker_obj):
    try:
        fd = ticker_obj.funds_data
        df = fd.top_holdings
        if df is None or df.empty:
            return []
        out = []
        for symbol, row in df.iterrows():
            out.append({
                "sym": str(symbol),
                "name": str(row.get("Name", symbol)),
                "weight": round(float(row.get("Holding Percent", 0)) * 100, 2),
            })
        return out
    except Exception as e:
        print(f"    보유종목 실패: {e}")
        return []


def fetch_one(spec):
    ticker = spec["t"]
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="45d").dropna(subset=["Close"])
        closes = hist["Close"].tolist()[-30:]
        if len(closes) < 2:
            return None
        chg30 = round((closes[-1] / closes[0] - 1) * 100, 2)
        price = round(float(closes[-1]), 2)
        expense = info.get("netExpenseRatio")
        div_yield = info.get("yield")
        aum = info.get("totalAssets")
        name = info.get("longName") or info.get("shortName") or ticker
        holdings = fetch_holdings(t)
        return {
            "t": ticker, "n": name, "cat": spec["cat"],
            "price": price, "chg30": chg30,
            "expense": round(float(expense), 3) if expense is not None else None,
            "div": round(float(div_yield) * 100, 2) if div_yield is not None else None,
            "aum": round(float(aum) / 1e9, 1) if aum else None,
            "spark": [round(float(c), 4) for c in closes],
            "holdings": holdings,
        }
    except Exception as e:
        print(f"  실패: {ticker} ({e})")
        return None


if __name__ == "__main__":
    out = []
    for i, spec in enumerate(ETFS, 1):
        row = fetch_one(spec)
        if row:
            out.append(row)
        print(f"{i}/{len(ETFS)} {spec['t']} {'OK' if row else 'SKIP'} "
              f"(holdings={len(row['holdings']) if row else 0})")
    with open("etf_dump2.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"완료: {len(out)}개 ETF")
