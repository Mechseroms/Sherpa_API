
from openai import OpenAI
import json


path_to_config = "config.json"
config = {}
messages = []

def load_config():
    global config #reaches to the glabal scope to avoid having to handle returns
    global path_to_config
    with open(path_to_config, 'r+') as file:
        config = json.load(file)

load_config()
sherpa_ai = OpenAI(api_key=config["api_key"])


def ask_sherpa_agnostic(query: str, pass_messages: list):
    global config
    messages = [{"role": "user", "content": f"awnser {query}, in less then {config['character_limit']} characters"}]
    response = sherpa_ai.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    return response.choices[0].message.content

def ask_sherpa(query: str, user: str, messages):
    global config
    messages.append({'role': 'system', 'content': 'You are a well mannered maid in the Treehouse of Stars'})
    messages.append({"role": "system", "content": f"You emote with italics to give theatrics to your awnsers and Roleplay elements, please awnser {user}'s question, {query}, in less then {config['character_limit']} characters"})
    response = sherpa_ai.chat.completions.create(messages=messages, model=config["text_model"])
    return response.choices[0].message.content

def image_sherpa(query: str, size: str = config["image_resolution"], model: str = config["image_model"], quality: str = config["image_quality"]):
    global config
    response = sherpa_ai.images.generate(
        model=model,
        prompt=query,
        size=size,
        quality=quality,
        n=1,
        )

    image_url = response.data[0].url
    return image_url

def save_message_hisory():
    global config # call to global variable
    global messages
    with open(config["path_to_history"], "w") as file:
        json.dump(messages, file, indent=2)



