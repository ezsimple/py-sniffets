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

def fetch_total_count():
    try:
        response = requests.get('https://a1.mkeasy.kro.kr/past-weather/api/total_count')
        response.raise_for_status()  # Raise an error for bad responses
        total_count = response.json().get('total_count', '0')
        return '{:,}'.format(int(total_count))  # Format with commas
    except (requests.RequestException, ValueError):
        return '0'  # Default value in case of an error

def create_app():
    app = Flask(__name__)

    @app.route('/old')
    def home():
        return render_template('index.html')

    @app.route('/skill')
    def skill_tree():
        return render_template('skill.html')

    @app.route('/')
    def projects():
        projects_data = load_projects()
        total_count = fetch_total_count()

        for project in projects_data['personal_projects']:
            project['description'] = project['description'].format(total_count=total_count)

        return render_template('card.html', 
                             personal_projects=projects_data['personal_projects'],
                             participated_projects=projects_data['participated_projects'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)