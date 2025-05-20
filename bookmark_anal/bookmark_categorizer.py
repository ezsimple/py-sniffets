import re
from collections import Counter, defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

INPUT_FILE = './valid_bookmarks.html'
OUTPUT_FILE = './bookmarks_categorized.html'

# 1. HTML 파싱 및 북마크 추출
def extract_bookmarks(html_path):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    bookmarks = []
    for a in soup.find_all('a', href=True):
        url = a['href']
        title = a.get_text(strip=True)
        bookmarks.append({'url': url, 'title': title})
    return bookmarks

# 2. 도메인 추출
def extract_domain(url):
    try:
        netloc = urlparse(url).netloc
        domain = re.sub(r'^www\.', '', netloc)
        parts = domain.split('.')
        # 한국형 도메인 처리: co.kr, or.kr, go.kr, ne.kr 등은 3단계까지 추출
        if len(parts) >= 3 and parts[-2] in ['co', 'or', 'go', 'ne'] and parts[-1] == 'kr':
            domain = '.'.join(parts[-3:])
        elif len(parts) > 2:
            domain = '.'.join(parts[-2:])
        return domain
    except Exception:
        return 'unknown'

# 3. 1차/2차 카테고리: 키워드 기반 분류
CATEGORY_KEYWORDS = [
    ("취업/이직", ["잡코리아", "사람인", "원티드", "이력서", "공고", "입사지원", "헤드헌터", "헤드헌팅", "커리어", "블라인드", "인크루트", "OKKY", "채용", "취업", "연봉", "경력"]),
    ("개발자료", ["GitHub", "코드", "Python", "React", "Java", "Spring", "Node", "VSCode", "API", "Docker", "Kubernetes", "NestJS", "TIL", "IntelliJ", "Android", "iOS", "프로그래밍", "개발자", "코딩", "LangChain", "Pandas", "Plotly", "OAuth", "Playwright", "PyTorch", "Jupyter", "JUSO.IO", "테크", "TDD", "OOP", "Refactoring", "디자인 패턴", "컴포넌트", "라이브러리", "모듈", "패키지", "프레임워크", "nomad", "ubuntu", "server", "redmine", "centos", "svn", "git", "sso", "데이터", "모니터링", "iot", "디지털", "데브옵스"]),
    ("AI/툴", ["AI", "ChatGPT", "Copilot", "GPT", "Ollama", "Codellama", "AI 도구", "AI Assistant", "AI 검색", "AI 활용", "AI 사업", "AI 웹서비스", "Deepseek", "Napkin AI", "Lilys AI", "Monica", "Mailtrap", "Obsidian", "RAG", "LangChain", "Copilot", "Chatbot", "AI 플랫폼"]),
    ("블로그/커뮤니티", ["블로그", "Tistory", "Brunch", "Velog", "Medium", "Forum", "커뮤니티", "Stack Overflow", "GeekNews", "Clien", "DevOcean", "TechBlog", "구루비", "OKKY", "Obsidian", "Cafe", "Naver Blog", "네이버 블로그", "티스토리"]),
    ("영상/유튜브", ["YouTube", "유튜브", "영상", "다시보기", "TV", "방송", "포트폴리오", "튜토리얼"]),
    ("뉴스/정보", ["뉴스", "정보", "설명", "가이드", "WikiDocs", "Wiki", "매거진", "설문조사", "뉴스데스크", "한국경제", "BizSpring", "FrontOverflow", "요즘IT", "TheoryDB"]),
    ("자격증/교육", ["자격증", "교육", "강의", "학습", "학원", "수업", "시험", "PWA", "Certification", "ProDS", "Data Scientist", "SQLD", "DAP", "ADP", "CKA", "강좌", "도장", "챌린지", "연수", "실습"]),
    ("쇼핑/생활", ["AliExpress", "쇼핑", "구매", "상품", "생활", "안경", "쿠팡", "G마켓", "옥션", "11번가", "네이버쇼핑", "직구", "Amazon", "eBay"]),
    ("기타", [])
]

