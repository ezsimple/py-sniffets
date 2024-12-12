from flask import Flask, render_template
import yaml
import os

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
        return render_template('card.html', 
                             personal_projects=projects_data['personal_projects'],
                             participated_projects=projects_data['participated_projects'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)