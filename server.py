# server.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64, tempfile, os, time
from analyze import analyze_handwriting
from export_docx import export_to_docx

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/process', methods=['POST'])
def process():
    tmp_path = ""
    try:
        # Use get_json(silent=True) to avoid crash on malformed JSON
        data = request.get_json(silent=True) or {}
        image_b64 = data.get('image')
        
        if not image_b64:
            return jsonify({"error": "No image data received. Please draw something first."}), 400

        # Save temp image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(base64.b64decode(image_b64))
            tmp_path = tmp.name

        # Analyze with EasyOCR and Subject Classifier
        analysis = analyze_handwriting(tmp_path)
        subject = analysis.get("subject", "General")

        # Create Subject Folder inside 'subjects/'
        output_dir = os.path.join("subjects", subject)
        os.makedirs(output_dir, exist_ok=True)
        
        # New Export Path
        filename = f"{analysis['title'][:20].replace(' ', '_')}_{int(time.time())}.docx"
        docx_path = os.path.join(output_dir, filename)
        
        export_to_docx(analysis, docx_path)

        return jsonify({
            "analysis": analysis,
            "docx_url": f"/download/{subject}/{os.path.basename(docx_path)}",
            "saved_path": docx_path
        })
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

@app.route('/download/<subject>/<filename>')
def download(subject, filename):
    path = os.path.join("subjects", subject, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found.", 404

if __name__ == '__main__':
    print("🚀 ScribeFlow Backend running at http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
