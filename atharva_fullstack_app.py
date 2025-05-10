
import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import openai
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app)
openai.api_key = "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"  # Replace with your real OpenAI key

DOCUMENT_TEXT = ""

# Serve the main HTML page
@app.route('/')
def index():
    return render_template_string(open("atharva_google_style_frontend.html").read())

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    print(f"🔍 Received query: {query}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        print("✅ Response received")
        return jsonify({"answer": response['choices'][0]['message']['content']})
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    global DOCUMENT_TEXT
    uploaded_file = request.files['file']
    if uploaded_file:
        ext = os.path.splitext(uploaded_file.filename)[1].lower()
        if ext == '.pdf':
            reader = PdfReader(uploaded_file)
            DOCUMENT_TEXT = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext in ['.txt', '.csv']:
            DOCUMENT_TEXT = uploaded_file.read().decode("utf-8")
        else:
            return jsonify({"message": "Unsupported file format"}), 400
        print(f"📄 Document uploaded and stored ({len(DOCUMENT_TEXT)} characters)")
        return jsonify({"message": "Document uploaded and processed successfully."})
    return jsonify({"message": "No file uploaded"}), 400

@app.route('/rag-query', methods=['POST'])
def rag_query():
    global DOCUMENT_TEXT
    data = request.get_json()
    query = data.get('query', '')
    prompt = f"""Use the following context from a document to answer the question:

{DOCUMENT_TEXT[:4000]}

Question: {query}
"""
    print(f"""🧠 RAG Prompt:
{prompt[:200]}...""")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print("✅ RAG response received")
        return jsonify({"answer": response['choices'][0]['message']['content']})
    except Exception as e:
        print(f"❌ OpenAI RAG error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

