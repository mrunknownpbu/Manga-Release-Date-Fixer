import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from archive_utils import scan_manga_archives, update_archive_date, batch_fix

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
COMICS_DIR = os.environ.get("COMICS_DIR", "/comics")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/chapters')
def chapters():
    return jsonify(scan_manga_archives(COMICS_DIR))

@app.route('/api/fix', methods=['POST'])
def fix_chapter():
    data = request.json
    chapter_path = data['chapter_path']
    official_date = data.get('official_date')
    result = update_archive_date(chapter_path, official_date)
    return jsonify(result)

@app.route('/api/fixall', methods=['POST'])
def fix_all():
    results = batch_fix(COMICS_DIR)
    return jsonify(results)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1996)