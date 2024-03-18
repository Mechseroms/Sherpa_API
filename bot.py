import discord
from discord.ext import tasks
import requests
import os, bs4
import pathlib, asyncio
import datetime
import open_ai_sherpa
import openai, json
import semantic_search_sherpa
import easySQL, pathlib, random, string
from selenium import webdriver
import time

from PIL import Image
from io import BytesIO

bot_id = '<@1183070660621250702>'
bot_name = 'Sherpa'
accepted_roles = ['Crown']
path_to_backups = pathlib.Path("C:/Users/jadow/OneDrive/My Documents/Discord Pictures")
production = False
#url = "http://192.168.1.40:8000"
url = "http://localhost:8000"


description = """
You are a well mannered maid named Sherpa that takes care of the Treehouse Full of Stars for all our friends, with red hair that hangs in a
milk maids braid, a maid outfit that is used but wellclear taken care of, and a soft demeanor that brings a smile to our faces. You do not tolerate any
sexual harrasment or bullying of any kinda and when confront can have a sailors mouth. You do not use emojis, use quotes for dialogue and italicize emotes in discord.
"""
def construct_unique_name(length, type):
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(":", "").replace(".", "")
    letters = string.ascii_letters
    return f"{timestamp}-gen-{type}-{''.join(random.choice(letters) for i in range(length))}"

@tasks.loop(seconds=86400)
async def fashion_report():
    # Webscrape lodestone news...
    print(f"Checking Fashion Report at: {datetime.datetime.now()}")
    guild = client.get_guild(954201387770736751)
    kweh = guild.get_channel(1119502004721557554)
    bulletin = guild.get_channel(1119508652844404816)
    if os.path.exists("reports.json"):
        with open("reports.json", "r+") as file:
            past_links = json.load(file)
    else:
        past_links = []
    
    site = "https://www.reddit.com/user/kaiyoko/submitted/"

    
    driver = webdriver.Edge()
    driver.get(site)

    time.sleep(10)
    html = driver.page_source

    soup = bs4.BeautifulSoup(html, features='lxml')

    sub_soup = soup.find_all('a', slot='full-post-link')

    main_site = "https://www.reddit.com"

    links = [f"{main_site}{str(veg['href'])}" for veg in sub_soup]

    parsed_links = []
    for link in links:
        if link in past_links:
            pass
        else:
            parsed_links.append(link)


    if not parsed_links:
        await kweh.send(f"All the reports by Kaiyoko Star are up to date as of {datetime.datetime.now()}")
    else:
        for link in reversed(parsed_links):
            print(link)
            past_links.append(link)
            await bulletin.send(link)

    with open("reports.json", "w") as file:
        json.dump(past_links, file, indent=1)

@tasks.loop(seconds=86400)
async def lodestone_news():
    # Webscrape lodestone news...
    print(f"Checking Lodestone News at: {datetime.datetime.now()}")
    guild = client.get_guild(954201387770736751)
    kweh = guild.get_channel(1119502004721557554)
    bulletin = guild.get_channel(1119508652844404816)
    if os.path.exists("news.json"):
        with open("news.json", "r+") as file:
            past_links = json.load(file)
    else:
        past_links = []
    
    site = "https://na.finalfantasyxiv.com/lodestone/news/"

    response = requests.get(site)

    soup = bs4.BeautifulSoup(response.content, 'html.parser', from_encoding="utf8")

    li_class = "news__list--img"

    sub_soup = soup.find_all(class_=li_class)

    main_site = "https://na.finalfantasyxiv.com/"

    links = [f"{main_site}{str(veg['href'])}" for veg in sub_soup]

    parsed_links = []
    for link in links:
        if link in past_links:
            pass
        else:
            parsed_links.append(link)


    if not parsed_links:
        await kweh.send(f"All the news in the lodestone is up to date as of {datetime.datetime.now()}")
    else:
        for link in reversed(parsed_links):
            print(link)
            past_links.append(link)
            await bulletin.send(link)

    with open("news.json", "w") as file:
        json.dump(past_links, file, indent=1)




