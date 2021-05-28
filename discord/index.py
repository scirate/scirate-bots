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
                intents = discord.Intents.default(), 
                help_command=None
)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='SciRate'))
    print(f'Logged in as {bot.user.name}')
    return

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def now(ctx, *, arg=None):
    if await _check_args(ctx, arg):
        return 
    res=[]
    embed = await _fetch(ctx, res, arg)
    if not embed:
            return await ctx.reply('`No Results Found`') 
    return await ctx.send(embed = embed)

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def start(ctx, *, arg=None):
    global called, break_loop 
    res=[]
    if arg:
        if len(arg) > 20:
            return await ctx.reply('`Query Character Limit Exceeded`')            
    if await _check_called(ctx, called):
        return 
    await ctx.reply('`Starting Subscription`')   
    called, break_loop = True, False
    while True and not break_loop:
        embed = await _fetch(ctx, res, arg)
        if not embed:
            return await ctx.reply('`No Results Found`')     
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
            try:
                chars = [len(i) for i in res]
                if chars[0] > 2048:
                    res = res[:-1]
            except:
                return False
            else:                            
                res[0] += '•'
                embed = discord.Embed(title = f'`Top SciRate papers`', 
                                    description = '\n•'.join(res),
                                    color = 0xe8e3e3)
                return embed

@start.error
@stop.error
async def start_stop_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return await ctx.reply('`Missing Permissions`') 
    else:
        pass 

async def _check_called(ctx, state):
    if state: 
        msg = await ctx.reply('`Session Already Active`')
        await msg.delete(delay=5)
        return state

async def _check_args(ctx, arg):
    if arg:
        if len(arg) > 20:
            await ctx.reply('`Query Character Limit Exceeded`')
            return True
    return False
    
help_dict = {
            "**Start Scites**": "<@&846783290332413964>`start <query>`", 
            "**Now Scites**": "<@&846783290332413964>`now <query>`",
            "**Stop Scites**": "<@&846783290332413964>`stop`"
            }

@bot.command()
async def help(ctx):
    embed = discord.Embed(title = f'`SciRate Help`', color = 0xe8e3e3)
    for key, value in help_dict.items():
        embed.add_field(name=key, value=value, inline=False)
    return await ctx.send(embed=embed)

bot.run(config.TOKEN, bot=True, reconnect=True)
