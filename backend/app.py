# import os
# import uuid
# from typing import List, Dict, Optional
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import google.generativeai as genai
# from dotenv import load_dotenv

# # 1. Load Environment Variables
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")

# if not API_KEY:
#     raise ValueError("No GEMINI_API_KEY found in .env file")

# genai.configure(api_key=API_KEY)

# # 2. Initialize FastAPI
# app = FastAPI(title="AI Interview Agent Backend")

# # 3. CORS Setup (Crucial for Frontend communication)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins (dev mode only). Change to your GitHub Pages URL in prod.
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 4. In-Memory Storage (Replaces database for this demo)
# # Structure: { "session_id": { "role": "Engineer", "history": [...] } }
# sessions: Dict[str, Dict] = {}

# # 5. Pydantic Models (Data Validation)
# class StartRequest(BaseModel):
#     role: str  # e.g., "Python Developer", "Sales Executive"

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str

# class FeedbackRequest(BaseModel):
#     session_id: str

# # 6. Core Agent Logic
# def get_gemini_response(session_id: str, user_input: Optional[str] = None):
#     """
#     Handles the conversation state and calls Gemini API.
#     """
#     if session_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session ID not found")
    
#     session_data = sessions[session_id]
#     role = session_data["role"]
#     history = session_data["history"]

#     # Initialize Model
#     # We use a system prompt to enforce "Interviewer" behavior
#     system_instruction = f"""
#     You are a professional, detail-oriented Technical Interviewer for a {role} position.
#     Your Goal: Assess the candidate's skills deeply.
    
#     Rules:
#     1. Ask ONE question at a time. Never ask lists of questions.
#     2. If the user's answer is short or vague, ask a follow-up question to clarify.
#     3. Do not be helpful or provide answers. Be neutral and professional.
#     4. Keep your responses concise (max 2-3 sentences) to keep the conversation flowing.
#     5. Start by introducing yourself briefly and asking the first relevant question.
#     """
    
#     model = genai.GenerativeModel(
#         model_name="gemini-1.5-flash", # Or "gemini-2.0-flash" if available to your key
#         system_instruction=system_instruction
#     )

#     # Convert our storage format to Gemini's chat format
#     # Gemini expects: [{'role': 'user', 'parts': [...]}, {'role': 'model', 'parts': [...]}]
#     chat_history = []
#     for msg in history:
#         role_label = "user" if msg["role"] == "user" else "model"
#         chat_history.append({"role": role_label, "parts": [msg["content"]]})

#     # Start Chat Session with history
#     chat_session = model.start_chat(history=chat_history)

#     # Generate Response
#     if user_input:
#         response = chat_session.send_message(user_input)
#         # Update our local history
#         history.append({"role": "user", "content": user_input})
#         history.append({"role": "model", "content": response.text})
#     else:
#         # Initial Greeting (First turn)
#         response = chat_session.send_message("Hello, I am ready for the interview.")
#         history.append({"role": "model", "content": response.text})

#     return response.text

# # 7. API Endpoints

# @app.get("/")
# async def health_check():
#     return {"status": "active", "message": "AI Interview Backend is Running"}

# @app.post("/start_interview")
# async def start_interview(request: StartRequest):
#     """
#     Initializes a new interview session.
#     """
#     session_id = str(uuid.uuid4())
    
#     # Initialize session storage
#     sessions[session_id] = {
#         "role": request.role,
#         "history": []
#     }
    
#     # Generate first question
#     first_question = get_gemini_response(session_id)
    
#     return {
#         "session_id": session_id,
#         "message": first_question
#     }

# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     """
#     Receives user answer and returns AI follow-up question.
#     """
#     response_text = get_gemini_response(request.session_id, request.message)
#     return {"message": response_text}

# @app.post("/end_interview")
# async def end_interview(request: FeedbackRequest):
#     """
#     Analyzes the entire conversation and provides detailed feedback.
#     """
#     if request.session_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session not found")
        
#     session_data = sessions[request.session_id]
    
#     # Evaluation Prompt
#     eval_prompt = f"""
#     The interview for {session_data['role']} has concluded.
#     Here is the transcript:
#     {session_data['history']}
    
#     Please provide a detailed evaluation in JSON format with the following fields:
#     - score (1-10)
#     - strengths (list of strings)
#     - areas_for_improvement (list of strings)
#     - overall_feedback (string)
#     """
    
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(eval_prompt)
    
#     # Cleanup session (optional, or keep for analytics)
#     # del sessions[request.session_id]
    
#     return {"feedback": response.text}

# # Run this file with: uvicorn app:app --reload












































# import os
# import uuid
# from typing import Dict, Optional
# from fastapi import FastAPI, HTTPException, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel

# # Import our custom modules (Ensure agent.py and voice.py exist in the same folder)
# from agent import InterviewAgent
# from voice import speech_to_text, text_to_speech

# app = FastAPI(title="AI Interview Agent Backend")

# # 1. CORS Setup (Crucial for Frontend communication)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 2. In-Memory Storage
# # Stores active interview sessions: { "session_id": InterviewAgent_Instance }
# sessions: Dict[str, InterviewAgent] = {}

# # 3. Data Models
# class StartRequest(BaseModel):
#     role: str

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str

# class FeedbackRequest(BaseModel):
#     session_id: str

# # 4. API Endpoints

# @app.get("/")
# async def health_check():
#     return {"status": "active", "message": "AI Interview Backend is Running"}

# @app.post("/start_interview")
# async def start_interview(request: StartRequest):
#     """
#     Starts a new interview session.
#     """
#     session_id = str(uuid.uuid4())
    
