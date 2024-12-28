from flask import Flask, render_template
import yaml
import os
import requests

def load_projects():
    # config 디렉토리 내의 projects.yml 파일 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, 'config', 'projects.yml')
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            projects = yaml.safe_load(file)
        return projects
    except FileNotFoundError:
        print(f"Error: projects.yml file not found at {yaml_path}")
        return {"personal_projects": [], "participated_projects": []}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {"personal_projects": [], "participated_projects": []}

def get_past_weather_count():
    try:
        response = requests.get('https://a1.mkeasy.kro.kr/past-weather/api/total_count')
        response.raise_for_status()  # Raise an error for bad responses
        count = response.json().get('total_count', '0')
        return '{:,}'.format(int(count))  # Format with commas
    except (requests.RequestException, ValueError):
        return '0'  # Default value in case of an error

def get_quotes_count():
    try:
        response = requests.get('https://a1.mkeasy.kro.kr/quotes/total')
        response.raise_for_status()  # Raise an error for bad responses
        count = response.json().get('count', '0')
        return '{:,}'.format(int(count))  # Format with commas
    except (requests.RequestException, ValueError):
        return '0'  # Default value in case of an error

def create_app():
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return 'OK'

    @app.route('/old')
    def home():
        return render_template('index.html')

    @app.route('/skill')
    def skill_tree():
        return render_template('skill.html')

    @app.route('/')
    def projects():
        projects_data = load_projects()
        count_weather_data = get_past_weather_count()
        count_quotes = get_quotes_count()

        for project in projects_data['personal_projects']:
            project['description'] = project['description'].format(count_weather_data=count_weather_data, count_quotes=count_quotes)

        return render_template('card.html', 
                             personal_projects=projects_data['personal_projects'],
                             participated_projects=projects_data['participated_projects'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)