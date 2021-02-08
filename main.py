import pandas as pd
from datetime import datetime, timedelta
from discord.ext import commands
import discord
import numpy as np
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


def get_points(id, prob):
    rand_points = np.random.choice(range(1, 12), p=prob)
    
    if rand_points == 11:
        try:
            db.loc[id, 'wallet'] +=  1000
        except KeyError:
            db.loc[id, 'wallet'] = 1000
        return 'lotto'
    elif rand_points ==  10:
        try:
            db.loc[id, 'gticket'] += 1
        except KeyError:
            db.loc[id, 'gticket'] = 1
        return 'gticket'
    else:
        try:
            db.loc[id, 'wallet'] += rand_points * 0.15
        except KeyError:
            db.loc[id, 'wallet'] = rand_points * 0.15
        return None
        


###########################################################
lotto_prob = [0.111] * 9
lotto_prob.append(0.001 - (1e-4))
lotto_prob.append(1e-4)
###########################################################
db, sdb = load_db()
log_db(db)
ay = commands.Bot(command_prefix='.', intents=intents)


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
    global db
    if message.author == ay.user:
        return
    if message.author.bot:
        return
    #register
    userid = message.author.id
    name = message.author.name if message.author.nick == None else message.author.nick 
    if userid not in db.index:
        db.loc[int(userid)] = 0
        db = db.index.astype("int")
    db.loc[userid,'name'] = name
    if not isinstance(message.channel, discord.channel.DMChannel):
        gift = get_points(userid, lotto_prob)
        if gift == 'lotto':
            print(f'{name} get 1000pts through Lotto')
            msg = f'📀 축하합니다! {name}님이 행운의 포인트 1000점을 획득하셨습니다!📀\n' +\
                    '포인트 확인: .소지품'
            await message.channel.send(msg)
        elif gift == 'gticket':
            print(f'{name} gets gacha ticket')
            msg = f"🎉 축하합니다! {name}님이 🎫가챠 티켓에 당첨되셨습니다!! 🎉"
            await message.channel.send(msg)
    await ay.process_commands(message)
##############################################################


@ay.command(name='명령어')
async def command(ctx):
    embed=discord.Embed(title="Alpha Y 명령어", description="명령어를 확인하세요.", color=0x00ff62)
    embed.add_field(name=".명령어", value="사용 가능한 명령어와 사용 방법을 알려줍니다.", inline=False)
    embed.add_field(name=".청소 [개수] [유저 포함 여부]", value="메시지를 삭제합니다. 사람 포함여부 : 1이면 유저 메시지도 포함합니다.", inline=False)
    embed.add_field(name=".소지품", value="소지품을 확인합니다. 이름 생략 시 본인 지갑을 확인합니다.", inline=False)
    embed.add_field(name=".상품확인", value="현재 구매 가능한 상품을 확인합니다.", inline=False)
    embed.add_field(name='.상품구입 [상품 번호] [개수]', value='상품을 구입합니다. 상품 번호는 ".상품확인"을 통해서 확인하세요. 개수는 생략 시 1 입니다.', inline=False)
    embed.add_field(name=".포인트선물 [이름]", value="자신의 포인트를 특정 유저에게 선물합니다.", inline=False)
    embed.add_field(name=".가챠", value="100pt로 가챠 게임을 시작합니다.", inline=False)
    embed.add_field(name=".흑우의전당", value="가챠 수익 순위를 확인합니다.", inline=False)
    embed.add_field(name=".랭킹", value="포인트 보유 순위를 확인합니다.", inline=False)
    embed.add_field(name=".정보설정 [이름]", value="타인의 정보를 설정할 수 있습니다. 본인은 안됨!", inline=False)
    embed.add_field(name=".타이머 [초]", value="타이머를 시작합니다.", inline=False)
    await ctx.send(embed=embed)


