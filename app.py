from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_hand_tracking')
def start_hand_tracking():
    try:
        subprocess.Popen(['python', 'mouse_mov.py'])
        return jsonify({"status": "Hand tracking started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
