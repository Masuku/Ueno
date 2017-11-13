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


def get_summonerinfo(summn_name : str):
    """サモナーネームを入力してstatusを取得"""
    API_KEY = "RGAPI-76bb5df1-c89e-4c7f-8eea-2de77a6a1fb5"
    watcher = RiotWatcher(API_KEY)
    region = "jp1"
    try:
        return watcher.summoner.by_name(region, summn_name)
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
def get_currentgame(summn_name : str):
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
