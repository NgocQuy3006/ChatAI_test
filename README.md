# 💬 ChatAI Test – AI Full-stack Intern Assignment

## 🎯 Mục tiêu
> Xây dựng một ứng dụng chat hỗ trợ:
> 1. Multi-turn conversation (cuộc hội thoại nhiều lượt)
> 2. Chat về ảnh được tải lên (Image Chat)
> 3. Chat về dữ liệu CSV (Data Chat)

---

## ⚙️ Tính năng chính

> ### 🗨️ Core Chat
> - Hiển thị lịch sử hội thoại (user + assistant)
> - Ghi rõ ai nói gì và khi nào
> - Hỗ trợ Markdown cơ bản

---

> ### 🖼️ Image Chat
> - Cho phép tải lên ảnh (PNG/JPG)
> - Hiển thị ảnh trong khung chat
> - Có thể hỏi về nội dung trong ảnh (VD: “Ảnh này có gì?”)

---

> ### 📊 CSV Data Chat
> - Nhận CSV từ **file upload** hoặc **URL (GitHub raw CSV link)**
> - Có thể hỏi:
>   - “Tóm tắt dataset này”
>   - “Hiển thị thống kê cơ bản”
>   - “Cột nào có nhiều giá trị bị thiếu nhất?”
>   - “Vẽ biểu đồ histogram cho cột price”
> - Kết quả hiển thị inline (text, bảng, hoặc biểu đồ)

---

## 🧩 Công nghệ sử dụng
> - **Frontend:** HTML / CSS / JavaScript  
> - **Backend:** Flask  
> - **Database:** SQLite  
> - **AI Model:** OpenAI API (hoặc local fallback nếu không có key)  
> - **Chart:** matplotlib / pandas  

---

## 📁 Cấu trúc dự án
```bash
test_intern/
├── demo.mp4
├── README.md
├── main.py
├── models.py
├── chat_routes.py
├── db.py
├── requirements.txt
├── .env
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/
└── instance/
    └── chat_history.db
```bash
## 🚀 Cách chạy project

---

### 🧩 1️⃣ Cài đặt thư viện
> **Lệnh cài đặt:**
> ```
> pip install -r requirements.txt
> ```

---

### ⚙️ 2️⃣ Chạy ứng dụng
> **Khởi động server:**
> ```
> python main.py
> ```
> Ứng dụng sẽ chạy tại:  
> 👉 http://127.0.0.1:5000  
> hoặc  
> 👉 http://localhost:5000  

---

### 🎥 Demo Video
> 🎬 Xem video demo tại đây:  
> [https://github.com/NgocQuy3006/ChatAI_test/raw/main/demo.mp4](https://github.com/NgocQuy3006/ChatAI_test/raw/main/demo.mp4)

---

### ✅ Ghi chú
> - Giữ file `.env` bí mật, không commit API key.  
> - Có xử lý lỗi cho CSV hỏng hoặc URL sai.  
> - Giao diện tối giản, rõ ràng, dễ dùng.  
> - Cấu trúc thư mục gọn gàng, dễ mở rộng.  

---

### 🪜 Commit & Push
> **Các lệnh Git cần chạy:**
> ```
> git add README.md demo.mp4
> git commit -m "Add full README and demo video"
> git push origin main
> ```
