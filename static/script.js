const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const chatForm = document.getElementById("chat-form");
const conversationList = document.getElementById("conversation-list");
const newChatBtn = document.getElementById("new-chat");

let currentConversationId = null;

// ==============================
//  Hàm hiển thị thời gian
// ==============================
function formatTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function loadConversations() {
  return fetch("/conversations")
    .then(res => res.json())
    .then(data => {
      conversationList.innerHTML = "";
      data.forEach(conv => {
        const li = document.createElement("li");
        li.classList.add("conversation-item");

        const span = document.createElement("span");
        span.textContent = conv.title;
        span.onclick = () => loadMessages(conv.id);

        const delBtn = document.createElement("button");
        delBtn.textContent = "🗑";
        delBtn.classList.add("delete-btn");
        delBtn.onclick = async (e) => {
          e.stopPropagation();
          if (confirm(`Xóa "${conv.title}"?`)) {
            const res = await fetch(`/delete_chat/${conv.id}`, { method: "DELETE" });
            if (res.ok) {
              localStorage.removeItem("lastConvId");
              loadConversations();
            } else alert(" Lỗi khi xóa cuộc trò chuyện!");
          }
        };

        li.appendChild(span);
        li.appendChild(delBtn);
        conversationList.appendChild(li);
      });
    });
}

function loadMessages(convId) {
  fetch(`/messages/${convId}`)
    .then(res => res.json())
    .then(msgs => {
      currentConversationId = convId;
      localStorage.setItem("lastConvId", convId);

      chatBox.innerHTML = "";
      msgs.forEach(m => {
        const div = document.createElement("div");
        div.className = `msg ${m.role}`;
        const time = m.timestamp || formatTime();
        div.innerHTML = `
          ${m.role === "user" ? "🧑" : "🤖"} ${m.content}
          <div class="msg-time">${time}</div>
        `;
        chatBox.appendChild(div);
      });
      chatBox.scrollTop = chatBox.scrollHeight;
    });
}

// ==============================
//  Gửi tin nhắn văn bản
// ==============================
chatForm.onsubmit = e => {
  e.preventDefault();
  const msg = messageInput.value.trim();
  if (!msg) return;

  const userDiv = document.createElement("div");
  userDiv.className = "msg user";
  userDiv.innerHTML = `
    🧑 ${msg}
    <div class="msg-time">${formatTime()}</div>
  `;
  chatBox.appendChild(userDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  messageInput.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, new_chat: false })
  })
    .then(res => res.json())
    .then(data => {
      chatBox.innerHTML = "";
      data.history.forEach(m => {
        const div = document.createElement("div");
        div.className = `msg ${m.role}`;
        const time = m.timestamp || formatTime();
        div.innerHTML = `
          ${m.role === "user" ? "🧑" : "🤖"} ${m.content}
          <div class="msg-time">${time}</div>
        `;
        chatBox.appendChild(div);
      });
      chatBox.scrollTop = chatBox.scrollHeight;
      loadConversations();
    })
    .catch(() => alert(" Lỗi khi gửi tin nhắn!"));
};

// ==============================
//  Tạo cuộc trò chuyện mới
// ==============================
newChatBtn.onclick = () => {
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "Bắt đầu cuộc trò chuyện mới", new_chat: true })
  })
    .then(() => {
      chatBox.innerHTML = "";
      localStorage.removeItem("lastConvId");
      loadConversations();
    });
};

// ==============================
//  Khi tải trang
// ==============================
window.onload = async () => {
  await loadConversations();
  const lastConv = localStorage.getItem("lastConvId");
  if (lastConv) {
    loadMessages(lastConv);
  }
};

// ========================================================
//  Chat với hình ảnh
// ========================================================
const imageSection = document.createElement("div");
imageSection.style = "margin-top:12px; padding-top:8px; border-top:1px solid #ccc;";

const uploadBtn = document.createElement("button");
uploadBtn.textContent = "📷 Tải ảnh";
uploadBtn.type = "button";
uploadBtn.style = "margin-bottom:6px; margin-right:6px;";

const imageInput = document.createElement("input");
imageInput.type = "file";
imageInput.accept = "image/png,image/jpeg";
imageInput.style = "display:none;";

const questionInput = document.createElement("input");
questionInput.placeholder = "Hỏi về ảnh (ví dụ: Trong ảnh có gì?)";
questionInput.style = "width:70%; margin-top:8px; margin-right:6px;";

const askBtn = document.createElement("button");
askBtn.textContent = "Hỏi ảnh";
askBtn.type = "button";

imageSection.appendChild(uploadBtn);
imageSection.appendChild(imageInput);
imageSection.appendChild(document.createElement("br"));
imageSection.appendChild(questionInput);
imageSection.appendChild(askBtn);
document.querySelector(".chat-container").appendChild(imageSection);

// === Khi nhấn nút tải ảnh ===
uploadBtn.onclick = () => imageInput.click();

