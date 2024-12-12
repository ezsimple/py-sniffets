from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/skill')
    def skill_tree():
        return render_template('skill.html')

    @app.route('/projects')
    def projects():
        personal_projects = [
            {
                'title': '리쿠르트 통계',
                'description': '월간 직원연락망.xls 분석으로 만든 통계용 챠트',
                'tech': 'Flask, pandas, matplotlib, seaborn',
                'image': 'image/recrute-thumbnail.png',
                'url': 'https://a1.mkeasy.kro.kr/hr_list'
            },
            {
                'title': '파일 서버',
                'description': '개인용 파일 서버 및 SSO 인증 처리',
                'tech': 'FastAPI, pydantic, keycloak, cookie, redis, middleware',
                'image': 'image/file-server-thumbnail.png',
                'url': 'https://a1.mkeasy.kro.kr/v1'
            },
            {
                'title': '명언 카드',
                'description': '명언 API 서버 구현, 한글 해석 및 공유기능 제공',
                'tech': 'FastAPI, SQLAlchemy, PostgreSQL, websocket, mqtt, deep-L translator',
                'image': 'image/famous-quotes-thumbnail.png',
                'url': 'https://a1.mkeasy.kro.kr/chat/'
            },
            {
                'title': '송악읍 과거 날씨',
                'description': '공공데이터 시계열 자료 사용, 10년치(380,436건)',
                'tech': '고속 데이터 전처리, FastAPI, pandas, SQLAlchemy, PostgreSQL, vega-lite',
                'image': 'image/past-weather-thumbnail.png',
                'url': 'https://a1.mkeasy.kro.kr/past-weather'
            },
        # ... 더 많은 프로젝트
        ]
    
        participated_projects = [
            # ... 참여 프로젝트 목록
            {
                'title': '한국렌탈',
                'description': '렌탈고객정보사이트, 기존 .NET 서비스를 java로 개편, 사내 ERP 연동, BackOffice 제공',
                'tech': 'Springboot, Thymeleaf, MyBatis, MSSQL, jQuery, dxGrid(devExpress)',
                'image': 'image/krsmart.png',
                'url': 'https://www.krsmart.com'
            },
            {
                'title': 'e커머스',
                'description': '상품관리, 통계, 정산 기능 개발',
                'tech': 'Springboot, JPA, QueryDSL, MyBatis, MySQL, CQRS',
                'image': 'image/oround.png',
                'url': 'https://oround.com'
            },
        ]
        return render_template('card.html', 
                            personal_projects=personal_projects,
                            participated_projects=participated_projects)

    return app

if __name__ == '__main__':
    app = create_app()  # create_app 함수 호출
    app.run(debug=True)  # 디버그 모드에서 실행