# 🤖 Multi-User WhatsApp AI Chatbot with Task Scheduling & LLM Integration

## 👤 Author
**Manav Gupta**  
📧 manav26102002@gmail.com  
📱 +91 95163 85315  
🔗 [GitHub Repo](https://github.com/MM21B038/whatsapp-bot)

---

## 📝 Overview
A powerful **WhatsApp AI chatbot** that enables users to:

- 🔹 Have general conversations
- 📅 Schedule reminders via **WhatsApp, Email, and Call**
- 🔁 Reschedule or ❌ delete tasks
- 🗣 Transcribe voice messages
- 👥 Support multiple users with independent task and chat context

This bot is integrated with **Meta’s WhatsApp API**, **OpenAI Assistant API**, **Twilio**, and **APScheduler**.

---

## ⚙️ Key Features

| Feature | Description |
|--------|-------------|
| 💬 Chat + LLM | GPT-4o-mini based assistant that handles casual & task-oriented messages |
| 📅 Schedule Task | Multi-channel reminders (WhatsApp, Email, Call) |
| 🔄 Reschedule/Delete | Modify or remove existing tasks with confirmation |
| 🗣 Voice Message | Accept audio, transcribe to text with Whisper, and respond accordingly |
| 👥 Multi-User | Tracks individual chats and tasks using thread-based context |
| 🧰 Assistant Tools | Uses real-time functions inside OpenAI Assistant: `schedule_job`, `delete_task`, `get_pending_tasks` |

---

## 📁 Folder Structure

```
├── app
│   ├── views.py                 # Webhook endpoints
│   ├── decorators/security.py   # Meta signature validation
│   ├── services
│   │   ├── openai_service.py    # Assistant orchestration
│   │   ├── scheduler.py         # Background task scheduler
│   │   ├── notifier.py          # WhatsApp, Email, Call sending
│   ├── utils
│   │   ├── voice_handler.py     # Audio file transcription
│   │   ├── whatsapp_utils.py    # Message formatting & sending
│   │   ├── time_handler.py      # Location + datetime logic
│   │   ├── pending_task.py      # Pending task access
│
├── .env                         # Configuration variables
├── run.py                       # App runner
├── web.py                       # Web debug tool (port 5000)
```

---

## 🚀 Development Journey

### 🔹 Phase 1: Outbound WhatsApp Message
- Used Meta API key and [Daveebbelaar’s repo](https://github.com/daveebbelaar/whatsapp-gpt) as base
- Implemented `send_message()` for outgoing chat

### 🔹 Phase 2: Inbound WhatsApp Message
- Created webhook receiver in `views.py`
- Built logic to parse user messages
- Added voice-to-text support via `Whisper`

### 🔹 Phase 3: LLM Integration (Together.ai)
- Initially used LLaMA3 Turbo from Together.ai (before OpenAI key)
- Stored chat logs in shelve-based DB

### 🔹 Phase 4: Task Tools
- Built WhatsApp, Email, and Call tools in `notifier.py`
- Created `schedule_job()` with APScheduler
- Implemented `status_cache` for tracking per-user job status

### 🔹 Phase 5: OpenAI Upgrade
- Integrated OpenAI Assistant API with `gpt-4o-mini-2024-07-18`
- Rewrote `generate_response()`:
  - Threads per user
  - Timestamp context
  - Real-time assistant tool execution
  - Robust fallback & error handling
- Replaced chat log DB with Assistant’s threads

### 🔹 Phase 6: Final Polish
- Updated response formatting with Markdown → WhatsApp style
- Improved multi-user state management
- Added local test server (`web.py`) on port 5000

---

## 🛠 Tech Stack

- **Python + Flask**  
- **Meta Graph API (WhatsApp)**  
- **OpenAI Assistant API (GPT-4o-mini)**  
- **Whisper (audio to text)**  
- **Twilio (Voice Call)**  
- **APScheduler**  
- **DiskCache & Shelve (Storage)**  
- **dotenv (Secrets)**  

---

## 🔗 Important Links
- 📂 GitHub Repo: [https://github.com/MM21B038/whatsapp-bot](https://github.com/MM21B038/whatsapp-bot)
- 📧 Email: manav26102002@gmail.com
- 📞 Mobile: +91 95163 85315

---

## 🙌 Acknowledgments
- Meta for providing WhatsApp API
- OpenAI for Assistant APIs
- Daveebbelaar’s repo for early scaffolding
- Together.ai (initial free access to LLaMA models)

---

## 📸 Screenshots
_Add screenshots of WhatsApp conversations, scheduling, and reminders here._

---

## 🧪 Local Testing
```
python run.py          # Starts the WhatsApp webhook server
python web.py          # Optional: Debug & see scheduled tasks on localhost:5000
```

---

## ✅ Future Improvements
- Authentication layer
- UI dashboard for non-tech users
- Integration with Google Calendar / Notion
- WhatsApp message templates (interactive replies, buttons)

---
