import os
import dotenv

if __name__ == "__main__":
    dotenv.load_dotenv()

    if token := os.environ.get("TOKEN"):
        import bot

        bot.main(token)
    else:
        print("Environment variable not found: TOKEN")
