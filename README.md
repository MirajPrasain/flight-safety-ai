# 🛫 AirPilot — AI Copilot for Crash Prevention

> An AI-driven system that simulates real aircraft incidents and generates life-saving advice — powered by MongoDB, LangChain, and Google Cloud.

---

## 🌍 Problem

Every year, hundreds of lives are lost due to preventable aircraft incidents. Human error, miscommunication, and slow reaction times are often contributing factors. What if AI could provide real-time, actionable pilot guidance during those moments?

---

## 💡 Solution

**AirPilot** simulates 5 real-world aviation crashes using historical data stored in MongoDB and generates AI-driven pilot advice that could have changed the outcome.

- 🧠 LangChain + LLM-generated recommendations
- 📊 MongoDB stores detailed crash data
- 🗣️ Voice Agent delivers real-time cockpit instructions
- ☁️ Designed to run on Google Cloud

---

## ✈️ Features

- [x] Web app interface with dropdown to select 5 real crashed flights
- [x] FastAPI backend with structured aviation telemetry
- [x] MongoDB integration for storing and querying crash data
- [x] LangChain chains for emergency advice and risk explanation
- [x] Text-to-speech pilot assistant (voice agent)
- [x] CLI + Web frontend support

---

## 🛠 Tech Stack

| Layer       | Tools |
|-------------|-------|
| Frontend    | HTML / JS / React (TBD) |
| Backend     | FastAPI |
| AI Chains   | LangChain, LLM (LLaMA3 / OpenAI) |
| Voice Agent | pyttsx3 / Google TTS |
| Database    | MongoDB Atlas |
| Cloud       | Google Cloud (App Engine / Cloud Run) |

---

## 📂 Project Structure

AirPilot/
├── backend/
│ ├── main.py # FastAPI backend entry
│ ├── models.py # Pydantic schemas
│ ├── database.py # MongoDB connection
│ ├── langchain_utils.py # LangChain chains & prompt logic
│ └── config.py # Secrets, constants
├── demo_cli.py # CLI to simulate flight scenarios
├── requirements.txt
├── .gitignore
├── .env (ignored)
├── README.md



---

## 🧪 How to Run

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/AirPilot.git
cd AirPilot