import discord
from discord.ext import commands
import os
import json
import random
from discord.ext.commands import Bot
import asyncio
import time
import re
from datetime import datetime, timedelta

intents = discord.Intents.all()
Bot = commands.Bot(command_prefix = "$", intents=intents)
Bot.remove_command('help') #removing common command help


token = '' #there must be token



mainshop = [{"name":"sub", "price":2500, "description":"week subscription"},
			{"name":"goldsub", "price":10000, "description":"month subscription"},
			{"name":"custom role", "price":1000, "description":"custom role's color and name"}]
#dictionary for shop


cmnds = [{"name":"shop", "description":"Shows you products able to buy"},
		 {"name":"echo", "description":"duplicate your message"},
		 {"name":"balance", "description":"Shows your balance"},
		 {"name":"ping", "description":"Returns: :ping_pong: ping"},
		 {"name":"slots", "description":"Your bet will be multiplied or you will lose"},
		 {'name':"custom_role", "description":"Creates custom role for you ||custom name and colour||, for example: $custom_role 0x2ecc71 test"},
		 {"name":"sub", "description":"Gives you sub role for a week"},
		 {"name":"gold_sub", "description":"Gives you gold sub role for a month"},
		 {"name":"give", "description":"By this command you can give somebody your gold coins with n amount"},
		 {"name":"quot", "description":"You can quote someone's message by message link sent in chat"},
		 {"name":"slap", "description":"You can slap somebody by mentioning him ||cost 20 gold coins||"},
		 {"name":"slapp", "description":"You can slap somebody by ID ||cost 20 gold coins||"},
		 {"name":"hug", "description":"You can hug somebody by mentioning him ||cost 20 gold coins||"},
		 {"name":"hugg", "description":"You can hug somebody by ID ||cost 20 gold coins||"}]
#dictionary for help command

@Bot.command()
async def shop(ctx):
	emb = discord.Embed(title = "Shop", color = 0x2ecc71)

	for item in mainshop:
		name = item["name"]
		price = item["price"]
		desc = item["description"]
		emb.add_field(name = name, value = f":moneybag: {price} | {desc}")

	await ctx.send(embed = emb)
#command printing shop in embedd using 'mainshop' dictionary

@Bot.command()
async def info(ctx):
	emb = discord.Embed(title = "commands", color = 0xf1c40f)

	for item in cmnds:
		name = item["name"]
		desc = item["description"]
		emb.add_field(name = name, value = f"{desc}")

	await ctx.send(embed = emb)
#help command using 'cmnds' dictionary


@Bot.command()
async def echo(ctx, *, message: str):
	await ctx.send(message)
#fun command repeating words in argument

@Bot.event
async def on_ready():

	await Bot.change_presence(activity=discord.Game(name="$info"))

	print("Ready...")
#printing string when bot is launched and setting his status

@Bot.command()
async def balance(ctx):
	await ctx.message.delete()
	await open_account(ctx.author)

	user = ctx.author

	users = await get_bank_data()

	wallet_amt = users[str(user.id)]["wallet"]

	emb = discord.Embed(title = f"<:BotApprove:793013434844315648> {ctx.author.name}'s balance", description = ':moneybag: {} gold coins'.format(wallet_amt), color = 0x2ecc71)
	await ctx.send(embed = emb)
#checking balance from json file

@Bot.command()
async def ping(ctx):
	t = time.time()
	message = await ctx.send(embed = discord.Embed(description = ':ping_pong: pong!'))
	emb = discord.Embed(description = f':ping_pong: ping: {str(int((time.time() - t )*1000))} ms', color = 0x3498db)
	await asyncio.sleep(1)
	await message.edit(embed = emb)
#checking ping of a bot

