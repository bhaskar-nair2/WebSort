from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from datetime import date
import os

# TODO:
# UPLOAD FILE
# Search Algorithm
# Yeild data to sockets

UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = ['xlsx', 'png']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/test')
def api():
    return jsonify([{
        "name": "Zara Ali",
        "age": "67",
        "sex": "female"
    },
        {
            "name": "hara Ali",
            "age": "67",
            "sex": "female"
        }])


@app.route('/api/file', methods=['POST'])
def filez():
    file = request.files['file']
    filename = str(date.today()) + secure_filename(file.filename)
    if file and allowed_file(filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        print('File Not Valid!')
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run()