@ay.command(name='소지품', aliases=['인벤토리', '가방', '지갑'])
async def wallet(ctx, *name):
    if name == ():
        uid = ctx.message.author.id
        name = db.loc[ctx.message.author.id,"name"]
    else:
        name = ' '.join(name)
        uid = db.loc[db['name']==name].index[0]
    speaker = db.loc[ctx.message.author.id,"name"]
    member_list = [m.name for m in ctx.channel.members if not m.bot]
    if name not in member_list:
        if prop_checker(speaker):
            msg = f'어 {speaker}아 '
            if prop_checker(name):
                if len(name) == 2:
                    msg += f'{name}이가 누구냐?'
                else:
                    msg += f'{name}이 누구냐?'
            else:
                msg += f'{name}가 누구냐?'
        else:
            msg = f'어 {speaker}야 '
            if prop_checker(name):
                if len(name) == 2:
                    msg += f'{name}이가 누구냐?'
                else:
                    msg += f'{name}이 누구냐?'
            else:
                msg += f'{name}가 누구냐?'
    
    cash = db.loc[uid, 'wallet']
    if db.isnull().loc[uid, 'info']:
        db.loc[uid, 'info'] = ""
    description = db.loc[uid, 'info']
    if db.isnull().loc[uid, 'gticket']:
        db.loc[uid, 'gticket'] = 0
    n_gticket = db.loc[uid, 'gticket']

    embed=discord.Embed(title=" ",description=description, color=0x00ffaa)
    embed.set_author(name=name, icon_url=ctx.message.author.avatar_url)
    embed.add_field(name="💰 포인트", value=int(cash), inline=False)
    embed.add_field(name="🎫 가챠티켓", value=int(n_gticket), inline=False)
    await ctx.send(embed=embed)
    if int(cash) in [111, 222, 333, 444, 555, 666, 777, 888, 999, 369]:
        db.loc[ctx.message.author.id, 'wallet'] += 10
        msg += f'\n{speaker}님에게 포인트 확인 보너스 10pt가 지급되었습니다!'
        await ctx.send(msg)

@ay.command(name='정보설정')
async def set_info(ctx, *name):
    if name == ():
        await ctx.send("정보를 설정할 대상이 필요합니다.")
        return
    name = ' '.join(name)
    uid = db.loc[db['name'] == name].index[0]
    if uid == ctx.message.author.id:
        await ctx.send("자신의 평판은 남에 의해 결정 되는 법..")
        return
    await ctx.send(f"{name}의 현재 정보: {db.loc[name,'info']}\n바꿀 정보를 입력해주세요.")
    
    def check(msg):
        return msg.channel == ctx.channel and msg.author == ctx.message.author
    try:
        reply = await ay.wait_for("message", check=check, timeout=10)
        db.loc[uid,'info'] = reply.content
        speaker = db.loc[ctx.message.author.id,"name"]
        print(f'Change Info: {speaker}>>{name}, to {reply.content}')
        await ctx.send(f'변경되었습니다. 👍')
    except asyncio.TimeoutError:
        await ctx.send('시간 초과! ⏲')
        return
    
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
@commands.guild_only()
async def give_pt(ctx, *taker):
    if taker == ():  
        return
    taker = ' '.join(taker)
    taker_id = db.loc[db['name']==taker].index[0]
    giver_id = ctx.message.author.id
    giver = db.loc[giver_id,'name']
    member_list = [m.name for m in ctx.channel.members if not m.bot]
    if taker not in member_list:
        await ctx.send(f'어 그게 누군데')
        return
    await ctx.send(f'현재 {giver}님이 보유하신 포인트는 {int(db.loc[giver_id,"wallet"])}pt 입니다.\n얼마만큼 선물하시겠습니까? [⏲ 5초]')

    def check(msg):
        return msg.author == ctx.message.author and msg.channel == ctx.channel
    try:
        reply = await ay.wait_for("message", check=check, timeout=5)
        amount = int(reply.content)
        if amount < -1:
            await ctx.send('어 돈복사 버그는 막았다 ^^')
            return
        if db.loc[giver_id, "wallet"] < amount:
            await ctx.send('어 돈복사 버그는 막아놧다^^')
            return
        print(f'Give PT: {giver}>>{taker}, {amount}pt')
        db.loc[giver_id, "wallet"] -= amount
        db.loc[taker_id, "wallet"] += amount
        await ctx.send(f'{giver}님이 {amount}pt 를 {taker}님께 선물했습니다! 👍')
    except asyncio.TimeoutError:
        await ctx.send('시간 초과! ⏲')
        return
    except:
        await ctx.send('뭔가 잘ㅈ못됏다.. 다시ㄱㄱ')
        return

