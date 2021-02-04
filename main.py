import pandas as pd
from discord.ext import commands
import discord
import numpy as np
import time
import threading
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
###################################





###########
class AlphaY(discord.ext.commands.Bot):
    def __init__(self):
        super().__init__(command_prefix ='#')
        self.lotto_prob = [(1-1e-5)/9]*9
        self.lotto_prob.append(1e-5)
        self.data = self.load_data()
        self.log_data()

    def get_points(self, speaker):
        try:
            rand_points = np.random.choice(range(1,11), p = self.lotto_prob)
            if rand_points == 10:
                self.data.loc[speaker,'wallet'] += 100
                return True
            else:
                self.data.loc[speaker,'wallet'] += 1
        except KeyError:
            self.data.loc[speaker,'wallet'] = 0

    def load_data(self):
        try:
            data = pd.read_csv('data.csv', index_col = 0, header = 0)
        except:
            data = pd.DataFrame()
        return data
        
    def log_data(self):
        self.data.to_csv('data.csv')
        threading.Timer(5, function=self.log_data).start()
    ######################################################
    async def on_ready(self):
        print('Logged on as', self.user)
    #####################################################
    async def on_message(self, message):    
        if message.author == self.user:
            return
        if message.author.bot:
            return
        #############################
        speaker = message.author.name
        if self.get_points(speaker):
            msg = f'축하합니다! {speaker}님이 랜덤 포인트 100점을 획득하셨습니다!\n' +\
                  '지갑 확인하기: #지갑'
            await message.channel.send(msg)
        #############################
    #@self.command()
    async def 명령어(ctx):    
        msg = '#지갑 : 지갑을 확인합니다. 포인트를 모아서 상품으로 교환할 수 있습니다.\n'+\
              '#청소 : 메세지를 지웁니다.'
        await message.channel.send(msg)

    #@self.command()
    async def 지갑(ctx): 
        cash = self.data.loc[speaker, 'wallet']
        msg = f'{speaker}님이 보유하신 포인트는 {int(cash)}pt 입니다.'
        await message.channel.send(msg, delete_after = 3.0)
    
    #@self.command()
    async def 청소(ctx): 
            await self.delete_messages(self.cached_messages)
    

ay = AlphaY()
ay.run('ODA2ODA2ODI0NDcxODg3ODky.YBuzaA.CuOrsmWoi9S8oxBbC6xsfX7ovmE')
