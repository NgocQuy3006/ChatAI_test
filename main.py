import typing
if not hasattr(typing, "TypeAliasType"):
    typing.TypeAliasType = type

from flask import Flask, render_template
from chat_routes import chat_bp
from db import init_db
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

#  cấu hình upload ảnh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB

# Giữ nguyên phần còn lại
app.register_blueprint(chat_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