imageInput.onchange = async () => {
  const file = imageInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("image", file);

  try {
    const res = await fetch("/upload-image", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (res.ok && data.url) {
      const userDiv = document.createElement("div");
      userDiv.className = "msg user";
      userDiv.innerHTML = `
        🧑 <img src="${data.url}" class="chat-image">
        <div class="msg-time">${formatTime()}</div>
      `;
      chatBox.appendChild(userDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
      imageInput.value = "";
    } else {
      alert("❌ " + (data.error || "Không thể tải ảnh"));
    }
  } catch (err) {
    alert(" Lỗi khi tải ảnh!");
  }
};

// === Khi nhấn “Hỏi ảnh” ===
askBtn.onclick = async () => {
  const q = questionInput.value.trim();
  if (!q) return alert("Nhập câu hỏi về ảnh trước!");

  const userDiv = document.createElement("div");
  userDiv.className = "msg user";
  userDiv.innerHTML = `
    🧑 ${q}
    <div class="msg-time">${formatTime()}</div>
  `;
  chatBox.appendChild(userDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  questionInput.value = "";

  try {
    const res = await fetch("/image-question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();

    const botDiv = document.createElement("div");
    botDiv.className = "msg assistant";

    if (res.ok) {
      botDiv.innerHTML = `
        🤖 ${data.reply}<br><img src="${data.image_url}" class="chat-image">
        <div class="msg-time">${formatTime()}</div>
      `;
    } else {
      botDiv.textContent = "🤖 Lỗi: " + (data.error || "Không rõ lỗi");
    }

    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (err) {
    alert(" Lỗi khi gửi câu hỏi!");
  }
};

// ========================================================
//  Chat với CSV
// ========================================================
const csvSection = document.createElement("div");
csvSection.className = "csv-section";

csvSection.innerHTML = `
  <div class="csv-upload-box">
    <input type="file" id="csvFileInput" accept=".csv,.xlsx" hidden>
    <button id="chooseCsvBtn">📂 Chọn CSV/XLSX</button>
    <button id="uploadCsvBtn" class="main">⬆ Upload</button>
  </div>
  <div class="csv-url-box">
    <input type="text" id="csvUrlInput" placeholder="Nhập URL CSV...">
    <button id="csvUrlBtn">Tải</button>
  </div>
  <div class="csv-ask-box">
    <input type="text" id="csvQuestionInput" placeholder="Hỏi về dữ liệu CSV...">
    <button id="csvAskBtn" class="main">Hỏi</button>
  </div>
`;

document.querySelector(".chat-container").appendChild(csvSection);

const csvFileInput = csvSection.querySelector("#csvFileInput");
const chooseCsvBtn = csvSection.querySelector("#chooseCsvBtn");
const uploadCsvBtn = csvSection.querySelector("#uploadCsvBtn");
const csvUrlInput = csvSection.querySelector("#csvUrlInput");
const csvUrlBtn = csvSection.querySelector("#csvUrlBtn");
const csvQuestionInput = csvSection.querySelector("#csvQuestionInput");
const csvAskBtn = csvSection.querySelector("#csvAskBtn");

chooseCsvBtn.onclick = () => csvFileInput.click();

uploadCsvBtn.onclick = async () => {
  if (!csvFileInput.files.length) return alert("Chưa chọn file CSV hoặc Excel!");
  const formData = new FormData();
  formData.append("csv", csvFileInput.files[0]);

  const res = await fetch("/upload-csv", { method: "POST", body: formData });
  const data = await res.json();

  const userDiv = document.createElement("div");
  userDiv.className = "msg user";
  userDiv.innerHTML = `
    🧑 📂 Đã tải lên: ${csvFileInput.files[0].name}
    <div class="msg-time">${formatTime()}</div>
  `;
  chatBox.appendChild(userDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (res.ok) {
    try {
      const previewRes = await fetch("/csv-preview");
      const previewData = await previewRes.json();

      const botDiv = document.createElement("div");
      botDiv.className = "msg assistant";

      if (previewData.error) {
        botDiv.innerHTML = `🤖 Lỗi khi đọc file: ${previewData.error}`;
      } else {
        botDiv.innerHTML = `
          🤖 Dữ liệu bạn vừa tải lên:<br><pre>${previewData.preview}</pre>
          <div class="msg-time">${formatTime()}</div>
        `;
      }

      chatBox.appendChild(botDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch {
      alert("❌ Lỗi khi xem trước file!");
    }
  } else {
    alert("❌ " + (data.error || "Không thể tải file!"));
  }
};

csvUrlBtn.onclick = async () => {
  const url = csvUrlInput.value.trim();
  if (!url) return alert("Nhập URL trước!");
  const res = await fetch("/csv-from-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  const data = await res.json();
  alert(data.message || data.error);
};

csvAskBtn.onclick = async () => {
  const q = csvQuestionInput.value.trim();
  if (!q) return alert("Nhập câu hỏi trước!");

  const userDiv = document.createElement("div");
  userDiv.className = "msg user";
  userDiv.innerHTML = `
    🧑 ${q}
    <div class="msg-time">${formatTime()}</div>
  `;
  chatBox.appendChild(userDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  csvQuestionInput.value = "";

  try {
    const res = await fetch("/csv-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: q }),
    });
    const data = await res.json();

    const botDiv = document.createElement("div");
    botDiv.className = "msg assistant";
    botDiv.innerHTML = `
      🤖 ${data.reply || data.error || ""}
      <div class="msg-time">${formatTime()}</div>
    `;
    chatBox.appendChild(botDiv);

    if (data.charts && Array.isArray(data.charts)) {
      data.charts.forEach(url => {
        const img = document.createElement("img");
        img.src = url;
        img.className = "chat-image";
        img.style = "margin-top:8px; max-width:100%; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.2)";
        chatBox.appendChild(img);
      });
    }

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch {
    alert("Lỗi khi gửi câu hỏi về CSV!");
  }
};
