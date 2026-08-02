# -*- coding: utf-8 -*-
"""
통합 사이트용 대형 유니버스(미국 대형주 다수 + 한국 주요주 + 코인)의
실제 시세를 받아와 JSON으로 저장합니다. daily_feed의 일일 캐시(cache/*.json)와는
별개로, 통합 웹페이지 전용 데이터 스냅샷입니다 — 종목 수가 훨씬 많고
기간 토글용으로 더 긴 일봉 이력(최근 약 1년, 260거래일)을 받습니다.

이번 업데이트로 추가된 것: 한글 검색용 별칭, 업종(섹터/산업) 분류,
다우지수 편입 여부, 실제 관련 뉴스(제목 한글 번역 + 원문 링크).

주의: yfinance는 공식 API가 아니라 비공식 라이브러리라, 티커 수가 많으면
이 스크립트가 몇 분 걸릴 수 있습니다. 뉴스 번역까지 포함하면 더 걸려요.
"""
import json
import time

import yfinance as yf

from translate import to_korean

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

# 한글 검색용 별칭(예: "애플" 검색 시 AAPL이 나오도록) — 영문 정식명과 별개로
# 한국에서 흔히 부르는 이름을 등록해둔다.
US_ALIAS = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "GOOGL": "알파벳 구글", "META": "메타 페이스북",
    "NVDA": "엔비디아", "AVGO": "브로드컴", "MU": "마이크론", "ORCL": "오라클", "CRM": "세일즈포스",
    "ADBE": "어도비", "AMD": "AMD 에이엠디", "INTC": "인텔", "CSCO": "시스코", "IBM": "아이비엠",
    "QCOM": "퀄컴", "TXN": "텍사스인스트루먼트", "NOW": "서비스나우", "INTU": "인튜이트",
    "PLTR": "팔란티어", "CRWD": "크라우드스트라이크", "PANW": "팔로알토네트웍스", "SNOW": "스노우플레이크",
    "UBER": "우버", "ABNB": "에어비앤비", "SHOP": "쇼피파이", "PYPL": "페이팔", "SPOT": "스포티파이",
    "EA": "일렉트로닉아츠", "TTWO": "테이크투인터랙티브",
    "JPM": "제이피모건 JP모건", "V": "비자", "MA": "마스터카드", "BAC": "뱅크오브아메리카",
    "WFC": "웰스파고", "GS": "골드만삭스", "MS": "모건스탠리", "AXP": "아메리칸익스프레스",
    "C": "씨티그룹", "SCHW": "찰스슈왑", "BLK": "블랙록", "PNC": "피엔씨파이낸셜", "USB": "유에스뱅코프",
    "COF": "캐피탈원",
    "UNH": "유나이티드헬스", "JNJ": "존슨앤드존슨", "LLY": "일라이릴리", "PFE": "화이자",
    "ABBV": "애브비", "MRK": "머크", "TMO": "써모피셔사이언티픽", "ABT": "애보트", "DHR": "다나허",
    "BMY": "브리스톨마이어스스퀴브", "GILD": "길리어드사이언스", "ISRG": "인튜이티브서지컬",
    "VRTX": "버텍스파마슈티컬스", "REGN": "리제네론",
    "AMZN": "아마존", "COST": "코스트코", "WMT": "월마트", "NKE": "나이키", "MCD": "맥도날드",
    "SBUX": "스타벅스", "HD": "홈디포", "TGT": "타겟", "PG": "피앤지 P&G", "KO": "코카콜라",
    "PEP": "펩시코", "LULU": "룰루레몬", "CMG": "치폴레", "BKNG": "부킹홀딩스", "MAR": "메리어트",
    "NFLX": "넷플릭스", "DIS": "디즈니", "CMCSA": "컴캐스트", "TMUS": "티모바일", "VZ": "버라이즌",
    "T": "에이티앤티 AT&T", "CHTR": "차터커뮤니케이션스",
    "CAT": "캐터필러", "HON": "허니웰", "XOM": "엑슨모빌", "CVX": "셰브론", "BA": "보잉",
    "GE": "제너럴일렉트릭 GE", "UPS": "유피에스", "LMT": "록히드마틴", "RTX": "RTX 레이시온",
    "DE": "존디어", "MMM": "쓰리엠 3M", "CSX": "씨에스엑스", "UNP": "유니온퍼시픽",
    "NSC": "노퍽서던", "SLB": "슐럼버거", "COP": "코노코필립스",
}

