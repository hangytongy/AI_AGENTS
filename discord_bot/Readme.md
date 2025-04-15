### Steps to run

1. '''sudo apt install python3 python3-pip -y'''
2. git clone https://github.com/hangytongy/AI_AGENTS.git
3. cd AI_AGENTS/discord_bot
4. python3 -m venv venv
5. source venv/bin/activate
6. pip install -r requirements.txt
7. cp .env_example .env
8. nano .env #fill in .env with your discord token, channel ID and openai key
9. python3 discord.py
