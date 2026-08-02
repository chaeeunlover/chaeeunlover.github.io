# -*- coding: utf-8 -*-
"""
영어 뉴스 헤드라인·요약을 한국어로 옮기는 곳.

정식 번역 API(Google Cloud Translation, DeepL 등)는 가입·카드 등록이
필요해서, 대신 구글 번역 웹페이지가 내부적으로 쓰는 무료 엔드포인트를
씁니다(가입 불필요 — 오픈소스 googletrans 라이브러리도 같은 방식을
씁니다). 정식 API가 아니라 예고 없이 막힐 수 있어서, 실패하면(네트워크
문제, 엔드포인트 변경 등) 원문 영어를 그대로 돌려줍니다 — 지어낸
번역을 보여주는 대신 "번역 실패 시 원문 노출"을 선택했습니다.
"""

import requests

_ENDPOINT = "https://translate.googleapis.com/translate_a/single"


def to_korean(text, timeout=6):
    if not text or not text.strip():
        return text
    try:
        r = requests.get(_ENDPOINT, params={
            "client": "gtx", "sl": "auto", "tl": "ko", "dt": "t", "q": text,
        }, timeout=timeout)
        if r.status_code != 200:
            return text
        data = r.json()
        translated = "".join(seg[0] for seg in data[0] if seg and seg[0])
        return translated or text
    except Exception:
        return text
