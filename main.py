import json
import random
import time
import requests
import hgtk
import discord
from discord.ext import commands
from bs4 import BeautifulSoup


def parse_quotes():
    url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=%EB%AA%85%EC%96%B8'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    quotes = [quote.text.strip() for quote in soup.find_all('p', class_='lngkr')]
    authors = [author.text.strip() for author in soup.find_all('span', class_='engnm')]

    return quotes, authors


def generate_number():
    return random.sample(range(1, 10), 3)


def count_strikes_and_balls(secret_number, guess):
    strikes = 0
    balls = 0
    for i in range(3):
        if guess[i] == secret_number[i]:
            strikes += 1
        elif guess[i] in secret_number:
            balls += 1
    return strikes, balls


def validate_input(guess):
    if not guess.isdigit() or len(guess) != 3:
        return False
    if len(set(guess)) != 3:
        return False
    return True


# 봇의 설정
token = 'MTE4OTAyNzMzNjYwODI4NDcxMg.G9r1Qa.mnHEXBMQDh0DbLHp9Qgo9rj2I9IxE7KlYnwia4'
prefix = ''

# 봇 객체 생성
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
responding = False

# 키워드와 대답 사전
keyword_responses = {}

# 이미 있는 단어 알기위해 단어목록 저장
history = []
# 키 발급은 https://krdict.korean.go.kr/openApi/openApiInfo
apikey = '480720C2EC23D1B81390E37674841507'

# 좀 치사한 한방단어 방지 목록
blacklist = ['즘', '틱', '늄', '슘', '퓸', '늬', '뺌', '섯', '숍', '튼', '름', '늠', '쁨']

# 파일 경로
file_path = 'keyword_responses.json'


# 지정한 두 개의 문자열 사이의 문자열을 리턴하는 함수
# string list에서 단어, 품사와 같은 요소들을 추출할때 사용됩니다
def midReturn(val, s, e):
    if s in val:
        val = val[val.find(s) + len(s):]
        if e in val:
            val = val[:val.find(e)]
    return val


# 지정한 두 개의 문자열 사이의 문자열 여러개를 리턴하는 함수
# string에서 XML 등의 요소를 분석할때 사용됩니다
def midReturn_all(val, s, e):
    if s in val:
        tmp = val.split(s)
        val = []
        for i in range(0, len(tmp)):
            if e in tmp[i]:
                val.append(tmp[i][:tmp[i].find(e)])
    else:
        val = []
    return val


def findword(query):
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&pos=1&q=' + query
    response = requests.get(url)
    ans = []

    # 단어 목록을 불러오기
    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        # 이미 쓴 단어가 아닐때
        if w not in history:
            # 한글자가 아니고 품사가 명사일때
            word = midReturn(w, '<word>', '</word>')
            pos = midReturn(w, '<pos>', '</pos>')
            if len(word) > 1 and pos == '명사' and word not in history and not word[len(word) - 1] in blacklist:
                ans.append(w)
    if len(ans) > 0:
        return random.choice(ans)
    else:
        return ''


