#!/usr/bin/env python3
"""review-calendar 코어 테스트

index.html 안의 RC-CORE 블록(파서 + 3-way 병합)을 그대로 뽑아 QuickJS로 실행해 검증합니다.
    pip install quickjs
    python3 test/core.test.py
"""
import json
import re
import sys
from pathlib import Path

import quickjs

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "index.html").exists() else HERE.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

m = re.search(r"/\* =+\n   RC-CORE:START.*?RC-CORE:END\n   =+ \*/", HTML, re.S)
if not m:
    print("RC-CORE 블록을 찾지 못했습니다")
    sys.exit(1)
CORE = m.group(0)

ctx = quickjs.Context()
ctx.eval(CORE)
ctx.eval("""
var NOW = new Date(2026, 10, 20);   // 2026-11-20

function parse(text){ return parseNotice(text, NOW); }
function j(x){ return JSON.stringify(x); }
""")

WISDOM = "\n".join([
    "[Web발신]",
    "[위즈덤하우스 드림] 《소맥거핀의 인체 친구들 8》 인스타 서포터즈 당첨을 축하드립니다!",
    "안녕하세요, 출판사 위즈덤하우스 드림입니다.",
    "[소맥거핀의 인체 친구들 8] 인스타 서포터즈에 선정되셨습니다.",
    "도서는 11/8(토)까지 발송 예정입니다.",
    "",
    "아래 미션을 모두 완료해 주세요.",
    "1) 개인 SNS(인스타) 도서 리뷰 업로드",
    "2) 온라인 서점 2곳 이상 리뷰 등록",
    "3) 링크 취합해 구글폼 제출",
    "",
    "필수 해시태그: #소맥거핀의인체친구들 #초등추천도서 #초등학습만화 #초등교과연계 #위즈덤하우스",
    "계정 태그: @wisdomhouse_kids",
    "제출 링크: https://forms.gle/MKusfaUHYEBys9Fr9",
    "마감일: ~11/15(일) 자정까지",
    "",
    "문의: 위즈덤하우스 드림",
])

EZ = "\n".join([
    "[Web발신]",
    "[이지프렌즈] 11월 서평단 안내드립니다.",
    "안녕하세요, 이지프렌즈입니다.",
    "11월 서평단 도서 두 권이 발송되었습니다.",
    "📚 『고래가 노래하는 곳』",
    "📚 『오승리, 호찌민에 가다』",
    "",
    "서평은 두 권 모두 작성해 주세요.",
    "1) 『고래가 노래하는 곳』 서평 업로드",
    "2) 『오승리, 호찌민에 가다』 서평 업로드",
    "3) 인증 폼 제출",
    "",
    "마감: 11월 29일(일요일) 밤 12시까지",
    "🔗 인증 폼 링크",
    "https://forms.gle/JH7TYwtNmJt2NPG19",
    "",
    "감사합니다.",
])

WAITING = "\n".join([
    "[Web발신]",
    "[샘터] 『나의 거리에게』 서평단에 선정되셨습니다.",
    "가이드라인은 별도 메일로 보내드립니다.",
    "1) 가이드라인 메일 수신 확인",
    "2) 서평 작성 및 업로드",
    "3) 인증/링크 제출",
    "문의: 샘터 (isamtoh)",
])

SEOUL = "\n".join([
    "[Web발신]",
    "[서울문화사 어린이책] '김경일의 마음 수업2' 서포터즈 활동 안내드립니다.",
    "안녕하세요. 서울문화사 어린이책입니다.",
    "서포터즈 활동 관련 안내 말씀드립니다.",
    "",
    "▷도서명 : 김경일의 마음 수업2",
    "▷활동 기간 : 11/10(화) ~ 11/22(일)",
    "▷마감일 : 11/22(일)까지",
    "▷미션",
    "1) 활동 리뷰 작성",
    "2) 회신 링크(구글폼) 제출",
    "▷회신 링크",
    "https://forms.gle/DGKfJkyPJyRFWQyY6",
    "",
    "관련 문의 사항은 '서울문화사 어린이책'으로 연락 주세요.",
    "감사합니다.",
])

fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} {detail}")
        fails.append(name)


def run(expr):
    return json.loads(ctx.eval(f"j({expr})"))


print("[1] 첫 번째 문자 (위즈덤하우스 · 인스타 서포터즈)")
p = run(f"parse({json.dumps(WISDOM)})")
check("제목", p["title"] == "소맥거핀의 인체 친구들 8", p["title"])
check("제공처", p["provider"] == "위즈덤하우스", p["provider"])
check("유형", p["type"] == "인스타 서포터즈", p["type"])
check("마감일 2026-11-15", p["deadline"] == "2026-11-15", p["deadline"])
check("미션 3개", len(p["missions"]) == 3, p["missions"])
check("미션 내용", p["missions"][2] == "링크 취합해 구글폼 제출", p["missions"])
check("계정 태그", p["accounts"] == ["@wisdomhouse_kids"], p["accounts"])
check("해시태그 5개", len(p["hashtags"]) == 5, p["hashtags"])
check("해시태그 순서", p["hashtags"][0] == "#소맥거핀의인체친구들", p["hashtags"])
check("제출 링크", p["links"] == ["https://forms.gle/MKusfaUHYEBys9Fr9"], p["links"])
check("원문 보관", p["original"] == WISDOM.strip(), "원문 길이 %d" % len(p["original"]))

print("[2] 두 번째 문자 (이지프렌즈 · 서평단, 『』 + 11월 29일(일요일) + 🔗 링크)")
p2 = run(f"parse({json.dumps(EZ)})")
check("겹낫표 제목 2권", p2["title"] == "고래가 노래하는 곳 / 오승리, 호찌민에 가다", p2["title"])
check("제공처", p2["provider"] == "이지프렌즈", p2["provider"])
check("유형", p2["type"] == "서평단", p2["type"])
check("마감일 2026-11-29", p2["deadline"] == "2026-11-29", p2["deadline"])
check("미션 3개", len(p2["missions"]) == 3, p2["missions"])
check("인증 폼 링크", p2["links"] == ["https://forms.gle/JH7TYwtNmJt2NPG19"], p2["links"])

print("[3] 세 번째 문자 (샘터 · 날짜 없음)")
p3 = run(f"parse({json.dumps(WAITING)})")
check("제목", p3["title"] == "나의 거리에게", p3["title"])
check("제공처", p3["provider"] == "샘터", p3["provider"])
check("마감일 없음", p3["deadline"] == "", p3["deadline"])
check("미션 3개", len(p3["missions"]) == 3, p3["missions"])

print("[4] 네 번째 문자 (서울문화사 어린이책 · ▷이름표)")
p4 = run(f"parse({json.dumps(SEOUL)})")
check("도서명", p4["title"] == "김경일의 마음 수업2", p4["title"])
check("제공처", p4["provider"] == "서울문화사 어린이책", p4["provider"])
check("유형", p4["type"] == "서포터즈", p4["type"])
check("마감일 2026-11-22", p4["deadline"] == "2026-11-22", p4["deadline"])
check("미션 2개", p4["missions"] == ["활동 리뷰 작성", "회신 링크(구글폼) 제출"], p4["missions"])
check("회신 링크 URL", p4["links"] == ["https://forms.gle/DGKfJkyPJyRFWQyY6"], p4["links"])

FLAT = ("[Web발신] [이지프렌즈] 11월 서평단 안내. 1) 『고래가 노래하는 곳』 서평 업로드 2) 『오승리, 호찌민에 가다』 서평 업로드 "
        "3) 인증 폼 제출 마감: 11월 29일(일요일) 밤 12시까지 🔗 인증 폼 링크 https://forms.gle/JH7TYwtNmJt2NPG19 감사합니다.")
print("[5] 줄바꿈이 사라진 복사본")
p5 = run(f"parse({json.dumps(FLAT)})")
check("미션 3개로 나뉨", p5["missions"] == ["『고래가 노래하는 곳』 서평 업로드", "『오승리, 호찌민에 가다』 서평 업로드", "인증 폼 제출"], p5["missions"])
check("마감일", p5["deadline"] == "2026-11-29", p5["deadline"])
check("링크", p5["links"] == ["https://forms.gle/JH7TYwtNmJt2NPG19"], p5["links"])

