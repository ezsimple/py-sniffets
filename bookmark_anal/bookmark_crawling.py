import json
import requests
from bs4 import BeautifulSoup
import time
import logging

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from langdetect import detect
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Rate limiting configuration
MIN_WAIT = 1  # Minimum wait time between requests (seconds)
MAX_RETRIES = 1  # Maximum number of retries for failed requests

def summarize_text(content, ratio=0.2, method='textrank', min_length=40, max_length=500):
    """
    사용 예:
    summary = summarize_text(content, ratio=0.2)

    텍스트 요약 함수 - 여러 방법 지원
    
    Args:
        content (str): 요약할 원본 텍스트
        ratio (float): 원본 대비 요약 비율 (0.0~1.0)
        method (str): 요약 방법 ('lexrank', 'luhn', 'lsa', 'textrank', 'bert')
        min_length (int): 최소 요약 길이
        max_length (int): 최대 요약 길이
        
    Returns:
        str: 요약된 텍스트
    """
    if not content or len(content) < min_length:
        return content  # 텍스트가 너무 짧으면 그대로 반환
        
    # 최대 길이 계산 (비율 기반)
    calculated_max = min(max_length, int(len(content) * ratio))
    if calculated_max < min_length:
        calculated_max = min_length
    
    try:
        if method == 'lexrank' or method == 'textrank' or method == 'luhn' or method == 'lsa':
            # sumy 라이브러리 사용 (여러 알고리즘 지원)
            # 언어 감지 시도
            try:
                language = detect(content[:5000])
                if language not in ['ko', 'en']:  # 지원하는 언어가 아니면 영어로 가정
                    language = 'en'
            except:
                language = 'en'  # 기본값은 영어
                
            parser = PlaintextParser.from_string(content, Tokenizer(language))
            stemmer = Stemmer(language)
            
            if method == 'lexrank':
                summarizer = LexRankSummarizer(stemmer)
            elif method == 'luhn':
                summarizer = LuhnSummarizer(stemmer)
            elif method == 'lsa':
                summarizer = LsaSummarizer(stemmer)
            else:  # textrank
                summarizer = TextRankSummarizer(stemmer)
                
            summarizer.stop_words = get_stop_words(language)
            
            # 문장 수 계산 (대략적으로 비율에 맞게)
            sentence_count = max(1, int(len(content.split('. ')) * ratio))
            
            # 요약 생성
            summary_sentences = summarizer(parser.document, sentence_count)
            summary = ' '.join([str(sentence) for sentence in summary_sentences])
            
            # 길이 제한 적용
            if len(summary) > calculated_max:
                summary = summary[:calculated_max].rsplit(' ', 1)[0] + '...'
                
            return summary
                
    except Exception as e:
        print(f"요약 처리 중 오류 발생: {e}")
        # 간단한 대체 방법: 처음 몇 문장 추출
        sentences = content.split('. ')
        sentence_count = max(1, int(len(sentences) * ratio))
        simple_summary = '. '.join(sentences[:sentence_count]) + '.'
        
        # 길이 제한 적용
        if len(simple_summary) > calculated_max:
            simple_summary = simple_summary[:calculated_max].rsplit(' ', 1)[0] + '...'
            
        return simple_summary


def get_content(url):
    """Get content from URL with error handling and rate limiting"""
    retries = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # PDF 파일의 경우 크롤링하지 않음
    if url.endswith('.pdf'):
        logging.info(f"Skipping PDF: {url}")
        return None
    
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # 올바른 인코딩 감지
            if 'charset' in response.headers.get('content-type', '').lower():
                detected_encoding = response.headers['content-type'].split('=')[-1]
            else:
                detected_encoding = response.apparent_encoding
            if detected_encoding.lower() == 'euc-kr':
                detected_encoding = 'cp949'
            response.encoding = detected_encoding

            # Extract content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = ' '.join(lines)

            try:
                # 문서 요약 라이브러리 사용
                # 20%의 내용만 요약
                summary = summarize_text(content, ratio=0.2)
                return summary if summary else content[:2000]
            except:
                return content[:2000]
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error fetching {url}: {str(e)}")
            retries += 1
            time.sleep(MIN_WAIT * (2 ** retries))  # Exponential backoff
            
    return None

def append_to_json_file(data, file_path):
    """Append data to JSON file while maintaining valid JSON format"""
    try:
        # Read existing data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        
        # Add new data
        existing_data.append(data)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logging.error(f"Error appending to JSON file: {str(e)}")
        raise

def main():
    # Load bookmarks
    INPUT_FILE = 'parsed_bookmarks.json'
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)
    
    total_bookmarks = len(bookmarks)
    
    save_file_path = 'parsed_crawling.json'
    existing_urls = set()
    try:
        with open(save_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_urls = set(item['url'] for item in existing_data)
    except FileNotFoundError:
        logging.info(f"File not found: {save_file_path}")
    
    for i, bookmark in enumerate(bookmarks):
        url = bookmark['url']
        title = bookmark['title']
        if url in existing_urls:
            logging.info(f"Skipping existing URL: {url}")
            logging.info(f"Progress: {progress:.1f}% ({i+1}/{total_bookmarks})")
            continue

        try:
            content = get_content(url)
            if content:
                data = {
                    'url': url,
                    'title': title,
                    'content': content
                }
                append_to_json_file(data, save_file_path)
                logging.info(f"Successfully crawled and saved: {url}")
                
        except Exception as e:
            logging.error(f"Error processing bookmark {i}: {str(e)}")
        finally:
            # Show progress
            progress = (i + 1) / total_bookmarks * 100
            logging.info(f"Progress: {progress:.1f}% ({i+1}/{total_bookmarks})")
        
        # Rate limiting
        time.sleep(MIN_WAIT)
    
    logging.info("Crawling completed")

if __name__ == "__main__":
    main()