#     # Create a new Agent instance for this user
#     try:
#         new_agent = InterviewAgent(session_id, request.role)
#         sessions[session_id] = new_agent
        
#         # Get the first greeting/question from the AI
#         first_message = new_agent.generate_question(user_input=None)
        
#         # Optional: Convert first message to audio
#         audio_b64 = text_to_speech(first_message)
        
#         return {
#             "session_id": session_id,
#             "message": first_message,
#             "audio": audio_b64
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     """
#     Text-only chat endpoint.
#     """
#     if request.session_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session ID not found")
    
#     agent = sessions[request.session_id]
    
#     # Get AI response
#     response_text = agent.generate_question(request.message)
    
#     # Convert AI response to Audio
#     audio_b64 = text_to_speech(response_text)
    
#     return {
#         "message": response_text,
#         "audio": audio_b64
#     }

# @app.post("/voice_chat")
# async def voice_chat_endpoint(
#     session_id: str = Form(...), 
#     audio_file: UploadFile = File(...)
# ):
#     """
#     Voice-to-Voice endpoint.
#     Receives audio blob -> Transcribes -> Gets AI Response -> Returns Text + Audio.
#     """
#     if session_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session ID not found")

#     # 1. Save temporary audio file
#     temp_filename = f"temp_{session_id}.wav"
#     with open(temp_filename, "wb") as buffer:
#         buffer.write(await audio_file.read())

#     # 2. Transcribe Audio (STT)
#     user_text = speech_to_text(temp_filename)
    
#     # Clean up temp file
#     if os.path.exists(temp_filename):
#         os.remove(temp_filename)

#     if not user_text:
#         return JSONResponse(status_code=400, content={"message": "Could not understand audio"})

#     # 3. Get AI Response
#     agent = sessions[session_id]
#     ai_text = agent.generate_question(user_text)

#     # 4. Convert AI Response to Audio (TTS)
#     ai_audio_b64 = text_to_speech(ai_text)

#     return {
#         "user_transcription": user_text,
#         "message": ai_text,
#         "audio": ai_audio_b64
#     }

# @app.post("/end_interview")
# async def end_interview(request: FeedbackRequest):
#     """
#     Ends the session and generates feedback.
#     """
#     if request.session_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session ID not found")
    
#     agent = sessions[request.session_id]
#     feedback = agent.generate_feedback()
    
#     # Cleanup session
#     del sessions[request.session_id]
    
#     return {"feedback": feedback}

# # Run with: uvicorn app:app --reload












import os
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent import InterviewAgent
from voice import (
    text_to_speech,
    convert_webm_to_wav,
    speech_to_text_from_wav,
)

app = FastAPI(title="AI Interview Agent Backend")

# 1. CORS Setup (for frontend on localhost / GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. In-Memory Sessions
sessions: Dict[str, InterviewAgent] = {}


# 3. Pydantic Models
class StartRequest(BaseModel):
    role: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class FeedbackRequest(BaseModel):
    session_id: str


# 4. API Endpoints
@app.get("/")
async def health_check():
    return {"status": "active", "message": "AI Interview Backend is Running"}


@app.post("/start_interview")
async def start_interview(request: StartRequest):
    """
    Starts a new interview session and returns first question + audio.
    """
    session_id = str(uuid.uuid4())

    try:
        agent = InterviewAgent(session_id, request.role)
        sessions[session_id] = agent

        first_message = agent.generate_question(user_input=None)
        audio_b64 = text_to_speech(first_message)

        return {
            "session_id": session_id,
            "message": first_message,
            "audio": audio_b64,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start interview: {str(e)}",
        )


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles text answer and returns next question + audio.
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session ID not found")

    agent = sessions[request.session_id]
    response_text = agent.generate_question(request.message)
    audio_b64 = text_to_speech(response_text)

    return {
        "message": response_text,
        "audio": audio_b64,
    }


@app.post("/voice_chat")
async def voice_chat_endpoint(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
):
    """
    Voice-to-voice endpoint.
    Browser sends WebM -> convert to WAV -> STT -> Gemini -> TTS -> return.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session ID not found")

    # 1. Save temporary WebM file
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    webm_path = os.path.join(temp_dir, f"{session_id}.webm")

    with open(webm_path, "wb") as buffer:
        buffer.write(await audio_file.read())

    # 2. Convert WebM -> WAV
    wav_path = convert_webm_to_wav(webm_path)
    if not wav_path:
        if os.path.exists(webm_path):
            os.remove(webm_path)
        return JSONResponse(
            status_code=400,
            content={"message": "Could not convert audio file"},
        )

    # 3. STT on WAV
    user_text = speech_to_text_from_wav(wav_path)

    # Cleanup temp files
    if os.path.exists(webm_path):
        os.remove(webm_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)

    if not user_text:
        return JSONResponse(
            status_code=400,
            content={"message": "Could not understand audio"},
        )

    # 4. Get AI response from transcript
    agent = sessions[session_id]
    ai_text = agent.generate_question(user_text)

    # 5. TTS for AI response
    ai_audio_b64 = text_to_speech(ai_text)

    return {
        "user_transcription": user_text,  # frontend will show as user chat
        "message": ai_text,               # bot reply
        "audio": ai_audio_b64,           # bot voice
    }


@app.post("/end_interview")
async def end_interview(request: FeedbackRequest):
    """
    Ends the session and returns feedback.
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session ID not found")

    agent = sessions[request.session_id]
    feedback = agent.generate_feedback()

    # Optional: delete session
    del sessions[request.session_id]

    return {"feedback": feedback}
