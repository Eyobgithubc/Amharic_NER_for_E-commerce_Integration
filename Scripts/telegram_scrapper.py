import csv
import os
import re  
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError


load_dotenv('C:/Users/teeyob/Amharic_NER_for_E-commerce_Integration/Scripts/env.txt')
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('phone')
print(api_id )

size_pattern = re.compile(r'(?i)\bSize\b[:\- ]?([0-9, ]+)', re.UNICODE)
price_pattern = re.compile(r'(?i)\bPrice\b[:\- ]?([0-9, ]+ birr)', re.UNICODE)  
call_pattern = re.compile(r'(?i)\bcall\b[:\- ]?(\+?[0-9 ]+)', re.UNICODE)
address_pattern = re.compile(r'አድራሻ.*', re.UNICODE)  

async def scrape_channel(client, channel_username, writer, media_dir):
    entity = await client.get_entity(channel_username)
    channel_title = entity.title 
    
    async for message in client.iter_messages(entity, limit=10000):
        media_path = None
        full_message_text = ""

      
        if message.raw_text:
            full_message_text = message.raw_text.strip() 
        
        
        size_match = size_pattern.search(full_message_text)
        price_match = price_pattern.search(full_message_text)
        call_match = call_pattern.search(full_message_text)
        address_match = address_pattern.search(full_message_text)

       
        size = size_match.group(1) if size_match else "N/A"
        price = price_match.group(1) if price_match else "N/A"
        call = call_match.group(1) if call_match else "N/A"
        address = address_match.group(0) if address_match else "N/A"

        
        temp_message_text = f"{full_message_text}\n\nSize: {size}\nPrice: {price}\nCall: {call}\nAddress: {address}"
        print(temp_message_text)  

       
        if message.media and hasattr(message.media, 'photo'):
            filename = f"{channel_username}_{message.id}.jpg"
            media_path = os.path.join(media_dir, filename)
            await client.download_media(message.media, media_path)

        
        writer.writerow([channel_title, channel_username, message.id, full_message_text, size, price, call, address, message.date, media_path])


client = TelegramClient('scraping_session1', api_id, api_hash, timeout=60)

async def main():
    await client.start()

    
    media_dir = 'photos'
    os.makedirs(media_dir, exist_ok=True)

    
    with open('telegram_ethio_brand_data.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['Channel Title', 'Channel Username', 'ID', 'Message', 'Size', 'Price', 'Call', 'Address', 'Date', 'Media Path'])

        
        channels = [
            '@ethio_brand_collection',  
        ]

        
        for channel in channels:
            while True:
                try:
                    await scrape_channel(client, channel, writer, media_dir)
                    print(f"Scraped data from {channel}")
                    await asyncio.sleep(5)  
                    break 
                except FloodWaitError as e:
                    print(f"Flood wait of {e.seconds} seconds required. Waiting...")
                    await asyncio.sleep(e.seconds)  
                except Exception as e:
                    print(f"Error: {e}")
                    break  


with client:
    client.loop.run_until_complete(main())
