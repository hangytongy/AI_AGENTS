### Steps to run

1. ```sudo apt install python3 python3-pip -y```
2. ```git clone https://github.com/hangytongy/AI_AGENTS.git```
3. ```cd AI_AGENTS/discord_bot```
4. ```python3 -m venv venv```
5. ```source venv/bin/activate```
6. ```pip install -r requirements.txt```
7. ```cp .env_example .env```
8. ```nano .env #fill in .env with your discord token, channel ID and openai key```
9. ```python3 discord.py```
10. 
```
sudo tee /etc/systemd/system/discord.service > /dev/null <<EOF
[Unit]
Description=Monitor RUSD price and TVL
After=network.target

[Service]
Type=simple
ExecStart=/root/AI_AGENTS/discord_bot/venv/bin/python3 /root/AI_AGENTS/discord_bot/discord.py
WorkingDirectory=/root/AI_AGENTS/discord_bot
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```
11.
```
systemctl daemon-reload
systemctl enable discord.service
systemctl start discord.service
```
