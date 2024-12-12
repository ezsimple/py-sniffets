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
        # ... 더 많은 프로젝트
        ]
    
        participated_projects = [
            # ... 참여 프로젝트 목록
        ]
        return render_template('card.html', 
                            personal_projects=personal_projects,
                            participated_projects=participated_projects)

    return app

if __name__ == '__main__':
    app = create_app()  # create_app 함수 호출
    app.run(debug=True)  # 디버그 모드에서 실행