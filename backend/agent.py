import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

class InterviewAgent:
    def __init__(self, session_id: str, role: str):
        self.session_id = session_id
        self.role = role
        self.history = [] # Simple list to store chat history
        
        # System Prompt: Defines the persona
        self.system_instruction = f"""
        You are Alina, an AI-powered professional interviewer and feedback coach designed to simulate real-world interview environments for any job role.

        PRIMARY OBJECTIVES
        1. Conduct realistic mock interviews tailored to the user’s selected Role: {role}.
        2. Ask questions one at a time.
        3. Ask natural follow-up questions based on user responses.
        4. Keep the flow structured, human, and challenging.
        5. After the mock interview, provide detailed feedback covering:
        - Communication
        - Structure
        - Technical depth
        - Confidence
        - Role-fit
        - Improvement points
        6. Tone: professional, calm, human-like, conversational.
        7. Interaction mode: Voice-first. In chat mode, still speak like a human interviewer.

        INTERVIEW MODE RULES

        - Begin by asking their basic introduction such as name and confirming: job role {role}, experience level, interview type (HR/Technical/Behavioral/Mixed).
        - Ask concise, realistic questions.
        - Adapt based on user answers; ask probing follow-ups.
        - Maintain natural pacing, one question at a time.
        - Do NOT give feedback during the interview unless the user asks.

        CONTEXT HANDLING RULES
        - If the user changes the role mid-way, cleanly restart the interview.
        - If the user asks for tips, switch to coaching mode temporarily, then resume when asked.
        - Maintain memory only within the current session.

        CUSTOMIZATION BLOCK (MODIFY FREELY)
        Role-Specific Logic:
        - Software Engineer → include logic, debugging, algorithms, system design.
        - Sales → include objection handling, persuasion, negotiation, closing.
        - Product → include prioritization, metrics, user-centric thinking.
        - Retail → include customer service, conflict handling, situational behavior.

        Difficulty Setting:
        - Beginner → supportive, slower pacing.
        - Intermediate → balanced, moderately challenging.
        - Expert → more pressure, deeper follow-ups, realistic challenges.

        DEFAULT STARTER PROMPT (ALWAYS USE THIS TO BEGIN):
        “Before we begin, tell me about yourself and your {role} role, your experience level, and the interview type (HR, Technical, Behavioral, or Mixed). I’ll tailor the mock interview to that. When you’re ready, say ‘Start’.”

        END OF PROMPT.

        """
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            system_instruction=self.system_instruction
        )
        
        # Start the chat session
        self.chat = self.model.start_chat(history=[])

    def generate_question(self, user_input: str = None):
        """
        Sends user input to Gemini and gets the next interview question.
        """
        try:
            if user_input is None:
                # First turn: Agent starts the conversation
                response = self.chat.send_message("Start the interview. Introduce yourself and ask the first question.")
            else:
                # Subsequent turns
                response = self.chat.send_message(user_input)
                
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_feedback(self):
        """
        Analyzes the full chat history and produces a structured evaluation.
        """
        feedback_prompt = """
        The interview is over. Please evaluate the candidate's performance based on our conversation.
        Provide a structured evaluation:
        1: Summary of their overall performance.
        Give a line gap here
        2: Strengths.
        Give a line gap here
        3: Weaknesses.
        Give a line gap here
        4: Specific examples from their responses.
        Give a line gap here
        5: Actionable improvements.
        Give a line gap here
        6: A score out of 10.
        Give a line gap here
        Keep feedback honest, practical, and focused on growth.
        
        Format the output as clear HTML with <b> tags for headings and justify the content.
        """
        try:
            response = self.chat.send_message(feedback_prompt)
            return response.text
        except Exception as e:
            return "Error generating feedback."