@Bot.command()
@commands.cooldown(1, 6, commands.BucketType.user)
async def slots(ctx, amount = None):
	user = ctx.author
	await open_account(user) #checking if user is in the json file by 'open_account' function -- see down 385 line


	bal = await update_bank(user) #variable for changing wallet amount, also see down


	if amount == None:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> Please enter your bet", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	amount = int(amount)
	if amount>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	if amount<=0:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> Bet must be positive", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return
	#some checks


	embe = discord.Embed(description = "**Calculating your chances**", color = 0x2ecc71)
	message = await ctx.send(embed = embe)
	await asyncio.sleep(3)
	await message.edit(embed = discord.Embed(description = "**Is that really random ?**", color = 0x2ecc71))
	await asyncio.sleep(3)


	if random.randint(1 ,100) > 60:
		await update_bank(user, -1*amount, "wallet")


		await update_bank(user, round(1.75*amount), "wallet")
		await message.edit(embed = discord.Embed(description = "<:BotApprove:793013434844315648> Your bet was multiplied by 1.75", color = 0x2ecc71))
	else:
		await update_bank(user, -1*amount, "wallet")
		await message.edit(embed = discord.Embed(description = "I'm sorry to hear that, you lost your bet", color = 0x2ecc71))
	#slot system with 60% chance for winning and 40% chance to lose

	





@Bot.command()
async def custom_role(ctx, colour: str, *, name: str):
	colour = discord.Color(value=int(colour, 16)) #getting hexadecimal number for colour
	print(colour)
	user = ctx.author
	await open_account(user)
	await ctx.message.delete()

	bal = await update_bank(user)

	if 1000>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await ctx.guild.create_role(name = name, colour = colour)
	await discord.utils.get(ctx.guild.roles, name = name).edit(position=ctx.author.top_role.position+1, mentionable = True, hoist = True)
	#creating role with mentionable and it's colour in your nickname

	await update_bank(user, -1000, "wallet")

	role = discord.utils.get(ctx.guild.roles, name = name)
	
	await user.add_roles(role)
	#adding member's role to him

	emb = discord.Embed(description = "<:BotApprove:793013434844315648> You bought custom role for a week!", color = 0x2ecc71)
	await ctx.send(embed = emb)
	#there I am using server emoji, feel free to change it

	await asyncio.sleep(604800)
	await user.remove_roles(role)
	await ctx.author.send('Your weekly custom role has come to an end')
	#deleting role after week


@Bot.command()
async def sub(ctx):
	sub_role = ctx.guild.get_role(792351598901723167)
	await open_account(ctx.author)
	await ctx.message.delete()

	user = ctx.author

	bal = await update_bank(user)

	if 2500>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(user, -2500, "wallet")

	await user.add_roles(sub_role)

	emb = discord.Embed(description = "<:BotApprove:793013434844315648> You bought subscription for a week!", color = 0x2ecc71)
	await ctx.send(embed = emb)

	await asyncio.sleep(604800)
	await user.remove_roles(sub_role)
	await ctx.author.send('Your weekly subscription has come to an end')



@Bot.command()
async def gold_sub(ctx):
	gold_sub_role = ctx.guild.get_role(792351598901723167)
	await open_account(ctx.author)
	await ctx.message.delete()

	user = ctx.author

	bal = await update_bank(user)

	if 10000>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(user, -10000, "wallet")

	await user.add_roles(gold_sub_role)

	emb = discord.Embed(description = "<:BotApprove:793013434844315648> You bought subscription for a month!", color = 0x2ecc71)
	await ctx.send(embed = emb)

	await asyncio.sleep(2592000)
	await user.remove_roles(gold_sub_role)
	await ctx.author.send('Your monthly subscription has expired')