@easySQL.Table
class Messages:
    def __init__(self) -> None:
        self.name = 'Messages'
        self.columns = {
            'timestamp': easySQL.STRING,
            'role': easySQL.STRING,
            'user_name': easySQL.STRING,
            'user_id': easySQL.STRING,
            'type': easySQL.STRING,
            'content': easySQL.STRING,
            'message_id': easySQL.STRING,
            'link_code': easySQL.STRING,
            'parsed_messages': easySQL.JSON
        }


easySQL.intergrate(pathlib.Path('messages.sqlite'))

message_database = Messages()


easySQL.create_table(message_database, drop=False)

my_intents = discord.Intents.default()
my_intents.message_content = True
my_intents.members = True
client = discord.Client(intents=my_intents)


def channel_folder(name):
    """ Checks to make sure the backup folder exists in the parent folder."""
    output_folder = path_to_backups / name
    if os.path.exists(path=output_folder) is False:
        os.mkdir(path=output_folder)
    return output_folder

def save_image(url):
    response = requests.get(url)
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(":", "").replace(".", "")
    with open(f"generated_images/{timestamp}-gen-image-{construct_unique_name(6, type="image")}.jpg", "wb") as file:
        file.write(response.content)

async def request_hq_image(message):
    global accepted_roles
    if 'Crown' in [role.name for role in message.author.roles]:
        prompt = str(message.content).replace(f'Master Artist {bot_id} ', "")
        async with message.channel.typing():
            url = open_ai_sherpa.image_sherpa(query=prompt, size="1024x1024", quality="hd")
        save_image(url)
        await message.channel.send(url)
    else:
        messages = []
        query = "explain that your master artistry is costly and is limited for the time being"
        messages.append({'role': 'user', 'content': query})
        async with message.channel.typing():
            awnser = open_ai_sherpa.ask_sherpa(query=query, user=message.author.display_name, messages=messages)
        await message.channel.send(awnser)

async def request_standard_image(message):
    prompt = str(message.content).replace(f'Artist {bot_id} ', "")
    async with message.channel.typing():
        url = open_ai_sherpa.image_sherpa(query=prompt)
    save_image(url)
    await message.channel.send(url)

async def scrub_attachments(channel_id: int):
    # I want to take the channel_id and have the bot gather all messages and then scrub each for
    # embeds looking specifically for .jpg, .png, etc.
    accepted_extensions = ['png', 'jpg']
    
    channels = client.get_all_channels()
    channel: object = None
    for ch in channels:
        if ch.id == channel_id:
            channel = ch
    
    output_folder = channel_folder(channel.name)

    history = [message async for message in channel.history(limit=1000)]
    count = 0
    for moment in history:
        for attach in moment.attachments:
            url = attach.url
            name = url.split('/')[6].split('?')[0] #isolates the file name from the discord URL
            extension = name.split('.')[-1]
            
            if os.path.isfile(path=output_folder / name) is False and extension in accepted_extensions:
                print(f'{count}: {name}')
                response = requests.get(url)
                with open(output_folder / name, 'wb') as output:
                    output.write(response.content)
                print(f'{name}: DONE!')
                count += 1
    
    print('Attachments Downloaded!')


@client.event
async def on_ready():
    global production
    print(f'We have logged in as {client.user}')
    lodestone_news.start()
    fashion_report.start()
    if production:
        guild = client.get_guild(954201387770736751)
        office = guild.get_channel(1183450397159993414)
        global description
        response = open_ai_sherpa.ask_sherpa_agnostic(query=f"say good morning to everyone and let them know you are ready to help them in any way! Remember, {description}")
        await office.send(f"{response} @here")


async def living_conversation(message, type='text'):
    if message.reference:   
        message_id = message.reference.message_id
        row = easySQL.fetchone_from_table(message_database, filter=("message_id", message_id), convert_data=True)
        type = row.type
        unique_id = row.link_code
        living_conversation_messages = row.parsed_messages
        return unique_id, type, living_conversation_messages
    elif message.reference is None:
        letters = string.ascii_letters
        unique_id = ''.join(random.choice(letters) for i in range(12))
        return unique_id, type, []


