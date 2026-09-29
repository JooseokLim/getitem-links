#!/usr/bin/env python3
"""오늘의겟템 파이프라인 기록(data/records/*.md)을 읽어 index.html을 다시 생성한다.
새 제품이 추가되면 이 스크립트만 다시 실행하면 된다: python3 generate.py
"""
import re
import shutil
from pathlib import Path

SOURCE_ROOT = Path("/Users/jooseok/ClaudeCode/Study/shopping-shorts")
RECORDS_DIR = SOURCE_ROOT / "data/records"
THUMBS_SRC_DIR = SOURCE_ROOT / "output"

SITE_ROOT = Path(__file__).resolve().parent
THUMBS_DST_DIR = SITE_ROOT / "assets/thumbs"

# 낮은 번호일수록 먼저 만든 영상이라, 역순(최신 먼저)으로 노출한다.
def sort_key(path: Path) -> tuple:
    m = re.match(r"(\d+)", path.stem)
    return (int(m.group(1)) if m else 0, path.stem)


def parse_record(path: Path):
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"^- 제목:[ \t]*(.+)$", text, re.MULTILINE)
    link_m = re.search(r"^- 쿠팡 링크:[ \t]*(\S+)[ \t]*$", text, re.MULTILINE)
    if not title_m or not link_m:
        return None
    return {
        "id": path.stem,
        "title": title_m.group(1).strip(),
        "link": link_m.group(1).strip(),
    }


def main():
    THUMBS_DST_DIR.mkdir(parents=True, exist_ok=True)
    records = sorted(RECORDS_DIR.glob("*.md"), key=sort_key, reverse=True)

    items = []
    for path in records:
        item = parse_record(path)
        if item is None:
            print(f"skip (링크 없음): {path.name}")
            continue

        thumb_src = THUMBS_SRC_DIR / f"{item['id']}_thumbnail.png"
        if not thumb_src.exists():
            print(f"skip (썸네일 없음): {path.name}")
            continue
        thumb_name = f"{item['id']}.png"
        shutil.copyfile(thumb_src, THUMBS_DST_DIR / thumb_name)
        item["thumb"] = f"assets/thumbs/{thumb_name}"
        items.append(item)

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