# 1차 카테고리 분류 함수
def categorize_by_keyword(bookmarks, max_cat1=10):
    # 취업/이직 관련 도메인 목록
    job_domains = [
        'jobkorea.co.kr', 'saramin.co.kr', 'wanted.co.kr', 'incruit.com', 'teamblind.com',
        'okky.kr', 'jobs.okky.kr', 'blind.com', 'jobplanet.co.kr', 'jobis.co', 'peoplenjob.com'
    ]
    shopping_domains = [
        'coupang.com', 'gmarket.co.kr', '11st.co.kr', 'auction.co.kr', 'ssg.com', 'wemakeprice.com',
        'interpark.com', 'aliexpress.com', 'amazon.com', 'ebay.com', 'street.co.kr', 'musinsa.com',
        'smartstore.naver.com', 'store.naver.com', 'naver.com', 'lotteon.com', 'shinsegaemall.ssg.com',
        'tmon.co.kr', 'cjmall.com', 'hmall.com', 'danawa.com', 'yes24.com', 'bookcube.com', 'g9.co.kr'
    ]
    dev_domains = [
        'stackoverflow.com', 'github.com', 'velog.io', 'tistory.com', 'medium.com', 'dev.to',
        'geeksforgeeks.org', 'codepen.io', 'hashnode.dev', 'programmers.co.kr', 'okky.kr',
        'brunch.co.kr', 'notion.so', 'wikidocs.net', 'd2.naver.com', 'blog.naver.com', 'blogspot.com',
        'kaggle.com', 'leetcode.com', 'baekjoon.net', 'inflearn.com', 'udemy.com', 'coursera.org',
        'edwith.org', 'school.programmers.co.kr', 'docs.python.org', 'npmjs.com', 'pypi.org', 'readthedocs.io'
    ]
    def find_cat1(title, url):
        domain = extract_domain(url)
        if domain in shopping_domains:
            return "쇼핑/생활"
        if domain in job_domains:
            return "취업/이직"
        if domain in dev_domains:
            return "개발자료"
        # '프리랜서' 키워드 우선 분류
        if '프리랜서' in title or '프리랜서' in url:
            return "취업/이직"
        for cat1, keywords in CATEGORY_KEYWORDS:
            for kw in keywords:
                if kw.lower() in title.lower() or kw.lower() in url.lower():
                    return cat1
        return "기타"
    # 1차 카테고리 지정
    for b in bookmarks:
        b['cat1'] = find_cat1(b['title'], b['url'])
    # 실제로 사용된 1차 카테고리만 추출(최대 max_cat1)
    used_cats = [b['cat1'] for b in bookmarks]
    cat1_counts = Counter(used_cats)
    top_cat1s = [cat for cat, _ in cat1_counts.most_common(max_cat1)]
    # 기타 처리
    for b in bookmarks:
        if b['cat1'] not in top_cat1s:
            b['cat1'] = "기타"
    return bookmarks, top_cat1s

# 2차 카테고리: 1차 카테고리 내 세부 키워드 자동 분류
# 2차 카테고리 추출 시 의미 없는 단어(불용어) 및 짧은 단어 필터링
STOPWORDS = set([
    'com', 'net', 'org', 'kr', 'co', 'to', 'js', 'for', 'www', 'google', 'naver', 'www2', 'html', 'php',
    'and', 'the', 'with', 'from', 'about', 'this', 'that', 'are', 'was', 'you', 'your', 'http', 'https',
    'kibana', 'package', 'test', 'sample', 'temp', 'main', 'project', 'service', 'home', 'index', 'default', 'null', 'undefined', 'etc'
])

def is_valid_cat2_word(w):
    w = w.lower()
    if w in STOPWORDS:
        return False
    if re.fullmatch(r'[a-zA-Z]+', w):
        return len(w) > 4
    if re.fullmatch(r'[가-힣]+', w):
        return len(w) > 1
    return False

def categorize_secondary(bookmarks):
    # 각 1차 카테고리별 대표 키워드(상위 N개)를 2차 카테고리로 지정
    N = 5
    cat2_dict = {}
    for cat1, _ in CATEGORY_KEYWORDS:
        titles = [b['title'] for b in bookmarks if b['cat1'] == cat1]
        # 제목에서 단어 빈도 집계(짧은 단어, 특수문자 제외)
        words = []
        for t in titles:
            words += re.findall(r'[\w가-힣]{2,}', t)
        counter = Counter([w.lower() for w in words if is_valid_cat2_word(w.lower())])
        cat2_dict[cat1] = [w for w, _ in counter.most_common(N)]
    # 북마크별 2차 카테고리 지정
    for b in bookmarks:
        title = b['title']
        cat1 = b['cat1']
        found = [w for w in cat2_dict.get(cat1, []) if w in title.lower()]
        b['cat2'] = found[0] if found else ''
    return bookmarks

# 5. 크롬 호환 북마크 HTML 생성
def generate_chrome_bookmarks(bookmarks, cat1_list):
    html = ['<!DOCTYPE NETSCAPE-Bookmark-file-1>']
    html.append('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">')
    html.append('<TITLE>Bookmarks</TITLE>')
    html.append('<H1>Bookmarks</H1>')
    html.append('<DL><p>')
    for cat1 in cat1_list + ['기타']:
        html.append(f'  <DT><H3>{cat1}</H3>')
        html.append('  <DL><p>')
        cat1_bms = [b for b in bookmarks if b['cat1'] == cat1]
        # 2차 카테고리별 그룹핑
        cat2_groups = defaultdict(list)
        for b in cat1_bms:
            cat2_groups[b['cat2']].append(b)
        for cat2, items in cat2_groups.items():
            if cat2:
                html.append(f'    <DT><H3>{cat2}</H3>')
                html.append('    <DL><p>')
            for b in items:
                html.append(f'      <DT><A HREF="{b["url"]}" ADD_DATE="0">{b["title"]}</A>')
            if cat2:
                html.append('    </DL><p>')
        html.append('  </DL><p>')
    html.append('</DL><p>')
    return '\n'.join(html)

if __name__ == '__main__':
    bookmarks = extract_bookmarks(INPUT_FILE)
    bookmarks, cat1_list = categorize_by_keyword(bookmarks, max_cat1=10)
    bookmarks = categorize_secondary(bookmarks)
    html = generate_chrome_bookmarks(bookmarks, cat1_list)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'북마크 분류 및 변환 완료: {OUTPUT_FILE}')
