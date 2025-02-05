import requests

from imgdescgenlib.chatbot.base import ChatbotBase
from imgdescgenlib.chatbot.exceptions import ChatbotHttpRequestFailed, ChatbotPayloadTooLarge

class ChatbotClientBase(ChatbotBase):
    """
    Chatbot base HTTP client 
    """
    def __init__(self):
        self.session = requests.Session()

    def _check_response(self, response: requests.Response):
        """
        Checks if response status is success and raises exception if failed
        """
        if response.status_code != 200:
            if response.status_code == 413:
                # probably image too large
                raise ChatbotPayloadTooLarge(response.status_code)

            raise ChatbotHttpRequestFailed(response.status_code)
