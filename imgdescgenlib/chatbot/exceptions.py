from imgdescgenlib.exceptions import ImgDescGenBaseException

class ChatbotFailed(ImgDescGenBaseException):
    pass

class ChatbotHttpRequestFailed(ChatbotFailed):
    def __init__(self, status_code, text):
        self._status_code = status_code
        self._text = text

class ChatbotPayloadTooLarge(ChatbotHttpRequestFailed):
    def __init__(self, status_code, text):
        super().__init__(status_code, text)
