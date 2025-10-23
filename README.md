# 💬 ChatAI Test – AI Full-stack Intern Assignment

## 🚀 Mục tiêu
Xây dựng một ứng dụng chat hỗ trợ:
1. 💭 Multi-turn conversation (cuộc hội thoại nhiều lượt)
2. 🖼️ Chat về ảnh được tải lên (Image Chat)
3. 📊 Chat về dữ liệu CSV (Data Chat)

---

## ⚙️ Tính năng chính

### 💬 Core Chat
- Hiển thị lịch sử hội thoại (user + assistant)
- Ghi rõ ai nói gì và khi nào
- Hỗ trợ Markdown cơ bản

### 🖼️ Image Chat
- Cho phép tải lên ảnh (PNG/JPG)
- Hiển thị ảnh trong khung chat
- Có thể hỏi về nội dung trong ảnh (VD: “Ảnh này có gì?”)

### 📊 CSV Data Chat
- Nhận CSV từ **file upload** hoặc **URL (GitHub raw CSV link)**
- Có thể hỏi:
  - “Tóm tắt dataset này”
  - “Hiển thị thống kê cơ bản”
  - “Cột nào có nhiều giá trị bị thiếu nhất?”
  - “Vẽ biểu đồ histogram cho cột price”
- Kết quả hiển thị inline (text, bảng, hoặc biểu đồ)

---

## 🧩 Công nghệ sử dụng
- **Frontend:** React / TailwindCSS  
- **Backend:** FastAPI / Flask  
- **AI Model:** OpenAI / Claude / LLaMA (tùy chọn)  
- **Database:** SQLite / PostgreSQL (tùy thiết lập)  
- **Chart:** Chart.js / Recharts  

---

## 🧠 Cấu trúc dự án

test_intern/
├── demo.mp4 # 🎥 Video demo
├── README.md
├── main.py
├── models.py
├── chat_routes.py
├── templates/
├── static/
├── uploads/
├── .env
└── requirements.txt

yaml
Sao chép mã

---

## 🪜 Cách chạy project

### 1️⃣ Cài đặt thư viện
```bash
pip install -r requirements.txt
2️⃣ Chạy ứng dụng
bash
Sao chép mã
python main.py
Ứng dụng sẽ chạy tại http://localhost:8000 hoặc http://127.0.0.1:5000

🎥 Demo Video
👉 Cách 1: Xem video trực tiếp tại GitHub
Nhấn vào liên kết hoặc hình bên dưới để phát video demo:



🔹 Đảm bảo file demo.mp4 nằm trong thư mục gốc của repo (chung với README.md).

✅ Ghi chú
Giữ file .env bí mật, không commit API key.

Có xử lý lỗi cho CSV hỏng hoặc URL sai.

Giao diện tối giản nhưng rõ ràng, dễ dùng.

🧑‍💻 Assignment for AI Full-stack Intern – Built with ❤️ by [Your Name]

yaml
Sao chép mã

---

## 🪜 Sau đó commit và push:
Mở **Git Bash / Terminal** trong thư mục `D:\test_intern` rồi chạy:

```bash
git add README.md demo.mp4
git commit -m "Add full README and demo video"
git push origin main
