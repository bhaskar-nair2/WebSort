from flask import Flask, render_template, request
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from datetime import date
import os
import threading
import Sorter
from random import random
from queue import Queue

# TODO:
# UPLOAD FILE
# Search Algorithm
# Yeild data to sockets

UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = ['xlsx', 'png']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socket = SocketIO(app)

updater = Queue()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/refresh', methods=['POST'])
def refresh():
    pa_count = request.form['pa_count']
    file = request.files['file']
    filename = str(date.today()) + secure_filename(file.filename)
    if file and allowed_file(filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        re_thread = threading.Thread(target=lambda: re_threader(app.config['UPLOAD_FOLDER'] + filename, int(pa_count)))
        re_thread.start()
    else:
        print('File Not Valid!')
    return render_template('index.html')


def re_threader(file_loc, pacount):
    srt = Sorter.ReDataMaker(file_loc, pacount, updater)
    srt.refresh()


def thread_test():
    number = round(random() * 10, 3)
    socket.emit('newnumber', {'number': number}, namespace='/api')


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
