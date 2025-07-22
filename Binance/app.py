import os
import asyncio
import json
import re
from telethon import TelegramClient
from dotenv import load_dotenv
import logging
import httpx
from flask import Flask, request

# --- Windows Specific asyncio policy ---
# This is required to run asyncio inside a thread on Windows, which Flask's dev server does.
# It has no effect on Linux (like on Render).
if os.name == 'nt': # 'nt' stands for Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Configuration ---
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channels_raw = os.getenv('TELEGRAM_CHANNELS')
bot_token = os.getenv('BOT_TOKEN')
my_chat_id = os.getenv('MY_CHAT_ID')
session_name = 'telegram_user_session'
STATE_FILE = 'telegram_monitor_state.json'

# --- Validation ---
if not all([api_id, api_hash, channels_raw, bot_token, my_chat_id]):
    raise ValueError("One or more required environment variables are missing.")

channel_list = [channel.strip() for channel in channels_raw.split(',')]

# --- State Management ---
def load_state():
    """Loads the last processed message IDs from a file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Saves the last processed message IDs to a file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def escape_markdown(text: str) -> str:
    """
    Escapes special characters for Telegram's legacy Markdown mode.
    This prevents errors when a message contains characters like '*' or '_'
    that are not part of a valid Markdown syntax.
    """
    # Characters to escape for Markdown (legacy) are: _, *, `, [
    # We use a regex to find and escape them by adding a backslash before them.
    return re.sub(r'([_*`\[])', r'\\\1', text)


# --- Bot Sender Function ---
async def send_message_via_bot(message_text, source_channel):
    """Sends a message to your personal chat via the bot using httpx."""
    
    # Escape the incoming message text to prevent Telegram API errors
    escaped_message_text = escape_markdown(message_text)
    
    full_message = f"📢 **Source:** {source_channel}\n\n{escaped_message_text}"
    bot_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': my_chat_id,
        'text': full_message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(bot_api_url, json=payload)
            response.raise_for_status()
            logging.info(f"Message from {source_channel} successfully forwarded.")
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to send message via bot. Status: {e.response.status_code}, Response: {e.response.text}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending message via bot: {e}")

# --- Core Logic ---
async def check_new_messages():
    """
    Connects to Telegram, checks for new messages, and forwards them.
    On the first run for a channel, it sets a baseline to the newest message
    without processing it. On subsequent runs, it only processes messages
    newer than the baseline.
    """
    logging.info("Starting check for new messages...")
    state = load_state()
    
    client = TelegramClient(session_name, int(api_id), api_hash)

    async with client:
        for channel in channel_list:
            # Use .get() to return None if the channel is not in the state yet
            last_id = state.get(channel)

            try:
                # If it's the first time we check this channel, we set a baseline.
                if last_id is None:
                    logging.info(f"First time checking '{channel}'. Setting baseline to the latest message.")
                    # Get the single most recent message from the channel
                    last_message = await client.get_messages(channel, limit=1)
                    if last_message:
                        # Save its ID as the starting point. We don't process it.
                        state[channel] = last_message[0].id
                        logging.info(f"Baseline for '{channel}' set to message ID: {state[channel]}.")
                    else:
                        # If the channel is empty, we start from the beginning.
                        state[channel] = 0
                        logging.info(f"Channel '{channel}' appears to be empty. Setting baseline to 0.")
                    # Skip to the next channel in the list for this run
                    continue

                # If we already have a baseline, process messages since that ID.
                newest_id = last_id
                logging.info(f"Checking channel: {channel} for messages since ID {last_id}")
                
                # Get messages newer than the last recorded ID.
                messages = await client.get_messages(channel, min_id=last_id, limit=100)
                
                # Messages are returned newest first, so we reverse to process oldest to newest.
                for message in reversed(messages):
                    if message and message.text:
                        source_channel_info = f"@{message.chat.username}" if message.chat.username else message.chat.title
                        
                        # --- Filtering Logic ---
                        if 'binance' in message.text.lower() or message.text.startswith('https://www.binance.com/'):
                            logging.info(f"Message {message.id} from {source_channel_info} matched filter. Forwarding...")
                            await send_message_via_bot(message.text, source_channel_info)
                    
                    # Keep track of the newest message ID we've seen in this batch.
                    if message.id > newest_id:
                        newest_id = message.id

                # If we processed new messages, update the state with the newest ID.
                if newest_id > last_id:
                    state[channel] = newest_id

            except Exception as e:
                logging.error(f"Error processing channel {channel}: {e}")

    save_state(state)
    logging.info("Check finished.")

# --- Flask Web Service ---
app = Flask(__name__)

@app.route('/')
def health_check():
    """A simple endpoint to confirm the service is up."""
    return "Telegram Monitor is alive.", 200

@app.route('/run-check', methods=['POST', 'GET'])
def run_check():
    """The main endpoint that a cron job will call."""
    # Note: Using a secret in the request to prevent unauthorized calls is recommended
    # For example: if request.headers.get('X-Cron-Secret') != os.getenv('CRON_SECRET'):
    #                  return "Unauthorized", 401
    
    logging.info("'/run-check' endpoint triggered.")
    try:
        # This is a robust way to run an async function from a sync context,
        # especially in a threaded environment like Flask's dev server.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(check_new_messages())
        return "Check completed successfully.", 200
    except Exception as e:
        logging.error(f"An error occurred during the check: {e}")
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    # This part is for local testing, Render will use gunicorn
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
