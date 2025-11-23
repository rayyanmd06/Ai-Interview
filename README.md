> **"Your personal, intelligent voice-based interview coach."**

***

## 🌟 Project Overview

**AI Interview Partner** is a cutting-edge, real-time conversational agent designed to simulate realistic job interviews. Built with **FastAPI** and **Google's Gemini AI**, it acts as an empathetic yet rigorous interviewer that adapts to your chosen role (e.g., "Python Developer", "Product Manager").

### 🎯 Our Mission
To democratize interview preparation by providing a free, accessible, and highly intelligent tool that helps students and professionals build confidence, improve communication, and land their dream jobs.

### ✨ Key Features
*   **🗣️ Voice-First Interaction:** Talk naturally with the AI using Push-to-Talk (PTT) or Continuous Mode.
*   **🧠 Context-Aware:** The AI remembers your previous answers and asks relevant follow-up questions.
*   **📊 Detailed Feedback:** Receive a structured performance report (Strengths, Weaknesses, Score) at the end.
*   **🎨 Immersive UI:** A stunning, galaxy-themed glassmorphism interface for a focused experience.
*   **⚡ Low Latency:** Optimized audio processing for near-instant conversational turns.

***

## 🛠️ Prerequisites

Before you blast off, ensure you have the following installed:

1.  **Python 3.9+**: [Download Here](https://www.python.org/downloads/)
2.  **Git**: [Download Here](https://git-scm.com/downloads)
3.  **Google Gemini API Key**: Get it free from [Google AI Studio](https://aistudio.google.com/).
4.  **FFmpeg**: Required for audio processing.
    *   *Windows:* Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, and add the `bin` folder to your System PATH.

***

## ⚙️ Installation Guide

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-interview-partner.git
cd ai-interview-partner
```

### 2. Create a Virtual Environment
It's best practice to isolate project dependencies.

**🪟 Windows (CMD/PowerShell):**
```powershell
python -m venv venv
# Activate it:
venv\Scripts\activate
```

**🍎 Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
We use `pip` to install all required Python libraries.
```bash
pip install -r requirements.txt
```

> **📝 Note:** If you don't have a `requirements.txt` yet, create one with these contents:
> `fastapi uvicorn python-multipart google-generativeai gTTS pydub SpeechRecognition python-dotenv`

### 4. Configure Environment Variables
Create a `.env` file in the root directory (where `main.py` is) to keep your API key safe.

```ini
# .env file
GEMINI_API_KEY=your_actual_api_key_here
```

***

## 🚀 How to Run the Application

### Step 1: Start the Backend Server
Open your terminal (CMD/PowerShell), ensure your virtual environment is active `(venv)`, and run:

```bash
uvicorn main:app --reload
```
*   You should see: `INFO: Uvicorn running on http://127.0.0.1:8000`
*   Keep this terminal **OPEN** and running.

### Step 2: Launch the Frontend 🌐
1.  Navigate to the `frontend` folder in your file explorer.
2.  **Double-click** on `index.html` to open it in your default browser (Chrome/Edge recommended for voice support).
3.  Alternatively, if using VS Code, right-click `index.html` and select **"Open with Live Server"**.

***

## 🎮 How to Use

1.  **Enter Your Role:** On the welcome screen, type the job role you want to practice (e.g., "Data Scientist").
2.  **Start Interview:** Click the **"Start Interview"** button. The screen will transition to the chat interface.
3.  **Speak or Type:**
    *   **🎤 Voice:** Click the **Mic** button (or use Push-to-Talk if configured) to speak your answer. The AI will listen and respond vocally.
    *   **⌨️ Text:** Type your answer in the box and hit Enter.
4.  **End & Review:** When you're done, click **"End Interview"**. The AI will generate a comprehensive **Feedback Report** grading your performance.

***

## 📂 Project Structure

```
ai-interview-partner/
├── 📂 backend/             # Python Logic
│   ├── main.py             # FastAPI Server & Routes
│   ├── interview_agent.py  # Gemini AI Logic & Prompts
│   ├── voice.py            # TTS (Text-to-Speech) & STT Logic
│   └── .env                # API Keys (Hidden)
├── 📂 frontend/            # User Interface
│   ├── index.html          # Main Structure
│   ├── style.css           # Glassmorphism Styling
│   ├── script.js           # Logic & API Calls
│   └── 📂 assets/          # Background videos/images
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

***

## 🤝 Contribution

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

***

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

***

<div align="center">

**Made with ❤️ by Rayyan**  
*Empowering careers through AI.*

</div>
```

### **How to use this:**
1.  Create a file named `README.md` in your project folder.
2.  Copy the entire code block above.
3.  Paste it into the file and save.
4.  It will render beautifully on GitHub with the badges, sections, and formatting