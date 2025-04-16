from flask import Flask, render_template  # Flask 웹 프레임워크와 템플릿 렌더링 기능을 임포트합니다.
import yaml  # YAML 파일을 파싱하기 위해 yaml 모듈을 임포트합니다.
import os  # 운영 체제와 상호작용하기 위해 os 모듈을 임포트합니다.
import requests  # HTTP 요청을 보내기 위해 requests 모듈을 임포트합니다.
import time  # 현재 시간을 가져오기 위해 time 모듈을 임포트합니다.

def load_projects():
    """
    config 디렉토리 내의 projects.yml 파일을 로드하여 프로젝트 데이터를 반환합니다.
    파일이 없거나 파싱에 실패할 경우 기본값을 반환합니다.
    """
    # 현재 파일의 디렉토리 경로를 가져옵니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # projects.yml 파일의 경로를 생성합니다.
    yaml_path = os.path.join(current_dir, 'config', 'projects.yml')

    try:
        # projects.yml 파일을 읽고 파싱합니다.
        with open(yaml_path, 'r', encoding='utf-8') as file:
            projects = yaml.safe_load(file)
        return projects
    except FileNotFoundError:
        # 파일이 없을 경우 에러 메시지를 출력하고 기본값을 반환합니다.
        print(f"Error: projects.yml file not found at {yaml_path}")
        return {"personal_projects": [], "participated_projects": []}
    except yaml.YAMLError as e:
        # YAML 파싱에 실패할 경우 에러 메시지를 출력하고 기본값을 반환합니다.
        print(f"Error parsing YAML file: {e}")
        return {"personal_projects": [], "participated_projects": []}

def get_past_weather_count():
    """
    과거 날씨 데이터의 총 개수를 가져와서 포맷팅된 문자열로 반환합니다.
    요청에 실패할 경우 기본값을 반환합니다.
    """
    try:
        # 과거 날씨 데이터의 총 개수를 가져오는 API 요청을 보냅니다.
        response = requests.get('https://a1.mkeasy.kro.kr/past-weather/api/total_count')
        response.raise_for_status()  # 응답이 실패한 경우 예외를 발생시킵니다.
        count = response.json().get('total_count', '0')  # 응답에서 총 개수를 가져옵니다.
        return '{:,}'.format(int(count))  # 숫자를 천 단위로 포맷팅하여 반환합니다.
    except (requests.RequestException, ValueError):
        # 요청에 실패하거나 값이 잘못된 경우 기본값을 반환합니다.
        return '0'

def get_quotes_count():
    """
    명언 데이터의 총 개수를 가져와서 포맷팅된 문자열로 반환합니다.
    요청에 실패할 경우 기본값을 반환합니다.
    """
    try:
        # 명언 데이터의 총 개수를 가져오는 API 요청을 보냅니다.
        response = requests.get('https://a1.mkeasy.kro.kr/quotes/total')
        response.raise_for_status()  # 응답이 실패한 경우 예외를 발생시킵니다.
        count = response.json().get('count', '0')  # 응답에서 총 개수를 가져옵니다.
        return '{:,}'.format(int(count))  # 숫자를 천 단위로 포맷팅하여 반환합니다.
    except (requests.RequestException, ValueError):
        # 요청에 실패하거나 값이 잘못된 경우 기본값을 반환합니다.
        return '0'

def create_app():
    """
    Flask 애플리케이션을 생성하고 라우트를 설정합니다.
    """
    app = Flask(__name__)  # Flask 애플리케이션 인스턴스를 생성합니다.

    @app.route('/health')
    def health():
        """
        애플리케이션의 상태를 확인하는 엔드포인트입니다.
        """
        return 'OK'

    @app.route('/privacy-policy')
    def protect_terms():
        """
        개인정보 보호 정책 페이지를 렌더링하는 엔드포인트입니다.
        """
        return render_template('privacy-policy.html')

    @app.route('/skill')
    def skill_tree():
        """
        기술 트리 페이지를 렌더링하는 엔드포인트입니다.
        현재 시간을 템플릿에 전달합니다.
        """
        return render_template('skill.html', time=int(time.time()))

    @app.route('/')
    def projects():
        """
        프로젝트 데이터를 로드하고, 날씨 데이터와 명언 데이터를 가져와서
        템플릿에 전달하는 엔드포인트입니다.
        """
        projects_data = load_projects()  # 프로젝트 데이터를 로드합니다.
        count_weather_data = get_past_weather_count()  # 과거 날씨 데이터의 총 개수를 가져옵니다.
        count_quotes = get_quotes_count()  # 명언 데이터의 총 개수를 가져옵니다.

        # 각 개인 프로젝트의 설명에 날씨 데이터와 명언 데이터를 포맷팅하여 삽입합니다.
        for project in projects_data['personal_projects']:
            project['description'] = project['description'].format(count_weather_data=count_weather_data, count_quotes=count_quotes)

        # 프로젝트 데이터를 템플릿에 전달하여 렌더링합니다.
        return render_template('card.html',
                             personal_projects=projects_data['personal_projects'],
                             participated_projects=projects_data['participated_projects'],
                             time=int(time.time()))

    return app  # 생성된 Flask 애플리케이션 인스턴스를 반환합니다.

if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션을 생성합니다.
    app.run(debug=True)  # 애플리케이션을 디버그 모드로 실행합니다.