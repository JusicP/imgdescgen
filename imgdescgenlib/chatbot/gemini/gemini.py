from imgdescgenlib.chatbot.client_base import ChatbotClientBase
from imgdescgenlib.chatbot.gemini.exceptions import GeminiModelRequired
from imgdescgenlib.chatbot.gemini.schemas import (
    GeminiConfig,
    GeminiModelListResponse,
    GeminiGenerateContentResponse
)
from imgdescgenlib.images import Images
from imgdescgenlib.schemas import ImageDescription

from pydantic import TypeAdapter

class GeminiClient(ChatbotClientBase):
    """
    Gemini client, requires API key to work.
    """
    BASE_URL = "https://generativelanguage.googleapis.com"

    def __init__(self, config: GeminiConfig = None):
        if not config:
            config = GeminiConfig()
        self._config = config

        super().__init__()

    def _get_chatbot_structured_output(self, response: GeminiGenerateContentResponse) -> list[ImageDescription]:
        """
        Extracts JSON object with image metadata from response dict: general description and list of keywords and converts it to dict type.

        Returns list[ImageDescription].
        """
        adapter = TypeAdapter(list[ImageDescription])
        return adapter.validate_json(
            response.candidates[0].content["parts"][0]["text"]
        )

    def get_available_models(self) -> GeminiModelListResponse:
        """
        Returns list of available and supported by library models from Gemini API.
        Notes: 
            - available doesn't mean that they are available for your API key.
            - supported means that they support generation methods: generateContent and countTokens.
        """
        response = self.session.get(
            f"{self.BASE_URL}/v1beta/models?key={self._config.api_key}",
        )

        self._check_response(response)

        model_list_response = GeminiModelListResponse(**response.json())
        return model_list_response.get_supported_models()

    def get_config(self) -> GeminiConfig:
        """
        Returns config object.
        """
        return self._config

    # def _upload_image(self, image: Image) -> str:
    #         """
    #         Uploads image to the Gemini storage using media.load method of the File API and returns URL.
    #         """
    #         if not self._config.model_name:
    #             raise GeminiModelRequired

    #         image_buffer = image.save_to_buffer()
    #         image_len = image_buffer.getbuffer().nbytes

    #         headers = {
    #             "X-Goog-Upload-Protocol": "resumable",
    #             "X-Goog-Upload-Command": "start",
    #             "X-Goog-Upload-Header-Content-Length": str(image_len),
    #             "X-Goog-Upload-Header-Content-Type": "image/jpeg",
    #             "Content-Type": "application/json"
    #         }
    #         metadata = {
    #             "file": {
    #                 "display_name": image.get_filename()
    #             }
    #         }

    #         res = self.session.post(
    #             f"{self.BASE_URL}/upload/v1beta/files?key={self._config.api_key}",
    #             headers=headers,
    #             json=metadata
    #         )

    #         upload_url = res.headers.get("X-Goog-Upload-URL")
    #         if not upload_url:
    #             raise Exception("Failed to get upload URL")

    #         upload_headers = {
    #             "Content-Length": str(image_len),
    #             "X-Goog-Upload-Offset": "0",
    #             "X-Goog-Upload-Command": "upload, finalize"
    #         }

    #         res = self.session.post(upload_url, headers=upload_headers, data=image_buffer.getbuffer())
    #         res_json = res.json()

    #         file_uri = res_json["file"]["uri"]
    #         return file_uri

    def generate_image_description(self, images: Images) -> dict:
        """
        Sends generateContent request to Gemini to generate JSON object that contains image metadata: general description and list of keywords 
        """
        if not self._config.model_name:
            raise GeminiModelRequired

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

        total_size = images.calculate_size()
        # TODO: take out size constraints to config

        # if total image size > 20mb, upload files to the server and get urls
        if total_size > 20*1024*1024: # 20mb
            raise NotImplementedError
            # for img in images._images:
            #     img_uri = self._upload_image(img)
            #     payload["contents"][0]["parts"].append(
            #         {
            #             "file_data": {
            #                 "mimeType": "image/jpeg",
            #                 "file_uri": img_uri
            #             }
            #         }
            #     )
        else:
            imgs_base64 = images.encode_base64()
            for img_base64 in imgs_base64:
                payload["contents"][0]["parts"].append(
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_base64
                        }
                    }
                )

        response = self.session.post(
            f"{self.BASE_URL}/v1beta/{self._config.model_name.name}:generateContent?key={self._config.api_key}",
            headers=headers,
            json=payload
        )
        self._check_response(response)

        response_model = GeminiGenerateContentResponse(**response.json())
        if response_model.candidates[0].finishReason != "STOP":
            raise Exception(f"Gemini stopped to generate tokens: {response_model.candidates[0].finishReason}")

        return self._get_chatbot_structured_output(response_model)