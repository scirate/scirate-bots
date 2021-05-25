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
    await bot.change_presence(activity=discord.Game(name='SciRate'))
    print(f'Logged in as {bot.user.name}')
    return

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def top(ctx, *, arg=None):
    global called, break_loop 
    res=[]
    while arg:
        if len(arg) > 20:
            return await ctx.reply('`Query Character Limit Exceeded`')
        elif called:
            msg = await ctx.reply('`Session Already Active`')
            return await msg.delete(delay=5)    
        break          
    await ctx.reply('`Starting Subscription`')   
    called, break_loop = True, False
    while True and not break_loop:
        embed = None
        embed = await _fetch(ctx, res, arg)     
        await ctx.send(embed = embed)
        await asyncio.sleep(config.TIME)  

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def stop(ctx):
    global called, break_loop
    if not called:
        return await ctx.reply('`No Subscription To Cancel`')    
    break_loop, called = True, False
    return await ctx.reply('`Subscription Cancelled`')
     
async def _fetch(ctx, res, arg=None):
    if arg:
        render_link=f'https://scirate.com/search?utf8=%E2%9C%93&q={arg}'
    elif arg == None:
        render_link=f'https://scirate.com/'
    async with aiohttp.ClientSession() as session:
        async with session.get(render_link) as response:
            if response.status != 200:
                await ctx.reply('`Falied to fetch data | Try again later`', mention_author=False)
            resp_text = await response.text()
            soup = BeautifulSoup(resp_text, 'html.parser')
            res = []
            ratings = list(map(lambda x : x.text, soup.find_all("button", class_="btn btn-default count")[:10]))
            for title, rating in list(zip(soup.find_all("div", class_="title")[:10], ratings)):
                res.append(f'**{rating}** [`{title.find("a").contents[0]}`]({"https://scirate.com" + title.find("a")["href"]})')               
            res[0] = '•' + res[0]
            chars = [len(i) for i in res]
            if chars[0] > 2048:
                res = res[:-1]
            embed = discord.Embed(title = f'`Top SciRate papers`', 
                                        description = '\n•'.join(res),
                                        color = 0xe8e3e3)
            return embed

@top.error
@stop.error
async def top_stop_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return await ctx.reply('`Missing Permissions`') 
    else:
        pass           

bot.run(config.TOKEN, bot=True, reconnect=True)
