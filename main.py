import pandas as pd
from datetime import datetime, timedelta
from discord.ext import commands
import discord
import numpy as np
import time
import threading
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

###################################
def load_db():
    try:
        db = pd.read_csv('db.csv', index_col = 0, header = 0)
    except:
        db = pd.dbFrame()
    return db

def log_db(db):
    db.to_csv('db.csv')
    threading.Timer(5, function=log_db, args=(db,)).start()

def get_points(speaker, prob):
    rand_points = np.random.choice(range(1,11), p = prob)
    try:
        if rand_points == 10:
            db.loc[speaker,'wallet'] = db.loc[speaker,'wallet'] + 100
            return True
        else:
            db.loc[speaker,'wallet'] = db.loc[speaker,'wallet'] + rand_points * 0.1
    except KeyError:
        db.loc[speaker,'wallet'] = 0

###########################################################
ay = commands.Bot(command_prefix='.')
lotto_prob = [(1-1e-5)/9]*9
lotto_prob.append(1e-5)
db = load_db()
log_db(db)
print('init done.')

@ay.event
async def on_ready():
    print('Logged on as', ay.user.name)
    print('id', ay.user.id)
    print('------------')


@ay.event
async def on_message(message):
    if message.author == ay.user:
        return
    if message.author.bot:
        return
    speaker = message.author.name
    if get_points(speaker, lotto_prob):
        msg = f'축하합니다! {speaker}님이 랜덤 포인트 100점을 획득하셨습니다!\n' +\
                '지갑 확인하기: #지갑'
        await message.channel.send(msg)
    await ay.process_commands(message)
##############################################################

@ay.command(name='명령어')
async def command(ctx):    
    msg = '#지갑 : 지갑을 확인합니다. 포인트를 모아서 상품으로 교환할 수 있습니다.\n'+\
          '#청소 : 메세지를 지웁니다.'
    await ctx.send(msg)

@ay.command(name='지갑')
async def wallet(ctx):
    speaker = ctx.message.author.name
    cash = db.loc[speaker, 'wallet']
    msg = f'{speaker}님이 보유하신 포인트는 {int(cash)}pt 입니다.'
    await ctx.send(msg)

@ay.command(name='청소')
async def clear(ctx, amount = 50, bot = 1):
    if not 0 < amount < 100:
        await ctx.send(f'메세지 개수를 다시 설정해주세요. (1~99)')
        return
    with ctx.channel.typing():
        if bot:
            def _check(message):
                return message.author.bot
        else:
            def _check(message):
                return True
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit = amount,
                                        after = datetime.now() - timedelta(days=7),
                                        check = _check)
        await ctx.send(f"{len(deleted):,} 개의 메세지를 삭제했습니다.", delete_after = 5)

#############################
ay.run(os.getenv('TOKEN'))



