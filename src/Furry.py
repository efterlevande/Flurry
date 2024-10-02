import os
import sys
import json
import discord
import re
import random
import subprocess
import asyncio
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
from asyncio import sleep
import textwthing
from random import randrange
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord import FFmpegPCMAudio
from discord.ext import bridge
from gtts import gTTS
import gspread
from oauth2client.service_account import ServiceAccountCredentials 
scopes = [
    "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scopes=scopes)
file = gspread.authorize(creds)
t = file.open("name1")
sheet = t.sheet1
q = file.open("name2")
shoot = q.sheet1

def sorts():
    sheet.sort((2, 'des'))
    shoot.sort((2, 'des'))

print("Importing data from secrets file...")
secrets_file = 'popbot-secrets'
with open(secrets_file) as f:
    popbot_secrets = f.read()
print("Reconstructing data as dict...")
secrets = json.loads(popbot_secrets)
del(popbot_secrets)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True 
intents.guilds = True           
intents.members = True           
intents.presences = True
client = bridge.Bot(command_prefix="!", intents=intents)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        invalid_args = discord.Embed(title='Error', color=0xff0000)
        invalid_args.add_field(name='Invalid amount of arguments', value='Missing arguments..', inline=False)
        await ctx.respond(embed=invalid_args)
    if isinstance(error, commands.MissingPermissions):
        invalid_perms = discord.Embed(title='Error', color=0xff0000)
        invalid_perms.add_field(name='Permission denied', value='You dont have the permission to use this command.', inline=False)
        await ctx.respond(embed=invalid_perms)

@client.bridge_command(brief="get your ping")
async def ping(ctx):
    await ctx.respond(f":ping_pong: Pong: {round(client.latency * 1000)}ms")
    return

@client.bridge_command(brief="Convert units")
async def convert(ctx, query: str):
    match = re.match(r"([\d.]+)\s*([a-zA-Z]+)\s*to\s*([a-zA-Z]+)", query)
    if match:
        amount = float(match.group(1)) 
        from_unit = match.group(2).lower()
        to_unit = match.group(3).lower()
        result = None
        if from_unit == "kg" and to_unit == "lbs":
            result = amount * 2.20462  
            await ctx.respond(f"{amount} kg is {result:.2f} lbs")
        elif from_unit == "lbs" and to_unit == "kg":
            result = amount / 2.20462  
            await ctx.respond(f"{amount} lbs is {result:.2f} kg")
        elif from_unit == "in" and to_unit == "cm":
            result = amount * 2.54  
            await ctx.respond(f"{amount} in is {result:.2f} cm")
        elif from_unit == "cm" and to_unit == "in":
            result = amount / 2.54  
            await ctx.respond(f"{amount} cm is {result:.2f} in")
        elif from_unit == "c" and to_unit == "f":
            result = (amount * 1.8) + 32
            await ctx.respond(f"{amount} °C is {result:.2f} °F")
        elif from_unit == "f" and to_unit == "c":
            result = (amount - 32) / 1.8
            await ctx.respond(f"{amount} °F is {result:.2f} °C")
        else:
            await ctx.respond(f"Sorry, I don't recognize the conversion from {from_unit} to {to_unit}.")
    else:
        await ctx.respond("Please provide a valid conversion query like '123 kg to lbs'.")



@client.bridge_command(brief="russian roulette",description="game of life and death!")
async def rusroulet(ctx):
  user = ctx.author
  await ctx.respond("""
  ╔═╗───────╔╗╔╗
║╬╠═╦╦╦╗╔═╣╚╣╚╦═╗
║╗╣╬║║║╚╣╩╣╔╣╔╣╩╣
╚╩╩═╩═╩═╩═╩═╩═╩═╝
  """)
  await ctx.respond("I will be generating two numbers, if they match you die, if they don't you live to see another day!")
  num1 = random.randint(0,6)
  num2 = random.randint(0,6)
  if num1 == num2:
    await ctx.respond(f"Your Numbers are {num1} and {num2}, You Loose!")
    role = discord.utils.get(user.guild.roles, name="Muted")
    await user.add_roles(role)
    await ctx.respond("Muted For 10 Minutes as Result of losing!")
    await asyncio.sleep(600)
    await user.remove_roles(role, atomic=True)
  else:
    await ctx.respond(f"Your Numbers are {num1} and {num2}, You live to see another day!")
  return

@client.bridge_command(brief="get user avatar")
async def av(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.respond(userAvatarUrl)
    return		

@client.bridge_command(brief="calculator")
async def math(ctx,opreation:str):
    await ctx.respond(eval(opreation))
    return
	

@client.bridge_command(brief="make the bot say something!")
async def echo(ctx, *, lol):
    await ctx.respond(lol)
    return


@client.bridge_command(brief="i speak what u say uwu")
async def tts(ctx, *, text):
	language = "en"
	vo = gTTS(text=text,lang=language,slow=False,tld="ie")
	vo.save("tts.mp3")
	await ctx.respond(file=discord.File('tts.mp3'))
	os.system("rm tts.mp3")
	return

@client.bridge_command(brief="surf the internet.", description="search using duckduckgo.")
async def search(ctx, *, earch):
   lo = earch.replace(" ","+")
   ct = (f'https://duckduckgo.com/?q={lo}')
   embed = discord.Embed()
   embed.description = f"Search Result: [{earch}]({ct})"
   await ctx.respond(embed=embed)
   return


@client.bridge_command()    
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.respond("I don't have permission to ban members.")
        await ctx.respond("bot does not work")
        return
    await member.ban(reason=reason)
    await ctx.respond(f'{member.mention} has been banned. Reason: {reason or "No reason provided."}')

@client.bridge_command()
async def clear(ctx, amount=5):
    if ctx.author.guild_permissions.manage_messages or ctx.author.id == 720697133531004981:
        amount = amount + 1
        await ctx.channel.purge(limit=amount)
        amount = amount - 1
        clembed = discord.Embed(title='Clear', color=0x123456)
        clembed.add_field(name='Teletubbies vacuum.', value=f'Number of messages deleted: {amount}')
        await ctx.respond(embed=clembed)
        print(f'[ADMIN] Cleared {amount} messages in {ctx.channel}. Invoked by {ctx.message.author}')
    else:
        await ctx.respond("you are not permitted for this action")
    return

@client.bridge_command(brief="roll a dice")
async def roll(ctx, limit=5):
    limit = limit + 1
    print("[DEBUG] got here")
    number = randrange(1,limit)
    await ctx.respond(f":game_die: {number}")
    return
    
@client.bridge_command(name="8ball", brief="ask the bot something")
async def eightball(ctx):
	ers = ["yes", "no", "im not sure", "fuck off"]
	joke = random.choice(ers)
	await ctx.respond(joke)

@client.bridge_command()
async def bmi(ctx, weight:float,*, hgt:float):
	we = weight
	hg = hgt*hgt
	bmi = we/hg
	await ctx.respond(f"Bmi = {bmi} kg/m²")
	return


@client.bridge_command(name="thinge")
async def thinge(ctx, user: discord.User):
    await ctx.respond(f"<@{user.id}> got thinged!")  
    value = user.name
    queer = ctx.author  
    wheer = queer.name
    if wheer not in shoot.col_values(1):
        shoot.append_row([wheer, 1], value_input_option="USER_ENTERED")
    else:
        inded = shoot.col_values(1).index(wheer) + 1
        existing_value = shoot.cell(inded, 2).value
        if existing_value is None:
            existing_value = 0
        else:
            existing_value = int(existing_value)
        shoot.update_cell(inded, 2, existing_value + 1)  
    sorts()
    if value not in sheet.col_values(1):
        sheet.append_row([value, 1], value_input_option="USER_ENTERED") 
    else:
        index = sheet.col_values(1).index(value) + 1 
        existing_value_cell = sheet.cell(index, 2)
        if existing_value_cell.value is None:
            existing_value = 0
        else:
            existing_value = int(existing_value_cell.value)
        sheet.update_cell(index, 2, existing_value + 1)
    sorts()
    return


@client.bridge_command(name="thingesboard")
async def leaderboard(ctx):
    embed1 = discord.Embed(title="thinged Leaderboard", description= "thinge victims", colour=discord.Colour.purple())
    embed1.add_field(name=f"1. @{sheet.acell('A2').value}", value= sheet.acell('B2').value + " thinges", inline=False)
    embed1.add_field(name=f"2. @{sheet.acell('A3').value}",value= sheet.acell('B3').value + " thinges", inline=False)
    embed1.add_field(name=f"3. @{sheet.acell('A4').value}",value= sheet.acell('B4').value + " thinges", inline=False)
    embed1.add_field(name=f"4. @{sheet.acell('A5').value}",value= sheet.acell('B5').value + " thinges", inline=False)
    embed1.add_field(name=f"5. @{sheet.acell('A6').value}",value= sheet.acell('B6').value + " thinges", inline=False)
    embed1.add_field(name=f"6. @{sheet.acell('A7').value}",value= sheet.acell('B7').value + " thinges", inline=False)
    embed1.add_field(name=f"7. @{sheet.acell('A8').value}",value= sheet.acell('B8').value + " thinges", inline=False)
    embed1.add_field(name=f"8. @{sheet.acell('A9').value}",value= sheet.acell('B9').value + " thinges", inline=False)
    embed1.add_field(name=f"9. @{sheet.acell('A10').value}",value= sheet.acell('B10').value + " thinges", inline=False)
    embed1.add_field(name=f"10. @{sheet.acell('A11').value}",value= sheet.acell('B11').value + " thinges", inline=False)
    embed1.set_footer(text=f"powered by cumatron 300000")
    await ctx.respond(embed=embed1)
    return

@client.bridge_command(name="thingistboard")
async def lead(ctx):
    embed1 = discord.Embed(title="thingist Leaderboard", description= "thingists", colour=discord.Colour.purple())
    embed1.add_field(name=f"1. @{shoot.acell('A2').value}", value= shoot.acell('B2').value + " thinged", inline=False)
    embed1.add_field(name=f"2. @{shoot.acell('A3').value}",value= shoot.acell('B3').value + " thinged", inline=False)
    embed1.add_field(name=f"3. @{shoot.acell('A4').value}",value= shoot.acell('B4').value + " thinged", inline=False)
    embed1.add_field(name=f"4. @{shoot.acell('A5').value}",value= shoot.acell('B5').value + " thinged", inline=False)
    embed1.add_field(name=f"5. @{shoot.acell('A6').value}",value= shoot.acell('B6').value + " thinged", inline=False)
    embed1.add_field(name=f"6. @{shoot.acell('A7').value}",value= shoot.acell('B7').value + " thinged", inline=False)
    embed1.add_field(name=f"7. @{shoot.acell('A8').value}",value= shoot.acell('B8').value + " thinged", inline=False)
    embed1.add_field(name=f"8. @{shoot.acell('A9').value}",value= shoot.acell('B9').value + " thinged", inline=False)
    embed1.add_field(name=f"9. @{shoot.acell('A10').value}",value= shoot.acell('B10').value + " thinged", inline=False)
    embed1.add_field(name=f"10. @{shoot.acell('A11').value}",value= shoot.acell('B11').value + " thinged", inline=False)
    embed1.set_footer(text=f"powered by cumatron 300000")
    await ctx.respond(embed=embed1)
    return


@client.bridge_command(brief="play music",description="supported sites: https://docs.yt-dlp.org/en/latest/supportedsites.html")
async def play(ctx, *, link: str = None):
    vcc = ctx.author.voice
    if not vcc:
        await ctx.respond("You need to be in a voice channel to use this command.")
        return
    if not link:
        await ctx.respond("Please provide a valid link or search query.")
        return
    if "&" in link:
        await ctx.respond("Invalid link format.")
        return
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        await ctx.respond("Joining your voice channel...")
        voice_client = await vcc.channel.connect()
    elif voice_client.channel != vcc.channel:
        await ctx.respond(f"Moving to your voice channel {vcc.channel.name}...")
        await voice_client.move_to(vcc.channel)
    if voice_client.is_playing():
        await ctx.respond("I'm already playing music!")
        return
    await ctx.respond(f"Processing your request for: {link}")
    try:
        ytdlp_command = f"yt-dlp --cookies cookies.txt -x --audio-format opus -o song.opus {link}" if link.startswith(("https://", "http://")) else f"yt-dlp -x --audio-format opus -o song.opus 'ytsearch:\"{link}\"'"

        process = await asyncio.create_subprocess_shell(
            ytdlp_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            await ctx.respond(f"Error downloading audio: {stderr.decode('utf-8')}")
            return
        audio_source = discord.FFmpegPCMAudio("song.opus")
        voice_client.play(audio_source)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        os.remove("song.opus")
        await ctx.respond("Finished playing the track!")
    except Exception as e:
        await ctx.respond(f"An error occurred: {str(e)}")

@client.bridge_command(brief="disconnect from the voice channel")
async def disconnect(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.respond("Disconnected from the voice channel.")
    else:
        await ctx.respond("I'm not connected to any voice channel.")


@client.bridge_command(brief="quotes")
async def makeaquote(ctx,*,quote):
    myim = Image.open("black.png")
    title_text = f"""  {textwthing.fill(quote, width=30)} 
                         -{ctx.author}"""
    I1 = ImageDraw.Draw(myim)
    font = ImageFont.truetype('dank.ttf',55)
    I1.text((10,10), title_text, fill=(255,255,255))
    myim.save("quote.png")
    await ctx.respond(file=discord.File('quote.png'))
    os.system("rm quote.png")
    return

@client.bridge_command(brief="Get server information")
async def serverinfo(ctx):
    svr_name = ctx.guild.name
    member_count = len(ctx.guild.members)
    role_count = len(ctx.guild.roles)
    embed = discord.Embed(title="Flurry", description="Server Information", color=discord.Color.red())
    embed.set_thumbnail(url=str(ctx.guild.icon.url)) 
    embed.add_field(name="Server Name:", value=svr_name, inline=True)
    embed.add_field(name="Number of Members:", value=member_count, inline=True)
    embed.add_field(name="Number of Roles:", value=role_count, inline=True)
    await ctx.respond(embed=embed)

@client.bridge_command(brief="Download video from any site")
async def download(ctx, url: str):
    await ctx.respond("Downloading your video... Please wait.")

    try:
        command = f"yt-dlp --cookies cookies.txt -o '%(title)s.%(ext)s' {url}"
        subprocess.run(command, shell=True, check=True)
        files = [f for f in os.listdir() if f.endswith('.mp4') or f.endswith('.m4a')]
        if files:
            latest_file = max(files, key=os.path.getctime) 
            await ctx.respond(file=discord.File(latest_file))
            os.remove(latest_file)  
        else:
            await ctx.respond("Failed to download the video. No file was found.")

    except subprocess.CalledProcessError:
        await ctx.respond("An error occurred while trying to download the video. Please check the URL and try again.")
    except Exception as e:
        await ctx.respond(f"An unexpected error occurred: {e}")

@client.event
async def on_ready():
    print('[BOT] Bot ready.')
    print('[BOT] Started logging')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='LOVE EVERYONE'))

#The below code runs the bot.
print("i have no idea how this started but, yes.")
print("using token: " +secrets["token"])
print("----------------------")
client.run(secrets["token"])
