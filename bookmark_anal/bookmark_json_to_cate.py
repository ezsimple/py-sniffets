import re
import json
from collections import Counter, defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# 1차 카테고리: 키워드 기반 분류
# 1차 카테고리 : 취업/이직, 개발자료, AI/툴, 블로그/커뮤니티, 영상/유튜브, 뉴스/정보, 자격증/교육, 쇼핑/생활, 기타
# 1차 카테고리: 정규표현식 기반 분류
DEPTH1_CATEGORIES = [
    ("취업/이직", [
        r"(잡코리아|잡플래닛|OKKY|회사|투자|IT노조|사람인|원티드|이력서|공고|입사지원|헤드헌터|프리랜서|정규직|계약직|개발자|버는|고용|채용|노동|연봉|복지|커리어|블라인드|인크루트|OKKY|채용|취업|연봉|경력|면접|면접준비|면접질문|면접답변|면접경험|면접후기|면접팁)"
    ]),
    ("개발자료", [
        r"(PWA|Vue|D3|OpenADR|Scala|Django|장고|MinIO|k8s|n8n|Secret|Cross|Origin|String|산딸기|오라클|Rasberrypi|eGov|kubernetes|geoip|TDD|OOP|JDK|CSS|Vagrant|Ansible|OpenJDK|프론트엔드|백엔드|Rust|러스트|파이썬|Python|frontend|backend|AWS|Azure|IBM|Cloud|Keycloak|MyBatis|iBatis|Nexus|TypeScript|Kafka|bootstrap|Grid|HTML|Responsive|Web|Design|Maven|Gradle|Docker|도커|Effective|Svelte|스벨트|JPA|QueryDSL|SPA|CRA|SSR|CSR|storm.js|Netty|Socket|Elastic|DBCP|Ajax|Query|TLS|CWE|Storybook|Babel|ECMAScript|Chart.js|Next.js|React|MariaDB|MySQL|Oracle|MSSQL|PostgreSQL|elasticSearch|mongoDB|몽고DB|Client|Cloudflare|Stack|Overflow|GitHub|딥러닝|구루비|gloovy|코드|Python|React|Java|Spring|Node|VSCode|API|Docker|Kubernetes|NestJS|TIL|IntelliJ|Android|iOS|프로그래밍|코딩|LangChain|Pandas|Plotly|OAuth|Playwright|PyTorch|Jupyter|JUSO\.IO|테크|TDD|OOP|Refactoring|디자인\s패턴|컴포넌트|라이브러리|모듈|패키지|프레임워크|nomad|ubuntu|server|redmine|centos|svn|git|sso|데이터|모니터링|iot|디지털|데브옵스)"
    ]),
    ("AI/툴", [
        r"(AI|지피터스|bolt|Firebase\sStudio|Artificial\sIntelligence|Machine\sLearning|Deep\sLearning|Perplexity|ChatGPT|GPT-4|GPT-3\.5|GPT-3|Copilot|GitHub\sCopilot|GPT|Ollama|Codellama|AI\s도구|AI\sAssistant|AI\s검색|AI\s활용|AI\s사업|AI\s웹서비스|Deepseek|Napkin\sAI|Lilys\sAI|Monica|Mailtrap|Obsidian|RAG|LangChain|Chatbot|AI\s플랫폼|LLM|Large\sLanguage\sModel|Transformer|BERT|RoBERTa|T5|GPT-2|GPT-J|GPT-Neo|GPT-NeoX|Claude|Claude\s2|Claude\s3|Claude\sInstant|Claude\s3\.5|Claude\s4|Claude\s5|Claude\s6|Claude\s7|Claude\s8|Claude\s9|Claude\s10|Claude\s11|Claude\s12|Claude\s13|Claude\s14|Claude\s15|Claude\s16|Claude\s17|Claude\s18|Claude\s19|Claude\s20)"
    ]),
    ("블로그/커뮤니티", [
        r"(블로그|Tistory|Brunch|Velog|Medium|Forum|커뮤니티|GeekNews|DevOcean|TechBlog|Obsidian|Cafe|Naver\sBlog|네이버\s블로그|티스토리)"
    ]),
    ("영상/유튜브", [
        r"(YouTube|유튜브|영상|다시보기|TV|방송|포트폴리오|튜토리얼)"
    ]),
    ("뉴스/정보", [
        r"(뉴스|정보|설명|가이드|WikiDocs|Wiki|매거진|설문조사|뉴스데스크|한국경제|BizSpring|FrontOverflow|요즘IT|TheoryDB)"
    ]),
    ("자격증/교육", [
        r"(자격증|교육|강의|학습|학원|수업|시험|Certification|ProDS|Data\sScientist|SQLD|DAP|ADP|ADsP|준전문가|CKA|강좌|도장|챌린지|연수|실습)"
    ]),
    ("쇼핑/생활", [
        r"(AliExpress|쇼핑|구매|상품|생활|안경|쿠팡|G마켓|옥션|11번가|네이버쇼핑|직구|Amazon|eBay)"
    ]),
    ("기타", [])
]
def make_depth1_by_keyword(title):
    # 정규표현식으로 카테고리 매칭
    for category, patterns in DEPTH1_CATEGORIES:
        for pattern in patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return category
    return "기타"


