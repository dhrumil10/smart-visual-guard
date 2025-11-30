
# 🛡️ Smart Visual Guard

Smart Visual Guard is an AI-powered home safety assistant that watches your camera feeds, detects critical events (fire, baby safety issues, and unauthorized intrusion), and sends intelligent alerts to your phone.  
Under the hood it uses computer vision + a multi-agent RAG system to not only detect *what* happened, but also tell you *what to do next*.

---

## ✨ Key Features (planned)

- 🔥 **Fire / Smoke Detection** – detect potential indoor fires from camera feeds.
- 👶 **Baby Monitoring** – watch a crib zone and alert if the baby is missing or unusual activity is detected.
- 🚶‍♂️ **Intrusion Detection** – detect people entering restricted areas (e.g., door, backyard).
- 🤖 **Multi-Agent RAG Brain**
  - Event triage (is this really critical?).
  - Fetches safety guidance from a small knowledge base (RAG).
  - Generates human-readable alerts and summaries.
- 📲 **Notifications**
  - Send alerts to mobile / messaging apps (e.g., email or Telegram).
- 📊 **Event History**
  - Store events + snapshots for review.

> This project is a learning playground for: **FastAPI**, **computer vision**, and **agentic/RAG pipelines**.

---

## 🧠 High-Level Architecture

```text
[ Cameras / RTSP Streams ]
               |
               v
      [ Vision Worker ]
      - OpenCV + YOLO
      - Fire/Baby/Intrusion logic
               |
               v
        [ Core API (FastAPI) ]
      - Receives events
      - Stores events in DB
      - Calls multi-agent RAG
               |
               v
     [ Multi-Agent + RAG Layer ]
      - Triage agent
      - Guidance agent (RAG over safety docs)
      - Summary agent
               |
               v
       [ Notification Layer ]
      - Email / Telegram / Push
               |
               v
       [ User Client (Web/Mobile) ]





<img width="1536" height="1024" alt="ChatGPT Image Nov 30, 2025, 03_18_06 PM" src="https://github.com/user-attachments/assets/e5560ede-c6c1-4e8f-a1f7-7665f8f867a0" />
