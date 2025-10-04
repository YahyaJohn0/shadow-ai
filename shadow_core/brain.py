# shadow_core/brain.py
import os
from config import OPENAI_API_KEY
from openai import OpenAI
import asyncio

class ShadowBrain:
    """
    Simple wrapper for OpenAI chat usage.
    Extend this class to add Groq/other fallback providers and tool routing.
    """
    def __init__(self, model="gpt-4o-mini"):
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set in environment (.env)")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model

    async def ask(self, messages, max_tokens=600):
      """
        messages: list of dicts like [{"role":"user","content":"..."}]
       """
      resp = await asyncio.to_thread(
        lambda: self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens
        )
    )
    # Fixed: access .content of ChatCompletionMessage
      choice = resp.choices[0].message
      return choice.content  # <-- changed from choice["content"]

    async def think(self, user_text, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_text})
        return await self.ask(messages)
