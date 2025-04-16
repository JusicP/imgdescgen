from imgdescgenlib.exceptions import ImgDescGenBaseException

# FIXME: should it inherit ImgDescGenBaseException?
class ChatbotFailed(ImgDescGenBaseException):
    pass

class ChatbotHttpRequestFailed(ChatbotFailed):
    def __init__(self, status_code, text):
        super().__init__(f"HTTP request failed with status code {status_code}: {text}")

        self._status_code = status_code
        self._text = text

class ChatbotPayloadTooLarge(ChatbotHttpRequestFailed):
    pass