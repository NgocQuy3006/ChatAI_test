from flask import Blueprint, request, jsonify, session, current_app, url_for
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from db import SessionLocal
from models import Conversation, Message
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from flask import jsonify
import pandas as pd
from io import StringIO
import urllib.request
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
# =======================================================
# ⚙️ Cấu hình API
# =======================================================
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

chat_bp = Blueprint("chat_bp", __name__)

print("🔑 Đã tải API key:", "✅" if OPENROUTER_API_KEY else "❌ (Chưa có key)")


# =======================================================
#  Chat API chính
# =======================================================
@chat_bp.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    is_new_chat = request.json.get("new_chat", False)
    if not user_msg:
        return jsonify({"error": "Message cannot be empty"}), 400

    db = SessionLocal()
    conv_id = session.get("conversation_id")

    # Nếu là chat mới → đóng cuộc cũ
    if is_new_chat and conv_id:
        old_conv = db.query(Conversation).get(conv_id)
        if old_conv:
            old_conv.ended_at = datetime.now()
        session.pop("conversation_id", None)
        session.pop("history", None)
        db.commit()

    # Nếu chưa có cuộc hội thoại → tạo mới
    if not session.get("conversation_id"):
        new_conv = Conversation()
        db.add(new_conv)
        db.commit()
        session["conversation_id"] = new_conv.id
        session["history"] = []

    conv_id = session["conversation_id"]
    history = session["history"]

    #  Lưu tin nhắn user
    db.add(Message(role="user", content=user_msg, conversation_id=conv_id))
    db.commit()

    history.append({
        "role": "user",
        "content": user_msg,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    #  Gọi OpenRouter API
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "Referer": "https://openrouter.ai/chat",
            "Origin": "https://openrouter.ai",
            "X-Title": "My GPT App",
        }

        data = {
            "model": "openai/gpt-4o-mini",
            "max_tokens": 600,
            "messages": (
                [{"role": "system", "content": "You are a helpful assistant."}]
                + [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
            ),
        }

        res = requests.post(API_URL, headers=headers, json=data, timeout=60)
        res_json = res.json()

        if "choices" not in res_json:
            print(" API ERROR:", res_json)
            ai_reply = f"Lỗi từ OpenRouter ({res.status_code}): {res_json.get('error', {}).get('message', str(res_json))}"
        else:
            ai_reply = res_json["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        ai_reply = f"Lỗi mạng khi gọi API: {e}"
    except Exception as e:
        ai_reply = f"Lỗi không xác định khi gọi API: {e}"

    # Lưu phản hồi AI
    db.add(Message(role="assistant", content=ai_reply, conversation_id=conv_id))
    db.commit()
    db.close()

    # Cập nhật lịch sử session
    history.append({
        "role": "assistant",
        "content": ai_reply,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    session["history"] = history
    session.modified = True

    return jsonify({"history": history, "conversation_id": conv_id})


# =======================================================
#  Danh sách các cuộc hội thoại
# =======================================================
@chat_bp.route("/conversations", methods=["GET"])
def list_conversations():
    db = SessionLocal()
    conversations = db.query(Conversation).order_by(Conversation.id.desc()).all()
    data = [
        {
            "id": c.id,
            "title": f"Cuộc trò chuyện #{c.id}",
            "created_at": c.created_at.strftime("%H:%M:%S"),
            "ended_at": c.ended_at.strftime("%H:%M:%S") if c.ended_at else None,
        }
        for c in conversations
    ]
    db.close()
    return jsonify(data)


# =======================================================
#  Lấy tin nhắn của 1 cuộc hội thoại
# =======================================================
@chat_bp.route("/messages/<int:conv_id>", methods=["GET"])
def get_messages(conv_id):
    db = SessionLocal()
    messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.id).all()
    data = [{"role": m.role, "content": m.content, "timestamp": m.timestamp.strftime("%H:%M:%S")} for m in messages]
    db.close()
    return jsonify(data)

# =======================================================
#  Upload + hỏi ảnh (Vision)
# =======================================================
ALLOWED_EXT = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@chat_bp.route("/upload-image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "Không có file"}), 400

    f = request.files["image"]
    if f.filename == "":
        return jsonify({"error": "Chưa chọn file"}), 400
    if not allowed_file(f.filename):
        return jsonify({"error": "Chỉ chấp nhận PNG/JPG"}), 400

    #  Upload ảnh trực tiếp lên Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(f)
        img_url = upload_result["secure_url"]  # URL công khai Cloudinary

        # Lưu URL này vào session để dùng cho câu hỏi ảnh
        session["uploaded_image"] = img_url
        session.modified = True

        return jsonify({"url": img_url})
    except Exception as e:
        print(" Lỗi upload Cloudinary:", e)
        return jsonify({"error": f"Lỗi upload ảnh: {str(e)}"}), 500


@chat_bp.route("/image-question", methods=["POST"])
def image_question():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Câu hỏi không được để trống"}), 400

    img_url = session.get("uploaded_image")  #  Lấy URL từ Cloudinary
    if not img_url:
        return jsonify({"error": "Chưa upload ảnh nào"}), 400

    db = SessionLocal()
    conv_id = session.get("conversation_id")
    if not conv_id:
        new_conv = Conversation()
        db.add(new_conv)
        db.commit()
        session["conversation_id"] = new_conv.id
        session["history"] = []
        conv_id = new_conv.id

    db.add(Message(role="user", content=f"[Hỏi ảnh] {question}", conversation_id=conv_id))
    db.commit()

    #  Gọi OpenRouter Vision API
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "Referer": "https://openrouter.ai/chat",
            "Origin": "https://openrouter.ai",
            "X-Title": "My GPT App",
        }

        data = {
            "model": "openai/gpt-4o",
            "max_tokens": 800,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": img_url}},
                    ],
                }
            ],
        }

        res = requests.post(API_URL, headers=headers, json=data, timeout=60)
        res_json = res.json()

        if "choices" not in res_json:
            print(" API ERROR (Vision):", res_json)
            answer = f"Lỗi API trả về: {res_json.get('error', {}).get('message', res_json)}"
        else:
            answer = res_json["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        answer = " Hết thời gian chờ phản hồi từ API."
    except requests.exceptions.RequestException as e:
        answer = f"Lỗi khi kết nối API: {e}"
    except Exception as e:
        answer = f"Lỗi không xác định khi gọi API: {e}"

    db.add(Message(role="assistant", content=f"[Ảnh] {answer}", conversation_id=conv_id))
    db.commit()
    db.close()

    return jsonify({"reply": answer, "image_url": img_url})
# =======================================================
# 🗑 Xóa cuộc trò chuyện khỏi database
# ======================================================
@chat_bp.route("/delete_chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    db = SessionLocal()
    try:
        conv = db.query(Conversation).get(chat_id)
        if not conv:
            db.close()
            return jsonify({"error": "Không tìm thấy cuộc trò chuyện"}), 404

        # Xóa tất cả tin nhắn thuộc cuộc trò chuyện này
        db.query(Message).filter(Message.conversation_id == chat_id).delete()

        # Xóa chính cuộc trò chuyện
        db.delete(conv)
        db.commit()
        db.close()

        return jsonify({"message": f"Đã xóa cuộc trò chuyện #{chat_id}"}), 200
    except Exception as e:
        db.rollback()
        db.close()
        print(" Lỗi khi xóa:", e)
        return jsonify({"error": f"Lỗi khi xóa: {str(e)}"}), 500

# =======================================================
#  📊 CSV Data Chat
# =======================================================
ALLOWED_CSV_EXT = {"csv","xlsx"}
MAX_CSV_BYTES = 5 * 1024 * 1024  # 5MB

def allowed_csv(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_CSV_EXT

def save_csv_temp(file_storage):
    os.makedirs("tmp", exist_ok=True)
    fname = secure_filename(file_storage.filename)
    path = os.path.join("tmp", fname)
    file_storage.save(path)
    return path

def fetch_csv_url(url):
    os.makedirs("tmp", exist_ok=True)
    fname = os.path.basename(url) or "remote.csv"
    path = os.path.join("tmp", secure_filename(fname))
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = resp.read()
        if len(data) > MAX_CSV_BYTES:
            raise ValueError("File quá lớn (>5MB)")
        with open(path, "wb") as f:
            f.write(data)
    return path


@chat_bp.route("/upload-csv", methods=["POST"])
def upload_csv():
    if "csv" not in request.files:
        return jsonify({"error": "Không có file CSV"}), 400
    f = request.files["csv"]
    if f.filename == "":
        return jsonify({"error": "Chưa chọn file"}), 400
    if not allowed_csv(f.filename):
        return jsonify({"error": "Chỉ chấp nhận file .csv"}), 400

    try:
        path = save_csv_temp(f)
        session["csv_path"] = path
        session.modified = True
        return jsonify({"message": f"Đã tải file {f.filename} thành công!"})
    except Exception as e:
        return jsonify({"error": f"Lỗi upload CSV: {e}"}), 500


@chat_bp.route("/csv-from-url", methods=["POST"])
def csv_from_url():
    url = (request.json or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "URL không được để trống"}), 400
    try:
        path = fetch_csv_url(url)
        session["csv_path"] = path
        session.modified = True
        return jsonify({"message": f"Tải CSV thành công từ URL: {os.path.basename(path)}"})
    except Exception as e:
        return jsonify({"error": f"Lỗi tải CSV: {e}"}), 400
# =======================================================
# 📊 CSV / Excel Data Chat — hỗ trợ cả .csv & .xlsx
# =======================================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask import jsonify, session, request, url_for, send_from_directory

@chat_bp.route("/csv-chat", methods=["POST"])
def csv_chat():
    question = (request.json or {}).get("message", "").strip()
    if not question:
        return jsonify({"error": "Câu hỏi không được để trống"}), 400

    csv_path = session.get("csv_path")
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({"error": "Chưa upload hoặc nhập file CSV/Excel nào!"}), 400

    # 🧩 Tự động nhận dạng CSV hoặc Excel
    try:
        ext = os.path.splitext(csv_path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(csv_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(csv_path)
        else:
            return jsonify({"error": "Định dạng file không được hỗ trợ!"}), 400
    except Exception as e:
        return jsonify({"error": f"Lỗi đọc file dữ liệu: {e}"}), 400

    # ✅ Nếu người dùng yêu cầu vẽ biểu đồ
    if any(k in question.lower() for k in ["vẽ biểu đồ", "plot", "chart", "biểu đồ"]):
        charts = []
        os.makedirs("tmp", exist_ok=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return jsonify({"error": "Không có cột số để vẽ biểu đồ!"}), 400

        try:
            # --- Biểu đồ cột ---
            plt.figure(figsize=(6,4))
            df[numeric_cols].head(10).plot(kind="bar")
            plt.title("Biểu đồ cột")
            plt.tight_layout()
            bar_path = "tmp/chart_bar.png"
            plt.savefig(bar_path)
            plt.close()
            charts.append(url_for("chat_bp.serve_tmp", filename="chart_bar.png"))

            # --- Biểu đồ đường ---
            plt.figure(figsize=(6,4))
            df[numeric_cols].head(20).plot(kind="line")
            plt.title("Biểu đồ đường")
            plt.tight_layout()
            line_path = "tmp/chart_line.png"
            plt.savefig(line_path)
            plt.close()
            charts.append(url_for("chat_bp.serve_tmp", filename="chart_line.png"))

            # --- Histogram ---
            plt.figure(figsize=(6,4))
            df[numeric_cols].hist(bins=20)
            plt.suptitle("Histogram (phân phối dữ liệu)")
            plt.tight_layout()
            hist_path = "tmp/chart_hist.png"
            plt.savefig(hist_path)
            plt.close()
            charts.append(url_for("chat_bp.serve_tmp", filename="chart_hist.png"))

            # --- Boxplot ---
            plt.figure(figsize=(6,4))
            sns.boxplot(data=df[numeric_cols])
            plt.title("Boxplot (biểu đồ hộp)")
            plt.tight_layout()
            box_path = "tmp/chart_box.png"
            plt.savefig(box_path)
            plt.close()
            charts.append(url_for("chat_bp.serve_tmp", filename="chart_box.png"))

            # --- Pie chart (nếu có cột phân loại) ---
            cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
            if cat_cols and numeric_cols:
                first_cat = cat_cols[0]
                first_num = numeric_cols[0]
                pie_data = df.groupby(first_cat)[first_num].sum().head(5)
                plt.figure(figsize=(5,5))
                plt.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
                plt.title(f"Biểu đồ tròn: {first_num} theo {first_cat}")
                pie_path = "tmp/chart_pie.png"
                plt.savefig(pie_path)
                plt.close()
                charts.append(url_for("chat_bp.serve_tmp", filename="chart_pie.png"))

            reply = "✅ Đã tự động tạo các biểu đồ từ dữ liệu của bạn:"
            return jsonify({"reply": reply, "charts": charts})
        except Exception as e:
            return jsonify({"error": f"Lỗi khi vẽ biểu đồ: {e}"}), 500

    # ✅ Nếu không yêu cầu vẽ biểu đồ → hỏi GPT
    try:
        preview = df.head(5).to_string()
        context = f"Tập dữ liệu có {df.shape[0]} hàng và {df.shape[1]} cột.\n5 dòng đầu tiên:\n{preview}"
        prompt = f"{context}\n\nNgười dùng hỏi: {question}\nHãy trả lời bằng tiếng Việt, dễ hiểu."

        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "openai/gpt-4o-mini", "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(API_URL, headers=headers, json=data, timeout=60)
        res_json = res.json()
        answer = res_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        answer = f"Lỗi khi gọi AI: {e}"

    return jsonify({"reply": answer})


# =======================================================
# 👁️ Xem trước dữ liệu CSV / Excel
# =======================================================
@chat_bp.route("/csv-preview", methods=["GET"])
def csv_preview():
    csv_path = session.get("csv_path")
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({"error": "Chưa upload file CSV hoặc Excel nào!"}), 400

    try:
        ext = os.path.splitext(csv_path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(csv_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(csv_path)
        else:
            return jsonify({"error": "Định dạng file không được hỗ trợ!"}), 400

        preview = df.head(5).to_string()
        return jsonify({"preview": preview})
    except Exception as e:
        return jsonify({"error": f"Lỗi đọc file dữ liệu: {e}"}), 400


# =======================================================
# 🖼️ Cho phép Flask phục vụ ảnh biểu đồ
# =======================================================
@chat_bp.route("/tmp/<path:filename>")
def serve_tmp(filename):
    return send_from_directory("tmp", filename)