@ay.command(name = '상품구입')
@commands.guild_only()
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
    buyer_id = ctx.message.author.id
    buyer = db.loc[buyer_id, 'name']
    price = sdb.loc[items,'가격']
    cash = db.loc[buyer_id, 'wallet']
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
    db.loc[buyer_id, 'wallet'] -=  (price * quantity)
    msg = f'🍰 해당 상품을 구매하셨습니다!\n{buyer}님의 잔고 : {int(db.loc[buyer_id, "wallet"])}pt\n'+\
        '# 개인 메세지를 확인해주세요.'
    print(f'Buy item: {buyer} >> {items}, {quantity}개')
    await ctx.send(msg)

@ay.command(name='가챠')
@commands.guild_only()
async def gacha(ctx):
    player_id = ctx.message.author.id
    player = db.loc[player_id,'name']
    if db.isnull().loc[player_id,'gticket']:
        db.loc[player_id,'gticket'] = 0
    if db.loc[player_id, 'wallet'] < 100 and db.loc[player_id,'gticket'] < 1:
        if prop_checker(player):
            msg = f'어 {player}아 씨드 100pt 없으면 저기 돈복사방 가서 앵벌이해라'
        else:
            msg = f'어 {player}야 씨드 100pt 없으면 저기 돈복사방 가서 앵벌이해라'
        await ctx.send(msg)
        return
    elif db.loc[player_id,'gticket'] >= 1:
        db.loc[player_id,'gticket'] -= 1
        await ctx.send("🎫가챠 티켓을 사용했습니다!")
    else:
        db.loc[player_id, 'wallet'] -=  100
        await ctx.send("100pt를 사용하고 가챠를 시작합니다...!")
    #value = [-200, -50 ,0, 70, 200, 250, 400, 500, 8200]
    value  = [-100, -50 ,0, 50, 300, '츄파춥스', 400, '새콤달콤', '투썸 아메리카노 Regular 2잔']
    gift_val = value[np.random.choice(range(len(value)),
                p = [.07, .255, .24, .23, .08, .06, .04, .02, .005])]
    await ctx.send("결과는 . . . . !")
    if isinstance(gift_val, int):    
        for n in str(abs(gift_val)) :
            await asyncio.sleep(1.5)
            await ctx.send(f". . . {n}")
        if gift_val > 100:
            await ctx.send("축하합니다! ...")
            await asyncio.sleep(np.random.randint(3,5))
            await ctx.send(f"💰💰💰 {gift_val}pt 당첨!!! 💰💰💰")
            print(f'{player} >> {gift_val} get through gacha')
        elif gift_val >= 0:
            await ctx.send(f"💰 크흠.. 어질어질해요~ 💰{gift_val}pt 획득..")
        elif gift_val < 0:
            await ctx.send("축하합니다! ...")
            await asyncio.sleep(np.random.randint(3,5))
            await ctx.send(f"🎇{gift_val:+}pt 감점!!!🎇")
        db.loc[player_id, 'wallet'] += int(gift_val)
        try:
            db.loc[player_id, 'blackcow'] += int(gift_val)
        except KeyError:
            db.loc[player_id, 'blackcow'] = int(gift_val)
    else:
        if sdb.loc[gift_val,"개수"] < 1:
            db.loc[player_id, 'wallet'] +=  sdb.loc[gift_val,'가격']
            await ctx.send(f"🎁 {gift_val} 당첨! 재고가 없어 {sdb.loc[gift_val,'가격']}pt로 지급합니다!")
            print(f'{player} >> {gift_val} get through gacha')
        else:
            storage_path = 'item/storage/'
            item_list = os.listdir(storage_path)
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
            await ctx.send(f"🎁 상품 당첨! 귀\n여운{gift_val[0]}\n{gift_val[1:]}을 드리겠습니다~")
            print(f'{player} >> {gift_val} get through gacha')
        
        try:
            db.loc[player_id, 'blackcow'] += sdb.loc[gift_val,'가격']
        except KeyError:
            db.loc[player_id, 'blackcow'] = sdb.loc[gift_val,'가격']
    
    if db.loc[player_id, 'wallet'] < 0:
        db.loc[player_id, 'wallet'] = 0

