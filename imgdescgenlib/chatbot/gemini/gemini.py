import json

from pydantic import BaseModel

from imgdescgenlib.chatbot.client_base import ChatbotClientBase

from pydantic_settings import BaseSettings, SettingsConfigDict

class GeminiConfig(BaseSettings):
    """
    Gemini config class, used to store API key and other settings.
    """
    model_config = SettingsConfigDict(env_prefix='GEMINI_')

    api_key: str = ""
    # TODO: write image schema from GeminiImageDescription
    image_description_prompt: str = 'Write a detailed description and key words of the each image, ' \
                'with this JSON schema: Image = {"description": str, "keywords": list[str]} Return: list[Image]}.'

class GeminiImageDescription(BaseModel):
    """
    Gemini image description class, used to store image metadata.
    """
    description: str
    keywords: list[str]

class GeminiClient(ChatbotClientBase):
    """
    Gemini client, requires API key to work.
    """
    def __init__(self, config: GeminiConfig):
        self._config = config

        super().__init__()

    def _get_chatbot_dictionary_response(self, response_json: str) -> list[GeminiImageDescription]:
        """
        Parses chatbot response from JSON string.
        Extracts JSON object with image metadata: general description and list of keywords and converts it to dict type.

        Returns dictionary.
        """
        return json.loads(response_json["candidates"][0]["content"]["parts"][0]["text"])

    def generate_image_description(self, imgs_base64: list[str]) -> dict:
        """
        Sends generateContent request to Gemini to generate JSON object that contains image metadata: general description and list of keywords 
        Accepts list of base64 encoded jpeg images or single object.
        """

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": self._config.image_description_prompt,
                    },
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json", # specify json response to get just json string without markdown
            }
        }

        for img_base64 in imgs_base64:
            payload["contents"][0]["parts"].append(
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": img_base64
                    }
                }
            )

        response = self.session.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self._config.api_key}", headers=headers, json=payload)
        self._check_response(response)

        return self._get_chatbot_dictionary_response(response.json())