import os
from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import whisper
from googletrans import Translator
import tempfile
import io
from pydub import AudioSegment
import numpy as np
import torch

UPLOAD_FOLDER = os.getcwd() + '/uploads'
ALLOWED_EXTENSIONS = {'mp3'}
CHUNK_SIZE = 8 * 1024 * 1024

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model = whisper.load_model("base")

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
            global model
            all_transcriptions = []

            # Create a BytesIO stream to buffer the uploaded file
            audio_stream = io.BytesIO(file.read())

            try:
                # Process the file in chunks
                while True:
                    # Create temporary audio file for this chunk
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                        chunk = audio_stream.read(CHUNK_SIZE)

                        # Break the loop if we have read all chunks
                        if len(chunk) == 0:
                            break

                        # Write the chunk to the temporary file and transcribe it
                        tmp.write(chunk)
                        tmp.flush()  # Flush buffers to disk to ensure all data is written

                        # Seek the temporary file to the beginning
                        tmp.seek(0)

                        # Transcribe the audio chunk
                        result = model.transcribe(tmp.name)
                        all_transcriptions.append(result["text"])
                        print(f"Transcribed chunk: {tmp.name}")

            except Exception as e:
                return jsonify(error=str(e)), 500

            # Combine all transcriptions into one
            transcription = ''.join(all_transcriptions)
            print(transcription)

            response = jsonify({'transcribedText': transcription})
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