@ay.command(name="흑우의전당")
async def blackcow_show(ctx):
    bcs = db.sort_values(by=['blackcow'], ascending=False)
    bc_list = bcs['name'].to_list()
    value_list = bcs['blackcow'].to_list()
    embed=discord.Embed(title="흑우의 전당", description="가챠로 얻은 수익 순위입니다.", color=0xdd4040)
    embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/2526/PNG/512/award_medal_winner_icon_151762.png")
    for i in range(len(bc_list)):
        embed.add_field(name=f"{i+1}. {bc_list[i]}", value=f"{value_list[i]:+.0f}pt", inline=False)
        if i == 2:
            break
    await ctx.send(embed=embed)

@ay.command(name="랭킹")
async def ranking_show(ctx):
    rankers = db.sort_values(by=['wallet'], ascending=False)
    rankers_list = rankers['name'].to_list()
    value_list = rankers['wallet'].to_list()
    embed=discord.Embed(title="포인트 순위", description="보유한 포인트 순위입니다.", color=0xdd4040)
    embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/2526/PNG/512/award_medal_winner_icon_151762.png")
    for i in range(len(rankers_list)):
        embed.add_field(name=f"{i+1}. {rankers_list[i]}", value=f"{value_list[i]:+.0f}pt", inline=False)
        if i == 2:
            break
    await ctx.send(embed=embed)


@ay.command(name="타이머")
async def timer(ctx, *args):
    args = int("".join(args))
    await ctx.send(f"⏳ 타이머를 시작합니다! [{args}초] ⏳")
    await asyncio.sleep(args)
    await ctx.send(f"⌛ 타이머 종료! ⌛")

@ay.command(name="관리자")
async def admin(ctx, *args):
    if ctx.message.author.id != 398359177682092042:
        await ctx.send("관리자만 사용 가능합니다.")
        return
    await ctx.send("명령어를 입력해주세요.\n# 포인트, 가챠티켓, 상품등록, 상품제거")
    def check(msg):
        return msg.author.id == 398359177682092042 and msg.channel == ctx.channel
    try:
        reply = await ay.wait_for("message", check=check, timeout=10)
        if "취소" in reply.content:
            await ctx.send("취소하셨습니다!")
            return
        cmd = reply.content.split(" ")
        target_name = cmd[1]
        target_id = db.loc[db["name"] == target_name].index
        if len(target_id) != 1:
            await ctx.send("해당 이름을 가진 유저가 없거나 2명 이상입니다.")
            return
        target_id = target_id[0]
        if cmd[0] == "포인트":
            #포인트 호준 1
            amount = int(cmd[2])
            db.loc[target_id, "wallet"] += amount
            await ctx.send(f"{target_name}님의 포인트 {amount:+} 했습니다.")
        elif cmd[0] == "가챠티켓":
            amount = int(cmd[2])
            db.loc[target_id, "gticket"] += amount
            await ctx.send(f"{target_name}님의 가챠티켓 {amount:+} 했습니다.")
        elif cmd[0] == "상품등록":
            #상품등록 김호준 츄파춥스 250
            item = " ".join(cmd[2:-1])
            owner = target_name
            price = int(cmd[-1])
            await ctx.send("몇개를 추가하시겠습니까?")
            reply = await ay.wait_for("message", check = check, timeout=10)
            amount = int(reply.content)
            if item not in sdb.index:
                quantity = amount
                item_dict = {"상품":item,"가격":price,"개수":quantity,"등록자":owner}
                sdb = sdb.append(item_dict, ignore_index = True)
                await ctx.send("정상적으로 등록되었습니다.")
            else:
                sdb.loc[item,"개수"] += amount
                await ctx.send("정상적으로 등록되었습니다.")
        elif cmd[0] == "상품제거":
            #상품삭제 투썸 머머머머
            item = " ".join(cmd[1:])
            sdb.drop([item], inplace = True)
            await ctx.send("정상적으로 제거되었습니다.")
    except asyncio.TimeoutError:
        await ctx.send('시간 초과! ⏲')
        return
        
    

#############################
# 
ay.run(os.getenv('TOKEN'))
# 홀짝 , 포인트빵, 가챠 슬롯머신,지갑순위, 포인트훔치기 시스템

# ? 
# ?  
# ?   
# ? 
