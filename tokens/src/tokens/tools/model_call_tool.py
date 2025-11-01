from crewai.tools import tool
import openai

@tool
class OpenAICompatibleTool:
    """Tool for calling OpenAI-compatible LLM endpoints."""
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name

    def _run(self, prompt: str) -> str:
        client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
