import json
import pandas as pd
from datetime import date, datetime
from telethon import TelegramClient

import os
from dotenv import load_dotenv

load_dotenv()

# Setting configuration values
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
api_hash = str(api_hash)
phone = os.getenv("TELEGRAM_PHONE")
username = os.getenv("TELEGRAM_USERNAME")
user_input_channel = os.getenv("TELEGRAM_USER_INPUT_CHANNEL")

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)

class Scraper: 

    def __init__(self, api_id, api_hash, phone, username, user_input_channel):
        self.channel = user_input_channel
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.username = username
        self.client = TelegramClient(self.username, self.api_id, self.api_hash)
        self.client.start()
        
    async def scrape_messages(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            await self.client.sign_in(self.phone, input('Enter the code: '))
        
        if not self.channel:
            self.channel = input('Enter entity (telegram URL or entity id): ')

        print('scraping messages')
        data = [] 
        async for message in self.client.iter_messages(self.channel, reverse=True):
            data.append([message.sender_id, message.text, message.date, message.id, message.peer_id.channel_id ])

        df = pd.DataFrame(data, columns=["message.sender_id", "message.text", "message.date", "message.id", "message.peer_id.channel_id" ]) # creates a new dataframe
        df.to_csv(self.channel.split('/')[1] + '.csv', encoding='utf-8')
        return df
    

def main(): 
    scraper = Scraper(api_id, api_hash, phone, username, user_input_channel)
    scraper.client.start()
    scraper.client.connect()
    scraper.client.loop.run_until_complete(scraper.scrape_messages())

main()