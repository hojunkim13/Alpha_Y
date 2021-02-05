import pandas as pd
from datetime import datetime, timedelta
from discord.ext import commands
import discord
import numpy as np
import time
import threading
import logging
import os
import asyncio
from dotenv import load_dotenv
from utils import prop_checker, log_db, load_db, get_points
load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
###################################


###########################################################
ay = commands.Bot(command_prefix='.')
lotto_prob = [(1-1e-4)/9]*9
lotto_prob.append(1e-4)
db, sdb = load_db()
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
async def wallet(ctx, name = ctx.message.author.name):
    if name == None:
        name = ctx.message.author.name
    else:
        name = message.content.split(' ')[1:].join('')
        try:
            cash = db.loc[name, 'wallet']
            msg = f'{name}님이 보유하신 포인트는 {int(cash)}pt 입니다.'
            if int(cash) in [111, 222, 333, 444, 555, 666, 777, 888, 999, 369]:
                db.loc[name, 'wallet'] = db.loc[name, 'wallet'] + 10
                msg += f'\n포인트 확인 보너스 10점!'
        except:
            if prop_checker(ctx.message.author.name):
                msg = f'어 {ctx.message.author.name}아 '
                if prop_check(name):
                    msg += f'{}이가 누구냐?'
                else:
                    msg += f'{}가 누구냐?'
            else:
                msg = f'어 {ctx.message.author.name}야 '
                if prop_check(name):
                    msg += f'{}이가 누구냐?'
                else:
                    msg += f'{}가 누구냐?'
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


@ay.command(name='상품')
async def item(ctx):
    embed=discord.Embed(title="상품 교환소", description="포인트를 상품으로 교환할 수 있습니다.", color=0x5cb85c)
    embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/651/PNG/512/Icon_Business_Set_00003_A_icon-icons.com_59841.png")
    for index, items in sdb.iterrows():
        embed.add_field(name = f"```{index}``` [{items['개수']}]", value = f"가격: {items['가격']}pt", inline = False)
    await ctx.send(embed=embed)
    
#############################
ay.run(os.getenv('TOKEN'))
##Todo 홀짝 , 포인트빵, 지갑 삼육구 666 111 이벤트
##Todo 포인트선물, 물건구매


