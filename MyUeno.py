#-*- coding:utf-8 -*-
import asyncio
import discord
from discord.ext import commands
from urllib.parse import quote
import httplib2
import requests
from requests import HTTPError
import json
import os
import re
import random
from oauth2client.contrib import gce
from riotwatcher import RiotWatcher #Riot API wrapper
import types

bot = commands.Bot(command_prefix="!", description="aaaaa") #

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

#on_message events
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    # Let"s talk with 上野さん
    elif message.content.startswith("!hi"):
        # remove initial command
        # botid = "<@"+bot.user.id +">"
        # send = re.sub(botid,"",message.content)
        send = re.sub("!hi","",message.content)
        KEY = "32613949566f4b4b4e686d533437644c4e744a57574b577a3772724a68573845523734643152434948712e"
        # endpoint setting
        endpoint = "https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=REGISTER_KEY"
        url = endpoint.replace("REGISTER_KEY", KEY)

        # input a messages
        utt_content = send
        context = ""

        #forming
        payload = {"utt" : utt_content, "context": context}
        headers = {"Content-type": "application/json"}

        # sending a message
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        data = r.json()

        # take response and talk recognization code
        response = data["utt"]
        context = data["context"]

        await bot.send_message(message.channel, response)
        i=0 #counting talkscc
        while True:
            i+=1
            print(context) #context = talk recognization code
            #check initial command
            def check(msg):
                return msg.content.startswith("!talk")
            message = await bot.wait_for_message(timeout=20.0,author=message.author,check=check)
            if message is None:
                break
            elif message.author != bot.user and message.content.startswith("!talk"):
                print(i)
                send = re.sub("!talk","",message.content)
                payload["utt"] = send
                payload["context"] = data["context"]
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                data = r.json()
                response = data["utt"]
                context = data["context"]
                await bot.send_message(message.channel, response)
                asyncio.sleep(2)
            else:
                break

    elif message.content.startswith("!hello"):
        msg = "Hello!!! {0.author.mention}".format(message)
        await bot.send_message(message.channel, msg)

    elif message.content.startswith("!close"):
        await bot.close()

    elif message.content.startswith("!delete"):
        def is_me(m):
            return m.author == bot.user
        deleted = await bot.purge_from(message.channel, limit=100, check=is_me)
        await bot.send_message(message.channel, "Deleted {} message(s)".format(len(deleted)))
    else:
        return


##############################bot.command###################################

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except Exception:
        await bot.say("Format has to be in NdN!")
        return

    result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description="For when you wanna settle the score some other way")
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command(description="random img")
async def img(search_word : str):
    """search images and choose randomly"""
    API_KEY = "AIzaSyA7LE-k7siyvDUqcSpitW4j1SGbVrfoyTQ"
    ENGINE_ID = "017124472341657688815:nmd6rufrz3o"
    URL = "https://www.googleapis.com/customsearch/v1?key=" + API_KEY + "&cx=" + ENGINE_ID + "&searchType=image&q=" + quote(search_word)
    # await bot.say(URL_TEMPLATE)
    # http = credentials.authorize(httplib2.Http())
    r = requests.get(URL)
    data = r.json()
    links = []
    for item in data["items"]:
        links.append(item["link"])
    await bot.say(random.choice(links))

@bot.command(description="league of legends")
async def lol(summn_name : str):
    """サモナーネームを入力してstatusを取得"""
    API_KEY = "RGAPI-76bb5df1-c89e-4c7f-8eea-2de77a6a1fb5"
    watcher = RiotWatcher(API_KEY)
    region = "jp1"
    try:
        me = watcher.summoner.by_name(region, summn_name)
        await bot.say(me)
        #ranked_stats = watcher.league.by_summoner(region, me["id"])
        #print(ranked_stats)
    except HTTPError as err:
        if err.me.status_code == 429:
            print("We should retry in {} seconds.".format(e.headers["Retry-After"]))
            print("this retry-after is handled by default by the RiotWatcher library")
            print("future requests wait until the retry-after time passes")
        elif err.me.status_code == 400:
            bot.say("BAD REQUEST")
        elif err.me.status_code == 403:
            bot.say("API key is expired")
        elif err.me.status_code == 404:
            print("Summoner with that ridiculous name not found.")
        else:
            raise

    try:
        curr_game_stats = watcher.spectator.by_summoner(region, me["id"])
        mini = str(int(curr_game_stats["gameLength"]/60))
        sec = str(curr_game_stats["gameLength"]%60)
        await bot.say("GameMode:"+curr_game_stats["gameMode"]+", "+mini+"min."+sec+"sec.")
        parti = curr_game_stats["participants"]
        player_list = [parti[i]["summonerName"] for i in range(len(parti))]
        await bot.say(player_list)
    except HTTPError as err:
        if err.response.status_code == 429:
            await bot.say("We should retry in {} seconds.".format(e.headers["Retry-After"]))
            await bot.say("this retry-after is handled by default by the RiotWatcher library")
            await bot.say("future requests wait until the retry-after time passes")
        elif err.response.status_code == 404:
            await bot.say("Summoner is currently not in game.")
        else:
            raise
# @bot.command()
# async def bga():
#     url = "https://ja.boardgamearena.com/#!welcome"
#     await bot.say(url)

bot.run("MzcxOTEwMDY2Mjc1ODc2ODY0.DM8fwQ.1UNuCCqNp1ViXydh0Gd2rjqOEM8")
