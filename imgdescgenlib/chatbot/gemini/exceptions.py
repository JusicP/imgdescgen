from imgdescgenlib.chatbot.exceptions import ChatbotFailed

class GeminiFailed(ChatbotFailed):
    """
    Gemini failed exception.
    """
    pass

class GeminiModelRequired(GeminiFailed):
    """
    Gemini model required exception.
    """
    pass
