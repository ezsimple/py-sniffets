#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus

# .env 파일 로드
load_dotenv()

# SQLAlchemy 설정
Base = declarative_base()

class MinoCompanyScoreOnBlind(Base):
    """회사 평점 모델"""
    __tablename__ = 'MinoCompanyScoreOnBlind'
    
    company_name = Column(String, primary_key=True)
    company_score = Column(Float, nullable=False)
    company_info = Column(String, nullable=False)
    company_reviews = Column(String, nullable=True)
    company_review_summary = Column(String, nullable=True)
    reg_at = Column(DateTime, nullable=False)
    mod_at = Column(DateTime, nullable=False)

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        # 환경 변수에서 데이터베이스 연결 정보 가져오기
        host = os.getenv('PG_HOST')
        user = os.getenv('PG_USER')
        password = quote_plus(os.getenv('PG_PW'))  # 비밀번호 URL 인코딩
        database = os.getenv('PG_DB')
        
        # 데이터베이스 URL 생성
        db_url = f"postgresql://{user}:{password}@{host}/{database}"
        print(f"데이터베이스 연결 URL: {db_url}")
        
        # 엔진 생성
        engine = create_engine(db_url)
        
        # 테이블 생성 전 확인
        # print("테이블 생성 전 테이블 목록 확인...")
        # with engine.connect() as conn:
        #     result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        #     existing_tables = [row[0] for row in result]
        #     print(f"기존 테이블 목록: {existing_tables}")
        
        # 테이블 생성
        # print("테이블 생성 시도...")
        Base.metadata.create_all(engine)
        # print("테이블 생성 완료")
        
        # 테이블 생성 후 확인
        # print("테이블 생성 후 테이블 목록 확인...")
        # with engine.connect() as conn:
        #     result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        #     updated_tables = [row[0] for row in result]
        #     print(f"업데이트된 테이블 목록: {updated_tables}")
        
        # 세션 생성
        Session = sessionmaker(bind=engine)
        session = Session()
        
        return session
    except Exception as e:
        print(f"데이터베이스 연결 오류: {str(e)}")
        return None

def save_companies_to_db(json_file):
    """JSON 파일의 회사 정보를 PostgreSQL에 저장"""
    session = None
    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        if not companies:
            print("저장할 회사 정보가 없습니다.")
            return
        
        # 데이터베이스 연결
        session = get_db_connection()
        if not session:
            return
        
        # 현재 시간
        now = datetime.now()
        
        # 회사 정보 저장
        for company in companies:
            try:
                # 회사 정보 추출
                # print(f"\n[DEBUG] 처리 중인 회사 정보: {json.dumps(company, ensure_ascii=False, indent=2)}")
                # input()
                
                company_name = company['name']
                company_score = float(company['rating']) if company['rating'] != '정보 없음' else None
                
                # 회사 소개 정보 추출 및 포맷팅
                company_info = []
                if 'company_info' in company:
                    info = company['company_info']
                    if isinstance(info, dict):
                        if '홈페이지' in info:
                            company_info.append(f"홈페이지: {info['홈페이지']}")
                        if '업계' in info:
                            company_info.append(f"업계: {info['업계']}")
                        if '본사' in info:
                            company_info.append(f"본사: {info['본사']}")
                        if '설립' in info:
                            company_info.append(f"설립: {info['설립']}")
                        if '직원수' in info:
                            company_info.append(f"직원수: {info['직원수']}")
                        if '연봉정보' in info:
                            company_info.append(f"연봉정보: {info['연봉정보']}")
                    elif isinstance(info, str):
                        company_info.append(info)
                
                company_info_str = '\n'.join(company_info) if company_info else ''
                company_reviews = json.dumps(company.get('reviews', []), ensure_ascii=False)
                company_review_summary = company.get('review_summary', '')
                
                # print(f"[DEBUG] 추출된 정보:")
                # print(f"- 회사명: {company_name}")
                # print(f"- 평점: {company_score}")
                # print(f"- 소개: {company_info_str}")
                # print(f"- 리뷰 수: {len(json.loads(company_reviews)) if company_reviews else 0}")
                # print(f"- 요약: {company_review_summary[:100]}...")
                
                # 기존 회사 정보 조회
                existing_company = session.query(MinoCompanyScoreOnBlind).filter_by(company_name=company_name).first()
                
                if existing_company:
                    # 기존 회사 정보 업데이트
                    existing_company.company_score = company_score
                    existing_company.company_info = company_info_str
                    existing_company.company_reviews = company_reviews
                    existing_company.company_review_summary = company_review_summary
                    existing_company.mod_at = now
                    print(f"[INFO] 회사 정보 업데이트: {company_name}")
                else:
                    # 새로운 회사 정보 추가
                    new_company = MinoCompanyScoreOnBlind(
                        company_name=company_name,
                        company_score=company_score,
                        company_info=company_info_str,
                        company_reviews=company_reviews,
                        company_review_summary=company_review_summary,
                        reg_at=now,
                        mod_at=now
                    )
                    session.add(new_company)
                    print(f"[INFO] 새로운 회사 정보 추가: {company_name}")
                
            except Exception as e:
                print(f"[ERROR] 회사 정보 저장 중 오류 ({company_name}): {str(e)}")
                continue
        
        # 변경사항 저장
        session.commit()
        print("\n[INFO] 모든 회사 정보가 데이터베이스에 저장되었습니다.")
        
    except Exception as e:
        print(f"[ERROR] 데이터베이스 저장 중 오류: {str(e)}")
        if session:
            session.rollback()
    
    finally:
        if session:
            session.close()

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python save_to_db.py <JSON 파일 경로>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"파일을 찾을 수 없습니다: {json_file}")
        sys.exit(1)
    
    save_companies_to_db(json_file)

if __name__ == "__main__":
    main()