import asyncio
import discord 
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import aiohttp 
from bs4 import BeautifulSoup
import config

called = False
break_loop = False
bot=commands.Bot(command_prefix=commands.when_mentioned_or(config.PREFIX), 
                intents = discord.Intents.default()
)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Watching Scirate'))
    print(f'Logged in as {bot.user.name}')
    return

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def top(ctx):
    res = []
    global called
    global break_loop    
    if called:
        msg = await ctx.reply('`Session Already Active`')
        return await msg.delete(delay=5)
    else: 
        await ctx.reply('`Starting Subscription`')   
        called = True
        break_loop = False
        while True and not break_loop:
            embed = None
            embed = await _fetch(ctx, res)
            await ctx.send(embed = embed)
            await asyncio.sleep(24*60*60)  

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def stop(ctx):
    global called, break_loop    
    break_loop, called = True, False
    return await ctx.reply('`Subscription Cancelled`')
     
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
            embed = discord.Embed(title = f'`Top SciRate papers`', 
                                        description = '\n'.join(res),
                                        color = 0xe8e3e3)
            return embed

@top.error
@stop.error
async def top_stop_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return await ctx.reply('Missing Permissions')            

bot.run(config.TOKEN, bot=True, reconnect=True)