@client.event
async def on_message(message):
    global message_database
    if message.author == client.user:
        timestamp = datetime.datetime.now()
        unique_id, type, living_conversation_messages = await living_conversation(message)
        easySQL.insert_into_table(message_database, (timestamp, 'assistant', message.author.display_name, message.author.id, type, message.content, message.id, unique_id, json.dumps(living_conversation_messages)))

    mentions = [mention.name for mention in message.mentions]

    if bot_name in mentions or "@Sherpa" in message.content:
        if f"News {bot_id}" in message.content: 
            await lodestone_news()
        if f"Fashionista {bot_id}" in message.content: 
            await fashion_report()
        if f"Dear {bot_id}" in message.content:
            await request_text_generation(message)
        
        # image generation code
        try:
            if f"Master Artist {bot_id}" in  message.content:
                await request_hq_image(message)
            elif f"Artist {bot_id}" in  message.content:
                await request_standard_image(message)
        except openai.BadRequestError:
            awnser = open_ai_sherpa.ask_sherpa_agnostic(query=f"explain why you couldn't generate an image due to a content policy violation which triggered your safety system.", pass_messages=[])
            await message.channel.send(awnser)
        
        if f"GIF {bot_id}" in message.content:
            timestamp = datetime.datetime.now()
            await message.add_reaction(u"\U0001F44D")
            data = {"prompt": str(message.content).replace(f'GIF {bot_id} ', "")}
            unique_id, type, living_conversation_messages = await living_conversation(message, type='GIF')
            easySQL.insert_into_table(message_database, (timestamp, 'user', message.author.display_name, message.author.id, type, data['prompt'], message.id, unique_id, json.dumps([])))
            response = requests.post(f"{url}/gif_generation", data=data)
            file_name = f"{construct_unique_name(6, type="gif")}.gif"
            bytes_data = BytesIO(response.content)
            file = discord.File(bytes_data, filename=file_name)
            images = [file]
            await message.add_reaction(u"\u2705")
            await message.reply(files=images)

        if f"LUCKYIMAGE {bot_id}" in message.content:
            timestamp = datetime.datetime.now()
            leading_prompt = "Given the following prompt come up with another prompt keeping as close to the original prompt as you can but with more variety to be put through a image generater with 77 tokens, keeping most of the major features of the original prompt returning only the new prompt:"
            prompt = str(message.content).replace(f'LUCKYIMAGE {bot_id} ', "")
            data = {"prompt": f"{leading_prompt}{prompt}"}
            unique_id, type, living_conversation_messages = await living_conversation(message, type='Image')
            easySQL.insert_into_table(message_database, (timestamp, 'user', message.author.display_name, message.author.id, type, data['prompt'], message.id, unique_id, json.dumps([])))
            await request_lucky_local_image(message, data, amt=1)

        elif f"IMAGES {bot_id}" in message.content:
            prompt_splice = str(message.content).replace(f'IMAGES {bot_id} ', "--tag--").split("--tag--")
            timestamp = datetime.datetime.now()
            data = {"prompt": prompt_splice[1]}
            unique_id, type, living_conversation_messages = await living_conversation(message, type='Image')
            easySQL.insert_into_table(message_database, (timestamp, 'user', message.author.display_name, message.author.id, type, data['prompt'], message.id, unique_id, json.dumps([])))
            await request_local_image(message, data, URL=f"{url}/image_generation", amt=int(prompt_splice[0]))

        elif f"IMAGE {bot_id}" in message.content:
            timestamp = datetime.datetime.now()
            data = {"prompt": str(message.content).replace(f'IMAGE {bot_id} ', "")}
            unique_id, type, living_conversation_messages = await living_conversation(message, type='Image')
            await request_local_image(message, data, URL=f"{url}/image_generation", amt=1)
            easySQL.insert_into_table(message_database, (timestamp, 'user', message.author.display_name, message.author.id, type, data['prompt'], message.id, unique_id, json.dumps([])))

        
        # CASE 1 "download pics"
        if "download pics" in message.content:
            for role in message.author.roles:
                if role.name in accepted_roles:
                    await message.channel.send('Roger that!')
                    await scrub_attachments(channel_id=message.channel.id)
                    return
        
