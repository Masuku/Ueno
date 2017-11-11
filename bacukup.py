#-*- coding:utf-8 -*-
import asyncio
import discord
from discord.ext import commands
from urllib.parse import urljoin
from urllib.parse import quote
from urllib.parse import urlencode
import urllib.request
import httplib2
import json
import os
import re
import random
from oauth2client.contrib import gce
from riotwatcher import RiotWatcher #Riot API wrapper
from requests import HTTPError
import pya3rt
import types

bot = commands.Bot(command_prefix='!', description='aaaaa') #

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message): #メンションに返信
        API_KEY = "jPOnGtEHD6pSi5Tcl81r8wy53vviHL55"
        client = pya3rt.TalkClient(API_KEY)
        botid = "<@"+bot.user.id +">"
        send = re.sub(botid,"",message.content) #mention文字列を取り除く
        resp = client.talk(send)
        # print(send)
        if resp["status"]==0:
            reply = resp["results"][0]["reply"]
            await bot.send_message(message.channel, reply)

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await bot.send_message(message.channel, msg)

    if message.content.startswith('!close'):
        await bot.close()

    if message.content.startswith('!delete'):
        def is_me(m):
            return m.author == bot.user
        deleted = await bot.purge_from(message.channel, limit=100, check=is_me)
        await bot.send_message(message.channel, 'Deleted {} message(s)'.format(len(deleted)))
    else:
        return

KEY = "32613949566f4b4b4e686d533437644c4e744a57574b577a3772724a68573845523734643152434948712e"
#エンドポイントの設定
endpoint = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=REGISTER_KEY'
url = endpoint.replace('REGISTER_KEY', KEY)

#1回目の会話の入力
utt_content = raw_input('>>')

payload = {'utt' : utt_content, 'context': ''}
headers = {'Content-type': 'application/json'}

#送信
r = requests.post(url, data=json.dumps(payload), headers=headers)
data = r.json()

#jsonの解析
response = data['utt']
context = data['context']

#表示
print "response: %s" %(response)

#2回目以降の会話(Ctrl+Cで終了)
while True:
    utt_content = raw_input('>>')
    payload['utt'] = utt_content
    payload['context'] = data['context']

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = r.json()

    response = data['utt']
    context = data['context']

    print "response: %s" %(response)

##############################bot.command###################################

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command(description='random img')
async def img(search_word : str):
    """画像を検索して表示"""
    API_KEY = "AIzaSyA7LE-k7siyvDUqcSpitW4j1SGbVrfoyTQ"
    ENGINE_ID = "017124472341657688815:nmd6rufrz3o"
    URL = "https://www.googleapis.com/customsearch/v1?key=" + API_KEY + "&cx=" + ENGINE_ID + "&searchType=image&q=" + quote(search_word)
    # await bot.say(URL_TEMPLATE)
    # http = credentials.authorize(httplib2.Http())
    html_content = urllib.request.urlopen(URL)
    str_html = html_content.read().decode("utf-8")
    match = re.search(r'ou":"?([\'" >]+)', str_html)
    data = json.loads(str_html)
    links = []
    for item in data["items"]:
        links.append(item["link"])
    await bot.say(random.choice(links))

@bot.command(description='league of legends')
async def lol(summn_name : str):
    API_KEY = "RGAPI-bde36e47-7fe5-4136-8401-6bdd0607b292"
    watcher = RiotWatcher(API_KEY)
    region = "jp1"
    try:
        me = watcher.summoner.by_name(region, summn_name)
        await bot.say(me)
    except HTTPError as err:
        if err.me.status_code == 429:
            print('We should retry in {} seconds.'.format(e.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.me.status_code == 403:
            bot.say('API key looks like expired')
        elif err.me.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise

    try:
        current_game = watcher.spectator.by_summoner(region, me['id'])
        await bot.say('ゲームモード:'+current_game["gameMode"])
    except HTTPError as err:
        if err.response.status_code == 429:
            await bot.say('We should retry in {} seconds.'.format(e.headers['Retry-After']))
            await bot.say('this retry-after is handled by default by the RiotWatcher library')
            await bot.say('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            await bot.say('Summoner is currently not in game.')
        else:
            raise
# @bot.command()
# async def bga():
#     url = 'https://ja.boardgamearena.com/#!welcome'
#     await bot.say(url)


bot.run('MzcxOTEwMDY2Mjc1ODc2ODY0.DM8fwQ.1UNuCCqNp1ViXydh0Gd2rjqOEM8')
