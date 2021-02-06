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
from utils import prop_checker

intents = discord.Intents.default()
intents.members = True
load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
###################################


def load_db():
    try:
        db = pd.read_csv('db.csv', index_col=0, header=0)
    except:
        db = pd.DataFrame()
    sdb = pd.read_csv('item/items.csv', index_col=0, header=0)
    return db, sdb


def log_db(db):
    db.to_csv('db.csv')
    sdb.to_csv('item/items.csv')
    threading.Timer(5, function=log_db, args=(db,)).start()


def get_points(speaker, prob):
    rand_points = np.random.choice(range(1, 11), p=prob)
    try:
        if rand_points == 10:
            db.loc[speaker, 'wallet'] +=  000
            return True
        else:
            db.loc[speaker, 'wallet'] += rand_points * 0.15
    except KeyError:
        db.loc[speaker, 'wallet'] = 0


###########################################################
ay = commands.Bot(command_prefix='.', intents=intents)
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
    status_list = [discord.Status.idle, discord.Status.online]
    activity_list = [discord.Game("Who am I..?"),
                    discord.Streaming(name = '랄숭이', url='https://www.twitch.tv/aba4647'),
                    discord.Activity(type=discord.ActivityType.listening, name="사쿠란보"),
                    discord.Activity(type=discord.ActivityType.watching, name="ㅎㅎ;; ㅋㅋ;; ㅈㅅ!!")]
    status = status_list[np.random.choice(len(status_list), p = [0.1,0.9])]
    activity = np.random.choice(activity_list)
    await ay.change_presence(activity=activity)
    

@ay.event
async def on_message(message):
    if message.author == ay.user:
        return
    if message.author.bot:
        return
    speaker = message.author.name
    if get_points(speaker, lotto_prob):
        msg = f'축하합니다! {speaker}님이 행운의 포인트 1000점을 획득하셨습니다!\n' +\
            '지갑 확인하기: .지갑'
        await message.channel.send(msg)
    await ay.process_commands(message)
##############################################################


@ay.command(name='명령어')
async def command(ctx):
    embed=discord.Embed(title="Alpha Y 명령어", description="명령어를 확인하세요.", color=0x00ff62)
    embed.add_field(name=".명령어", value="사용 가능한 명령어와 사용 방법을 알려줍니다.", inline=False)
    embed.add_field(name=".청소 [개수] [유저 포함 여부]", value="메시지를 삭제합니다. 사람 포함여부 : 1이면 유저 메시지도 포함합니다.", inline=False)
    embed.add_field(name=".지갑", value="지갑을 확인합니다. 이름 생략 시 본인 지갑을 확인합니다.", inline=False)
    embed.add_field(name=".상품확인", value="현재 구매 가능한 상품을 확인합니다.", inline=False)
    embed.add_field(name='.상품구입 [상품 번호] [개수]', value='상품을 구입합니다. 상품 번호는 ".상품확인"을 통해서 확인하세요. 개수는 생략 시 1 입니다.', inline=False)
    embed.add_field(name=".포인트선물 [이름]", value="자신의 포인트를 특정 유저에게 선물합니다.", inline=False)
    await ctx.send(embed=embed)


@ay.command(name='지갑')
async def wallet(ctx, name=None):
    if name == None:
        name = ctx.message.author.name
    else:
        name = ' '.join(ctx.message.content.split(' ')[1:])
    try:
        cash = db.loc[name, 'wallet']
        msg = f'{name}님이 보유하신 포인트는 {int(cash)}pt 입니다.'
        if int(cash) in [111, 222, 333, 444, 555, 666, 777, 888, 999, 369]:
            db.loc[name, 'wallet'] += 10
            msg += f'\n포인트 확인 보너스 10pt가 지급되었습니다!'
    except:
        if prop_checker(ctx.message.author.name):
            msg = f'어 {ctx.message.author.name}아 '
            if prop_checker(name):
                if len(name) == 2:
                    msg += f'{name}이가 누구냐?'
                else:
                    msg += f'{name}이 누구냐?'
            else:
                msg += f'{name}가 누구냐?'
        else:
            msg = f'어 {ctx.message.author.name}야 '
            if prop_checker(name):
                if len(name) == 2:
                    msg += f'{name}이가 누구냐?'
                else:
                    msg += f'{name}이 누구냐?'
            else:
                msg += f'{name}가 누구냐?'
    await ctx.send(msg)


