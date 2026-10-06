from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class GroqLLMWrapper:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def invoke(self, prompt):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_completion_tokens=2048,
            top_p=1,
            stream=False,
            stop=None
        )
        content = completion.choices[0].message.content or ""
        return type('Response', (), {'content': content})()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is missing or invalid in .env file. AI analysis cannot proceed.")
    client = Groq(api_key=api_key)
    return GroqLLMWrapper(client, "openai/gpt-oss-120b")
