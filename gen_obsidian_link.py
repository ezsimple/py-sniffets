#!/usr/bin/env python3
# coding: utf-8
# ---------------------------------------------------
# 옵시디언 자동 링크 생성기
# pip install nltk scikit-learn numpy chardet
# 
# 사용자의 옵시디언 볼트 경로 설정
# 사용법 : vault_path = "E:\\obsidian"  
# 주의 : 윈도우환경에서 테스트 되었음. 2025.05.07
# ---------------------------------------------------
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import chardet

# NLTK 리소스 다운로드 (처음 실행 시)
for resource in ['punkt_tab', 'punkt', 'stopwords']:
    try:
        nltk.data.find('tokenizers/punkt' if resource == 'punkt_tab' else f'corpora/{resource}')
    except LookupError:
        nltk.download(resource)

class ObsidianAutoLinker:
    def __init__(self, vault_path, similarity_threshold=0.3, max_links_per_file=5, 
                 exclude_folders=None, excluded_files=None):
        """
        옵시디언 자동 링크 생성기 초기화
        
        Args:
            vault_path: 옵시디언 볼트 경로
            similarity_threshold: 문서 간 유사도 임계값
            max_links_per_file: 파일당 최대 링크 수
            exclude_folders: 제외할 폴더 목록
            excluded_files: 제외할 파일 목록
        """
        self.vault_path = vault_path
        self.similarity_threshold = similarity_threshold
        self.max_links_per_file = max_links_per_file
        self.exclude_folders = exclude_folders or []
        self.excluded_files = excluded_files or []
        
        # 한국어 불용어 (stopwords) 리스트
        self.korean_stopwords = [
            '이', '그', '저', '것', '수', '등', '및', '에', '에서', '의', '을', '를',
            '이다', '또는', '그리고', '하지만', '그러나', '따라서', '때문에', '이러한',
            '그러한', '있다', '없다', '하다', '되다', '있는', '없는', '한다', '된다'
        ]
        self.stopwords = set(stopwords.words('english') + self.korean_stopwords)
        
        # 마크다운 파일 목록과 내용을 저장할 딕셔너리
        self.files = {}
        self.file_contents = {}
        self.tfidf_matrix = None
        self.vectorizer = None
        
    def is_excluded(self, file_path):
        """
        파일이나 폴더가 제외 목록에 있는지 확인
        """
        rel_path = os.path.relpath(file_path, self.vault_path)
        
        # 제외 폴더 확인
        for folder in self.exclude_folders:
            if rel_path.startswith(folder):
                return True
        
        # 제외 파일 확인
        if rel_path in self.excluded_files:
            return True
            
        return False
    
    def detect_encoding(self, file_path):
        """파일의 인코딩 감지"""
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                return result['encoding']
        except Exception:
            return 'utf-8'  # 기본값으로 UTF-8 사용
    
    def get_markdown_files(self):
        """
        옵시디언 볼트에서 모든 마크다운 파일을 찾아 목록화
        """
        for root, _, files in os.walk(self.vault_path):
            if self.is_excluded(root):
                continue
                
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    if not self.is_excluded(file_path):
                        rel_path = os.path.relpath(file_path, self.vault_path)
                        self.files[rel_path] = file_path
        
        print(f"{len(self.files)} 개의 마크다운 파일을 찾았습니다.")
        return self.files
    
    def preprocess_text(self, text):
        """
        텍스트 전처리: 토큰화, 불용어 제거
        """
        # 마크다운 링크 제거
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
        
        # 마크다운 서식 제거
        text = re.sub(r'[#*`_]+', '', text)
        
        # 특수문자 제거
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 토큰화
        tokens = word_tokenize(text.lower())
        
        # 불용어 제거
        filtered_tokens = [word for word in tokens if word not in self.stopwords]
        
        return ' '.join(filtered_tokens)
    
    def extract_file_contents(self):
        """모든 마크다운 파일의 내용 추출 및 전처리"""
        self.file_contents = {}
        
        for file in self.files:
            abs_path = self.files[file]
            try:
                # 여러 인코딩 시도
                encodings = ['utf-8', 'cp949', 'euc-kr', 'ascii']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
                            content = f.read()
                        break  # 성공하면 반복문 탈출
                    except Exception:
                        continue
                
                if content is None:
                    # 모든 인코딩 시도가 실패한 경우 기본값으로 UTF-8 사용
                    with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                
                # 전처리
                processed_content = self.preprocess_text(content)
                
                # 저장
                self.file_contents[file] = {
                    'original': content,
                    'processed': processed_content
                }
                
            except Exception as e:
                print(f"파일을 읽는 중 오류 발생: {file} - {e}")
                continue  # 오류가 발생해도 계속 진행
        
        print(f"{len(self.file_contents)} 개의 파일 내용을 처리했습니다.")
        return self.file_contents
    
    def create_tfidf_matrix(self):
        """
        TF-IDF 벡터화를 사용해 문서 간 유사도를 계산할 수 있는 행렬 생성
        """
        documents = []
        for file in self.files:
            if file in self.file_contents:
                documents.append(self.file_contents[file]['processed'])
        
        if not documents:
            print("처리된 문서가 없습니다.")
            return None
        
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        print("TF-IDF 행렬을 생성했습니다.")
        return self.tfidf_matrix
    
    def find_similar_documents(self):
        """
        코사인 유사도를 사용해 유사한 문서들을 찾음
        """
        similar_docs = {}
        backlinks = {}

        # 각 문서에 대해 유사한 문서 찾기
        for i, file in enumerate(self.files):
            if file not in self.file_contents:
                continue

            # 현재 문서와 다른 문서들 간의 유사도 계산
            similarities = cosine_similarity(
                self.tfidf_matrix[i:i+1], 
                self.tfidf_matrix
            ).flatten()

            # 유사도가 임계값 이상인 문서들 찾기
            similar_indices = np.where(similarities > self.similarity_threshold)[0]

            # 유사한 문서들 중에서 상위 n개만 선택
            similar_files = []
            for j in similar_indices:
                if j != i:  # 자기 자신 제외
                    other_file = list(self.files.keys())[j]
                    if other_file in self.file_contents:
                        similar_files.append(other_file)
                        # 백링크도 저장
                        if other_file not in backlinks:
                            backlinks[other_file] = []
                        backlinks[other_file].append(file)

            similar_docs[file] = similar_files

        return similar_docs, backlinks
    
    def create_backlinks(self, similar_docs):
        """
        양방향 링크 생성을 위한 역링크 목록 생성
        """
        backlinks = {file: [] for file in self.files}
        
        for file, similar_files in similar_docs.items():
            for similar_file, similarity in similar_files:
                backlinks[similar_file].append((file, similarity))
        
        # 각 파일의 역링크도 유사도 순으로 정렬하고 최대 개수 제한
        for file in backlinks:
            backlinks[file] = sorted(backlinks[file], key=lambda x: x[1], reverse=True)
            backlinks[file] = backlinks[file][:self.max_links_per_file]
        
        return backlinks
    
    def add_links_to_files(self, similar_docs, backlinks):
        """
        파일에 유사 문서에 대한 링크 추가
        """
        updated_files = []
        
        for file_path, similar_files in similar_docs.items():
            if not similar_files:
                continue
                
            abs_path = self.files[file_path]
            original_content = self.file_contents[file_path]['original']
            
            # 링크 섹션 생성
            links_section = "## 아웃링크\n\n"
            for similar_file in similar_files[:self.max_links_per_file]:
                # 파일 경로에서 파일명만 추출
                file_name = os.path.basename(similar_file)
                # 확장자 제거
                file_name = os.path.splitext(file_name)[0]
                links_section += f"- [[{file_name}]]\n"
            
            # 백링크 섹션 생성
            backlinks_section = ""
            if file_path in backlinks:
                backlinks_section = "\n## 백링크\n\n"
                for backlink in backlinks[file_path][:self.max_links_per_file]:
                    file_name = os.path.basename(backlink)
                    file_name = os.path.splitext(file_name)[0]
                    backlinks_section += f"- [[{file_name}]]\n"
            
            # 아웃링크 섹션 업데이트
            related_pattern = r'## 아웃링크\s*\n(.*?)(?=\n##|\Z)'
            backlinks_pattern = r'## 백링크\s*\n(.*?)(?=\n##|\Z)'
            
            # 아웃링크 섹션 업데이트
            if re.search(related_pattern, original_content, re.DOTALL):
                updated_content = re.sub(
                    related_pattern,
                    links_section,
                    original_content,
                    flags=re.DOTALL
                )
            else:
                updated_content = original_content + "\n\n" + links_section
            
            # 백링크 섹션 업데이트
            if backlinks_section and re.search(backlinks_pattern, updated_content, re.DOTALL):
                updated_content = re.sub(
                    backlinks_pattern,
                    backlinks_section,
                    updated_content,
                    flags=re.DOTALL
                )
            elif backlinks_section:
                updated_content += "\n\n" + backlinks_section
            
            # 파일 내용이 변경되었으면 저장
            if updated_content != original_content:
                try:
                    self.update_file(abs_path, updated_content)
                    updated_files.append(file_path)
                except Exception as e:
                    print(f"파일 업데이트 중 오류 발생: {file_path} - {e}")
        
        print(f"{len(updated_files)} 개의 파일이 업데이트되었습니다.")
        return updated_files

    def update_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)
        except Exception as e:
            print(f"파일 업데이트 중 오류 발생: {file_path} - {e}")
    
    def generate_links_report(self, similar_docs):
        """
        생성된 링크에 대한 보고서 생성
        """
        report = "# 옵시디언 자동 링크 생성 보고서\n\n"
        report += f"총 {len(self.files)}개의 마크다운 파일을 분석했습니다.\n\n"
        
        # 링크가 생성된 파일 수
        files_with_links = sum(1 for file, similar in similar_docs.items() if similar)
        report += "## 요약\n\n"
        report += f"- 분석된 파일: {len(self.files)}개\n"
        report += f"- 링크가 생성된 파일: {files_with_links}개\n"
        report += f"- 유사도 임계값: {self.similarity_threshold}\n"
        report += f"- 파일당 최대 링크 수: {self.max_links_per_file}\n\n"
        
        # 각 파일별 링크 정보
        report += "## 파일별 링크 정보\n\n"
        for file, similar_files in similar_docs.items():
            if similar_files:
                report += f"### {os.path.basename(file)}\n"
                report += "#### 유사 문서\n"
                for similar_file in similar_files:
                    report += f"- [[{os.path.basename(similar_file)}]]\n"
                report += "\n"
        
        return report
    
    def run(self):
        """
        자동 링크 생성 프로세스 실행
        """
        print("옵시디언 자동 링크 생성기를 시작합니다...")
        
        # 1. 마크다운 파일 찾기
        self.get_markdown_files()
        print(f"{len(self.files)} 개의 마크다운 파일을 찾았습니다.")
        
        # 2. 파일 내용 추출
        self.extract_file_contents()
        print(f"{len(self.file_contents)} 개의 파일 내용을 처리했습니다.")
        
        # 3. TF-IDF 행렬 생성
        self.create_tfidf_matrix()
        
        # 4. 유사한 문서 찾기 (이제 backlinks도 함께 반환)
        similar_docs, backlinks = self.find_similar_documents()
        
        # 5. 파일에 링크 추가
        updated_files = self.add_links_to_files(similar_docs, backlinks)
        
        # 6. 보고서 생성
        report = self.generate_links_report(similar_docs)
        report_path = os.path.join(self.vault_path, "자동_링크_생성_보고서.md")
        
        try:
            self.update_file(report_path, report)
            print(f"보고서가 생성되었습니다: {report_path}")
        except Exception as e:
            print(f"보고서 생성 중 오류 발생: {e}")
        
        print("옵시디언 자동 링크 생성기를 종료합니다.")
        return updated_files

# 사용 예시
if __name__ == "__main__":
    vault_path = "E:\\obsidian"  # 사용자의 옵시디언 볼트 경로로 변경
    
    # 제외할 폴더와 파일 목록 설정
    exclude_folders = [
        "templates",  # 템플릿 폴더
        ".obsidian",  # 옵시디언 설정 폴더
        "첨부 파일"   # 첨부 파일 폴더
    ]
    
    excluded_files = [
        "index.md",  # 인덱스 파일
        "README.md"  # README 파일
    ]
    
    # 자동 링크 생성기 초기화 및 실행
    auto_linker = ObsidianAutoLinker(
        vault_path=vault_path,
        similarity_threshold=0.3,  # 유사도 임계값 (0.0 ~ 1.0)
        max_links_per_file=5,      # 파일당 최대 링크 수
        exclude_folders=exclude_folders,
        excluded_files=excluded_files
    )
    
    # 실행
    updated_files = auto_linker.run()