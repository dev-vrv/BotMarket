import os
import logging
from dotenv import load_dotenv

# Environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS').split(',')))
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL')

# Base dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging
if not os.path.exists(os.path.join(BASE_DIR, 'log')):
    os.makedirs(os.path.join(BASE_DIR, 'log'))
    
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.path.join(BASE_DIR, 'log/bot.log'),
    encoding='utf-8',
    datefmt="%Y-%m-%d %H:%M:%S"
)