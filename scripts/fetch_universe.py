# -*- coding: utf-8 -*-
"""
통합 사이트용 대형 유니버스(미국 대형주 다수 + 한국 주요주 + 코인)의
실제 시세를 받아와 JSON으로 저장합니다. daily_feed의 일일 캐시(cache/*.json)와는
별개로, 통합 웹페이지 전용 데이터 스냅샷입니다 — 종목 수가 훨씬 많고
기간 토글용으로 더 긴 일봉 이력(최근 약 1년, 260거래일)을 받습니다.

주의: yfinance는 공식 API가 아니라 비공식 라이브러리라, 티커 수가 많으면
이 스크립트가 몇 분 걸릴 수 있습니다.
"""
import json
import time

import yfinance as yf

US = [
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "AVGO", "MU", "ORCL", "CRM", "ADBE",
    "AMD", "INTC", "CSCO", "IBM", "QCOM", "TXN", "NOW", "INTU", "PLTR", "CRWD",
    "PANW", "SNOW", "UBER", "ABNB", "SHOP", "PYPL", "SPOT", "EA", "TTWO",
    "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "C", "SCHW", "BLK", "PNC", "USB", "COF",
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY", "GILD", "ISRG", "VRTX", "REGN",
    "AMZN", "COST", "WMT", "NKE", "MCD", "SBUX", "HD", "TGT", "PG", "KO", "PEP", "LULU", "CMG", "BKNG", "MAR",
    "NFLX", "DIS", "CMCSA", "TMUS", "VZ", "T", "CHTR",
    "CAT", "HON", "XOM", "CVX", "BA", "GE", "UPS", "LMT", "RTX", "DE", "MMM", "CSX", "UNP", "NSC", "SLB", "COP",
]
KR = [
    "005930.KS", "000660.KS", "035420.KS", "035720.KS", "005380.KS", "000270.KS",
    "005490.KS", "051910.KS", "006400.KS", "207940.KS", "373220.KS", "068270.KS",
    "105560.KS", "055550.KS", "015760.KS",
    "012330.KS", "028260.KS", "066570.KS", "003550.KS", "009150.KS", "010130.KS",
    "032830.KS", "086790.KS", "316140.KS", "011200.KS", "034730.KS", "018260.KS",
    "010950.KS", "097950.KS", "090430.KS", "000810.KS", "011070.KS", "259960.KS",
    "036570.KS", "251270.KS", "352820.KS",
]
CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD", "ADA-USD", "DOGE-USD", "LINK-USD", "DOT-USD", "LTC-USD"]

KR_NAMES = {
    "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "035420.KS": "NAVER", "035720.KS": "카카오",
    "005380.KS": "현대차", "000270.KS": "기아", "005490.KS": "POSCO홀딩스", "051910.KS": "LG화학",
    "006400.KS": "삼성SDI", "207940.KS": "삼성바이오로직스", "373220.KS": "LG에너지솔루션",
    "068270.KS": "셀트리온", "105560.KS": "KB금융", "055550.KS": "신한지주", "015760.KS": "한국전력",
    "012330.KS": "현대모비스", "028260.KS": "삼성물산", "066570.KS": "LG전자", "003550.KS": "LG",
    "009150.KS": "삼성전기", "010130.KS": "고려아연", "032830.KS": "삼성생명", "086790.KS": "하나금융지주",
    "316140.KS": "우리금융지주", "011200.KS": "HMM", "034730.KS": "SK", "018260.KS": "삼성에스디에스",
    "010950.KS": "S-Oil", "097950.KS": "CJ제일제당", "090430.KS": "아모레퍼시픽", "000810.KS": "삼성화재",
    "011070.KS": "LG이노텍", "259960.KS": "크래프톤", "036570.KS": "엔씨소프트", "251270.KS": "넷마블",
    "352820.KS": "하이브",
}
CRYPTO_NAMES = {
    "BTC-USD": "비트코인", "ETH-USD": "이더리움", "SOL-USD": "솔라나", "XRP-USD": "리플",
    "AVAX-USD": "아발란체", "ADA-USD": "에이다", "DOGE-USD": "도지코인", "LINK-USD": "체인링크",
    "DOT-USD": "폴카닷", "LTC-USD": "라이트코인",
}

BARS_N = 260  # 약 1년치 일봉 (기간 토글: 1개월/3개월/6개월/1년에 씀)


def fetch_one(ticker, market):
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="1y")
        if hist is None or hist.empty:
            return None
        hist = hist.tail(BARS_N).dropna(subset=["Open", "High", "Low", "Close"])
        bars = [
            {"o": round(float(r.Open), 4), "h": round(float(r.High), 4),
             "l": round(float(r.Low), 4), "c": round(float(r.Close), 4),
             "v": int(r.Volume) if r.Volume == r.Volume else 0,
             "d": idx.strftime("%Y-%m-%d")}
            for idx, r in zip(hist.index, hist.itertuples())
        ]
        if len(bars) < 2:
            return None
        last_close = bars[-1]["c"]
        prev_close = bars[-2]["c"]
        chg = (last_close / prev_close - 1) * 100 if prev_close else 0.0
        name = KR_NAMES.get(ticker) or CRYPTO_NAMES.get(ticker) or (info.get("shortName") or ticker)
        cap = info.get("marketCap") or 0
        return {
            "t": ticker, "n": name, "market": market,
            "price": last_close, "chg": round(chg, 2),
            "per": round(float(info.get("trailingPE") or 0), 1),
            "div_yield": round(float(info.get("dividendYield") or 0), 2),
            "cap": float(cap),
            "bars": bars,
        }
    except Exception as e:
        print(f"  실패: {ticker} ({e})")
        return None


def fetch_group(tickers, market, out):
    for i, tk in enumerate(tickers, 1):
        row = fetch_one(tk, market)
        if row:
            out.append(row)
        print(f"[{market}] {i}/{len(tickers)} {tk} {'OK' if row else 'SKIP'}")


if __name__ == "__main__":
    started = time.time()
    out = []
    fetch_group(US, "us", out)
    fetch_group(KR, "kr", out)
    fetch_group(CRYPTO, "crypto", out)
    with open("universe_dump.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"완료: {len(out)}개 티커, {time.time()-started:.0f}초 소요")
