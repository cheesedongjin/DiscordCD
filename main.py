import discord
from discord.ext import commands
import json
import time
import random

# 봇의 설정
token = 'MTE4OTAyNzMzNjYwODI4NDcxMg.G9r1Qa.mnHEXBMQDh0DbLHp9Qgo9rj2I9IxE7KlYnwia4'
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
    if message.author.bot or "고양시" in message.content:
        return

    if "사랑" in message.content or "좋" in message.content:
        if "고양" in message.content:
            await message.add_reaction('❤️')
        return

    if message.author.name == "_cheese_07" and "//" in message.content:
        keyword = message.content.split("//")[:-1]
        response = message.content.split("//")[-1]
        kss = "고양"
        filtered_list = [item for item in keyword if item != "" and item != " "]
        if len(filtered_list) >= 2:
            for ks in keyword:
                kss += "//" + ks
            keyword_responses[kss] = response
            await message.channel.send(f"키워드 '{kss.replace('//', ', ')}'에 대한 대답이 'username님, {response}'로 설정되었습니다.")
            save_responses()
        else:
            await message.channel.send(f"뭔가 잘못되었네요. 정확한 형식으로 다시 한 번 시도해주세요.")
        return

    for j in range(10, 0, -1):
        for res in keyword_responses:
            try:
                keyword = res.split("//")
                response = keyword_responses[res]
                if len(keyword) >= j and response:
                    bo = False
                    for i in range(0, len(keyword)):
                        if not keyword[i] in message.content:
                            bo = True
                            break
                    if not bo:
                        sent = await message.channel.send(f"{message.author.mention}님, {response}")
                        if len(sent.content) > 2000:
                            time.sleep(1.5)
                            await sent.edit(content="(삭제된 메시지입니다)")
                        return
            except ValueError:
                pass

    if "고양" in message.content and "고양시" not in message.content:
        fail_response = [
            "잘 알아듣지 못했어요:(",
            "부르셨나요? 무슨 말인지 모르겠어요ㅠㅠ",
            "미안해요, 이해가 안 되네요ㅠㅠ",
            "뭔가 잘못 알아들었나봐요:(",
            "다시 말해주실 수 있나요? 이해가 안 돼요:(",
            "죄송해요, 잘 모르겠어요ㅠㅠ",
            "무슨 말씀이신지 이해하지 못했어요:(",
            "제가 뭔가를 놓쳤나요? 이해가 안 가네요ㅠㅠ"
        ]
        await message.channel.send(random.choice(fail_response))
    await bot.process_commands(message)


# 봇 시작
bot.run(token)