@ay.command(name='청소')
async def clear(ctx, amount=60, human=0):
    if not 0 < amount < 100:
        await ctx.send(f'메세지 개수를 다시 설정해주세요. (1~99)')
        return
    with ctx.channel.typing():
        if not human:
            def _check(message):
                if message.content == '':
                    return True
                else:
                    return message.author.bot or '.' == message.content[0]
        else:
            def _check(message):
                return True
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount,
                                          after=datetime.now() - timedelta(days=7),
                                          check=_check)
        await ctx.send(f"{len(deleted):,} 개의 메세지를 삭제했습니다.", delete_after=5)


@ay.command(name='상품확인')
async def item(ctx):
    embed = discord.Embed(
        title="상품 교환소", description="포인트를 상품으로 교환할 수 있습니다.", color=0x5cb85c)
    embed.set_thumbnail(
        url="https://cdn.icon-icons.com/icons2/651/PNG/512/Icon_Business_Set_00003_A_icon-icons.com_59841.png")
    cntr = 1
    for index, items in sdb.iterrows():
        embed.add_field(
            name=f"```{cntr}.{index}``` ", value=f"가격: {items['가격']}pt\t{items['개수']}개 남음", inline=False)
        cntr += 1
    await ctx.send(embed=embed)


@ay.command(name='포인트선물')
async def give_pt(ctx, *taker):
    taker = ' '.join(taker)
    giver = ctx.message.author.name
    member_list = [m.name for m in ctx.channel.members if not m.bot]
    if taker not in member_list:
        await ctx.send(f'어 그게 누군데')
        return
    await ctx.send(f'현재 {giver}님이 보유하신 포인트는 {int(db.loc[giver,"wallet"])}pt 입니다.\n얼마만큼 선물하시겠습니까? [⏲ 5초]')

    def check(msg):
        return msg.author == ctx.message.author and msg.channel == ctx.channel
    try:
        reply = await ay.wait_for("message", check=check, timeout=5)
        amount = int(reply.content)
        if db.loc[giver, "wallet"] < amount:
            await ctx.send('어 돈복사 버그는 막아놧다^^')
            return
        print(f'Give PT: {giver}>>{taker}, {amount}pt')
        db.loc[giver, "wallet"] -= amount
        db.loc[taker, "wallet"] += amount
        await ctx.send(f'{giver}님이 {amount}pt 를 {taker}님께 선물했습니다! 👍')
    except asyncio.TimeoutError:
        await ctx.send('시간 초과! ⏲')
        return
    except:
        await ctx.send('뭔가 잘ㅈ못됏다.. 다시ㄱㄱ')
        return

@ay.command(name = '상품구입')
async def purchase(ctx, items_idx, quantity = 1):
    try:
        items_idx = int(items_idx)-1
        items = sdb.index[items_idx]
        quantity = int(quantity)
    except:
        await ctx.send(f'숫자만 입력 가능합니다.')
        return
    if quantity < 1:
        await ctx.send(f'1개 이상만 구매할 수 있습니다.')
    if len(sdb.loc[items]) ==0:
        await ctx.send(f'상품 이름을 다시 확인해보세요.')
        return
    if sdb.loc[items,'개수'] < quantity:
        await ctx.send(f'해당 상품의 수량이 부족합니다.')
        return
    buyer = ctx.message.author.name
    price = sdb.loc[items,'가격']
    cash = db.loc[buyer, 'wallet']
    if cash < price * quantity:
        await ctx.send(f'잔고가 부족합니다.')
        return
    storage_path = 'item/storage/'
    item_list = os.listdir(storage_path)
    target_items = [i for i in item_list if items[:2] in i][0:quantity]
    for i in range(quantity):
        file = discord.File(storage_path+target_items[i])
        if ctx.message.author.dm_channel:
            await ctx.message.author.dm_channel.send(file = file)
        elif ctx.message.author.dm_channel is None:
            channel = await ctx.message.author.create_dm()
            await ctx.message.author.dm_channel.send(file = file)
        os.remove(storage_path+target_items[i])
    await ctx.message.author.dm_channel.send('🍰 구매하신 상품이 도착했습니다.')
    sdb.loc[items, '개수'] -= quantity
    db.loc[buyer, 'wallet'] -=  (price * quantity)
    msg = f'🍰 해당 상품을 구매하셨습니다!\n{buyer}님의 잔고 : {int(db.loc[buyer, "wallet"])}pt\n'+\
        '# 개인 메세지를 확인해주세요.'
    print(f'Buy item: {buyer} >> {items}, {quantity}개')
    await ctx.send(msg)

