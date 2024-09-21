from flask import Flask, render_template

app = Flask(__name__)

# 이미지 목록
HOST = '127.0.0.1'
PORT = 5000
PATH = 'static' # Flask에서는 정적 파일(이미지등)을 제공하기 위해선 static 디렉토리를 사용합니다.

images = [
    {'url': f'{PATH}/image1.jpg', 'title': '이미지 1'},
    {'url': f'{PATH}/image2.jpg', 'title': '이미지 2'},
    {'url': f'{PATH}/image3.jpg', 'title': '이미지 3'},
]

@app.route('/')
def gallery():
    return render_template('gallery.html', images=images)

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