DOW30 = {
    "AAPL", "AMZN", "AXP", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", "GS", "HD", "HON",
    "IBM", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "NVDA", "PG", "CRM", "UNH", "VZ", "V", "WMT",
}

SECTOR_KO = {
    "Technology": "기술", "Financial Services": "금융", "Healthcare": "헬스케어",
    "Consumer Cyclical": "임의소비재", "Consumer Defensive": "필수소비재",
    "Communication Services": "커뮤니케이션", "Industrials": "산업재", "Energy": "에너지",
    "Basic Materials": "소재", "Real Estate": "리츠·부동산", "Utilities": "유틸리티",
}
INDUSTRY_KO = {
    "Consumer Electronics": "가전·전자기기", "Software - Infrastructure": "인프라 소프트웨어",
    "Software - Application": "응용 소프트웨어", "Semiconductors": "반도체",
    "Semiconductor Equipment & Materials": "반도체 장비", "Internet Content & Information": "인터넷 콘텐츠",
    "Internet Retail": "인터넷 유통", "Specialty Retail": "전문 유통", "Discount Stores": "대형마트",
    "Banks - Diversified": "대형 은행", "Banks - Regional": "지방 은행", "Capital Markets": "증권·자산운용",
    "Credit Services": "카드·여신", "Insurance - Diversified": "종합보험", "Insurance - Life": "생명보험",
    "Asset Management": "자산운용", "Drug Manufacturers - General": "대형 제약",
    "Drug Manufacturers - Specialty & Generic": "특수·제네릭 제약", "Biotechnology": "바이오테크",
    "Medical Devices": "의료기기", "Medical Instruments & Supplies": "의료용품",
    "Healthcare Plans": "건강보험", "Diagnostics & Research": "진단·연구",
    "Restaurants": "외식", "Household & Personal Products": "생활용품", "Beverages - Non-Alcoholic": "음료",
    "Packaged Foods": "가공식품", "Apparel Retail": "의류 유통", "Apparel Manufacturing": "의류 제조",
    "Footwear & Accessories": "신발·액세서리", "Lodging": "호텔·숙박", "Travel Services": "여행",
    "Entertainment": "엔터테인먼트", "Telecom Services": "통신", "Electronic Gaming & Multimedia": "게임",
    "Aerospace & Defense": "항공우주·방산", "Farm & Heavy Construction Machinery": "중장비",
    "Railroads": "철도", "Integrated Freight & Logistics": "물류", "Specialty Industrial Machinery": "산업기계",
    "Building Products & Equipment": "건자재", "Oil & Gas Integrated": "정유·가스",
    "Oil & Gas Equipment & Services": "에너지 장비·서비스", "Oil & Gas E&P": "석유·가스 탐사개발",
    "Conglomerates": "복합기업",
}


def build_news(ticker):
    try:
        items = yf.Ticker(ticker).news or []
    except Exception as e:
        print(f"    뉴스 실패: {ticker} ({e})")
        return []
    out = []
    for it in items[:3]:
        c = it.get("content") or {}
        title_en = c.get("title")
        if not title_en:
            continue
        link = ((c.get("clickThroughUrl") or {}).get("url")
                or (c.get("canonicalUrl") or {}).get("url") or "")
        provider = (c.get("provider") or {}).get("displayName") or ""
        pub = c.get("pubDate") or ""
        out.append({
            "title": to_korean(title_en),
            "title_en": title_en,
            "link": link,
            "provider": provider,
            "date": pub[:10] if pub else "",
        })
        if len(out) >= 2:
            break
    return out


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
        sector_en = info.get("sector") or ""
        industry_en = info.get("industry") or ""
        row = {
            "t": ticker, "n": name, "market": market,
            "price": last_close, "chg": round(chg, 2),
            "per": round(float(info.get("trailingPE") or 0), 1),
            "div_yield": round(float(info.get("dividendYield") or 0), 2),
            "cap": float(cap),
            "bars": bars,
        }
        if market == "us":
            row["alias"] = US_ALIAS.get(ticker, "")
            row["sector"] = SECTOR_KO.get(sector_en, sector_en)
            row["industry"] = INDUSTRY_KO.get(industry_en, industry_en)
            row["dow30"] = ticker in DOW30
            row["news"] = build_news(ticker)
        elif market == "kr":
            row["news"] = build_news(ticker)
        return row
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
