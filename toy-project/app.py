from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()  # create_app 함수 호출
    app.run(debug=True)  # 디버그 모드에서 실행