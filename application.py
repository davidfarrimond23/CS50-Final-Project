import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from flask_session import Session
from tempfile import mkdtemp, gettempdir
from helpers import searchFunc, stringBuilder, insertData
import random
import secrets
import json

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt'}
testdict = {}
# use placenames db
db = SQL("sqlite:///placenames.db")


# configure app
app = Flask(__name__)


# auto load templates & upload folder check
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#secure file function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#user id generator
def randomnumber(N):
	minimum = pow(10, N-1)
	maximum = pow(10, N) - 1
	return random.randint(minimum, maximum)

@app.before_first_request
def _run_on_start():
    folder = 'static/layers/session/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

#when index called
@app.route("/", methods=["GET", "POST"])
def index():
    #check if get request
    if request.method == "GET":
        #check if session id set
        if session.get("id") == None:
            #if no session id- create it
            session["id"] = randomnumber(10)
            #build you a temp file.
            return render_template("index.html", entryfile = "static/layers/placenameslayer_1.js")
        else:
            return render_template("index.html", entryfile = "static/layers/placenameslayer_1.js")

##str(session["id"]),

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template("upload.html")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = "./uploads/"
            dir_list = os.listdir(path)
            return render_template("data.html", files = dir_list)
    return ''

@app.route('/data', methods=['GET', 'POST'])
def get_data():
    path = "./uploads/"
    dir_list = os.listdir(path)
    if request.method == 'GET':
        #find files in path
        #create list of uploads
        return render_template("data.html", files = dir_list)
    if request.method == "POST":
        filename = request.form.get("filename")
        path = "./uploads/"
        testdict = searchFunc(os.path.join(path, filename), db)
        file_path = "static/layers/session/" + str(session["id"]) + ".txt"
        json.dump(testdict, open(file_path,'w'))
        return render_template("dataprocessed.html", files = dir_list, rows = testdict, filename = filename)


##create the layer file:
@app.route('/mapit', methods=['GET', 'POST'])
def get_mapthis():
    if request.method == "POST":
        file_path = "static/layers/session/" + str(session["id"]) + ".txt"
        with open(file_path, "r") as file:
            data = file.read()
            testdict = json.loads(data)
        filepath = ('static/layers/session/' + str(session["id"]) + '.js')
        insertData(testdict, filepath)
        page_title = request.form.get("filename")
        with open('uploads/' + page_title, 'r') as file:
            stuff = file.read()
        return render_template("map.html", entryfile = filepath, stuff = stuff, page_title = page_title)
        ##TODO:
        ##load"mapit.html" with
    elif request.method == "GET":
        return render_template("index.html", entryfile = "static/layers/placenameslayer_1.js")