@ay.command(name='가챠')
async def gacha(ctx):
    player = ctx.message.author.name
    if db.loc[player, 'wallet'] < 100:
        if prop_checker(player):
            msg = f'어 {player}아 씨드 100pt 없으면 저기 돈복사방 가서 앵벌이해라'
        else:
            msg = f'어 {player}야 씨드 100pt 없으면 저기 돈복사방 가서 앵벌이해라'
        await ctx.send(msg)
        return
    db.loc[player, 'wallet'] -=  100
    await ctx.send("가챠를 시작합니다...")
    #value = [-200, -50 ,0, 70, 200, 250, 400, 500, 8200]
    value  = [-200, -50 ,0, 70, 200, '츄파춥스', 400, '새콤달콤', '투썸 아메리카노 Regular 2잔']
    gift_val = value[np.random.choice(range(len(value)),
                p = [.05, .255, .24, .21, .12, .06, .04, .02, .005])]
    await ctx.send("결과는 . . . . !")
    if isinstance(gift_val, int):    
        for n in str(abs(gift_val)) :
            await asyncio.sleep(np.random.randint(2,5))
            await ctx.send(f". . . {n}")
        if gift_val > 100:
            await ctx.send("축하합니다! ...")
            await asyncio.sleep(np.random.randint(2))
            await ctx.send(f"💰💰💰 {gift_val}pt 당첨!!! 💰💰💰")
        elif gift_val >= 0:
            await ctx.send(f"💰 크흠.. 어질어질해요~ 💰{gift_val}pt 획득..")
        elif gift_val < 0:
            await ctx.send("축하합니다! ...")
            await asyncio.sleep(np.random.randint(2))
            await ctx.send(f"🎇{gift_val:+}pt 감점!!!🎇")
        db.loc[player, 'wallet'] += int(gift_val)
        try:
            db.loc[player, 'blackcow'] += int(gift_val)
        except KeyError:
            db.loc[player, 'blackcow'] = int(gift_val)
    else:
        if sdb.loc[gift_val,"개수"] < 1:
            db.loc[player, 'wallet'] +=  sdb.loc[gift_val,'가격']
            await ctx.send(f"🎁 {gift_val} 당첨! 재고가 없어 {sdb.loc[gift_val,'가격']}pt로 지급합니다!")
            
        else:
            storage_path = 'item/storage/'
            target_items = [i for i in item_list if gift_val[:2] in i][0]
            file = discord.File(storage_path+target_items)
            if ctx.message.author.dm_channel:
                await ctx.message.author.dm_channel.send(file = file)
            elif ctx.message.author.dm_channel is None:
                channel = await ctx.message.author.create_dm()
                await ctx.message.author.dm_channel.send(file = file)
            os.remove(storage_path+target_items)
            sdb.loc[gift_val, '개수'] = sdb.loc[gift_val, '개수'] - 1
            await ctx.message.author.dm_channel.send('🎁 상품이 도착했습니다.')
            await ctx.send("🎁 상품 당첨! 귀\n여운{gift_val[0]}\n{gift_val[1:]}을 드리겠습니다~")
        
        try:
            db.loc[player, 'blackcow'] += sdb.loc[gift_val,'가격']
        except KeyError:
            db.loc[player, 'blackcow'] = sdb.loc[gift_val,'가격']

@ay.command(name="흑우의전당")
async def blackcow_show(ctx):
    bcs = db['blackcow'].sort_values(ascending=False)
    bc_list = bcs.index.to_list()
    value_list = bcs.to_list()
    embed=discord.Embed(title="흑우의 전당", description="가챠에서 가장 높은 득점을 한 순위입니다.", color=0xdd4040)
    embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/2526/PNG/512/award_medal_winner_icon_151762.png")
    for i in range(len(bc_list)):
        embed.add_field(name=f"{i+1}. {bc_list[i]}", value=f"{value_list[i]:+.0f}pt", inline=False)
        if i == 2:
            break
    await ctx.send(embed=embed)

#############################
# 
ay.run(os.getenv('TOKEN'))
# Todo 홀짝 , 포인트빵, 가챠 슬롯머신, 명예의전당

# ? 가차시스템. 꽝, 0.5배 , 2배, 츄파춥스, 4배, 새콤달콤,투썸>>> 7개
# ?           25   25    15,    12,    10    10      3
# ?                   60     75     87    97       
# ? 포인트훔치기 시스템
