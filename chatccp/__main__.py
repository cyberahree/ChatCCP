from bot import ChatCCP

from dotenv import load_dotenv
from pathlib import Path

if __name__ == "chatccp" or __name__ == "__main__":
    load_dotenv(
        Path(__file__).parent.parent / ".env"
    )

    bot = ChatCCP()
    bot.run()