import requests

from imgdescgenlib.chatbot.base import ChatbotBase

class ChatbotRequestFailed(Exception):
    pass

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
            raise ChatbotRequestFailed