@Bot.command()
async def give(ctx, member:discord.Member, amount = None):
	await open_account(ctx.author)
	await open_account(member)
	await ctx.message.delete()


	if amount == None:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> Please enter amount", color = 0x2ecc71)
		await ctx.send(embed = emb)
		return

	bal = await update_bank(ctx.author)

	amount = int(amount)
	if amount>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	if amount<=0:
		emb = discord.Embed(description = '<:BotReject:793013434794246144> amount must be positive', color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(ctx.author, -1*amount, "wallet")
	await update_bank(member, 1*amount, "wallet")

	emb = discord.Embed(description = f"<:BotApprove:793013434844315648> You gave {member.name} {amount} gold coins", color = 0x2ecc71)
	await ctx.send(embed = emb)


@Bot.command()
@commands.has_permissions(administrator = True)
async def take(ctx, member:discord.Member, amount = None):
	await open_account(member)

	if amount == None:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> Please enter amount", color = 0x2ecc71)
		await ctx.send(embed = emb)
		return

	bal = await update_bank(member)

	amount = int(amount)
	if amount>bal:
		await ctx.send("<:BotReject:793013434794246144> That member don't have that much gold coins")
		return

	if amount<=0:
		emb = discord.Embed(description = '<:BotReject:793013434794246144> amount must be positive', color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(member, -1*amount, "wallet")

	emb = discord.Embed(description = f"<:BotApprove:793013434844315648> You took from {member.name} {amount} gold coins", color = 0x2ecc71)
	await ctx.send(embed = emb)
	#administrator command for taking money from another user, for example in order to punish


@Bot.command()
@commands.has_permissions(administrator = True)
async def award(ctx, member:discord.Member, amount = None):
	await open_account(member)

	if amount == None:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> Please enter amount", color = 0x2ecc71)
		await ctx.send(embed = emb)
		return

	bal = await update_bank(member)

	amount = int(amount)

	if amount<=0:
		emb = discord.Embed(description = '<:BotReject:793013434794246144> amount must be positive', color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(member, 1*amount, "wallet")

	emb = discord.Embed(description = f"<:BotApprove:793013434844315648> You gave {member.name} {amount} gold coins", color = 0x2ecc71)
	await ctx.send(embed = emb)
	#admin command for awarding users without losing yourself money -- gold coins in my case

@Bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		emb = discord.Embed(description = '<:BotReject:793013434794246144> You missed required argument', color = 0xe74c3c)
		await ctx.send(embed = emb)
	elif isinstance(error, commands.MissingPermissions):
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have permissions to do that", color = 0xe74c3c)
		await ctx.send(embed = emb)
	elif isinstance(error, commands.CommandNotFound):
		emb = discord.Embed(description = "<:BotReject:793013434794246144> This command doesn't exist", color = 0xe74c3c)
		await ctx.send(embed = emb)
	elif isinstance(error, commands.CommandOnCooldown):
		emb = discord.Embed(description = '<:BotReject:793013434794246144> Please be patient, there is cooldown', color = 0xe74c3c)
		await ctx.send(embed = emb)
	else:
		raise error
	#some errors managing, like cooldown and not every arguments were given



@Bot.event
async def on_message(message):
	await open_account(message.author)

	if len(message.content) > 10:
		user = message.author

		users = await get_bank_data()

		act_cash = random.randrange(2)

		users[str(user.id)]["wallet"] += act_cash

		with open("mainbank.json", "w") as f:
			json.dump(users, f)
	#there is active coins system
	#for each message longer than 10 symbols bot adds 1 or 2 coins


	if message.content.startswith('https://discord.com') or message.content.startswith('http://discord.com'):
		link = message.content.split('/')
		msssg = await Bot.get_guild(int(link[-3])).get_channel(int(link[-2])).fetch_message(int(link[-1]))
		await message.delete()
		emb = discord.Embed(title = f'{message.author.name} quoted {str(msssg.author.name)}', description = f'{msssg.content}', color = 0x1abc9c)
		await message.channel.send(embed = emb)
	#functionality of these lines is: if somebody sends in chat message link, bot fetches message content and sending message in which you can see who sent link, who was quoted and quoted message

	await Bot.process_commands(message)


async def open_account(user):
	
	users = await get_bank_data()


	if str(user.id) in users:
		return False
	else:
		users[str(user.id)] = {}
		users[str(user.id)]["wallet"] = 0

	with open("mainbank.json", "w") as f:
		json.dump(users, f)

	return True
	#checking if user is in the json file


async def get_bank_data():
	with open("mainbank.json", "r") as f:
		users = json.load(f)

	return users
	#getting amount user's coins

async def update_bank(user, change = 0, mode = "wallet"):
	users = await get_bank_data()

	users[str(user.id)][mode] += change

	with open("mainbank.json", "w") as f:
		json.dump(users, f)

	bal = users[str(user.id)]["wallet"]

	return bal
	#changing amount of user's money function



@Bot.command()
async def slap(ctx, member : discord.Member):
	items = [
	discord.Embed(title = None, description = f"For the whole chat there was a noise from a {ctx.author.mention} slap {member.mention} in the face!", color=0x3498db), 
	discord.Embed(title = None, description = f"{ctx.author.mention} gave countless slaps in the face {member.mention}, which even exceeded the five-year plan for slaps.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} slapped {member.mention}", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} saying \"random do not let me down\" slapped {member.mention}. Spoiler: his expectations were not met.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} wanted to give all existing slaps in the world for {member.mention}, but there was only enough money for one.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} with a slap in the face, he broke not only {member.mention} face, but also the fourth wall. Hello everyone, they keep me in a dark basement on a chain and I run out of ideas, if I don't fulfill the quota, I will feel very bad.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} and {member.mention} met, spark, storm, madness, slap!", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} gave such a slap {member.mention} that he broke his arm in four places.", color=0x3498db),
	discord.Embed(title = None, description = f"{member.mention} got beaten by {ctx.author.mention}!", color=0x3498db)]
	randomitem = random.choice(items)	
	await ctx.message.delete()
	await open_account(ctx.author)

	bal = await update_bank(ctx.author)

	if 20>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(ctx.author, -20, "wallet")

	await ctx.send(embed=randomitem)
	


@Bot.command()
async def slapp(ctx, member_id:int):
	member = ctx.guild.get_member(member_id)
	items = [
	discord.Embed(title = None, description = f"For the whole chat there was a noise from a {ctx.author.mention} slap {member.mention} in the face!", color=0x3498db), 
	discord.Embed(title = None, description = f"{ctx.author.mention} gave countless slaps in the face {member.mention}, which even exceeded the five-year plan for slaps.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} slapped {member.mention}", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} saying random do not let me down slapped {member.mention}. Spoiler: his expectations were not met.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} wanted to give all existing slaps in the world for {member.mention}, but there was only enough money for one.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} with a slap in the face, he broke not only {member.mention} face, but also the fourth wall. Hello everyone, they keep me in a dark basement on a chain and I run out of ideas, if I don't fulfill the quota, I will feel very bad.", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} and {member.mention} met, spark, storm, madness, slap!", color=0x3498db),
	discord.Embed(title = None, description = f"{ctx.author.mention} gave such a slap {member.mention} that he broke his arm in four places.", color=0x3498db),
	discord.Embed(title = None, description = f"{member.mention} got beaten by {ctx.author.mention}!", color=0x3498db)]
	randomitem = random.choice(items)
	await ctx.message.delete()
	await open_account(ctx.author)

	bal = await update_bank(ctx.author)

	if 20>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(ctx.author, -20, "wallet")

	await ctx.send(embed=randomitem)




