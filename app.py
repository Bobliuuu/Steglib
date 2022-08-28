from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from werkzeug.utils import secure_filename
from steglib import predict_class, predict_possible, display_dct, display_lsb, lsb_decryption, dct_histogram
import steglib
from dotenv import dotenv_values
import cv2
import numpy as np
import os
import efficientnet

app = Flask(__name__)

config = dotenv_values()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Session stuff
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set a max image size 
app.config['SECRET_KEY'] = config['KEY']
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # 32 MB
app.config['UPLOAD_FOLDER'] = config['UPLOAD_FOLDER']
app.config['OUTPUT_FOLDER'] = config['OUTPUT_FOLDER']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
OUTPUT_FOLDER = app.config['OUTPUT_FOLDER']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/decode', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    session['filename'] = 'DNE'
    if filename != '' and uploaded_file and allowed_file(filename): 
        new_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(new_path)
        session['filename'] = filename
        result_path = os.path.join(OUTPUT_FOLDER, filename)
        encoding_type = predict_possible(new_path) # Take new filename path after saving
        print(encoding_type)
        return render_template('prediction.html', prediction = encoding_type)
    #return render_template('encode.html')

@app.route('/lsb')
def lsb():
    if not session['filename'] == 'DNE':
        lsb_filename = display_lsb(session['filename'])
        message, relevant_found = lsb_decryption(os.path.join(UPLOAD_FOLDER, session['filename']))
        if relevant_found: 
            found = "Hidden message found with this delimiter!"
        else:
            found = "Hidden message not found with this delimeter!"
        textfilepath = os.path.join(OUTPUT_FOLDER, session['filename'].split('.')[0] + '_message.txt')
        with open(textfilepath, 'w') as f:
            f.write(message)
        print(textfilepath)
        return render_template('lsb.html', lsb_image = lsb_filename, found = found, textfile = textfilepath)

@app.route('/dct')
def dct():
    if not session['filename'] == 'DNE':
        print(session['filename'])
        print(session['filename'].split('.')[0] + '_dct.png')
        dct_filename = display_dct(session['filename'])
        graph_filename = dct_histogram(session['filename'])
        print("answer: " + dct_filename)
        return render_template('dct.html', dct_image = dct_filename, graph_image = graph_filename)

@app.route('/effnet', methods=['GET', 'POST'])
def effnet():
    if not session['filename'] == 'DNE':
        class_type, class_name = predict_class(session['filename'])
        return render_template('effnet.html', classtype = class_type, classname = class_name)

@app.route('/final', methods=['GET', 'POST'])
def final():
    return render_template('final.html')

@app.route('/next', methods=['GET', 'POST'])
def next():
    return render_template('index.html')

@app.route('/redirect_index', methods=['GET', 'POST'])
def redirect_index():
    return render_template('index.html')

@app.route('/redirect_index_anchorabout', methods=['GET', 'POST'])
def redirect_index_anchorabout():
    return redirect(url_for('index', _anchor='team'))

@app.route('/redirect_about', methods=['GET', 'POST'])
def redirect_about():
    return render_template('about.html')

@app.route('/redirect_test', methods=['GET', 'POST'])
def redirect_test():
    return render_template('test.html')

@app.route('/redirect_encode', methods=['GET', 'POST'])
def redirect_encode():
    return render_template('encode.html')

@app.route('/redirect_decode', methods=['GET', 'POST'])
def redirect_decode():
    return render_template('decode.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)