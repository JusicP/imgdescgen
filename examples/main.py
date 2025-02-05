import os

from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.chatbot.gemini import GeminiClient
from imgdescgenlib.chatbot.exceptions import ChatbotFailed, ChatbotHttpRequestFailed, ChatbotPayloadTooLarge

if __name__ == "__main__":
    # usage example
    api_key = os.environ.get('GEMINI_API_KEY')

    img_desc_gen = ImgDescGen(GeminiClient(api_key))

    try:
        desc = img_desc_gen.generate_image_description("test.jpg")
    except ChatbotPayloadTooLarge:
        print("Error: payload too large, try image with smaller size")
    except ChatbotHttpRequestFailed as e:
        print(f"Error: http request failed with status code {e._status_code}")
    except ChatbotFailed:
        print(f"Error: chatbot failed")

    print(f"Generated description: {desc}")
    