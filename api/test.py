from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/test')
def test():
    return jsonify({"message": "Test works!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "OK"})
