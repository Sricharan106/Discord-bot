# 🐵 Monkey Bot

Monkey Bot is a powerful and playful Discord bot that combines AI assistance, server moderation, financial simulations in one smart package. Whether you're looking to manage your server, chat with an AI, or simulate your journey to becoming a virtual millionaire, Monkey Bot has something for everyone!

---

## 🚀 Features

### 🤖 General Commands

- `!hello` – Say hi to the bot
- `!bothelp` – Get a full list of bot features
- `!dm` – Send personal messages (to others or yourself)
- `!poll <question>` – Create quick yes/no polls
- `!search <query>` – Ask AI anything (powered by Google Gemini)

### 🛠️ Moderation Tools

- `!ban @user` – Ban users (server owner only)
- `!kick @user` – Kick users (server owner only)
- Auto-deletes messages with offensive language

### 💸 Banking System (Simulation)

- `!balance`, `!pocket` – Check balances
- `!deposit <amount>`, `!withdraw <amount>` – Manage funds
- `!beg` – Randomly get coins
- `!spend <item>` – Buy food, lottery, and more

### 👔 Jobs and Earnings

- `!job <profession>` – Choose a profession (once only!)
- `!work` – Earn based on your profession
- `!yourprofession` – Check your job

### 📈 Investment Simulation

- `!fd <amount>` – Fixed Deposit (safe 6% return in 7 days)
- `!sip <amount>` – SIP (random returns, moderate risk)
- `!stocks` – View real-time stock prices (daily refresh)
- `!buy <stock> <amount>` – Buy shares
- `!sell <stock> <amount>` – Sell shares
- `!yourstocks` – View your stock portfolio

### 📄 Profile Overview

- `!profile` – View your bank, pocket, job, and stocks in one place

---

## 🧠 Powered By

- [Discord.py](https://discordpy.readthedocs.io/)
- [Google Gemini AI](https://ai.google.dev/)
- JSON for persistent storage

---

## 📝 To-Do / Future Features

-⏰ Daily rewards
-📊 Leaderboard and ranking
-🧱 Upgrade system (boost income/stocks)
-🗃️ Switch from JSON to a proper database (e.g., SQLite or PostgreSQL)
-🌐 Web dashboard for bot stats

---

## 🔧 Setup Instructions

1. **Clone this repo**

   ```bash
   git clone https://github.com/yourusername/monkey-bot.git
   cd monkey-bot

   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.

   ```

3. **Create a .env file**

   ```bash
   DISCORD_TOKEN=your-discord-bot-token
   GOOGLE_API_KEY=your-gemini-api-key

   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

Made with ❤️ by Sricharan
