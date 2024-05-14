import os
from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import whisper
from googletrans import Translator

UPLOAD_FOLDER = os.getcwd() + '/uploads'
ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/transcribeFile', methods=['GET', 'POST'])
def upload_file():
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
            file_name = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            file.save(file_path)

            model = whisper.load_model("base")
            result = model.transcribe(file_path)
            print(result["text"])

            response = jsonify({'transcribedText': result["text"]})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

@app.route('/translateText', methods=['POST'])
def translate_text():
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data["textForTranslation"])
        print(data["destLanguage"])

        if data["textForTranslation"] != '' and data["destLanguage"] != '':
            translator = Translator()
            translation = translator.translate(data["textForTranslation"], dest=data["destLanguage"])
            print(translation.text)

            response = jsonify({ 'translatedText': translation.text })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        return jsonify({})
