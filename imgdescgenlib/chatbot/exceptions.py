class ChatbotFailed(Exception):
    pass

class ChatbotHttpRequestFailed(ChatbotFailed):
    def __init__(self, status_code):
        self._status_code = status_code

class ChatbotPayloadTooLarge(ChatbotHttpRequestFailed):
    def __init__(self, status_code):
        super().__init__(status_code)