@Bot.command()
async def hug(ctx, member : discord.Member):
	items = [
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} with all the warmth he could.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} threw a hook, pulled and hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} quietly crept up behind and... gently hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} without thinking about the consequences, hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} gave free hugs {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} and gave some candies", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} squeezed {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} and stuck in his texture", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} with his claws.", color=0xe91e63)]
	randomitem = random.choice(items)
	await ctx.message.delete()
	await open_account(ctx.author)

	bal = await update_bank(ctx.author)

	if 20>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(ctx.author, -20, "wallet")

	await ctx.send( embed = randomitem )
	



@Bot.command()
async def hugg(ctx, member_id:int):
	member = ctx.guild.get_member(member_id)
	items = [
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} with all the warmth he could.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} threw a hook, pulled and hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} quietly crept up behind and... gently hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} without thinking about the consequences, hugged {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} gave free hugs {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} and gave some candies", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} squeezed {member.mention}.", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} and stuck in his texture", color=0xe91e63),
	discord.Embed(title=None, description = f"{ctx.author.mention} hugged {member.mention} with his claws.", color=0xe91e63)]
	randomitem = random.choice(items)
	await ctx.message.delete()
	await open_account(ctx.author)

	bal = await update_bank(ctx.author)

	if 20>bal:
		emb = discord.Embed(description = "<:BotReject:793013434794246144> You don't have that much gold coins", color = 0xe74c3c)
		await ctx.send(embed = emb)
		return

	await update_bank(ctx.author, -20, "wallet")

	await ctx.send( embed = randomitem )


Bot.run(token)
#running bot