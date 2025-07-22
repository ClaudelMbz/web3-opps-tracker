import os
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
import logging
import httpx

# --- Configuration ---
# Enable logging to see potential errors
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
# Read the comma-separated list of channels
channels_raw = os.getenv('TELEGRAM_CHANNELS')
bot_token = os.getenv('BOT_TOKEN')
my_chat_id = os.getenv('MY_CHAT_ID')

# Name for the session file, which stores your authorization
session_name = 'telegram_user_session'

# --- Validation ---
if not all([api_id, api_hash, channels_raw, bot_token, my_chat_id]):
    raise ValueError("One or more required environment variables are missing from .env file.")

# Process the channel list string into a clean list
channel_list = [channel.strip() for channel in channels_raw.split(',')]

# Initialize the client
client = TelegramClient(session_name, int(api_id), api_hash)

# --- Bot Sender Function ---
async def send_message_via_bot(message_text, source_channel):
    """
    Sends a message to your personal chat via the bot using httpx.
    Includes the source of the message.
    """
    # Add the source channel to the message
    full_message = f"📢 **Source:** {source_channel}\n\n{message_text}"
    
    bot_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': my_chat_id,
        'text': full_message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True # Optional: to keep messages cleaner
    }
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(bot_api_url, json=payload)
            response.raise_for_status() # Raises an exception for 4xx or 5xx status codes
            logging.info(f"Message from {source_channel} successfully forwarded to chat ID {my_chat_id}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to send message via bot. Status: {e.response.status_code}, Response: {e.response.text}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending message via bot: {e}")


# This handler is now defined without a decorator.
# It will be attached dynamically in the main() function.
async def new_message_handler(event):
    """
    This function is triggered whenever a new message is posted
    in any of the specified channels. It filters the message and forwards it
    if it matches the criteria.
    """
    message_text = event.message.text
    
    # Get the username of the channel where the message was posted
    source_channel = f"@{event.chat.username}" if event.chat.username else event.chat.title

    if not message_text:
        logging.info(f"Received an empty message or media from {source_channel}, ignoring.")
        return

    print("------ New Message Received ------")
    logging.info(f"Checking message ID {event.message.id} from {source_channel}...")

    # --- Filtering Logic ---
    if 'binance' in message_text.lower() or message_text.startswith('https://www.binance.com/'):
        logging.info("Message matched filter. Forwarding...")
        print(f"Content:\n{message_text}")
        print("----------------------------------\n")
        await send_message_via_bot(message_text, source_channel)
    else:
        logging.info("Message did not match filter. Ignoring.")
        print("----------------------------------\n")

# --- Main Execution ---
async def main():
    """
    Main function to connect the client, validate channels, and run it.
    """
    print("Starting Telegram User Client...")
    
    # Connect the client first
    await client.start()
    print("Client connected successfully!")

    # --- Channel Validation ---
    valid_channels = []
    print("\nResolving channels from .env file...")
    for channel in channel_list:
        try:
            # get_input_entity will check if the channel exists and is accessible
            await client.get_input_entity(channel)
            valid_channels.append(channel)
            logging.info(f"  ✅ Successfully resolved: {channel}")
        except (ValueError, TypeError):
            # ValueError for bad usernames, TypeError for other invalid inputs
            logging.warning(f"  ❌ WARNING: Could not find channel '{channel}'. It will be ignored.")
    
    if not valid_channels:
        logging.error("Fatal: No valid channels found to monitor. Exiting.")
        return

    # Add the event handler dynamically with only the list of valid channels
    client.add_event_handler(new_message_handler, events.NewMessage(chats=valid_channels))

    print(f"\n🚀 Listening for new messages on: {', '.join(valid_channels)}")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Client stopped.")
