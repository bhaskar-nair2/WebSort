from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from werkzeug import exceptions
from datetime import date
import Sorter
import os
import threading
import queue

# TODO:
# Search Algorithm
# Yeild data to sockets

UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = ['xlsx', 'png']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = db = 'static/data/SearchDB'
socket = SocketIO(app, async_mode='threading')
status_q = queue.Queue()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/refresh', methods=['POST'])
def refresh():
    try:
        gpa_count = request.form['pa_count']
        spa_count = request.form['spa_count']
        rc_count = request.form['rc_count']
        file = request.files['file']
        filename = str(date.today()) + secure_filename(file.filename)
        if file and allowed_file(filename):
            socket.emit('OK', {"msg": ""})
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            re_thread = threading.Thread(
                target=lambda: re_threader(app.config['UPLOAD_FOLDER'] + filename, int(gpa_count),
                                           int(gpa_count) + int(spa_count),
                                           int(gpa_count) + int(spa_count) + int(rc_count)))
            status_handle = threading.Thread(target=que_handeler)
            re_thread.start()
            status_handle.start()
        else:
            socket.emit('WRONGFILE', {"msg": "Incorrect File Formt!"})
    except exceptions.HTTPException as e:
        print(e)
        socket.emit('NOFILE', {"msg": "No file provided!!"})
    return render_template('index.html')


def re_threader(file_loc, pacount, spacount, rccount):
    re = Sorter.ReDataMaker(file_loc, status_q, pacount, spacount, rccount)
    re.refresh()


@app.route('/api/sort', methods=['POST'])
def sort_it():
    try:
        file = request.files['file']
        filename = str(date.today()) + secure_filename(file.filename)
        if file and allowed_file(filename):
            socket.emit('OK', {"msg": ""})
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sort_thread = threading.Thread(target=lambda: sort_threader(app.config['UPLOAD_FOLDER'] + filename))
            status_handle = threading.Thread(target=que_handeler)
            sort_thread.start()
            status_handle.start()
        else:
            socket.emit('WRONGFILE', {"msg": "Incorrect File Formt!"})
    except exceptions.HTTPException as e:
        print(e)
        socket.emit('NOFILE', {"msg": "No file provided!!"})
    return render_template('index.html')


def sort_threader(file_loc):
    srt = Sorter.IdDataMaker(file_loc, status_q)
    srt.data_gen()


def que_handeler():
    while True:
        try:
            txt = status_q.get(True, 0.1)
            print(txt)
            socket.emit('update', {"status": 110, "text": txt})
            if txt == 'Insertion Done!!':
                socket.emit('update', {"status": 210, "text": "Insertion Done"})
            if txt == 'Refresh Done!!':
                socket.emit('update', {"status": 220, "text": 'Refreshed!'})
                break
            if txt == 'Sorting Done!!':
                socket.emit('update', {"status": 200, "text": 'Completed'})
                break
        except queue.Empty:
            pass


@app.route('/api/file', methods=['POST'])
def filez():
    file = request.files['file']
    filename = str(date.today()) + secure_filename(file.filename)
    if file and allowed_file(filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        print('File Not Valid!')
    return render_template('index.html')


@socket.on('connect', namespace='/api')
def test_connect():
    print('Client connected')


@socket.on('disconnect', namespace='/api')
def test_disconnect():
    print('Client disconnected')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
