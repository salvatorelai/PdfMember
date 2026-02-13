from openai import OpenAI
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = "gpt-3.5-turbo"

    def configure(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_summary(self, text: str, prompt_template: str = None) -> str:
        if not self.client:
            logger.warning("AI client not configured")
            return "AI Summary not available (Configuration missing)."
            
        if not text.strip():
            return "No text content to analyze."

        try:
            default_prompt = "Please analyze the following book content and provide a concise summary and key takeaways:"
            prompt = f"{prompt_template or default_prompt}\n\n{text[:10000]}" # Limit context
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            return f"AI Generation failed: {str(e)}"

ai_service = AIService()
