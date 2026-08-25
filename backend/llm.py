from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is missing or invalid in .env file. AI analysis cannot proceed.")
    
    return ChatGroq(
        groq_api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0.2
    )