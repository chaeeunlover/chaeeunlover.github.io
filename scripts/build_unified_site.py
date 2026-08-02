# -*- coding: utf-8 -*-
"""
StockPulse 통합 사이트(홈 + 시세 + ETF 허브)를 한 페이지(탭 전환, 새로고침 없음)로
만듭니다. universe_dump.json(미국 70여 종목 + 한국 15종목 + 코인 4종, 각 최근
약 1년 일봉 + 날짜)과 market_dump.json(지수·금·환율·VIX)을 읽어서 주입합니다.
ETF 허브 콘텐츠도 이 파일 안에 직접 내장되어 있습니다(외부 링크 아님).
"""
import json
import os

SCRATCH = r"C:\Users\Jae\AppData\Local\Temp\claude\c--Users-Jae-Desktop-------\9ed017ff-2dd8-4b90-aa6d-1a8768cb368f\scratchpad"

with open("universe_dump.json", encoding="utf-8") as f:
    UNIVERSE = json.load(f)
with open("market_dump.json", encoding="utf-8") as f:
    MARKET = json.load(f)

UNIVERSE_JSON = json.dumps(UNIVERSE, ensure_ascii=False)
MARKET_JSON = json.dumps(MARKET, ensure_ascii=False)

n_us = sum(1 for x in UNIVERSE if x["market"] == "us")
n_kr = sum(1 for x in UNIVERSE if x["market"] == "kr")
n_cr = sum(1 for x in UNIVERSE if x["market"] == "crypto")

with open("etf_dump2.json", encoding="utf-8") as f:
    ETFS = json.load(f)
ETFS_JSON = json.dumps(ETFS, ensure_ascii=False)

