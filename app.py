from flask import Flask, render_template, jsonify
from time import sleep

# TODO:
# UPLOAD FILE
# Search Algorithm
# Yeild data to sockets

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


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



if __name__ == '__main__':
    app.run()
