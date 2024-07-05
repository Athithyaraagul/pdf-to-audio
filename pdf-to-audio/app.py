from flask import Flask, render_template, request, send_file
import requests
import os
from gtts import gTTS
import fitz  # PyMuPDF


app = Flask(__name__)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_filename):
    try:
        doc = fitz.open(pdf_filename)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print("Failed to extract text from PDF:", str(e))
        return None

# Function to translate text using Microsoft Translator API
def translate_text(input_text, target_language):
    subscription_key = '2b86cbf9-f792-4fda-96c1-e941d2c71739'
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = 'centralindia'

    path = '/translate?api-version=3.0'
    params = '&to=' + target_language
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': location,
    }

    body = [{
        'text': input_text,
    }]

    response = requests.post(constructed_url, headers=headers, json=body)
    result = response.json()

    if response.status_code != 200:
        return None  # Translation failed

    translated_text = result[0]['translations'][0]['text']
    return translated_text

# Function to generate an audiobook from translated text
def generate_audiobook(translated_text, target_language, download_path):
    tts = gTTS(text=translated_text, lang=target_language)
    audio_filename = os.path.join(download_path, 'translated_audio.mp3')
    tts.save(audio_filename)
    return audio_filename

@app.route('/')
def home():
    return render_template('mainpage.html')

@app.route('/conversion')
def conversion():
    return render_template('conversionpage.html')

@app.route('/translate', methods=['POST'])
def translate():
    # Get the user's input
    pdf_file = request.files['pdf_file']
    target_language = request.form['target_language']
    download_path = request.form['download_path']

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        # Save the uploaded PDF file
        pdf_filename = os.path.join('uploads', 'input.pdf')
        pdf_file.save(pdf_filename)

        # Extract text from the PDF file
        input_text = extract_text_from_pdf(pdf_filename)

        if input_text is None:
            return "Failed to extract text from the PDF."

        # Translate the text
        translated_text = translate_text(input_text, target_language)

        if translated_text is None:
            return "Failed to translate the text."

        # Generate the audiobook
        audio_filename = generate_audiobook(translated_text, target_language, download_path)

        if audio_filename is None:
            return "Failed to generate the audiobook."

        # Provide a link to download the audiobook
        return send_file(audio_filename, as_attachment=True)

    else:
        return "Invalid file or language selection."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9256, debug=True)