print("[6] 날짜 연도 추정")
check("11월 기준 1/5 → 내년", run('(function(){var p=parse("마감: 1/5 까지");return p.deadline;})()') == "2027-01-05")
check("11월 기준 11/15 → 올해", run('(function(){var p=parse("마감일: ~11/15");return p.deadline;})()') == "2026-11-15")
check("11월 기준 12/24 → 올해", run('(function(){var p=parse("제출 마감 12/24");return p.deadline;})()') == "2026-12-24")
check("1월 20일 기준 12/25 → 그해 12월", run('(function(){var p=parseNotice("마감 12/25", new Date(2027,0,20));return p.deadline;})()') == "2027-12-25")

print("[7] 유용한 부가 기능")
check("해시태그 복사 문자열", run('parseNotice("#ab #cd @who", NOW).hashtags.join(" ")') == "#ab #cd")
check("forms.gle 앞 https 자동 보완", run('parseNotice("제출: forms.gle/ABC123", NOW).links[0]') == "https://forms.gle/ABC123")
check("링크 라벨", run('linkLabel("https://forms.gle/ABC123")') == "📝 제출 폼 열기")

print("[8] 3-way 병합 — 옛날 화면이 최신 기록을 덮어쓰지 않는가")
ctx.eval("""
var base = [
  { id:'a', title:'A', deadline:'2026-11-15', missions:[{id:'m1',text:'x',done:false}], updatedAt:1 },
  { id:'b', title:'B', deadline:'2026-11-29', missions:[], updatedAt:1 }
];
var server = [
  { id:'a', title:'A', deadline:'2026-11-15', missions:[{id:'m1',text:'x',done:true}], updatedAt:5 },
  { id:'b', title:'B', deadline:'2026-11-29', missions:[], updatedAt:1 },
  { id:'c', title:'C(다른 기기에서 추가)', deadline:'2026-12-01', missions:[], updatedAt:5 }
];
var stale = [
  { id:'a', title:'A', deadline:'2026-11-15', missions:[{id:'m1',text:'x',done:false}], updatedAt:1 },
  { id:'b', title:'B', deadline:'2026-11-29', missions:[], updatedAt:1 }
];
var mergedStale = mergeEntries(base, stale, server);
""")
check("옛 기기가 저장해도 새 항목 C 유지", run("(function(){var ids=mergedStale.map(function(e){return e.id;});return ids.indexOf('c')>=0;})()"))
check("다른 기기가 체크한 미션 유지", run("mergedStale[0].missions[0].done === true"))

ctx.eval("""
var mine = [
  { id:'a', title:'A 수정', deadline:'2026-11-16', missions:[{id:'m1',text:'x',done:true}], updatedAt:9 },
  { id:'b', title:'B', deadline:'2026-11-29', missions:[], updatedAt:1 }
];
var mergedMine = mergeEntries(base, mine, server);
""")
check("내 수정 우선 반영", run("mergedMine[0].title === 'A 수정'"))
check("내 미션 체크 반영", run("mergedMine[0].missions[0].done === true"))

check("내가 지운 항목은 지워짐", run("(function(){var m=mergeEntries(base, [{id:'a',title:'A',updatedAt:1}], server); return m.filter(function(e){return e.id==='b';}).length===0;})()"))
check("다른 기기 신규 항목은 살아남음", run("(function(){var m=mergeEntries([], [{id:'a',title:'A',updatedAt:1}], server); return m.length===3 && m.some(function(e){return e.id==='c';});})()"))
check("겹치는 항목은 하나로", run("(function(){var m=mergeEntries([], [{id:'a',title:'A',updatedAt:1}], server); return m.filter(function(e){return e.id==='a';}).length===1;})()"))

print("[9] 요약 문구")
check("찾은 항목 요약", run(f"parsedSummary(parse({json.dumps(WISDOM)})).join(', ')").startswith("제목, 제공처"))

print()
if fails:
    print(f"실패 {len(fails)}개: {fails}")
    sys.exit(1)
print("모든 테스트 통과 ✅")
