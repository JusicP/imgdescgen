from imgdescgenlib.images import Images

class ChatbotBase():
    """
    Chatbot base class
    """
    def generate_image_description(self, images: Images) -> dict:
        raise NotImplementedError