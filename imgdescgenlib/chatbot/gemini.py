import json

from imgdescgenlib.chatbot.client_base import ChatbotClientBase

class GeminiClient(ChatbotClientBase):
    """
    Gemini client, requires API key to work.
    """
    def __init__(self, api_key: str):
        self._api_key = api_key

        super().__init__()

    def _get_chatbot_dictionary_response(self, response_json: str) -> dict:
        """
        Parses chatbot response from JSON string.
        Extracts JSON object with image metadata: general description and list of keywords and converts it to dict type.

        Returns dictionary.
        """
        return json.loads(response_json["candidates"][0]["content"]["parts"][0]["text"])

    def generate_image_description(self, img_base64: str) -> dict:
        """
        Sends generateContent request to Gemini to generate JSON object that contains image metadata: general description and list of keywords 
        Accepts base64 encoded jpeg image.
        """

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": 'Write a detailed description and key words of the image, with this schema: {"description": str, "keywords": list[str]}"}.'
                    },
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json", # specify json response to get just json string without markdown
            }
        }

        response = self.session.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self._api_key}", headers=headers, json=payload)
        self._check_response(response)

        return self._get_chatbot_dictionary_response(response.json())