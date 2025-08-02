import argparse
from src.config.logging_setup import LoggingSetup
from src.config.settings import SettingsManager
from src.infrastructure.bot.basebot import Bot

CONFIG_PATH_YAML = "./config.yml"
ENV_PATH = ".env"

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="debug")
args = parser.parse_args()

settings = SettingsManager(CONFIG_PATH_YAML)
settings.load_env()
LoggingSetup(is_debug=args.debug)

bot = Bot()
bot.run()



