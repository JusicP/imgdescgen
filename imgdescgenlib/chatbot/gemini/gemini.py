from imgdescgenlib.chatbot.client_base import ChatbotClientBase
from imgdescgenlib.chatbot.exceptions import ChatbotFailed
from imgdescgenlib.chatbot.gemini.exceptions import GeminiModelRequired
from imgdescgenlib.chatbot.gemini.schemas import (
    GeminiConfig,
    GeminiFileListResponse,
    GeminiModelListResponse,
    GeminiGenerateContentResponse
)
from imgdescgenlib.image import Image
from imgdescgenlib.images import Images
from imgdescgenlib.schemas import ImageDescription

from pydantic import TypeAdapter

import logging
import base64
import hashlib
from io import BytesIO

logger = logging.getLogger("chatbotclient")
logger.setLevel(logging.getLogger().getEffectiveLevel())

class GeminiClient(ChatbotClientBase):
    """
    Gemini client, requires API key to work.
    """
    BASE_URL = "https://generativelanguage.googleapis.com"

    def __init__(self, config: GeminiConfig = None):
        super().__init__()

        if not config:
            config = GeminiConfig()
        self._config = config

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

    def _uploaded_files(self) -> GeminiFileListResponse:
        """
        Returns list of all files in Gemini storage.
        """
        headers = {
            "Content-Type": "application/json"
        }
        response = self.session.get(
            f"{self.BASE_URL}/v1beta/files?key={self._config.api_key}",
            headers=headers
        )
        self._check_response(response)

        return GeminiFileListResponse(**response.json())

    def _upload_image(self, image_buffer: BytesIO, image_filename: str) -> str:
        """
        Uploads image to the Gemini storage using media.load method of the File API and returns URL.
        """
        if not self._config.model_name:
            raise GeminiModelRequired

        image_len = image_buffer.getbuffer().nbytes

        headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(image_len),
            "X-Goog-Upload-Header-Content-Type": "image/jpeg",
            "Content-Type": "application/json"
        }
        metadata = {
            "file": {
                "display_name": image_filename
            }
        }

        res = self.session.post(
            f"{self.BASE_URL}/upload/v1beta/files?key={self._config.api_key}",
            headers=headers,
            json=metadata
        )

        upload_url = res.headers.get("X-Goog-Upload-URL")
        if not upload_url:
            raise ChatbotFailed("Failed to get upload URL")

        upload_headers = {
            "Content-Length": str(image_len),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize"
        }

        res = self.session.post(upload_url, headers=upload_headers, data=image_buffer.getbuffer())
        res_json = res.json()

        return res_json["file"]["uri"]

    def generate_image_description(self, images: Images) -> list[ImageDescription]:
        """
        Sends generateContent request to Gemini to generate JSON object that contains image metadata: general description and list of keywords 
        """
        if not self._config.model_name:
            raise GeminiModelRequired("Model name is required to use Gemini.")

        if self._config.max_image_count < len(images._images):
            raise ChatbotFailed(
                f"Max image count is {self._config.max_image_count}, but got {len(images._images)}. " \
                "Adjust this value in config if specification is changed: https://ai.google.dev/gemini-api/docs/vision?lang=rest#technical-details-image"
            )

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

        logger.debug(f"Total image size: {total_size} bytes")

        # if total image size > 20mb, upload files to the server and get urls
        if self._config.force_upload or total_size > 20*1024*1024: # 20mb
            logger.info(f"Total image size > 20mb, uploading files to the server")

            response = self._uploaded_files()

            # find image by hash or upload
            for img in images._images:
                buf = img.save_to_buffer()

                img_sha256Hash = base64.b64encode(hashlib.sha256(buf.getvalue()).hexdigest().encode()).decode('utf-8')
                img_uri = next(
                    (file.uri for file in response.files if file.sha256Hash == img_sha256Hash),
                    None
                )

                if not img_uri:
                    logger.debug(f"Image {img.get_filename()} doesn't exists on the server, uploading")
                    img_uri = self._upload_image(buf, img.get_filename())
                    assert img_uri
                    # what if upload fails
                else:
                    logger.debug(f"Image {img.get_filename()} already exists on the server, using existing uri")

                payload["contents"][0]["parts"].append(
                    {
                        "file_data": {
                            "mimeType": "image/jpeg",
                            "file_uri": img_uri
                        }
                    }
                )
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
            raise ChatbotFailed(f"Gemini stopped to generate tokens: {response_model.candidates[0].finishReason}")

        return self._get_chatbot_structured_output(response_model)