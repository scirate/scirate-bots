import asyncio
import discord 
from discord.ext import commands, tasks
import aiohttp 
from bs4 import BeautifulSoup
import config

called = False
bot=commands.Bot(command_prefix=commands.when_mentioned_or(config.PREFIX), 
                intents = discord.Intents.default()
)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Watching Scirate'))
    print(f'Logged in as {bot.user.name}')
    return

@bot.command()
async def top(ctx):
    global called
    if called:
        msg = await ctx.send('`Session Already Active`')
        return await msg.delete(delay=5)
    else:    
        called = True
        while True:
            embed = None
            embed = await _fetch(ctx, res)
            await ctx.send(embed = embed)
            await asyncio.sleep(24*60*60)        
     
async def _fetch(ctx, res):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://scirate.com/') as response:
            if response.status != 200:
                await ctx.reply('`Falied to fetch data | Try again later`', mention_author=False)
            resp_text = await response.text()
            soup = BeautifulSoup(resp_text, 'html.parser')
            res = []            
            for title in soup.find_all("div", class_="title")[:10]:
                res.append(f'[`{title.find("a").contents[0]}`]({"https://scirate.com" + title.find("a")["href"]})')               
            chars = [len(i) for i in res]
            if chars[0] > 2048:
                res = res[:-1]
            embed = discord.Embed(title = f'`Fetching Top Arxiv Posts`', 
                                        description = '\n'.join(res),
                                        color = 0xe8e3e3)
            return embed

bot.run(config.TOKEN, bot=True, reconnect=True)
