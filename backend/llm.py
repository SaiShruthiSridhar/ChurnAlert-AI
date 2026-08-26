from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


class GroqLLMWrapper:
    """
    Thin wrapper around the Groq client to keep the .invoke() interface
    that agent.py and app.py already use (response.content).
    Matches the playground call exactly — including reasoning_effort.
    """

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def invoke(self, prompt: str):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None,
        )
        return GroqResponse(completion.choices[0].message.content)


class GroqResponse:
    """Mimics LangChain AIMessage so response.content works everywhere."""

    def __init__(self, content: str):
        self.content = content


def get_llm() -> GroqLLMWrapper:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is missing or invalid in .env file. "
            "AI analysis cannot proceed."
        )
    client = Groq(api_key=api_key)
    return GroqLLMWrapper(client=client, model="openai/gpt-oss-120b")