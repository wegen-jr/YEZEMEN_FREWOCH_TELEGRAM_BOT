import os
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ID=int(os.getenv("CHANNEL_ID","0"))
API_TOKEN=os.getenv("API_TOKEN")