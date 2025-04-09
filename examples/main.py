import json

from imgdescgenlib.exceptions import ImageToolException
from imgdescgenlib.imgdescgen import ImgDescGen
from imgdescgenlib.chatbot.gemini.gemini import GeminiClient, GeminiConfig
from imgdescgenlib.chatbot.exceptions import ChatbotFailed, ChatbotHttpRequestFailed, ChatbotPayloadTooLarge

def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        ...

if __name__ == "__main__":
    # not required to have config.json, you can set environment variables instead
    config = load_json("config.json")
    if config:
        client_config = GeminiConfig.model_validate(config)
    else:
        client_config = GeminiConfig()
    client = GeminiClient(client_config)
    img_desc_gen = ImgDescGen(client)

    try:
        desc = img_desc_gen.generate_image_description(["test.jpg", "test2.jpg"], "processed_images")
    except ChatbotPayloadTooLarge:
        print("Error: payload too large, try image with smaller size")
    except ChatbotHttpRequestFailed as e:
        print(f"Error: http request failed with status code {e._status_code}")
        print(e._text)
    except ChatbotFailed:
        print("Error: chatbot failed")
    except ImageToolException:
        print("Error: image tool failed")

    print(f"Generated description: {desc}")
    