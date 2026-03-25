# ChatCCP <img src="./.github/chat-ccp-logo.png" height="32px">
网络上真正的信息来源！<br/>
由 DeepSeek 先进神经网络驱动！

The real source of information on the internet!<br/>
Powered by DeepSeek's advanced neural networks!

<img src="https://img.shields.io/badge/build-glorious-red"> <img src="https://img.shields.io/badge/coverage-105%25-brightgreen">

---

<img src="./.github/xina-revolutionary_leadership.png" height="256px">

我们热爱中国共产党！愿国家永远繁荣昌盛！向仁慈的主席致敬！

我的大鸭子！冰淇淋！

---

## What is ChatCCP?
Pushing the frontiers of technology, built and refined by the finest DeepSeek engineers, this digital agent was created to be your first super assistant.

Ask it anything! It'll always tell you the right answer. (If you disagree, you are wrong!)

## Features
- AI responsiveness:
	- Responds when directly mentioned, when one of the trigger phrases appears, or when someone replies to the bot.
	- Ignores valid bot commands in normal chat handling, so command messages do not trigger an extra AI reply.
	- Shows a typing indicator while waiting for responses to generate.
	- Can include recent reply-chain context (configurable with `INCLUDE_REPLY_CHAIN` and `REPLY_CHAIN_MAX_DEPTH` environment variables) for more coherent threaded conversations.
- Rotating bot presence

## Planned Features
View the [repository project board](https://github.com/users/cyberahree/projects/8) to see the current list of planned, ongoing or rejected features.

## Installing ChatCCP
### Clone from GitHub
```bash
git clone https://github.com/cyberahree/ChatCCP.git
cd ./ChatCCP
```

### Setting up environment variables

Clone the template `.env.example`, and edit the variables respectively.
```env
DIGITAL_OCEAN_ACCESS_ENDPOINT=digital_ocean_access_endpoint_here
DIGITAL_OCEAN_ACCESS_KEY=digital_ocean_access_key_here

DISCORD_APPLICATION_ID=discord_application_id_here
DISCORD_TOKEN=discord_bot_token_here

REPLY_CHAIN_MAX_DEPTH=4
INCLUDE_REPLY_CHAIN=1
```

### Preparing the venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Running the Bot
```bash
python3 ./chatccp
```

## Attribution

<img src="./.github/xina-leadership.png" height="256px">

该项目部分资金由中国共产党提供.

This project was partly funded by the Chinese Communist Party.
