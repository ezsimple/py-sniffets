import sys
import json
from bs4 import BeautifulSoup

def parse_chrome_bookmarks(html_path):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    bookmarks = []
    for a in soup.find_all('a', href=True):
        url = a['href']
        title = a.get_text(strip=True)

        # Empty title filtering
        if not title.strip():
            continue

        bookmarks.append({
            'url': url,
            'title': title
        })
    return bookmarks

def save_as_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python bookmark_to_json.py [북마크 html 파일 경로]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    json_file = "parsed_bookmarks.json"
    
    try:
        bookmarks = parse_chrome_bookmarks(html_file)
        save_as_json(bookmarks, json_file)
        print(f"북마크 JSON 파일 생성 완료: {json_file}")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        sys.exit(1)