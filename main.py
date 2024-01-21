import discord
from discord.ext import commands
import json
import time

# 봇의 설정
token = 'MTE4OTAyNzMzNjYwODI4NDcxMg.Gg7Ctk.Rom1aw2rHDCRC6An9cfEzoxYAAtaO7PujkJswo'
prefix = ''

# 봇 객체 생성
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# 키워드와 대답 사전
keyword_responses = {}

# 파일 경로
file_path = 'keyword_responses.json'


# 함수들 추가
def save_responses():
    with open(file_path, 'w') as file:
        json.dump(keyword_responses, file, ensure_ascii=False, indent=4)


def load_responses():
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            keyword_responses.update(data)
    except FileNotFoundError:
        print(f"No previous data found. Creating {file_path} file.")
        save_responses()  # Creates the file if it doesn't exist
    except json.JSONDecodeError:
        print("Error decoding JSON. Starting with an empty keyword_responses dictionary.")


# 봇이 준비되면 실행되는 이벤트 핸들러
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    load_responses()


# 메시지 수신 이벤트 핸들러
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "사랑" in message.content:
        await message.add_reaction('❤️')
        return

    if message.author.name == "_cheese_07" and "//" in message.content:
        try:
            keyword, response = message.content.split("//")
            keyword = keyword.strip()
            response = response.strip()
            keyword_responses[keyword] = response
            await message.channel.send(f"키워드 '{keyword}'에 대한 대답이 'username님, {response}'로 설정되었습니다.")
            save_responses()
            return
        except ValueError:
            await message.channel.send("입력 형식이 잘못되었습니다. 정확한 형식으로 다시 시도해주세요.")
            return

    for keyword, response in keyword_responses.items():
        if keyword in message.content:
            sent = await message.channel.send(f"{message.author.mention}님, {response}")
            if "도배" in sent.content:
                time.sleep(1)
                await sent.delete()
                await message.channel.send("(삭제된 메시지입니다)")
            return

    await message.channel.send("잘 알아듣지 못했어요:(")
    await bot.process_commands(message)


# 봇 시작
bot.run(token)