HTML = f"""<title>StockPulse</title>
<style>
:root{{
  --bg:#f5f6f8; --bg-2:#eceef2; --surface:#ffffff; --surface-2:#f1f3f6; --border:#e2e5ec;
  --text:#14161c; --text-muted:#565f6e; --text-faint:#8a93a3;
  --accent:#e8660c; --accent-dim:#ffe4cc;
  --accent-2:#0f9488; --accent-3:#7c5cdb;
  --up:#e0374a; --down:#2f6fe0; --good:#16a34a; --warn:#c2740a;
  --us-up:#16a34a; --us-down:#e0374a;
  --radius:14px; --shadow:0 4px 18px -8px rgba(20,22,30,.12); color-scheme: light;
}}
*{{box-sizing:border-box;}}
html,body{{margin:0;padding:0;background:var(--bg);}}
body{{
  color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased;
}}
.num{{font-family:ui-monospace,"Consolas","SF Mono",Menlo,monospace;font-variant-numeric:tabular-nums;}}
a{{color:inherit;text-decoration:none;}}
::selection{{background:var(--accent);color:#fff;}}
.shell{{max-width:1200px;margin:0 auto;padding:0 28px;position:relative;}}
.up{{color:var(--up);}} .down{{color:var(--down);}}
.up-us{{color:var(--us-up);}} .down-us{{color:var(--us-down);}}
.eyebrow{{display:inline-flex;align-items:center;gap:8px;font-size:13.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:16px;}}
.eyebrow::before{{content:"";width:16px;height:2px;background:var(--accent);display:inline-block;}}
#view-etf .eyebrow{{color:var(--accent-3);}}
#view-etf .eyebrow::before{{background:var(--accent-3);}}

header{{position:sticky;top:0;z-index:30;background:rgba(245,246,248,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);}}
header .shell{{display:flex;align-items:center;justify-content:space-between;padding:16px 28px;}}
.brand{{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.01em;}}
.brand .dot{{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px var(--accent-dim);}}
nav{{display:flex;gap:6px;font-size:15px;color:var(--text-muted);background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:5px;}}
nav a{{padding:9px 20px;border-radius:999px;font-weight:600;cursor:pointer;}}
nav a:hover{{color:var(--text);}}
nav a.active{{background:var(--accent);color:#ffffff;}}
.ig-btn{{display:inline-flex;align-items:center;gap:6px;background:var(--surface-2);border:1px solid var(--border);color:var(--text);font-weight:700;font-size:13.5px;padding:10px 18px;border-radius:999px;}}

.view{{display:none;position:relative;}}
.view.active{{display:block;}}
.view::before{{content:"";position:absolute;top:0;left:0;right:0;height:620px;pointer-events:none;}}
#view-home::before{{background:radial-gradient(920px 480px at 15% -14%,rgba(255,138,61,.16),transparent 65%),radial-gradient(700px 420px at 95% -8%,rgba(95,208,194,.09),transparent 60%);}}
#view-quotes::before{{background:radial-gradient(920px 480px at 85% -14%,rgba(95,208,194,.14),transparent 65%),radial-gradient(700px 420px at 5% -8%,rgba(255,138,61,.08),transparent 60%);}}
#view-etf::before{{background:radial-gradient(920px 480px at 50% -14%,rgba(177,140,255,.16),transparent 65%),radial-gradient(700px 420px at 90% 10%,rgba(255,138,61,.07),transparent 60%);}}
.section{{padding:56px 0 0;}}
h1.page-title{{font-size:clamp(38px,6vw,64px);margin:0 0 20px;letter-spacing:-.02em;line-height:1.08;}}
h2{{font-size:30px;margin:0 0 24px;letter-spacing:-.01em;}}
p.lede{{font-size:18px;color:var(--text-muted);max-width:640px;}}

/* 홈: 히어로 지수 카드 */
.hero-idx{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px;}}
.hero-idx .card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px 26px;box-shadow:var(--shadow);}}
.hero-idx .k{{font-size:14px;color:var(--text-muted);margin-bottom:12px;font-weight:600;}}
.hero-idx .v{{font-size:clamp(24px,3.2vw,32px);font-weight:800;letter-spacing:-.01em;}}
.hero-idx .chgline{{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;}}
.hero-idx .c{{font-size:15px;font-weight:700;}}
.hero-idx .idx-spark{{width:76px;height:30px;flex-shrink:0;}}
.ticker-strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:32px;box-shadow:var(--shadow);}}
.tick{{background:var(--surface);padding:20px;}}
.tick .k{{font-size:12.5px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;}}
.tick .v{{font-size:20px;font-weight:700;margin-bottom:6px;}}
.tick .c{{font-size:14px;font-weight:700;}}
.callout{{border-radius:var(--radius);margin-bottom:40px;box-shadow:var(--shadow);overflow:hidden;border:1px solid var(--border);}}
.callout .callout-inner{{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap;padding:32px 34px;}}
.callout .cb-left{{flex:1;min-width:240px;}}
.callout .cb-k{{font-size:13px;color:var(--accent);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px;}}
.callout .cb-name{{font-size:32px;font-weight:800;letter-spacing:-.02em;line-height:1.15;}}
.callout .cb-ticker{{font-size:14px;color:var(--text-faint);margin:6px 0 12px;letter-spacing:.02em;}}
.callout .cb-chg{{font-size:23px;font-weight:800;margin-bottom:14px;}}
.callout .cb-desc{{margin:0;font-size:15.5px;color:var(--text-muted);line-height:1.7;max-width:480px;}}
.callout .cb-chart{{width:260px;height:110px;flex-shrink:0;}}
@media (max-width:760px){{ .callout .cb-chart{{width:100%;height:90px;}} }}
.mini-cta{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:64px;}}
.mini-cta a{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px 26px;flex:1;min-width:220px;box-shadow:var(--shadow);transition:border-color .15s,transform .15s;}}
.mini-cta a:hover{{border-color:var(--accent);transform:translateY(-2px);}}
.mini-cta .t{{font-weight:800;font-size:17px;margin-bottom:6px;}}
.mini-cta .d{{font-size:14px;color:var(--text-faint);}}

/* 홈: 히트맵 */
.heatmap-section{{margin-bottom:56px;}}
.heatmap-section h2{{font-size:26px;margin-bottom:6px;}}
.heatmap-section .lede{{margin-bottom:28px;}}
.heatmap-block{{margin-bottom:22px;}}
.hm-head{{display:flex;align-items:baseline;justify-content:space-between;font-size:14px;font-weight:700;color:var(--text-muted);margin-bottom:10px;}}
.hm-head .n{{font-weight:600;color:var(--text-faint);font-size:12.5px;}}
.heatmap{{position:relative;width:100%;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border);box-shadow:var(--shadow);}}
#heatmap-us{{height:460px;}}
#heatmap-kr{{height:240px;}}
#heatmap-crypto{{height:140px;}}
.hm-cell{{position:absolute;box-sizing:border-box;border:1px solid rgba(255,255,255,.85);display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;cursor:pointer;transition:filter .12s;text-align:center;}}
.hm-cell:hover{{filter:brightness(1.22);}}
.hm-cell .t{{font-weight:800;font-family:ui-monospace,Consolas,monospace;line-height:1.2;color:#fff;}}
.hm-cell .c{{font-family:ui-monospace,Consolas,monospace;opacity:.92;line-height:1.2;color:#fff;}}

/* 시세: 급등/급락 리더보드 */
.leaderboard{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:26px 0 8px;}}
.lb-col{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);}}
.lb-head{{font-size:12.5px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px;}}
.lb-head.up{{color:var(--up);}} .lb-head.down{{color:var(--down);}}
.lb-list{{display:flex;flex-direction:column;gap:1px;}}
.lb-item{{display:flex;justify-content:space-between;align-items:center;padding:9px 6px;cursor:pointer;border-radius:8px;}}
.lb-item:hover{{background:var(--surface-2);}}
.lb-item .t{{font-weight:800;font-size:14px;font-family:ui-monospace,Consolas,monospace;}}
.lb-item .n{{font-size:11.5px;color:var(--text-faint);margin-left:8px;}}
.lb-item .c{{font-size:13.5px;font-weight:700;}}
@media (max-width:760px){{ .leaderboard{{grid-template-columns:1fr;}} }}

/* 시세: 필터 + 정렬 + 리스트/차트 */
.filter-row{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;margin:28px 0 24px;}}
.chip-group{{display:flex;gap:10px;flex-wrap:wrap;}}
.chip{{background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:9px 18px;font-size:14px;font-weight:600;cursor:pointer;color:var(--text-muted);}}
.chip:hover{{color:var(--text);}}
.chip.active{{background:var(--accent);color:#ffffff;border-color:var(--accent);}}
.search{{background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:10px 18px;font-size:14px;color:var(--text);width:220px;}}
.search::placeholder{{color:var(--text-faint);}}
.layout{{display:grid;grid-template-columns:360px 1fr;gap:0;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;min-height:680px;margin-bottom:64px;box-shadow:var(--shadow);}}
.list-pane{{border-right:1px solid var(--border);max-height:800px;overflow-y:auto;background:var(--bg-2);}}
.list-item{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:15px 20px;cursor:pointer;border-bottom:1px solid var(--border);}}
.list-item:hover{{background:var(--surface-2);}}
.list-item.active{{background:var(--surface-2);box-shadow:inset 3px 0 0 var(--accent);}}
.list-item .l{{display:flex;flex-direction:column;gap:3px;min-width:0;}}
.list-item .t{{font-weight:800;font-size:15.5px;}}
.list-item .n{{font-size:12px;color:var(--text-faint);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:130px;}}
.list-item canvas.mini2{{width:52px;height:26px;flex-shrink:0;}}
.list-item .r{{text-align:right;flex-shrink:0;}}
.list-item .p{{font-size:14.5px;font-weight:700;}}
.list-item .c{{font-size:12.5px;font-weight:700;}}
.chart-pane{{padding:32px 34px;background:var(--surface);}}
.chart-head{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;flex-wrap:wrap;gap:10px;}}
.chart-head h3{{margin:0;font-size:28px;}}
.chart-head .sub{{color:var(--text-faint);font-size:14px;margin-top:6px;}}
.chart-head .price{{font-size:36px;font-weight:800;text-align:right;}}
.chart-head .chg{{font-size:17px;font-weight:700;text-align:right;}}
.period-row{{display:flex;gap:8px;margin-top:18px;}}
.period-chip{{background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer;color:var(--text-muted);}}
.period-chip:hover{{color:var(--text);}}
.period-chip.active{{background:var(--accent);color:#ffffff;border-color:var(--accent);}}
.indicator-row{{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;}}
.ind-chip{{display:inline-flex;align-items:center;gap:7px;background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:7px 13px;font-size:12.5px;font-weight:700;cursor:pointer;color:var(--text-faint);}}
.ind-chip .dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;opacity:.35;}}
.ind-chip.active{{color:var(--text);border-color:var(--text-faint);}}
.ind-chip.active .dot{{opacity:1;}}
.ind-chip[data-ind="ma20"] .dot{{background:#e8660c;}}
.ind-chip[data-ind="ma60"] .dot{{background:#0f9488;}}
.ind-chip[data-ind="ma120"] .dot{{background:#7c5cdb;}}
.ind-chip[data-ind="vol"] .dot{{background:#8a93a3;}}
.chart-wrap{{position:relative;margin-top:16px;}}
#candles{{width:100%;height:400px;display:block;cursor:crosshair;}}
#volume{{width:100%;height:76px;display:block;margin-top:6px;}}
.candle-tip{{position:absolute;display:none;pointer-events:none;background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:10px 13px;font-size:12.5px;box-shadow:var(--shadow);z-index:5;line-height:1.55;white-space:nowrap;}}
.candle-tip .d{{color:var(--text-faint);margin-bottom:5px;font-size:11.5px;}}
.candle-tip .row{{display:flex;justify-content:space-between;gap:14px;}}
.candle-tip .row span:first-child{{color:var(--text-faint);}}
.candle-tip .row b{{font-weight:700;}}
.hint{{font-size:12.5px;color:var(--text-faint);margin-top:10px;}}
.stat-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:24px;padding-top:22px;border-top:1px solid var(--border);}}
.stat-row .k{{font-size:12.5px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;}}
.stat-row .v{{font-size:21px;font-weight:800;}}
.tag-row{{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;}}
.tag-badge{{display:inline-flex;align-items:center;font-size:11.5px;font-weight:700;padding:4px 10px;border-radius:999px;background:var(--surface-2);border:1px solid var(--border);color:var(--text-muted);}}
.tag-badge.dow{{background:var(--accent-dim);border-color:var(--accent);color:var(--accent);}}
.news-section{{margin-top:24px;padding-top:22px;border-top:1px solid var(--border);}}
.news-section .k{{font-size:12.5px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px;}}
.news-item{{display:block;padding:12px 0;border-top:1px solid var(--border);}}
.news-item:first-of-type{{border-top:none;padding-top:0;}}
.news-item .title{{font-size:14.5px;font-weight:600;color:var(--text);line-height:1.5;}}
.news-item:hover .title{{color:var(--accent);}}
.news-item .meta{{font-size:12px;color:var(--text-faint);margin-top:4px;}}
.news-empty{{color:var(--text-faint);font-size:13.5px;}}

/* ETF 허브 */
#view-etf .prose{{max-width:700px;}}
#view-etf section.sub{{padding:64px 0;}}
#view-etf section.sub + section.sub{{border-top:1px solid var(--border);}}
#view-etf h2{{font-size:32px;text-wrap:balance;}}
#view-etf h3{{font-size:19px;margin:0 0 10px;color:var(--text);}}
#view-etf p{{color:var(--text-muted);margin:0 0 16px;font-size:16px;}}
#view-etf .lead-def{{font-size:23px;font-weight:600;color:var(--text);line-height:1.5;max-width:820px;margin:8px 0 28px;padding-left:22px;border-left:3px solid var(--accent-3);}}
#view-etf .specsheet{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:6px;display:grid;grid-template-columns:repeat(4,1fr);overflow-x:auto;box-shadow:var(--shadow);margin-bottom:8px;}}
#view-etf .spec-cell{{padding:24px 20px;border-right:1px solid var(--border);min-width:170px;}}
#view-etf .spec-cell:last-child{{border-right:none;}}
#view-etf .spec-cell .k{{font-size:12.5px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px;}}
#view-etf .spec-cell .v{{font-size:16px;color:var(--text);line-height:1.55;}}
#view-etf .snap-head{{display:flex;align-items:baseline;justify-content:space-between;gap:20px;margin-bottom:24px;flex-wrap:wrap;}}
#view-etf .snap-head .live{{font-size:13px;color:var(--text-faint);}}
#view-etf .snap-head .live b{{color:var(--good);font-weight:700;}}
#view-etf .snap-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;}}
#view-etf .snap-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px;transition:border-color .15s;box-shadow:var(--shadow);}}
#view-etf .snap-card:hover{{border-color:var(--accent-3);}}
#view-etf .snap-card .row1{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;}}
#view-etf .snap-card .ticker{{font-size:18px;font-weight:800;letter-spacing:.01em;}}
#view-etf .snap-card .name{{font-size:12.5px;color:var(--text-faint);margin-top:3px;}}
#view-etf .snap-card .chg{{font-size:17px;font-weight:700;}}
#view-etf .snap-card .price{{font-size:30px;font-weight:800;margin-bottom:4px;}}
#view-etf .snap-card canvas.spark{{width:100%;height:52px;display:block;margin-bottom:14px;}}
#view-etf .snap-card .stats{{display:grid;grid-template-columns:1fr 1fr;gap:10px 6px;font-size:13.5px;border-top:1px solid var(--border);padding-top:13px;}}
#view-etf .snap-card .stats .k{{color:var(--text-faint);display:block;margin-bottom:3px;font-size:11.5px;}}
#view-etf .snap-card .stats .v{{color:var(--text);font-weight:600;}}
#view-etf .steps{{display:flex;flex-direction:column;gap:0;max-width:700px;}}
#view-etf .step{{display:grid;grid-template-columns:38px 1fr;gap:18px;padding:20px 0;border-top:1px solid var(--border);}}
#view-etf .step:last-child{{padding-bottom:0;}}
#view-etf .step .idx{{font-family:ui-monospace,Consolas,monospace;font-size:15px;color:var(--accent-3);padding-top:2px;font-weight:700;}}
#view-etf .step h4{{margin:0 0 8px;font-size:18px;}}
#view-etf .step p{{margin:0;font-size:15.5px;}}
#view-etf .cardgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;}}
#view-etf .infocard{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);}}
#view-etf .infocard .tag{{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.05em;color:var(--accent-3);text-transform:uppercase;margin-bottom:11px;}}
#view-etf .infocard h4{{margin:0 0 9px;font-size:17px;}}
#view-etf .infocard p{{margin:0;font-size:15px;}}
#view-etf .pros-cons{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
#view-etf .pc-col{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:26px;box-shadow:var(--shadow);}}
#view-etf .pc-col.good{{border-color:rgba(41,211,152,.35);}}
#view-etf .pc-col.warn{{border-color:rgba(255,178,56,.35);}}
#view-etf .pc-col h4{{margin:0 0 15px;font-size:18px;display:flex;align-items:center;gap:8px;}}
#view-etf .pc-col.good h4{{color:var(--good);}}
#view-etf .pc-col.warn h4{{color:var(--warn);}}
#view-etf .pc-col ul{{margin:0;padding:0;list-style:none;}}
#view-etf .pc-col li{{font-size:15px;color:var(--text-muted);padding:10px 0;border-top:1px solid var(--border);}}
#view-etf .pc-col li:first-child{{border-top:none;padding-top:0;}}
#view-etf .tablewrap{{overflow-x:auto;border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);}}
#view-etf table{{border-collapse:collapse;width:100%;min-width:600px;font-size:15px;}}
#view-etf th,#view-etf td{{text-align:left;padding:15px 18px;border-bottom:1px solid var(--border);white-space:nowrap;}}
#view-etf th{{color:var(--text-faint);font-weight:700;font-size:12.5px;text-transform:uppercase;letter-spacing:.05em;background:var(--surface-2);}}
#view-etf td{{color:var(--text-muted);}}
#view-etf td.hl{{color:var(--text);font-weight:700;}}
#view-etf tr:last-child td{{border-bottom:none;}}
#view-etf .faq{{max-width:740px;}}
#view-etf details{{border-top:1px solid var(--border);padding:20px 0;}}
#view-etf details:last-child{{border-bottom:1px solid var(--border);}}
#view-etf summary{{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;font-size:18px;font-weight:700;color:var(--text);}}
#view-etf summary::-webkit-details-marker{{display:none;}}
#view-etf summary::after{{content:"+";font-size:24px;color:var(--accent-3);font-weight:400;margin-left:16px;transition:transform .2s;}}
#view-etf details[open] summary::after{{transform:rotate(45deg);}}
#view-etf details p{{margin:14px 0 0;font-size:15.5px;}}
#view-etf .etf-cta{{background:linear-gradient(180deg,var(--surface),var(--bg));border:1px solid var(--border);border-radius:20px;padding:44px;text-align:center;margin-bottom:16px;box-shadow:var(--shadow);}}
#view-etf .etf-cta h2{{margin-bottom:10px;}}
#view-etf .etf-cta p{{max-width:480px;margin:0 auto 22px;}}
#view-etf .snap-card{{cursor:pointer;}}

/* ETF 상세 모달 */
.etf-modal-backdrop{{position:fixed;inset:0;background:rgba(20,22,30,.5);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;z-index:100;padding:20px;}}
.etf-modal-backdrop.active{{display:flex;}}
.etf-modal{{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:18px;max-width:520px;width:100%;max-height:84vh;overflow-y:auto;padding:34px;box-shadow:0 24px 60px -12px rgba(20,22,30,.28);}}
.etf-modal-close{{position:absolute;top:18px;right:18px;width:32px;height:32px;border-radius:50%;background:var(--surface-2);border:1px solid var(--border);color:var(--text-muted);font-size:18px;cursor:pointer;line-height:1;}}
.etf-modal-close:hover{{color:var(--text);}}
.etf-modal .tag{{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.05em;color:var(--accent-3);text-transform:uppercase;margin-bottom:12px;}}
.etf-modal h3{{font-size:26px;margin:0 0 4px;}}
.etf-modal .sub{{color:var(--text-faint);font-size:13.5px;margin-bottom:22px;}}
.etf-modal .stats2{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px;padding-bottom:22px;border-bottom:1px solid var(--border);}}
.etf-modal .stats2 .k{{font-size:11px;color:var(--text-faint);margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em;}}
.etf-modal .stats2 .v{{font-size:17px;font-weight:800;}}
.etf-modal .hold-title{{font-size:12px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px;}}
.etf-modal .hold-row{{display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid var(--border);}}
.etf-modal .hold-row:first-of-type{{border-top:none;}}
.etf-modal .hold-row .rank{{font-size:11.5px;color:var(--text-faint);width:16px;flex-shrink:0;}}
.etf-modal .hold-row .sym{{font-weight:700;font-size:13px;width:52px;flex-shrink:0;font-family:ui-monospace,Consolas,monospace;}}
.etf-modal .hold-row .name{{flex:1;font-size:12.5px;color:var(--text-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;}}
.etf-modal .hold-row .bar-wrap{{width:70px;height:6px;background:var(--border);border-radius:3px;overflow:hidden;flex-shrink:0;}}
.etf-modal .hold-row .bar{{height:100%;background:var(--accent-3);}}
.etf-modal .hold-row .w{{font-size:12px;font-weight:700;width:44px;text-align:right;flex-shrink:0;}}
.etf-modal .no-hold{{color:var(--text-faint);font-size:13.5px;line-height:1.7;margin:0;}}

footer{{padding:40px 0 60px;font-size:12.5px;color:var(--text-faint);border-top:1px solid var(--border);margin-top:20px;}}
footer .shell{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;}}

@media (max-width:760px){{
  nav{{display:none;}}
  .hero-idx,.ticker-strip{{grid-template-columns:1fr 1fr;}}
  .layout{{grid-template-columns:1fr;}}
  .list-pane{{max-height:280px;}}
  #view-etf .specsheet{{grid-template-columns:1fr 1fr;}}
  #view-etf .spec-cell{{border-bottom:1px solid var(--border);}}
  #view-etf .pros-cons{{grid-template-columns:1fr;}}
}}
</style>

<header>
  <div class="shell">
    <div class="brand"><span class="dot"></span> StockPulse</div>
    <nav id="tab-nav">
      <a data-view="home" class="active">홈</a>
      <a data-view="quotes">시세</a>
      <a data-view="etf">ETF 허브</a>
    </nav>
    <a class="ig-btn" href="#">인스타그램 →</a>
  </div>
</header>

<!-- ============ 홈 ============ -->
<div class="view active" id="view-home">
  <div class="shell" style="padding-top:48px;">
    <div class="eyebrow">StockPulse · 실시간</div>
    <h1 class="page-title">미국·한국 증시,<br>코인까지 한 곳에서</h1>
    <p class="lede" style="margin-bottom:40px;">매일 아침 인스타로 받아보는 요약 뒤에, 실제 데이터로 직접 확인하고 싶을 때 오는 곳이에요.</p>

    <div class="hero-idx" id="hero-idx"></div>
    <div class="ticker-strip" id="ticker-strip"></div>

    <div class="callout" id="callout"></div>

    <div class="heatmap-section">
      <div class="eyebrow">오늘의 시장 지도</div>
      <h2>한눈에 보는 상승·하락</h2>
      <p class="lede">네모 크기는 시가총액, 색은 오늘 등락률이에요. 클릭하면 그 종목 차트로 바로 이동해요.</p>
      <div class="heatmap-block">
        <div class="hm-head"><span>미국 종목</span><span class="n">시가총액 기준</span></div>
        <div class="heatmap" id="heatmap-us"></div>
      </div>
      <div class="heatmap-block">
        <div class="hm-head"><span>한국 종목</span><span class="n">시가총액 기준</span></div>
        <div class="heatmap" id="heatmap-kr"></div>
      </div>
      <div class="heatmap-block">
        <div class="hm-head"><span>코인</span><span class="n">시가총액 기준</span></div>
        <div class="heatmap" id="heatmap-crypto"></div>
      </div>
    </div>

    <div class="mini-cta">
      <a data-goto="quotes" data-filter="us"><div class="t">미국 종목 →</div><div class="d">{n_us}개 대형주, 실제 차트</div></a>
      <a data-goto="quotes" data-filter="kr"><div class="t">한국 종목 →</div><div class="d">코스피 주요 {n_kr}종목</div></a>
      <a data-goto="quotes" data-filter="crypto"><div class="t">코인 →</div><div class="d">비트코인·이더리움 등 {n_cr}종</div></a>
      <a data-goto="etf"><div class="t">ETF 허브 →</div><div class="d">ETF 처음부터 정리하기</div></a>
    </div>
  </div>
</div>

<!-- ============ 시세 ============ -->
<div class="view" id="view-quotes">
  <div class="shell" style="padding-top:48px; padding-bottom:20px;">
    <div class="eyebrow">시세 · 실제 캔들차트</div>
    <h2 style="font-size:34px;">미국 · 한국 · 코인, 한 화면에서</h2>
    <p class="lede">종목을 클릭하면 오른쪽 차트가 실제 데이터로 다시 그려져요. 기간 버튼으로 1개월~1년을 오가고, 차트 위에 마우스를 올리면 그 날짜의 실제 시가·고가·저가·종가를 볼 수 있어요.</p>

    <div class="leaderboard" id="leaderboard">
      <div class="lb-col">
        <div class="lb-head up">오늘의 급등 TOP5</div>
        <div class="lb-list" id="lb-up"></div>
      </div>
      <div class="lb-col">
        <div class="lb-head down">오늘의 급락 TOP5</div>
        <div class="lb-list" id="lb-down"></div>
      </div>
    </div>

    <div class="filter-row">
      <div class="chip-group" id="market-chips">
        <div class="chip active" data-market="all">전체 ({len(UNIVERSE)})</div>
        <div class="chip" data-market="us">미국 ({n_us})</div>
        <div class="chip" data-market="kr">한국 ({n_kr})</div>
        <div class="chip" data-market="crypto">코인 ({n_cr})</div>
      </div>
      <div class="chip-group">
        <div class="chip active" data-sort="chgdesc">급등순</div>
        <div class="chip" data-sort="chgasc">급락순</div>
        <div class="chip" data-sort="alpha">이름순</div>
      </div>
      <input class="search" id="search" placeholder="티커·회사명 검색 (한글도 가능, 예: 애플)">
    </div>

    <div class="layout">
      <div class="list-pane" id="list-pane"></div>
      <div class="chart-pane">
        <div class="chart-head">
          <div>
            <h3 id="c-name">-</h3>
            <div class="sub" id="c-sub">-</div>
            <div class="tag-row" id="c-tags"></div>
          </div>
          <div>
            <div class="price num" id="c-price">-</div>
            <div class="chg num" id="c-chg">-</div>
          </div>
        </div>
        <div class="period-row" id="period-row">
          <div class="period-chip" data-n="22">1개월</div>
          <div class="period-chip" data-n="65">3개월</div>
          <div class="period-chip" data-n="130">6개월</div>
          <div class="period-chip active" data-n="260">1년</div>
        </div>
        <div class="indicator-row" id="indicator-row">
          <div class="ind-chip active" data-ind="ma20"><span class="dot"></span>MA20</div>
          <div class="ind-chip active" data-ind="ma60"><span class="dot"></span>MA60</div>
          <div class="ind-chip" data-ind="ma120"><span class="dot"></span>MA120</div>
          <div class="ind-chip active" data-ind="vol"><span class="dot"></span>거래량</div>
        </div>
        <div class="chart-wrap">
          <canvas id="candles"></canvas>
          <div class="candle-tip" id="candle-tip"></div>
        </div>
        <canvas id="volume"></canvas>
        <div class="hint">마우스 휠로 확대·축소, 드래그로 좌우 이동할 수 있어요 (더블클릭하면 원래대로). 차트에 마우스를 올리면 실제 값이 보여요. MA20·MA60·거래량은 위 버튼으로 켜고 끌 수 있어요.</div>
        <div class="stat-row">
          <div><div class="k">PER</div><div class="v num" id="s-per">-</div></div>
          <div><div class="k">배당수익률</div><div class="v num" id="s-div">-</div></div>
          <div><div class="k">시장</div><div class="v" id="s-market">-</div></div>
          <div><div class="k">기간 수익률</div><div class="v num" id="s-range">-</div></div>
        </div>
        <div class="news-section" id="c-news"></div>
      </div>
    </div>
  </div>
</div>

<!-- ============ ETF 허브 ============ -->
<div class="view" id="view-etf">
  <div class="shell" style="padding-top:48px;">

    <section class="sub" style="padding-top:0;border-top:none;">
      <div class="eyebrow">ETF 허브</div>
      <h1 class="page-title" style="font-size:clamp(34px,5vw,52px);">ETF, 한 번 제대로<br>정리하고 갑니다</h1>
      <p class="lede" style="margin-bottom:8px;">
        인스타그램에서 매일 보여드리는 숫자들 뒤에는 항상 "ETF가 뭔데?"라는 질문이 남아요.
        여기서는 그 질문에 끝까지 답합니다 — 정의부터 실제 데이터, 고르는 기준까지 한 곳에서.
      </p>
      <div class="lead-def">ETF는 여러 종목을 묶은 바구니를, 주식처럼 거래소에서 실시간으로 사고파는 상품이에요.</div>
      <div class="specsheet">
        <div class="spec-cell"><div class="k">거래 방식</div><div class="v">일반 주식과 똑같이 장중 실시간으로 매매돼요. 은행 펀드처럼 하루 한 번만 가격이 정해지지 않아요.</div></div>
        <div class="spec-cell"><div class="k">핵심 특징</div><div class="v">분산투자 + 낮은 운용보수 + 실시간 매매, 이 세 가지가 ETF를 개별주·일반 펀드와 구분 짓는 축이에요.</div></div>
        <div class="spec-cell"><div class="k">주요 유형</div><div class="v">시장 전체형 · 섹터형 · 배당형 · 테마형 · 원자재형 · 채권형, 이렇게 6갈래로 나눠 볼 수 있어요.</div></div>
        <div class="spec-cell"><div class="k">오늘의 흐름</div><div class="v">반도체 섹터(SOXX)가 최근 30일 -15.8%로 크게 흔들리는 중이에요. 아래 스냅샷에서 실제 수치를 확인하세요.</div></div>
      </div>
    </section>

    <section class="sub">
      <div class="snap-head">
        <div><div class="eyebrow">오늘의 ETF 스냅샷</div><h2>말로만 말고, 실제 숫자로</h2></div>
        <div class="live"><b>●</b> 야후 파이낸스 실시간 데이터 · 최근 30일 흐름 · 카드를 클릭하면 실제 보유종목을 볼 수 있어요</div>
      </div>
      <div class="chip-group" id="etf-cat-chips" style="margin-bottom:20px;">
        <div class="chip active" data-cat="all">전체</div>
        <div class="chip" data-cat="broad">시장 전체형</div>
        <div class="chip" data-cat="sector">섹터형</div>
        <div class="chip" data-cat="dividend">배당형</div>
        <div class="chip" data-cat="thematic">테마형</div>
        <div class="chip" data-cat="commodity">원자재형</div>
        <div class="chip" data-cat="bond">채권형</div>
      </div>
      <div class="snap-grid" id="snap-grid"></div>
    </section>

    <section class="sub">
      <div class="eyebrow">개요</div>
      <h2 class="prose">펀드인데, 왜 주식처럼 거래될까요</h2>
      <div class="prose">
        <p>일반 펀드(뮤추얼펀드)는 은행이나 증권사 창구에서 가입하고, 가격(기준가)이 하루에 딱 한 번 장 마감 후에 정해져요.
        오늘 아침에 가입 신청을 넣어도 실제로 얼마에 샀는지는 저녁이 돼야 알 수 있죠.</p>
        <p>ETF(Exchange Traded Fund, 상장지수펀드)는 이 구조를 그대로 유지하면서 딱 하나만 바꿨어요 — 펀드 자체를
        증권거래소에 상장시켜서, 개별 주식처럼 실시간으로 사고팔 수 있게 만든 거예요. 그래서 "내가 지금 사려는 가격"이
        장중 언제든 화면에 그대로 보여요. 펀드의 분산투자 효과와, 주식의 즉시성을 합친 상품이라고 보면 정확해요.</p>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">작동원리</div>
      <h2 class="prose">가격이 어떻게 실시간으로 맞춰질까요</h2>
      <p class="prose">ETF 가격이 순자산가치(NAV)에서 크게 벗어나지 않는 이유는, 아래 순환 구조가 계속 작동하기 때문이에요.</p>
      <div class="steps">
        <div class="step"><div class="idx">01</div><div><h4>지정참가회사(AP)가 실제 주식 바구니를 모읍니다</h4>
          <p>대형 증권사 같은 지정참가회사가 ETF가 담기로 한 실제 종목들을 정해진 비율대로 사들여 하나의 바구니로 만들어요.</p></div></div>
        <div class="step"><div class="idx">02</div><div><h4>그 바구니를 ETF 운용사에 맡기고 ETF 주식을 받습니다</h4>
          <p>이 과정을 '설정(creation)'이라고 불러요. 반대로 ETF 주식을 맡기고 실제 종목 바구니를 돌려받는 과정은 '환매(redemption)'예요.</p></div></div>
        <div class="step"><div class="idx">03</div><div><h4>ETF 가격이 실제 가치보다 비싸지면 AP가 차익거래에 나섭니다</h4>
          <p>ETF가 비싸 보이면 AP는 실제 종목을 사서 ETF로 바꿔 파는 게 이득이라, 그 매도세가 가격을 다시 눌러줘요. 싸지면 반대로 작동하고요.</p></div></div>
        <div class="step"><div class="idx">04</div><div><h4>그 결과, 시장가와 실제 자산가치가 계속 좁혀집니다</h4>
          <p>이 차익거래 구조 덕분에 ETF는 개별 주식처럼 거래되면서도, 펀드 본연의 '실제 가치를 반영한다'는 성격을 유지해요.</p></div></div>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">주요 유형</div>
      <h2 class="prose">어디에 분산투자하느냐로 나뉩니다</h2>
      <div class="cardgrid">
        <div class="infocard"><span class="tag">Broad</span><h4>시장 전체형</h4><p>S&amp;P500·나스닥100처럼 지수 하나를 통째로 따라가요. SPY·VOO·QQQ가 대표적이에요.</p></div>
        <div class="infocard"><span class="tag">Sector</span><h4>섹터형</h4><p>기술·금융·에너지처럼 특정 업종에만 집중해요. 업종 전체가 흔들리면 그대로 같이 움직여요.</p></div>
        <div class="infocard"><span class="tag">Dividend</span><h4>배당형</h4><p>배당을 꾸준히 늘려온 기업 위주로 담아요. 시세차익보다 정기적인 현금 흐름이 목적일 때 봐요.</p></div>
        <div class="infocard"><span class="tag">Thematic</span><h4>테마형</h4><p>AI·전기차처럼 특정 성장 테마에 베팅해요. 방향이 맞으면 크지만, 변동성도 그만큼 커요.</p></div>
        <div class="infocard"><span class="tag">Commodity</span><h4>원자재형</h4><p>금·원유 같은 실물 자산에 투자하는 효과를 내요. 주식시장과 다르게 움직이는 경우가 많아요.</p></div>
        <div class="infocard"><span class="tag">Bond</span><h4>채권형</h4><p>국채·회사채에 투자해요. 대체로 주식보다 변동성이 낮지만, 금리 변화에는 민감해요.</p></div>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">장점과 한계</div>
      <h2 class="prose">숨기지 않고 같이 봅니다</h2>
      <div class="pros-cons">
        <div class="pc-col good"><h4>✓ 장점</h4><ul>
          <li>한 번의 매수로 수십~수백 종목에 자동 분산돼요</li>
          <li>대부분 액티브 펀드보다 운용보수가 훨씬 낮아요</li>
          <li>개별 종목 분석에 자신 없어도 시장 평균 수익을 노릴 수 있어요</li>
          <li>장중 실시간으로 원하는 가격에 사고팔 수 있어요</li>
        </ul></div>
        <div class="pc-col warn"><h4>▲ 한계</h4><ul>
          <li>분산된 만큼, 개별 우량주 하나만 잘 골랐을 때보다 수익이 평범할 수 있어요</li>
          <li>담긴 종목이 나쁘게 움직이면 그대로 같이 손실을 봐요 — 손실을 막아주진 않아요</li>
          <li>운용보수(연 %)가 낮다고 없는 건 아니라서, 초장기로 보면 무시 못 할 차이가 나요</li>
          <li>거래량이 적은 ETF는 사고팔 때 가격 차이(스프레드)가 예상보다 클 수 있어요</li>
        </ul></div>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">체크포인트</div>
      <h2 class="prose">고를 때 이 네 가지만 먼저 보세요</h2>
      <div class="cardgrid">
        <div class="infocard"><h4>운용보수(Expense Ratio)</h4><p>연 몇 %를 수수료로 떼는지예요. 같은 지수를 따라가는 ETF끼리는 보수가 낮을수록 유리해요.</p></div>
        <div class="infocard"><h4>순자산총액(AUM)</h4><p>운용 규모가 클수록 갑자기 상장폐지될 위험이 낮고, 대체로 거래도 더 원활해요.</p></div>
        <div class="infocard"><h4>일평균 거래량</h4><p>거래량이 적으면 사고팔 때 원하는 가격과 실제 체결가 차이가 벌어질 수 있어요.</p></div>
        <div class="infocard"><h4>추적오차</h4><p>ETF 수익률이 따라가려는 지수와 실제로 얼마나 비슷하게 움직였는지예요. 작을수록 잘 만든 ETF예요.</p></div>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">한눈에 비교</div>
      <h2 class="prose">ETF vs 개별주 vs 액티브펀드</h2>
      <div class="tablewrap">
        <table>
          <thead><tr><th>항목</th><th>ETF</th><th>개별주</th><th>액티브펀드</th></tr></thead>
          <tbody>
            <tr><td class="hl">분산 효과</td><td>높음 (자동 분산)</td><td>없음 (종목당 집중)</td><td>높음 (운용사 재량)</td></tr>
            <tr><td class="hl">거래 방식</td><td>실시간 거래소 매매</td><td>실시간 거래소 매매</td><td>하루 1회 기준가</td></tr>
            <tr><td class="hl">운용 방식</td><td>대부분 지수 추종(패시브)</td><td>해당 없음</td><td>펀드매니저 재량(액티브)</td></tr>
            <tr><td class="hl">평균 보수</td><td>연 0.03~0.75% 수준</td><td>매매수수료만</td><td>연 1~2%대가 흔함</td></tr>
            <tr><td class="hl">개별 종목 리스크</td><td>낮음 (한 종목 비중 제한)</td><td>높음 (전액 집중)</td><td>중간 (운용사 판단에 의존)</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="sub">
      <div class="eyebrow">FAQ</div>
      <h2 class="prose">자주 묻는 질문</h2>
      <div class="faq">
        <details open><summary>ETF랑 개별주, 초보자는 뭐부터 시작해야 하나요?</summary>
          <p>정답은 없지만, 개별 기업을 분석할 자신이 아직 없다면 시장 전체형 ETF(SPY·VOO 같은) 하나로 시작해서 감을 익힌 뒤,
          관심 있는 업종 ETF나 개별주로 넓혀가는 순서를 많이 추천해요. 반대로 순서를 정해두지 않고 이것저것 섞으면 정작
          전체 포트폴리오가 어떻게 구성돼 있는지 스스로도 파악하기 어려워져요.</p></details>
        <details><summary>운용보수는 언제, 어떻게 빠져나가나요?</summary>
          <p>따로 청구서가 오는 게 아니라, ETF 순자산에서 매일 조금씩 자동으로 차감돼요. 그래서 잔고에서 보수가 빠지는
          게 눈에 보이진 않지만, 장기 수익률에는 꾸준히 영향을 줘요.</p></details>
        <details><summary>배당 ETF는 매달 배당을 주나요?</summary>
          <p>ETF마다 달라요. 미국 배당 ETF는 분기 배당(연 4회)이 가장 흔하고, 그중 일부만 월 배당 구조예요. 사려는 ETF의
          실제 배당 주기는 공식 자료에서 직접 확인하는 게 정확해요.</p></details>
        <details><summary>ETF가 상장폐지될 수도 있나요?</summary>
          <p>네, 실제로 있는 일이에요. 보통 운용 규모(AUM)가 너무 작아 운용사가 수익을 내기 어려울 때 청산돼요. 청산 시
          보유자에게는 그 시점의 순자산가치만큼 현금으로 정산되는 게 일반적이라, 투자금이 사라지는 구조는 아니에요.</p></details>
      </div>
    </section>

    <section class="sub" style="padding-bottom:64px;">
      <div class="etf-cta">
        <div class="eyebrow" style="justify-content:center;">매일 아침 7시</div>
        <h2>오늘 뭐가 흔들렸는지, 인스타로 먼저 받아보세요</h2>
        <p>시황 요약과 오늘의 밸류체크 종목을 매일 카드뉴스로 올려요. 여기 허브는 궁금할 때마다 다시 찾아와서 읽는 용도로 써주세요.</p>
        <a class="ig-btn" href="#">인스타그램 팔로우 →</a>
      </div>
    </section>

  </div>
</div>

<div class="etf-modal-backdrop" id="etf-modal-backdrop">
  <div class="etf-modal" id="etf-modal"></div>
</div>

<footer>
  <div class="shell">
    <span>StockPulse — 정보 제공 목적이며 투자 권유가 아닙니다.</span>
    <span>데이터 출처: 야후 파이낸스</span>
  </div>
</footer>

<script>
const UNIVERSE = {UNIVERSE_JSON};
const MARKET = {MARKET_JSON};
const ETFS = {ETFS_JSON};
const MARKET_LABEL = {{us:"미국", kr:"한국", crypto:"코인"}};
const CAT_KO = {{broad:"시장 전체형", sector:"섹터형", dividend:"배당형", thematic:"테마형", commodity:"원자재형", bond:"채권형"}};

// ---- 색상 관례: 한국은 빨강=상승/파랑=하락, 미국·코인·ETF는 초록=상승/빨강=하락 ----
const US_UP = "#16a34a", US_DOWN = "#e0374a";
const KR_UP = "#e0374a", KR_DOWN = "#2f6fe0";
function dirColor(chg, market){{ return market === "kr" ? (chg>=0?KR_UP:KR_DOWN) : (chg>=0?US_UP:US_DOWN); }}
function dirClass(chg, market){{ return market === "kr" ? (chg>=0?"up":"down") : (chg>=0?"up-us":"down-us"); }}

// ---- 탭 전환 ----
function showView(id){{
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById("view-"+id).classList.add("active");
  document.querySelectorAll("#tab-nav a").forEach(a => a.classList.toggle("active", a.dataset.view===id));
  // 숨겨진 탭 안의 캔버스는 폭이 0으로 그려지므로, 탭이 보이게 될 때 다시 그려준다
  if(id==="quotes"){{ renderList(); drawCandles(lastBars, -1); drawVolume(lastBars); }}
  if(id==="etf") renderEtfGrid();
}}
document.querySelectorAll("#tab-nav a").forEach(a => a.addEventListener("click", () => showView(a.dataset.view)));
document.querySelectorAll("[data-goto]").forEach(el => {{
  el.addEventListener("click", (e) => {{
    e.preventDefault();
    showView(el.dataset.goto);
    if(el.dataset.filter){{ marketFilter = el.dataset.filter; syncMarketChips(); renderList(); }}
  }});
}});

function fmtChg(v, digits=2, market="us"){{
  const sign = v >= 0 ? "+" : "";
  return `<span class="num ${{dirClass(v, market)}}">${{sign}}${{v.toFixed(digits)}}%</span>`;
}}

// ---- 홈: 히어로 지수 ----
document.getElementById("hero-idx").innerHTML = MARKET.indices.map(i => `
  <div class="card">
    <div class="k">${{i.label}}</div>
    <div class="v num ${{dirClass(i.chg_pct,"us")}}">${{i.price.toLocaleString(undefined,{{maximumFractionDigits:2}})}}</div>
    <div class="chgline">
      <span class="c num ${{dirClass(i.chg_pct,"us")}}">${{i.chg_pct>=0?'+':''}}${{i.chg_pct.toFixed(2)}}%</span>
      <canvas class="idx-spark" data-code="${{i.code}}"></canvas>
    </div>
  </div>`).join("");
document.querySelectorAll(".idx-spark").forEach(cv => {{
  const idx = MARKET.indices.find(i => i.code === cv.dataset.code);
  if(idx && idx.intraday && idx.intraday.length > 1) drawMiniInline(cv, idx.intraday, dirColor(idx.chg_pct,"us"));
}});

document.getElementById("ticker-strip").innerHTML = [
  {{k:"VIX (변동성)", v:MARKET.extras.VIX.price.toFixed(2), c:MARKET.extras.VIX.chg}},
  {{k:"금(선물)", v:"$"+MARKET.extras.GOLD.price.toLocaleString(), c:MARKET.extras.GOLD.chg}},
  {{k:"원/달러", v:"₩"+MARKET.extras.KRW.price.toLocaleString(), c:MARKET.extras.KRW.chg}},
  {{k:"비트코인", v:(()=>{{const b=UNIVERSE.find(x=>x.t==="BTC-USD"); return b?"$"+b.price.toLocaleString():"-";}})(), c:(()=>{{const b=UNIVERSE.find(x=>x.t==="BTC-USD"); return b?b.chg:0;}})()}},
].map(x => `<div class="tick"><div class="k">${{x.k}}</div><div class="v num">${{x.v}}</div><div class="c">${{fmtChg(x.c)}}</div></div>`).join("");

const mover = UNIVERSE.slice().sort((a,b)=>Math.abs(b.chg)-Math.abs(a.chg))[0];
const worstSec = MARKET.sector_perf[MARKET.sector_perf.length-1], bestSec = MARKET.sector_perf[0];
const moverColor = dirColor(mover.chg, mover.market);
document.getElementById("callout").innerHTML = `
  <div class="callout-inner" style="background:linear-gradient(120deg, ${{moverColor}}22, ${{moverColor}}05 60%);">
    <div class="cb-left">
      <div class="cb-k">오늘의 대장주</div>
      <div class="cb-name">${{mover.n}}</div>
      <div class="cb-ticker num">${{mover.t.replace('-USD','').replace('.KS','')}}</div>
      <div class="cb-chg num ${{dirClass(mover.chg, mover.market)}}">${{mover.chg>=0?'+':''}}${{mover.chg.toFixed(2)}}%</div>
      <p class="cb-desc">${{UNIVERSE.length}}개 종목 중 오늘 가장 크게 움직였어요.
      업종별로는 ${{bestSec.label}}(${{bestSec.chg_pct>=0?"+":""}}${{bestSec.chg_pct.toFixed(1)}}%)이 가장 강했고, ${{worstSec.label}}(${{worstSec.chg_pct>=0?"+":""}}${{worstSec.chg_pct.toFixed(1)}}%)은 가장 부진했어요.</p>
    </div>
    <canvas class="cb-chart" id="cb-chart"></canvas>
  </div>`;
drawSpark(document.getElementById("cb-chart"), mover.bars.slice(-30).map(b=>b.c), moverColor);

// ---- 홈: 히트맵 (시가총액 크기 트리맵) ----
function squarify(data, x, y, w, h){{
  const items = data.filter(d => (d.weight||0) > 0).sort((a,b) => b.weight - a.weight);
  const total = items.reduce((s,d) => s+d.weight, 0);
  if(total <= 0 || !items.length || w<=0 || h<=0) return [];
  const area = w*h;
  const scaled = items.map(d => Object.assign({{}}, d, {{a: d.weight/total*area}}));
  const rects = [];
  function worstRatio(row, length){{
    const sum = row.reduce((s,d)=>s+d.a,0);
    let max=-Infinity, min=Infinity;
    row.forEach(d=>{{ if(d.a>max)max=d.a; if(d.a<min)min=d.a; }});
    return Math.max((length*length*max)/(sum*sum), (sum*sum)/(length*length*min));
  }}
  let remaining = scaled.slice();
  let cx=x, cy=y, cw=w, ch=h;
  while(remaining.length){{
    const shortSide = Math.min(cw, ch);
    let row = [remaining[0]];
    let i = 1;
    while(i < remaining.length){{
      const testRow = row.concat([remaining[i]]);
      if(worstRatio(testRow, shortSide) <= worstRatio(row, shortSide)){{ row = testRow; i++; }}
      else break;
    }}
    if(cw <= ch){{
      const rowSum = row.reduce((s,d)=>s+d.a,0);
      const rowH = rowSum / cw;
      let rxpos = cx;
      row.forEach(d => {{ const iw = d.a/rowH; rects.push(Object.assign({{}}, d, {{x:rxpos, y:cy, w:iw, h:rowH}})); rxpos += iw; }});
      cy += rowH; ch -= rowH;
    }} else {{
      const rowSum = row.reduce((s,d)=>s+d.a,0);
      const rowW = rowSum / ch;
      let rypos = cy;
      row.forEach(d => {{ const ih = d.a/rowW; rects.push(Object.assign({{}}, d, {{x:cx, y:rypos, w:rowW, h:ih}})); rypos += ih; }});
      cx += rowW; cw -= rowW;
    }}
    remaining = remaining.slice(row.length);
  }}
  return rects;
}}

function heatColor(chg){{
  const capped = Math.max(-6, Math.min(6, chg));
  const t = Math.max(Math.abs(capped)/6, 0.14);
  const base = [23,27,36], up = [255,77,94], down = [74,144,255];
  const target = capped >= 0 ? up : down;
  const mix = base.map((c,i) => Math.round(c + (target[i]-c)*t));
  return `rgb(${{mix.join(',')}})`;
}}

function renderHeatmap(containerId, tickers, marketVal){{
  const el = document.getElementById(containerId);
  const w = el.clientWidth, h = el.clientHeight;
  const items = tickers.map(t => ({{t:t.t, chg:t.chg, weight: Math.max(t.cap||0, 1)}}));
  const rects = squarify(items, 0, 0, w, h);
  el.innerHTML = rects.map(r => {{
    const showText = r.w > 42 && r.h > 28;
    const short = r.t.replace('-USD','').replace('.KS','');
    const fs = Math.max(10, Math.min(15, r.w/6.5));
    return `<div class="hm-cell" data-t="${{r.t}}" style="left:${{r.x}}px;top:${{r.y}}px;width:${{r.w}}px;height:${{r.h}}px;background:${{heatColor(r.chg)}};font-size:${{fs}}px;">
      ${{showText ? `<span class="t">${{short}}</span><span class="c">${{r.chg>=0?'+':''}}${{r.chg.toFixed(1)}}%</span>` : ''}}
    </div>`;
  }}).join("");
  el.querySelectorAll(".hm-cell").forEach(cell => {{
    cell.title = (() => {{ const s = UNIVERSE.find(x=>x.t===cell.dataset.t); return s ? `${{s.n}} ${{s.chg>=0?'+':''}}${{s.chg.toFixed(2)}}%` : ''; }})();
    cell.addEventListener("click", () => {{
      current = UNIVERSE.find(x => x.t === cell.dataset.t);
      marketFilter = marketVal; syncMarketChips();
      showView("quotes");
      renderList(); renderChart();
    }});
  }});
}}

function renderAllHeatmaps(){{
  renderHeatmap("heatmap-us", UNIVERSE.filter(s=>s.market==="us"), "us");
  renderHeatmap("heatmap-kr", UNIVERSE.filter(s=>s.market==="kr"), "kr");
  renderHeatmap("heatmap-crypto", UNIVERSE.filter(s=>s.market==="crypto"), "crypto");
}}
renderAllHeatmaps();
window.addEventListener("resize", renderAllHeatmaps);

// ---- 시세 탭 ----
let marketFilter = "all";
let sortMode = "chgdesc";
let searchQ = "";
let current = mover;
let periodN = 260;
let lastBars = [];
let viewStart = 0, viewCount = 260;
let dragging = false, dragStartX = 0, dragStartViewStart = 0;
let indicators = {{ma20:true, ma60:true, ma120:false, vol:true}};

document.querySelectorAll(".ind-chip").forEach(chip => {{
  chip.addEventListener("click", () => {{
    const k = chip.dataset.ind;
    indicators[k] = !indicators[k];
    chip.classList.toggle("active", indicators[k]);
    drawCandles(lastBars, -1);
    drawVolume(lastBars);
  }});
}});

function sma(closes, period){{
  const out = new Array(closes.length).fill(null);
  let sum = 0;
  for(let i=0;i<closes.length;i++){{
    sum += closes[i];
    if(i>=period) sum -= closes[i-period];
    if(i>=period-1) out[i] = sum/period;
  }}
  return out;
}}

function syncMarketChips(){{
  document.querySelectorAll("#market-chips .chip").forEach(c => c.classList.toggle("active", c.dataset.market===marketFilter));
}}
document.querySelectorAll("#market-chips .chip").forEach(c => c.addEventListener("click", () => {{
  marketFilter = c.dataset.market; syncMarketChips(); renderList();
}}));
document.querySelectorAll('.chip-group .chip[data-sort]').forEach(c => c.addEventListener("click", () => {{
  sortMode = c.dataset.sort;
  c.parentElement.querySelectorAll(".chip").forEach(x=>x.classList.remove("active"));
  c.classList.add("active");
  renderList();
}}));
document.getElementById("search").addEventListener("input", (e) => {{ searchQ = e.target.value.trim().toLowerCase(); renderList(); }});

function filteredSorted(){{
  let arr = UNIVERSE.filter(s => marketFilter==="all" || s.market===marketFilter);
  if(searchQ) arr = arr.filter(s => s.t.toLowerCase().includes(searchQ) || s.n.toLowerCase().includes(searchQ) || (s.alias && s.alias.toLowerCase().includes(searchQ)));
  arr = arr.slice();
  if(sortMode==="chgdesc") arr.sort((a,b)=>b.chg-a.chg);
  else if(sortMode==="chgasc") arr.sort((a,b)=>a.chg-b.chg);
  else arr.sort((a,b)=>a.t.localeCompare(b.t));
  return arr;
}}

function drawMiniInline(canvas, closes, color){{
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth||52, h = canvas.clientHeight||26;
  canvas.width = w*dpr; canvas.height = h*dpr;
  const ctx = canvas.getContext("2d"); ctx.scale(dpr,dpr);
  const lo = Math.min(...closes), hi = Math.max(...closes);
  const pad = (hi-lo)*0.15 || hi*0.01;
  const vmin = lo-pad, vmax = hi+pad;
  ctx.beginPath();
  closes.forEach((p,i) => {{
    const x=(w*i)/(closes.length-1), y=h-((p-vmin)/(vmax-vmin))*h;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  }});
  ctx.strokeStyle=color; ctx.lineWidth=1.6; ctx.lineJoin="round"; ctx.stroke();
}}

const listPane = document.getElementById("list-pane");
function renderList(){{
  const arr = filteredSorted();
  listPane.innerHTML = arr.map(s => `
    <div class="list-item ${{s.t===current.t?'active':''}}" data-t="${{s.t}}">
      <div class="l"><span class="t">${{s.t.replace('-USD','').replace('.KS','')}}</span><span class="n">${{s.n}}</span></div>
      <canvas class="mini2" data-t2="${{s.t}}"></canvas>
      <div class="r"><div class="p num">${{s.market==='crypto'?'$':(s.market==='kr'?'₩':'$')}}${{s.price.toLocaleString(undefined,{{maximumFractionDigits:2}})}}</div>
        <div class="c num ${{dirClass(s.chg, s.market)}}">${{s.chg>=0?'+':''}}${{s.chg.toFixed(1)}}%</div></div>
    </div>`).join("");
  if(!arr.length){{ listPane.innerHTML = '<div style="padding:24px;color:var(--text-faint);">검색 결과가 없어요.</div>'; }}
  listPane.querySelectorAll(".list-item").forEach(el => {{
    el.addEventListener("click", () => {{
      current = UNIVERSE.find(s => s.t === el.dataset.t);
      renderList(); renderChart();
    }});
  }});
  listPane.querySelectorAll("canvas.mini2").forEach(cv => {{
    const s = UNIVERSE.find(x => x.t === cv.dataset.t2);
    drawMiniInline(cv, s.bars.map(b=>b.c), dirColor(s.chg, s.market));
  }});
  renderLeaderboard();
}}

function renderLeaderboard(){{
  const arr = UNIVERSE.filter(s => marketFilter==="all" || s.market===marketFilter);
  const cell = s => `<div class="lb-item" data-t="${{s.t}}">
    <span><span class="t">${{s.t.replace('-USD','').replace('.KS','')}}</span><span class="n">${{s.n}}</span></span>
    <span class="c num ${{dirClass(s.chg, s.market)}}">${{s.chg>=0?'+':''}}${{s.chg.toFixed(1)}}%</span>
  </div>`;
  const gainers = arr.slice().sort((a,b)=>b.chg-a.chg).slice(0,5);
  const losers = arr.slice().sort((a,b)=>a.chg-b.chg).slice(0,5);
  document.getElementById("lb-up").innerHTML = gainers.map(cell).join("") || '<div style="color:var(--text-faint);font-size:13px;padding:6px;">데이터 없음</div>';
  document.getElementById("lb-down").innerHTML = losers.map(cell).join("") || '<div style="color:var(--text-faint);font-size:13px;padding:6px;">데이터 없음</div>';
  document.querySelectorAll("#leaderboard .lb-item").forEach(el => {{
    el.addEventListener("click", () => {{
      current = UNIVERSE.find(x => x.t === el.dataset.t);
      renderList(); renderChart();
    }});
  }});
}}

document.querySelectorAll(".period-chip").forEach(chip => {{
  chip.addEventListener("click", () => {{
    periodN = parseInt(chip.dataset.n, 10);
    document.querySelectorAll(".period-chip").forEach(c=>c.classList.remove("active"));
    chip.classList.add("active");
    resetView();
  }});
}});

function drawCandles(bars, hoverIdx){{
  hoverIdx = (typeof hoverIdx === "number") ? hoverIdx : -1;
  const cv = document.getElementById("candles");
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth, h = cv.clientHeight || 400;
  cv.width = w*dpr; cv.height = h*dpr;
  const ctx = cv.getContext("2d");
  ctx.scale(dpr,dpr);
  ctx.clearRect(0,0,w,h);
  if(!bars.length) return;
  const lo = Math.min(...bars.map(b=>b.l)), hi = Math.max(...bars.map(b=>b.h));
  const pad = (hi-lo)*0.08 || hi*0.02;
  const vmin = lo-pad, vmax = hi+pad;
  const Y = v => h - ((v-vmin)/(vmax-vmin))*h;
  ctx.strokeStyle = "rgba(20,22,30,.08)"; ctx.lineWidth = 1;
  for(let i=0;i<=3;i++){{ const y=(h/3)*i; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }}
  const n = bars.length, gap = w/n, bodyW = Math.max(gap*0.55, 1);
  bars.forEach((b,i) => {{
    const cx = gap*i + gap/2;
    const up = b.c >= b.o;
    ctx.strokeStyle = ctx.fillStyle = dirColor(up ? 1 : -1, current.market);
    ctx.lineWidth = 1.1;
    ctx.beginPath(); ctx.moveTo(cx, Y(b.h)); ctx.lineTo(cx, Y(b.l)); ctx.stroke();
    const top = Y(Math.max(b.o,b.c)), bot = Y(Math.min(b.o,b.c));
    ctx.fillRect(cx-bodyW/2, top, bodyW, Math.max(bot-top,1));
  }});
  const maSpecs = [
    {{key:"ma20", period:20, color:"#e8660c"}},
    {{key:"ma60", period:60, color:"#0f9488"}},
    {{key:"ma120", period:120, color:"#7c5cdb"}},
  ];
  const closes = bars.map(b=>b.c);
  maSpecs.forEach(spec => {{
    if(!indicators[spec.key]) return;
    const vals = sma(closes, spec.period);
    ctx.beginPath();
    let started = false;
    vals.forEach((v,i) => {{
      if(v==null) return;
      const cx = gap*i + gap/2, cy = Y(v);
      if(!started){{ ctx.moveTo(cx,cy); started = true; }} else ctx.lineTo(cx,cy);
    }});
    if(started){{ ctx.strokeStyle = spec.color; ctx.lineWidth = 1.6; ctx.lineJoin = "round"; ctx.stroke(); }}
  }});
  // 축 라벨: 왼쪽에 가격(Y), 아래쪽에 날짜(X) — 어디서부터 어디까지인지 감이 오도록
  ctx.font = "11px ui-monospace, Consolas, monospace";
  ctx.textBaseline = "middle";
  for(let i=0;i<=3;i++){{
    const y = (h/3)*i;
    const val = vmax - (i/3)*(vmax-vmin);
    const label = val.toLocaleString(undefined,{{maximumFractionDigits: val>=1000?0:2}});
    const ty = i===0 ? y+9 : (i===3 ? y-7 : y);
    const tw = ctx.measureText(label).width;
    ctx.fillStyle = "rgba(255,255,255,.85)";
    ctx.fillRect(4, ty-8, tw+8, 15);
    ctx.fillStyle = "#565f6e";
    ctx.fillText(label, 8, ty);
  }}
  if(n > 1){{
    ctx.textBaseline = "alphabetic";
    const seen = new Set();
    [0, Math.floor((n-1)/2), n-1].forEach(i => {{
      if(seen.has(i) || !bars[i].d) return;
      seen.add(i);
      const cx = gap*i + gap/2;
      const label = bars[i].d.slice(5);
      const tw = ctx.measureText(label).width;
      const tx = Math.max(2, Math.min(w-tw-2, cx - tw/2));
      ctx.fillStyle = "rgba(255,255,255,.85)";
      ctx.fillRect(tx-3, h-16, tw+6, 14);
      ctx.fillStyle = "#565f6e";
      ctx.fillText(label, tx, h-5);
    }});
  }}
  if(hoverIdx >= 0 && hoverIdx < n){{
    const cx = gap*hoverIdx + gap/2;
    ctx.save();
    ctx.strokeStyle = "rgba(20,22,30,.35)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(cx, 0); ctx.lineTo(cx, h); ctx.stroke();
    ctx.restore();
  }}
}}

function drawVolume(bars){{
  const cv = document.getElementById("volume");
  if(!indicators.vol || !bars.length){{ cv.style.display = "none"; return; }}
  cv.style.display = "block";
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth, h = cv.clientHeight || 76;
  cv.width = w*dpr; cv.height = h*dpr;
  const ctx = cv.getContext("2d");
  ctx.scale(dpr,dpr);
  ctx.clearRect(0,0,w,h);
  const vols = bars.map(b=>b.v||0);
  const vmax = Math.max(...vols) || 1;
  const n = bars.length, gap = w/n, bodyW = Math.max(gap*0.55,1);
  bars.forEach((b,i) => {{
    const cx = gap*i + gap/2;
    const up = b.c >= b.o;
    ctx.fillStyle = dirColor(up ? 1 : -1, current.market) + "8c";
    const bh = Math.max((vols[i]/vmax) * h, 1);
    ctx.fillRect(cx-bodyW/2, h-bh, bodyW, bh);
  }});
}}

function fmtVal(v){{
  const unit = current.market==="kr" ? "₩" : "$";
  return unit + v.toLocaleString(undefined,{{maximumFractionDigits:2}});
}}

const candlesEl = document.getElementById("candles");
const tipEl = document.getElementById("candle-tip");

function setView(start, count){{
  const bars = current.bars;
  count = Math.max(10, Math.min(bars.length, Math.round(count)));
  start = Math.max(0, Math.min(bars.length-count, Math.round(start)));
  viewStart = start; viewCount = count;
  lastBars = bars.slice(viewStart, viewStart+viewCount);
  const rangeChg = ((lastBars[lastBars.length-1].c / lastBars[0].c) - 1) * 100;
  const rangeEl = document.getElementById("s-range");
  rangeEl.textContent = (rangeChg>=0?"+":"")+rangeChg.toFixed(1)+"%";
  rangeEl.className = "v num " + dirClass(rangeChg, current.market);
  tipEl.style.display = "none";
  drawCandles(lastBars, -1);
  drawVolume(lastBars);
}}

function resetView(){{
  const count = Math.min(periodN, current.bars.length);
  setView(current.bars.length - count, count);
}}

candlesEl.addEventListener("wheel", (e) => {{
  if(!current.bars.length) return;
  e.preventDefault();
  const rect = candlesEl.getBoundingClientRect();
  const frac = Math.max(0, Math.min(1, (e.clientX-rect.left)/rect.width));
  const zoom = e.deltaY > 0 ? 1.15 : (1/1.15);
  const anchor = viewStart + frac*viewCount;
  const newCount = viewCount*zoom;
  setView(anchor - frac*newCount, newCount);
}}, {{passive:false}});

candlesEl.addEventListener("mousedown", (e) => {{
  dragging = true; dragStartX = e.clientX; dragStartViewStart = viewStart;
  candlesEl.style.cursor = "grabbing";
}});
window.addEventListener("mousemove", (e) => {{
  if(!dragging) return;
  const rect = candlesEl.getBoundingClientRect();
  const dx = e.clientX - dragStartX;
  const barsPerPixel = viewCount / rect.width;
  setView(dragStartViewStart - dx*barsPerPixel, viewCount);
}});
window.addEventListener("mouseup", () => {{
  if(dragging){{ dragging = false; candlesEl.style.cursor = ""; }}
}});
candlesEl.addEventListener("dblclick", () => resetView());

// 모바일 터치: 한 손가락 드래그로 이동
candlesEl.addEventListener("touchstart", (e) => {{
  if(e.touches.length !== 1) return;
  dragging = true; dragStartX = e.touches[0].clientX; dragStartViewStart = viewStart;
}}, {{passive:true}});
candlesEl.addEventListener("touchmove", (e) => {{
  if(!dragging || e.touches.length !== 1) return;
  const rect = candlesEl.getBoundingClientRect();
  const dx = e.touches[0].clientX - dragStartX;
  const barsPerPixel = viewCount / rect.width;
  setView(dragStartViewStart - dx*barsPerPixel, viewCount);
}}, {{passive:true}});
candlesEl.addEventListener("touchend", () => {{ dragging = false; }});

candlesEl.addEventListener("mousemove", (e) => {{
  if(dragging) return;
  if(!lastBars.length) return;
  const rect = candlesEl.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const w = rect.width;
  const n = lastBars.length;
  let i = Math.floor((x / w) * n);
  i = Math.max(0, Math.min(n-1, i));
  drawCandles(lastBars, i);
  const b = lastBars[i];
  const gap = w / n;
  const cx = gap*i + gap/2;
  let left = cx + 14;
  if(left + 190 > w) left = cx - 204;
  tipEl.style.left = Math.max(0,left) + "px";
  tipEl.style.top = "8px";
  tipEl.style.display = "block";
  tipEl.innerHTML = `<div class="d">${{b.d || ''}}</div>
    <div class="row"><span>시가</span><b class="num">${{fmtVal(b.o)}}</b></div>
    <div class="row"><span>고가</span><b class="num">${{fmtVal(b.h)}}</b></div>
    <div class="row"><span>저가</span><b class="num">${{fmtVal(b.l)}}</b></div>
    <div class="row"><span>종가</span><b class="num">${{fmtVal(b.c)}}</b></div>`;
}});
candlesEl.addEventListener("mouseleave", () => {{
  if(dragging) return;
  tipEl.style.display = "none";
  drawCandles(lastBars, -1);
}});

function renderChart(){{
  document.getElementById("c-name").textContent = current.n;
  document.getElementById("c-sub").textContent = current.t + " · " + MARKET_LABEL[current.market];
  const unit = current.market==="kr" ? "₩" : "$";
  document.getElementById("c-price").textContent = unit + current.price.toLocaleString(undefined,{{maximumFractionDigits:2}});
  const chgEl = document.getElementById("c-chg");
  chgEl.textContent = (current.chg>=0?"+":"")+current.chg.toFixed(2)+"% 오늘";
  chgEl.className = "chg num " + dirClass(current.chg, current.market);
  document.getElementById("s-per").textContent = current.per ? current.per+"배" : "-";
  document.getElementById("s-div").textContent = current.div_yield ? current.div_yield+"%" : "-";
  document.getElementById("s-market").textContent = MARKET_LABEL[current.market];

  const tags = [];
  if(current.sector) tags.push(`<span class="tag-badge">${{current.sector}}</span>`);
  if(current.industry && current.industry !== current.sector) tags.push(`<span class="tag-badge">${{current.industry}}</span>`);
  if(current.dow30) tags.push(`<span class="tag-badge dow">다우지수 편입</span>`);
  document.getElementById("c-tags").innerHTML = tags.join("");

  const news = current.news || [];
  const newsEl = document.getElementById("c-news");
  if(news.length){{
    newsEl.innerHTML = `<div class="k">관련 뉴스</div>` + news.map(a => {{
      const inner = `<div class="title">${{a.title}}</div><div class="meta">${{a.provider}}${{a.date?' · '+a.date:''}}</div>`;
      return a.link ? `<a class="news-item" href="${{a.link}}" target="_blank" rel="noopener">${{inner}}</a>` : `<div class="news-item">${{inner}}</div>`;
    }}).join("");
  }} else {{
    newsEl.innerHTML = `<div class="k">관련 뉴스</div><div class="news-empty">가져올 수 있는 최신 뉴스가 없어요.</div>`;
  }}

  resetView();
}}

// ---- ETF 허브 ----
let etfCatFilter = "all";

function fmtPct(v){{ return v!=null ? v.toFixed(2)+"%" : "정보 없음"; }}
function fmtAum(v){{ return v!=null ? "$"+v.toLocaleString()+"B" : "정보 없음"; }}

function renderEtfGrid(){{
  const arr = ETFS.filter(e => etfCatFilter==="all" || e.cat===etfCatFilter);
  document.getElementById("snap-grid").innerHTML = arr.map(e => {{
    const dir = dirClass(e.chg30, "us");
    const sign = e.chg30 >= 0 ? "+" : "";
    return `
      <div class="snap-card" data-t="${{e.t}}">
        <div class="row1">
          <div><div class="ticker num">${{e.t}}</div><div class="name">${{e.n}}</div></div>
          <div class="chg num ${{dir}}">${{sign}}${{e.chg30.toFixed(1)}}%</div>
        </div>
        <div class="price num">$${{e.price.toLocaleString(undefined,{{minimumFractionDigits:2,maximumFractionDigits:2}})}}</div>
        <canvas class="spark" data-t="${{e.t}}"></canvas>
        <div class="stats">
          <div><span class="k">운용보수</span><span class="v num">${{fmtPct(e.expense)}}</span></div>
          <div><span class="k">배당수익률</span><span class="v num">${{fmtPct(e.div)}}</span></div>
          <div><span class="k">순자산(AUM)</span><span class="v num">${{fmtAum(e.aum)}}</span></div>
          <div><span class="k">유형</span><span class="v">${{CAT_KO[e.cat]||e.cat}}</span></div>
        </div>
      </div>`;
  }}).join("");
  document.querySelectorAll("#snap-grid canvas.spark").forEach(cv => {{
    const e = ETFS.find(x => x.t === cv.dataset.t);
    drawSpark(cv, e.spark, dirColor(e.chg30, "us"));
  }});
  document.querySelectorAll("#snap-grid .snap-card").forEach(card => {{
    card.addEventListener("click", () => openEtfModal(ETFS.find(x => x.t === card.dataset.t)));
  }});
}}
document.querySelectorAll("#etf-cat-chips .chip").forEach(c => c.addEventListener("click", () => {{
  etfCatFilter = c.dataset.cat;
  document.querySelectorAll("#etf-cat-chips .chip").forEach(x=>x.classList.remove("active"));
  c.classList.add("active");
  renderEtfGrid();
}}));

const etfModalBackdrop = document.getElementById("etf-modal-backdrop");
function openEtfModal(e){{
  const holdRows = (e.holdings && e.holdings.length)
    ? e.holdings.map((h,i) => `
      <div class="hold-row">
        <span class="rank">${{i+1}}</span>
        <span class="sym">${{h.sym}}</span>
        <span class="name">${{h.name}}</span>
        <span class="bar-wrap"><span class="bar" style="width:${{Math.min(100, h.weight*5)}}%"></span></span>
        <span class="w num">${{h.weight.toFixed(2)}}%</span>
      </div>`).join("")
    : `<p class="no-hold">이 ETF는 개별 보유종목 데이터가 제공되지 않아요. 원자재형(금 실물 등)·채권형 ETF는 주식처럼 "구성 기업"이 없거나 야후 파이낸스가 상세 내역을 제공하지 않는 경우가 흔해요 — 실제로 없는 데이터를 지어내지 않고 그대로 알려드려요.</p>`;
  document.getElementById("etf-modal").innerHTML = `
    <button class="etf-modal-close" id="etf-modal-close">×</button>
    <div class="tag">${{CAT_KO[e.cat]||e.cat}}</div>
    <h3 class="num">${{e.t}}</h3>
    <div class="sub">${{e.n}}</div>
    <div class="stats2">
      <div><div class="k">운용보수</div><div class="v num">${{fmtPct(e.expense)}}</div></div>
      <div><div class="k">배당수익률</div><div class="v num">${{fmtPct(e.div)}}</div></div>
      <div><div class="k">순자산(AUM)</div><div class="v num">${{fmtAum(e.aum)}}</div></div>
    </div>
    <div class="hold-title">실제 상위 보유종목 (비중 기준)</div>
    ${{holdRows}}
  `;
  etfModalBackdrop.classList.add("active");
  document.getElementById("etf-modal-close").addEventListener("click", closeEtfModal);
}}
function closeEtfModal(){{ etfModalBackdrop.classList.remove("active"); }}
etfModalBackdrop.addEventListener("click", (e) => {{ if(e.target === etfModalBackdrop) closeEtfModal(); }});
document.addEventListener("keydown", (e) => {{ if(e.key === "Escape") closeEtfModal(); }});

function drawSpark(canvas, prices, color){{
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  canvas.width = w*dpr; canvas.height = h*dpr;
  const ctx = canvas.getContext("2d");
  ctx.scale(dpr,dpr);
  const lo = Math.min(...prices), hi = Math.max(...prices);
  const pad = (hi-lo)*0.12 || hi*0.01;
  const vmin = lo-pad, vmax = hi+pad;
  const pts = prices.map((p,i) => [ (w*i)/(prices.length-1), h - ((p-vmin)/(vmax-vmin))*h ]);
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); pts.forEach(p => ctx.lineTo(p[0], p[1]));
  const grad = ctx.createLinearGradient(0,0,0,h);
  grad.addColorStop(0, color+"55"); grad.addColorStop(1, color+"03");
  ctx.lineTo(w,h); ctx.lineTo(0,h); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); pts.forEach(p => ctx.lineTo(p[0], p[1]));
  ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.lineJoin = "round"; ctx.stroke();
}}
renderEtfGrid();

renderList();
renderChart();
window.addEventListener("resize", () => {{ drawCandles(lastBars, -1); drawVolume(lastBars); }});
</script>
"""

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "stockpulse.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
if os.path.isdir(SCRATCH):
    with open(os.path.join(SCRATCH, "stockpulse.html"), "w", encoding="utf-8") as f:
        f.write(HTML)
SITE_OUT_DIR = os.environ.get("SITE_OUT_DIR")
if SITE_OUT_DIR:
    with open(os.path.join(SITE_OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(HTML)

print("stockpulse.html 작성 완료 —", len(UNIVERSE), "개 티커,", len(ETFS), "개 ETF")