def checkexists(query):
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&sort=popular&num=100&pos=1&q=' + query
    response = requests.get(url)
    ans = ''

    # 단어 목록을 불러오기
    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        # 이미 쓴 단어가 아닐때
        if not (w in history):
            # 한글자가 아니고 품사가 명사일때
            word = midReturn(w, '<word>', '</word>')
            pos = midReturn(w, '<pos>', '</pos>')
            if len(word) > 1 and pos == '명사' and word == query:
                ans = w

    if len(ans) > 0:
        return ans
    else:
        return ''


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
    global responding

    if message.author.bot or "고양시" in message.content or responding:
        return

    if "사랑" in message.content or "좋" in message.content:
        if "고양" in message.content:
            await message.add_reaction('❤️')

    if message.author.name == "_cheese_07" and "//" in message.content:
        keyword = message.content.split("//")[:-1]
        response = message.content.split("//")[-1]
        all_ = message.content.split("//")
        kss = "고양"
        filtered_list = [item for item in all_ if item != "" and item != " "]
        if len(filtered_list) >= 2:
            for ks in keyword:
                kss += "//" + ks
            keyword_responses[kss] = response
            await message.channel.send(f"키워드 '{kss.replace('//', ', ')}'에 대한 대답이 '{response}'로 설정되었습니다.")
            save_responses()
        else:
            if filtered_list[0] == "리스트":
                emb = ''
                for idx, (key, value) in enumerate(keyword_responses.items(), start=1):
                    emb += f"{idx}. {key}: {value}\n"
                embed = discord.Embed(description=emb)
                await message.channel.send(embed=embed)
            elif filtered_list[0] == "삭제":
                emb = ''
                for idx, (key, value) in enumerate(keyword_responses.items(), start=1):
                    emb += f"{idx}. {key}: {value}\n"
                embed = discord.Embed(description=emb)
                embed.set_footer(text="삭제할 번호(1부터 정수만)를 선택해 주세요.")
                await message.channel.send(embed=embed)
                message_ = await bot.wait_for('message', check=lambda m: m.author == message.author)
                idx = int(message_.content)
                keyword_responses.pop(list(keyword_responses.keys())[idx - 1])
                save_responses()
                await message.author.send("아래는 수정된 리스트입니다.")
                emb = ''
                for idx, (key, value) in enumerate(keyword_responses.items(), start=1):
                    emb += f"{idx}. {key}: {value}\n"
                embed = discord.Embed(description=emb)
                embed.set_footer(text="수정된 리스트")
                await message.channel.send(embed=embed)
        return

    if "명언" in message.content and "고양" in message.content:
        quotes, authors = parse_quotes()
        ind = random.randint(0, len(quotes) - 1)
        await message.reply(embed=discord.Embed(description=quotes[ind]).set_footer(text=authors[ind]))
        return

    if "야구" in message.content and ("게임" in message.content or "숫자" in message.content)\
            and "고양" in message.content:
        responding = True
        secret_number = generate_number()
        rep = await message.reply(embed=discord.Embed(description='').add_field(name="야구 게임을 시작합니다", value=''))
        rephis = rep.embeds[0].fields[0].name
        attempts = 0
        while True:
            rep = await rep.edit(embed=discord.Embed(description=rephis).add_field(name=".\n3자리 숫자를 입력해주세요", value=''))
            rephis = rep.embeds[0].description + rep.embeds[0].fields[0].name
            guess_ = await bot.wait_for('message', check=lambda m: m.author == message.author)
            await rep.delete()
            guess = guess_.content
            rephis += ".\nㄴ " + guess
            if not isinstance(guess_.channel, discord.DMChannel):
                await guess_.delete()
            if not validate_input(guess):
                rep = await message.reply(embed=discord.Embed(description=rephis).add_field(
                    name=".\n올바른 입력이 아닙니다. 다시 시도하세요", value=''))
                rephis = rep.embeds[0].description + rep.embeds[0].fields[0].name
                continue
            attempts += 1
            guess = [int(x) for x in guess]
            strikes, balls = count_strikes_and_balls(secret_number, guess)
            rep = await message.reply(embed=discord.Embed(description=rephis).add_field(
                name=f".\n{strikes} 스트라이크, {balls} 볼", value=''))
            rephis = rep.embeds[0].description + rep.embeds[0].fields[0].name
            if strikes == 3:
                await rep.edit(embed=discord.Embed(
                    description=rephis).add_field(name=f".\n축하합니다! {attempts}번 만에 정답을 맞추셨습니다.", value=''))
                break
        responding = False
        return

    if "끝말" in message.content and "고양" in message.content:
        responding = True
        playing = True
        global history
        await message.reply(embed=discord.Embed(description='''
=============고양이 끝말잇기===============
사전 데이터 제공: 국립국어원 한국어기초사전
끝말잇기 코드 원본: https://blog.naver.com/pdj2885/221552896123
- - - 게임 방법 - - -
가장 처음 단어를 제시하면 끝말잇기가 시작됩니다
'/그만'을 입력하면 게임이 종료되며, '/다시'로
게임을 다시 시작할 수 있습니다.
- - - 게임 규칙 - - -
1. 사전에 등재된 명사여야 합니다
2. 적어도 단어의 길이가 두 글자 이상이어야 합니다
3. 이미 사용한 단어를 다시 사용할 수 없습니다
4. 두음법칙 적용 가능합니다 (ex. 리->니)
- - - 주의 사항 - - -
1. 고양이가 모르는 단어가 있을 수 있어요.
   그럴 때는 다른 단어로 시도해 주세요:(
2. 고양이가 부적절한 단어를 말할 수 있어요.
==========================================

먼저 시작하세요!
'''))

        sword = ''
        history = []
        while playing:
            query = ''
            word_ok = False

            while not word_ok:
                message = await bot.wait_for('message', check=lambda message__: message__.author == message.author)
                query = message.content
                word_ok = True

                if query == '/그만':
                    playing = False
                    await message.channel.send('고양이 승리!')
                    break
                elif query == '/다시':
                    history = []
                    await message.channel.send('고양이 승리!')
                    await message.channel.send('게임을 다시 시작합니다.')
                    word_ok = False
                else:
                    if query == '':
                        word_ok = False

                        if len(history) == 0:
                            await message.channel.send('단어를 입력하여 끝말잇기를 시작합니다.')
                        else:
                            await message.channel.send(sword + '(으)로 시작하는 단어를 입력해 주십시오.')

                    else:
                        # 첫 글자의 초성 분석하여 두음법칙 적용 -> 규칙에 아직 완벽하게 맞지 않으므로 차후 수정 필요
                        if not len(history) == 0 and not query[0] == sword and not query == '':
                            sdis = hgtk.letter.decompose(sword)
                            qdis = hgtk.letter.decompose(query[0])
                            if sdis[0] == 'ㄹ' and qdis[0] == 'ㄴ':
                                await message.reply('두음법칙 적용됨')
                            elif (sdis[0] == 'ㄹ' or sdis[0] == 'ㄴ') and qdis[0] == 'ㅇ' and qdis[1] in (
                                    'ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ', 'ㅒ', 'ㅖ'):
                                await message.reply('두음법칙 적용됨')
                            else:
                                word_ok = False
                                await message.reply(sword + '(으)로 시작하는 단어여야 합니다.')

                        if len(query) == 1:
                            word_ok = False
                            await message.reply('적어도 두 글자가 되어야 합니다')

                        if query in history:
                            word_ok = False
                            await message.reply('이미 입력한 단어입니다')

                        if query[len(query) - 1] in blacklist:
                            await message.channel.send('...')

                        if word_ok:
                            # 단어의 유효성을 체크
                            ans = checkexists(query)
                            if ans == '':
                                word_ok = False
                                await message.reply('유효한 단어를 입력해 주십시오')

            history.append(query)

            if playing:
                start = query[len(query) - 1]

                ans = findword(start + '*')

                if ans == '':
                    # ㄹ -> ㄴ 검색
                    sdis = hgtk.letter.decompose(start)
                    if sdis[0] == 'ㄹ':
                        newq = hgtk.letter.compose('ㄴ', sdis[1], sdis[2])
                        await message.channel.send(start + '->' + newq)
                        start = newq
                        ans = findword(newq + '*')

                if ans == '':
                    # (ㄹ->)ㄴ -> ㅇ 검색
                    sdis = hgtk.letter.decompose(start)
                    if sdis[0] == 'ㄴ' and sdis[1] in ('ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ', 'ㅒ', 'ㅖ'):
                        newq = hgtk.letter.compose('ㅇ', sdis[1], sdis[2])
                        await message.channel.send(start + '->' + newq)
                        ans = findword(newq + '*')

                if ans == '':
                    await message.channel.send(message.author.name + '님의 승리!')
                    break
                else:
                    answord = midReturn(ans, '<word>', '</word>')  # 단어 불러오기
                    ansdef = midReturn(ans, '<definition>', '</definition>')  # 품사 불러오기
                    history.append(answord)

                    await message.reply(query + '>' + answord + '\n(' + ansdef + ')\n')
                    sword = answord[len(answord) - 1]

        responding = False
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
                        response = response.replace("username", message.author.mention)
                        sent = await message.reply(response)
                        if len(sent.content) > 2000:
                            time.sleep(1.5)
                            await sent.edit(content="(삭제된 메시지입니다)")
                        return
            except ValueError:
                pass

    if "고양" in message.content:
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
        return


# 봇 시작
bot.run(token)
