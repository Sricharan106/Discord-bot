import random
import discord
import google.generativeai as genai
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime, time, timedelta
import asyncio

prices = None

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
YOUR_GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    if not update_stock_prices.is_running():
        update_stock_prices.start()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server, {member.name}! We're glad to have you here.")
    await bot.get_channel(1401155132573356112).send(f"Welcome {member.name} to the server!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(word in message.content.lower() for word in ["shit", "fuck", "nigga", "bitch", "son of a bitch ", "asshole"]):
        await message.delete()
        await message.channel.send(f"Watch your language, {message.author.mention}!")

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello! {ctx.author.mention}")
@bot.command()
async def bothelp(ctx):
    embed = discord.Embed(
        title="🤖 Welcome to Monkey Bot!",
        description="I'm your all-in-one assistant bot built to make your Discord experience smarter, fun, and a little more financially educated. Here's what I can do for you:",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="📜 General Commands",
        value=(
            "`!hello` - Say hi to the bot\n"
            "`!bothelp` - Show this help message\n"
            "`!dm` - Get a personal message from the bot\n"
            "`!poll` - Create a poll (Yes/No style)\n"
            "`!search <query>` - Ask anything using AI (powered by GEMINI)"
            "`!profile` - View your profile with bank and stock info"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ Moderation Commands",
        value=(
            "`!ban @user` - Ban a member from the server\n"
            "`!kick @user` - Kick a member from the server"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 Banking System (Game)",
        value=(
            "`!balance` - Check your bank balance\n"
            "`!deposit <amount>` - Deposit money into your bank\n"
            "`!withdraw <amount>` - Withdraw money from your bank\n"
            "`!pocket` - Check your pocket balance\n"
            "`!beg` - Ask for coins like a broke legend 😂\n"
            "`!spend` - Spend money on random stuff"
        ),
        inline=False
    )

    embed.add_field(
        name="👷‍♂️ Job & Earnings",
        value=(
            "`!job` - Choose a profession (once)\n"
            "`!work` - Do your job and earn some cash\n"
            "`!yourprofession` - See your current profession"
        ),
        inline=False
    )

    embed.add_field(
        name="📈 Investment Options (Simulation)",
        value=(
            "`!fd <amount>` – Fixed Deposit: Safe and steady returns. Low risk, low reward.\n"
            "`!sip <amount>` – SIP: Long-term growth with moderate risk. Consistent gains over time.\n"
            "`!stocks` – Show today’s available stock prices\n"
            "`!buy <stock> <amount>` – Invest in a stock of your choice\n"
            "`!sell <stock> <amount>` – Sell your stocks for profit (or loss 😅)\n"
            "`!yourstocks` – View your current stock holdings"
        ),
        inline=False
    )

    embed.add_field(
        name="💡 Tips",
        value=(
            "- Try not to spend all your money 😅\n"
            "- More features coming soon: daily rewards, upgrades, leaderboard, and more!"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def dm(ctx, *, args: str = None):  # after !dm evrythih will be stored as str in args
    if not args:
        await ctx.send("❌ Usage: `!dm @user message` or `!dm message`")
        return

    words = args.split()  # Split the message into words
    member = None   # default member to none
    message = args # storing everything in message

    # Check if first word is a mention
    if len(ctx.message.mentions) > 0:
        member = ctx.message.mentions[0]
        message = ' '.join(words[1:])  # Remove mention from message
    else:
        member = ctx.author  # DM yourself

    if not message.strip():
        await ctx.send("❌ Please include a message to send.")
        return

    try:
        await member.send(f"📩 **Message from {ctx.author.name}**:\n{message}")
        await ctx.send(f"✅ Message sent to {member.mention if member != ctx.author else 'yourself'}.")
    except discord.Forbidden:
        await ctx.send(f"❌ Couldn’t send DM to {member.mention if member != ctx.author else 'you'}. They might have DMs turned off.")

@bot.command()
async def poll(ctx, *, question: str = None):
    if not question:
        await ctx.send("❌ Usage: `!poll <question>`")
        return

    embed = discord.Embed(
        title="Poll",
        description=question,
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
@bot.command()
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if ctx.author.id != ctx.guild.owner_id:
        return await ctx.send("❌ Only the **server owner** can use this command.")

    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned.\n📝 Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if ctx.author.id != ctx.guild.owner_id:
        return await ctx.send("❌ Only the **server owner** can use this command.")

    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked.\n📝 Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")

@bot.command()
async def search(ctx, *, query: str = None):
    if not query:
        await ctx.send("❌ Usage: `!search <query>`")
        return
    
    try:
        await ctx.send(" 🤖 Thinking...")
        genai.configure(api_key=YOUR_GEMINI_API_KEY)

        # Initialize Gemini model
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        # Generate content
        response = model.generate_content(query)

        # Print response
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"❌ Error: `{e}`")


# fun part

BANK_FILE = "bank.json"

def load_bank_data():
    if not os.path.exists(BANK_FILE):
        with open(BANK_FILE, "w") as f:
            json.dump({}, f)
    with open(BANK_FILE, "r") as f:
        return json.load(f)

def save_bank_data(data):
    with open(BANK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_balance(user_id):
    bank_data = load_bank_data()
    return bank_data.get(str(user_id), {}).get("bank", 0)

def get_pocket_balance(user_id):
    bank_data = load_bank_data()
    return bank_data.get(str(user_id), {}).get("pocket", 0)

def update_balance(user_id, amount):
    bank_data = load_bank_data()
    user_id = str(user_id)

    if user_id not in bank_data:
        bank_data[user_id] = {"bank": 0, "pocket": 0}
    bank_data[user_id]["bank"] += amount

    save_bank_data(bank_data)

def update_pocket_balance(user_id, amount):
    bank_data = load_bank_data()
    user_id = str(user_id)

    if user_id not in bank_data:
        bank_data[user_id] = {"bank": 0, "pocket": 0}
    bank_data[user_id]["pocket"] += amount

    save_bank_data(bank_data)

def get_user_profession(user_id):
    bank_data = load_bank_data()
    return bank_data.get(str(user_id), {}).get("profession", None)

def update_user_profession(user_id, profession):
    bank_data = load_bank_data()
    user_id = str(user_id)

    # Ensure user data exists
    if user_id not in bank_data:
        bank_data[user_id] = {"bank": 0, "pocket": 0, "profession": profession}
    else:
        bank_data[user_id]["profession"] = profession

    save_bank_data(bank_data)

def get_owned_stocks(user_id):
    data = load_bank_data()
    return data.get(str(user_id), {}).get("stocks", {})

def update_owned_stocks(user_id, stock, amount):
    data = load_bank_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {"bank": 0, "pocket": 0, "stocks": {}}
    data[user_id]["stocks"][stock] = data[user_id]["stocks"].get(stock, 0) + amount
    save_bank_data(data)

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = get_balance(user_id)
    await ctx.send(f"💰 Your balance: {balance}")

@bot.command()
async def pocket(ctx):
    user_id = str(ctx.author.id)
    balance = get_pocket_balance(user_id)
    await ctx.send(f"💼 Your pocket balance: {balance}")

@bot.command()
async def deposit(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")

    if get_pocket_balance(str(ctx.author.id)) < amount:
        return await ctx.send("❌ Insufficient funds in your pocket.")
    user_id = str(ctx.author.id)
    update_balance(user_id, amount)
    update_pocket_balance(user_id, -amount)
    await ctx.send(f"✅ Deposited {amount} coins. Your new balance is: {get_balance(user_id)}")
    await ctx.send(f"💼 Your pocket balance is now: {get_pocket_balance(user_id)}")

@bot.command()
async def withdraw(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")

    user_id = str(ctx.author.id)
    if get_balance(user_id) < amount:
        return await ctx.send("❌ Insufficient funds.")

    update_balance(user_id, -amount)
    update_pocket_balance(user_id, amount)
    await ctx.send(f"✅ Withdrew {amount} coins. Your new balance is: {get_balance(user_id)}")
    await ctx.send(f"💼 Your pocket balance is now: {get_pocket_balance(user_id)}")

@bot.command()
async def beg(ctx):
    import random
    amount = random.randint(1, 100)
    update_pocket_balance(str(ctx.author.id), amount)
    await ctx.send(f"🙏 You begged and received {amount} coins! Your pocket balance is now: {get_pocket_balance(str(ctx.author.id))}")

@bot.command()
async def yourprofession(ctx):
    profession = get_user_profession(str(ctx.author.id))
    if profession:
        await ctx.send(f"💼 Your profession: {profession}")
    else:
        await ctx.send("❌ You don't have a profession set (JOB LESS).")

@bot.command()
async def job(ctx, *, profession: str):
    await ctx.send("💼 Choose your profession wisely — this is a one-time choice and **cannot be changed later**.\nAvailable jobs: Engineer, Doctor, Artist, Teacher, Chef")
    professions = ["Engineer", "Doctor", "Artist", "Teacher", "Chef"]
    user_id = str(ctx.author.id)

    profession = profession.title()  # make it case-insensitive like "doctor" -> "Doctor"

    if profession not in professions:
        await ctx.send(f"❌ Invalid profession. Choose from: {', '.join(professions)}")
        return

    if get_user_profession(user_id):
        await ctx.send("❌ You already have a profession.")
        return

    update_user_profession(user_id, profession)
    await ctx.send(f"🎉 {ctx.author.mention}, you are now a **{profession}**!\n🛠️ You can use `!work` to earn coins based on your profession.")

@bot.command()
async def work(ctx):
    user_id = str(ctx.author.id)
    profession = get_user_profession(user_id)

    if not profession:
        await ctx.send("❌ You don't have a profession set (JOB LESS).")
        return

    # Simulate work and earning money
    earnings = random.randint(200, 600)
    update_balance(user_id, earnings)
    await ctx.send(f"💼 You worked as a {profession} and earned {earnings} coins!")

@bot.command()
async def spend(ctx, *, item: str):
    user_id = str(ctx.author.id)
    item = item.lower()
    
    store = {
        "food": 30,
        "clothes": 100,
        "lottery": 100,
        "phone": 1200
    }

    if item not in store:
        await ctx.send(f"❌ Invalid item. Available items: {', '.join(store.keys())}")
        return
    cost = store[item]
    pocket_balance = get_pocket_balance(user_id)

    if pocket_balance < cost:
        await ctx.send("❌ Insufficient funds in your pocket.")
        return

    update_pocket_balance(user_id, -cost)
    await ctx.send(f"✅ You spent {cost} coins on {item}.")
    if item == "lottery":
        import random
        win = random.randint(0, 500)
        update_pocket_balance(user_id, win)
        await ctx.send(f"🎉 Lottery Result: You won ₹{win}!")

@bot.command()
async def profile(ctx):
    user_id = str(ctx.author.id)
    data = load_bank_data().get(user_id, {})
    bank = data.get("bank", 0)
    pocket = data.get("pocket", 0)
    profession = data.get("profession", "Jobless")
    stocks = data.get("stocks", {})

    stock_text = "\n".join(f"{name}: {qty} shares" for name, qty in stocks.items()) if stocks else "None"

    await ctx.send(
        f"📜 **Profile for {ctx.author.mention}**\n"
        f"💰 Bank Balance: ₹{bank}\n"
        f"💼 Pocket Balance: ₹{pocket}\n"
        f"🧑‍💼 Profession: {profession}\n"
        f"📈 Stocks:\n{stock_text}"
    )

# invest things

@tasks.loop(hours=24)
async def update_stock_prices():
    global prices
    prices = {
        "TechCorp": random.randint(80, 120),
        "GreenEnergy": random.randint(120, 180),
        "CryptoX": random.randint(200, 400)
    }
    print("✅ Stock prices updated:", prices)

@update_stock_prices.before_loop
async def before_update_stock_prices():
    await bot.wait_until_ready()
    # now = datetime.now()
    # target_time = datetime.combine(now.date(), time(hour=8, minute=0))
    # if now > target_time:
    #     target_time += timedelta(days=1)
    # await asyncio.sleep((target_time - now).total_seconds())


@bot.command()
async def fd(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")

    user_id = str(ctx.author.id)
    if get_balance(user_id) < amount:
        return await ctx.send("❌ Insufficient funds.")

    update_balance(user_id, -amount)
    await ctx.send(f"✅ You have invested {amount} coins.")

    await ctx.send(f"💰 Your fixed deposit is now active. You will receive a safe return of 6% after 7 days.")

    await ctx.send("7 days have completed! Your fixed deposit has matured.")
    interest = int(amount * 0.06) + int(amount)
    update_balance(user_id, interest)
    await ctx.send(f"🎉 You received {interest - amount} coins as interest. Your new balance is: {get_balance(user_id)}")

@bot.command()
async def sip(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")
    
    user_id = str(ctx.author.id)
    if get_balance(user_id) < amount:
        return await ctx.send("❌ Insufficient funds.")

    update_balance(user_id, -amount)
    await ctx.send(f"✅ You have invested {amount} coins.")

    percentage = random.randint(1, 15)  # Random interest rate between 1% and 15%
    if percentage < 5:
        await ctx.send(f"⚠️ Your SIP is active with a low return of {percentage}%. the market has downturns, so be cautious next time.")
        additional_loss = random.randint(1, 100)
        update_balance(user_id, -int(percentage/100*amount)-additional_loss)
        update_balance(user_id, amount)  # Return the principal amount
        await ctx.send(f"bad luck your loss is {int(percentage/100*amount)+additional_loss}, your balance is {get_balance(user_id)}")
        return

    else:
        await ctx.send(f"💰 Your SIP is now active. You will receive a safe return of {percentage}% after 30 days.")

        await ctx.send("30 days have completed! Your SIP has matured.")
        interest = int(amount * (percentage / 100)) + int(amount)
        update_balance(user_id, interest)
        await ctx.send(f"🎉 You received {interest - amount} coins as interest. Your new balance is: {get_balance(user_id)}")
        return


@bot.command()
async def stocks(ctx):
    await ctx.send("📈 Welcome to the Stock Market! Invest in stocks for high risk and potentially high rewards.")

    embed = discord.Embed(
        title="📊 Available Stocks",
        description="Choose a stock and invest using `!buy <stock> <amount>`",
        color=discord.Color.blue()
    )

    embed.add_field(name="🔹 TechCorp", value=f"High volatility, high reward `{prices['TechCorp']}`", inline=False)
    embed.add_field(name="🔸 GreenEnergy", value=f"Moderate risk, stable growth `{prices['GreenEnergy']}`", inline=False)
    embed.add_field(name="🪙 CryptoX", value=f"Very high risk, massive returns (or losses) `{prices['CryptoX']}`", inline=False)

    embed.add_field(name="Note", value="Every day(24 hours) stock market values changes.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, stock: str, amount: int):
    user_id = str(ctx.author.id)
    stock = stock.strip()
    if stock not in prices:
        await ctx.send(f"❌ Invalid stock. Available: {', '.join(prices.keys())}")
        return

    cost = prices[stock] * amount
    balance = get_balance(user_id)

    if balance < cost:
        return await ctx.send(f"❌ Not enough balance. You need ₹{cost} to buy {amount} of {stock}.")

    # Deduct cost
    update_balance(user_id, -cost)

    # Load bank data and add stocks
    data = load_bank_data()
    user_data = data.setdefault(user_id, {"bank": 0, "pocket": 0, "stocks": {}})
    user_stocks = user_data.setdefault("stocks", {})
    user_stocks[stock] = user_stocks.get(stock, 0) + amount
    save_bank_data(data)

    await ctx.send(f"✅ You bought {amount} shares of {stock} at ₹{prices[stock]} each.\n💰 Total: ₹{cost}")

@bot.command()
async def sell(ctx, stock: str, amount: int):
    user_id = str(ctx.author.id)
    stock = stock.strip()

    if stock not in prices:
        return await ctx.send(f"❌ Invalid stock. Available: {', '.join(prices.keys())}")

    if amount <= 0:
        return await ctx.send("❌ Amount must be greater than 0.")

    data = load_bank_data()
    user_data = data.get(user_id, {})
    user_stocks = user_data.get("stocks", {})

    if stock not in user_stocks or user_stocks[stock] < amount:
        return await ctx.send(f"❌ You don't own {amount} shares of {stock}.")

    sell_price = prices[stock] * amount
    user_stocks[stock] -= amount

    if user_stocks[stock] == 0:
        del user_stocks[stock]  # Clean up zero stock

    # Update bank balance and save
    user_data["stocks"] = user_stocks
    user_data["bank"] = user_data.get("bank", 0) + sell_price
    data[user_id] = user_data
    save_bank_data(data)

    await ctx.send(f"✅ You sold {amount} shares of {stock} for ₹{sell_price}.")


@bot.command()
async def yourstocks(ctx):
    user_id = str(ctx.author.id)
    data = load_bank_data()
    user_data = data.get(user_id, {})
    owned_stocks = get_owned_stocks(user_id)
    if owned_stocks:
        stock_text = ""
        for stock, qty in owned_stocks.items():
            price = prices.get(stock, 0)
            value = price * qty
            stock_text += f"{stock}: {qty} shares (₹{price} each = ₹{value})\n"
    else:
        stock_text = "None"

    await ctx.send(f"📈 **Your Stocks:**\n{stock_text}")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)