# 도메인 추출 함수
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
# 도메인 분류
JOB_DOMAINS = set([
    'jobkorea.co.kr', 'saramin.co.kr', 'wanted.co.kr', 'incruit.com', 'teamblind.com',
    'okky.kr', 'jobs.okky.kr', 'blind.com', 'jobplanet.co.kr', 'jobis.co', 'peoplenjob.com'
])
SHOPPING_DOMAINS = set([
    'coupang.com', 'gmarket.co.kr', '11st.co.kr', 'auction.co.kr', 'ssg.com', 'wemakeprice.com',
    'interpark.com', 'aliexpress.com', 'amazon.com', 'ebay.com', 'street.co.kr', 'musinsa.com',
    'smartstore.naver.com', 'store.naver.com', 'naver.com', 'lotteon.com', 'shinsegaemall.ssg.com',
    'tmon.co.kr', 'cjmall.com', 'hmall.com', 'danawa.com', 'yes24.com', 'bookcube.com', 'g9.co.kr',
    'coocha.co.kr/'
])
DEV_DOMAINS = set([
    'stackoverflow.com', 'github.com', 'velog.io', 'tistory.com', 'medium.com', 'dev.to',
    'geeksforgeeks.org', 'codepen.io', 'hashnode.dev', 'programmers.co.kr', 'okky.kr',
    'notion.so', 'wikidocs.net', 'd2.naver.com', 
    'kaggle.com', 'leetcode.com', 'baekjoon.net', 'inflearn.com', 'udemy.com', 'coursera.org',
    'edwith.org', 'school.programmers.co.kr', 'docs.python.org', 'npmjs.com', 'pypi.org', 'readthedocs.io'
])

# 카테고리 추출 시 의미 없는 단어(불용어) 및 짧은 단어 필터링
STOP_WORDS = set([
    'com', 'net', 'org', 'kr', 'co', 'to', 'js', 'for', 'www', 'google', 'naver', 'www2', 'html',
    'and', 'the', 'with', 'from', 'about', 'this', 'that', 'are', 'was', 'you', 'your', 'http', 'https',
    'package', 'test', 'sample', 'temp', 'main', 'project', 'service', 'home', 'index', 'default', 'null', 'undefined', 'etc'
])

# ./parsed_bookmarks.json 파일을 읽어와서 구현된 함수들을 사용하여 카테고리 분류를 수행하고 결과를 ./parsed_categorized.json 파일로 저장
def make_depth1_using_bookmarks():
    # JSON 파일 읽기
    with open('./parsed_bookmarks.json', 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)
    
    # 분류된 북마크 저장할 리스트
    categorized_bookmarks = []
    
    for bookmark in bookmarks:
        # 기본 정보 복사
        categorized_bookmark = bookmark.copy()
        
        # URL에서 도메인 추출
        domain = extract_domain(bookmark['url'])
        
        # 도메인 기반 카테고리 분류
        domain_category = "기타"
        if domain in JOB_DOMAINS:
            domain_category = "취업/이직"
        elif domain in SHOPPING_DOMAINS:
            domain_category = "쇼핑/생활"
        elif domain in DEV_DOMAINS:
            domain_category = "개발자료"
        
        # 키워드 기반 카테고리 분류
        keyword_category = make_depth1_by_keyword(bookmark['title'])
        
        # 도메인과 키워드 분류 결과 중 더 구체적인 카테고리 선택
        if keyword_category != "기타":
            category = keyword_category
        else:
            category = domain_category
        
        # 카테고리 정보 추가
        categorized_bookmark['depth1'] = category
        
        # 분류된 북마크 저장
        categorized_bookmarks.append(categorized_bookmark)
    
    # 결과 저장
    with open('./parsed_categorized.json', 'w', encoding='utf-8') as f:
        json.dump(categorized_bookmarks, f, ensure_ascii=False, indent=2)
    
    # 각 카테고리별 분류 통계 출력
    category_counter = Counter([b['depth1'] for b in categorized_bookmarks])
    print("\n카테고리 분류 결과:")
    for cat, count in category_counter.most_common():
        print(f"{cat}: {count}개")
    
    print(f"\n총 {len(categorized_bookmarks)}개의 북마크가 분류되었습니다.")

if __name__ == "__main__":
    make_depth1_using_bookmarks()