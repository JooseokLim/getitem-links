#!/usr/bin/env python3
"""오늘의겟템 파이프라인 기록(data/records/*.md)을 읽어 index.html을 다시 생성한다.
새 제품이 추가되면 이 스크립트만 다시 실행하면 된다: python3 generate.py

2026-11-13 — SOURCE_ROOT가 shopping-shorts 하나로 고정돼 있어서, synergy-shorts(새
파이프라인, 같은 "오늘의겟템" 채널 제품을 만드는 두 번째 프로젝트)의 제품은 처음부터
이 페이지에 반영될 방법이 없었다(생성 스크립트가 그 폴더를 아예 모름). 두 프로젝트 다
읽도록 SOURCE_ROOTS 리스트로 바꿨다. 두 프로젝트의 레코드 파일명(id)이 전부 달라서
(실측 확인: 겹치는 stem 없음) 썸네일 복사 시 덮어쓰기 충돌은 없다.

정렬 기준도 "파일명 앞 숫자"에서 "레코드의 저장일시"로 바꿨다 — 두 프로젝트를 합치면
번호 체계가 서로 독립적이라(예: synergy-shorts의 05_octolock이 shopping-shorts의
05_bathroomtable과 06_Cabinet 사이에 끼는 식), 숫자만으로는 실제 생성 순서를 더 이상
보장할 수 없기 때문.
"""
import datetime
import re
import shutil
from pathlib import Path

SOURCE_ROOTS = [
    Path("/Users/jooseok/ClaudeCode/Study/shopping-shorts"),
    Path("/Users/jooseok/ClaudeCode/Study/synergy-shorts"),
]

SITE_ROOT = Path(__file__).resolve().parent
THUMBS_DST_DIR = SITE_ROOT / "assets/thumbs"


def parse_record(path: Path):
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"^- 제목:[ \t]*(.+)$", text, re.MULTILINE)
    link_m = re.search(r"^- 쿠팡 링크:[ \t]*(\S+)[ \t]*$", text, re.MULTILINE)
    ts_m = re.search(r"^- 저장일시:[ \t]*(.+)$", text, re.MULTILINE)
    if not title_m or not link_m:
        return None
    saved_at = None
    if ts_m:
        try:
            saved_at = datetime.datetime.strptime(ts_m.group(1).strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    return {
        "id": path.stem,
        "title": title_m.group(1).strip(),
        "link": link_m.group(1).strip(),
        "saved_at": saved_at,
    }


def main():
    THUMBS_DST_DIR.mkdir(parents=True, exist_ok=True)

    parsed = []
    for source_root in SOURCE_ROOTS:
        records_dir = source_root / "data/records"
        thumbs_src_dir = source_root / "output"
        for path in sorted(records_dir.glob("*.md")):
            item = parse_record(path)
            if item is None:
                print(f"skip (링크 없음): {path.name}")
                continue

            thumb_src = thumbs_src_dir / f"{item['id']}_thumbnail.png"
            if not thumb_src.exists():
                print(f"skip (썸네일 없음): {path.name}")
                continue
            thumb_name = f"{item['id']}.png"
            shutil.copyfile(thumb_src, THUMBS_DST_DIR / thumb_name)
            item["thumb"] = f"assets/thumbs/{thumb_name}"
            parsed.append(item)

    # 저장일시가 있으면 최신순, 없으면(예전 레코드) 맨 뒤로 보낸다.
    items = sorted(
        parsed,
        key=lambda it: it["saved_at"] or datetime.datetime.min,
        reverse=True,
    )

    cards = "\n".join(
        f'''      <a class="card" href="{it['link']}" target="_blank" rel="noopener noreferrer sponsored">
        <img src="{it['thumb']}" alt="{it['title']}" loading="lazy">
        <div class="card-body">
          <p class="title">{it['title']}</p>
          <span class="cta">쿠팡에서 보기 →</span>
        </div>
      </a>'''
        for it in items
    )

    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>오늘의겟템 · 상품 링크</title>
<style>
  :root {{
    --bg: #0f1115;
    --card-bg: #1a1d24;
    --text: #f5f5f5;
    --sub: #a8adb8;
    --accent: #ffd60a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    padding: 32px 16px 64px;
  }}
  header {{
    text-align: center;
    margin-bottom: 28px;
  }}
  header h1 {{
    font-size: 22px;
    margin: 0 0 6px;
  }}
  header p {{
    margin: 0;
    color: var(--sub);
    font-size: 14px;
  }}
  .list {{
    max-width: 420px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .card {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: var(--card-bg);
    border-radius: 14px;
    padding: 10px;
    text-decoration: none;
    color: inherit;
  }}
  .card img {{
    width: 72px;
    height: 72px;
    object-fit: cover;
    border-radius: 10px;
    flex-shrink: 0;
  }}
  .card-body {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 0;
  }}
  .title {{
    margin: 0;
    font-size: 15px;
    line-height: 1.35;
  }}
  .cta {{
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
  }}
  footer {{
    max-width: 420px;
    margin: 32px auto 0;
    color: var(--sub);
    font-size: 11px;
    text-align: center;
    line-height: 1.6;
  }}
</style>
</head>
<body>
  <header>
    <h1>오늘의겟템</h1>
    <p>영상에서 본 제품, 여기서 찾아 들어가세요</p>
  </header>
  <div class="list">
{cards}
  </div>
  <footer>
    이 페이지의 일부 링크는 쿠팡 파트너스 활동의 일환으로,<br>이에 따른 일정액의 수수료를 제공받을 수 있습니다.
  </footer>
</body>
</html>
"""
    (SITE_ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"generated index.html with {len(items)} items")


if __name__ == "__main__":
    main()