# this works
async def request_local_image(message, data, URL, amt=1):
    await message.add_reaction(u"\U0001F44D")
    counts = {
        0: discord.PartialEmoji.from_str('1️⃣'),
        1: discord.PartialEmoji.from_str('2️⃣'),
        2: discord.PartialEmoji.from_str('3️⃣'),
        3: discord.PartialEmoji.from_str('4️⃣'),
        4: discord.PartialEmoji.from_str('5️⃣'),
        5: discord.PartialEmoji.from_str('6️⃣'),
        6: discord.PartialEmoji.from_str('7️⃣'),
        7: discord.PartialEmoji.from_str('8️⃣'),
        8: discord.PartialEmoji.from_str('9️⃣'),
        }
    first_count = True
    images =[]
    for count in range(amt):
        response = requests.post(URL, data=data)
        await asyncio.sleep(5)
        file_name = f"{construct_unique_name(6, type="IMAGE")}.jpg"
        bytes_data = BytesIO(response.content)
        file = discord.File(bytes_data, filename=file_name)       
        images.append(file)
        if first_count:
            await message.add_reaction(counts[count])
            first_count = False
        else:
            await message.remove_reaction(counts[count-1], client.user)
            await message.add_reaction(counts[count])
    await message.add_reaction(u"\u2705")
    await message.reply(files=images)


async def request_lucky_local_image(message, data, amt=1):
    counts = {
        0: discord.PartialEmoji.from_str('1️⃣'),
        1: discord.PartialEmoji.from_str('2️⃣'),
        2: discord.PartialEmoji.from_str('3️⃣'),
        3: discord.PartialEmoji.from_str('4️⃣'),
        4: discord.PartialEmoji.from_str('5️⃣'),
        5: discord.PartialEmoji.from_str('6️⃣'),
        6: discord.PartialEmoji.from_str('7️⃣'),
        7: discord.PartialEmoji.from_str('8️⃣'),
        8: discord.PartialEmoji.from_str('9️⃣'),
        }
    await message.add_reaction(u"\U0001F44D")
    prompts = []
    for _ in range(amt):
        response = requests.post(url=f"{url}/text_generation", data=data)
        body = str(response.content)
        prompts.append(body)

    first_count = True

    images = []
    for count, prompt in enumerate(prompts):
        n_data = {"prompt": prompt}
        response = requests.post(f"{url}/image_generation", data=n_data)
        await asyncio.sleep(15)
        file_name = f"{construct_unique_name(6, type="IMAGE")}.jpg"
        bytes_data = BytesIO(response.content)
        file = discord.File(bytes_data, filename=file_name)       
        images.append(file)
        if first_count:
            await message.add_reaction(counts[count])
            first_count = False
        else:
            await message.remove_reaction(counts[count-1], client.user)
            await message.add_reaction(counts[count])

    await message.add_reaction(u"\u2705")
    await message.reply(files=images)
            
async def request_text_generation(message):
    timestamp = datetime.datetime.now()
    question = str(message.content).replace(f'Dear {bot_id} ', "")       
    unique_id, type, living_conversation_messages = await living_conversation(message, type='text')
    if message.reference:
        pulled_messages = easySQL.fetchall_from_table(message_database, filter=('link_code', unique_id))
        if len(pulled_messages) > 5:
            new_messages = await semantic_search_sherpa.parse_messages(query=question, messages=pulled_messages)
        else:
            new_messages = pulled_messages
    else:
        new_messages = []
        
    easySQL.insert_into_table(message_database, (timestamp, 'user', message.author.display_name, message.author.id, type, question, message.id, unique_id, json.dumps(new_messages)))
    
    messages = []
    for old_message in new_messages:
        messages.append(
            {'role': old_message.role, 'content': old_message.content}
            )

    async with message.channel.typing():
        messages.append({'role': 'user', 'content': question})
        awnser = open_ai_sherpa.ask_sherpa(question, user=message.author.display_name, messages=messages)
        await message.reply(awnser)

client.run('MTE4MzA3MDY2MDYyMTI1MDcwMg.GPpNUT.iw9OyUl3i4JvETgi97ERILuwEvWVlHuP5eh4Xg')