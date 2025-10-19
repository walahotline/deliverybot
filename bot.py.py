import os
import logging
from flask import Flask, request, jsonify
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler
from telegram import Bot, Update

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EDIT THESE VALUES
BOT_TOKEN = os.environ.get('7407256981:AAEFnoMfwBK0kXtxKOkEIAnaAC4MSpSzusA') # Replace with your bot token from BotFather

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Video database - EDIT THIS WITH YOUR ACTUAL VIDEO FILE IDs
video_database = {
    'video1': {
        'file_id': 'AAMCBQADGQECX_ZYaPSPsFAvoSYidw25g6JovpgWiYwAAm4gAAJVSaBXv82JX7OcjbcBAAdtAAM2BA',  # EDIT THIS
        'title': 'Amazing Video 1',
        'description': 'This is the first amazing video'
    },
    'video2': {
        'file_id': 'YOUR_VIDEO_2_FILE_ID_HERE',  # EDIT THIS
        'title': 'Awesome Video 2',
        'description': 'This is the second awesome video'
    },
    'video3': {
        'file_id': 'YOUR_VIDEO_3_FILE_ID_HERE',  # EDIT THIS
        'title': 'Incredible Video 3', 
        'description': 'This is the third incredible video'
    }
    # ADD MORE VIDEOS AS NEEDED
}

def start(update: Update, context):
    """Handle /start command with video parameters"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    args = context.args
    
    logger.info(f"User {user_id} ({user_name}) started with args: {args}")
    
    if args and args[0] in video_database:
        # User came from website with specific video request
        video_id = args[0]
        video_data = video_database[video_id]
        
        update.message.reply_text(f"🎬 Sending your video: {video_data['title']}...")
        send_specific_video(update, context, video_data)
        
    else:
        # No specific video requested or invalid video ID
        update.message.reply_text(
            "Welcome! 👋\n\n"
            "This bot delivers videos from our website. "
            "Visit our website through the links in our Telegram channel to receive your videos!"
        )

def send_specific_video(update: Update, context, video_data):
    """Send specific video based on video data"""
    user_id = update.effective_user.id
    
    try:
        bot.send_video(
            chat_id=user_id,
            video=video_data['file_id'],
            caption=f"🎥 {video_data['title']}\n\n{video_data['description']}\n\nEnjoy! 😊"
        )
        logger.info(f"Video sent successfully to user {user_id}: {video_data['title']}")
        
    except Exception as e:
        logger.error(f"Error sending video to user {user_id}: {e}")
        update.message.reply_text("Sorry, there was an error sending the video. Please try again.")

def handle_message(update: Update, context):
    """Handle regular messages"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"Message from user {user_id}: {message_text}")
    
    update.message.reply_text(
        "📹 I automatically send videos to users who come from our website.\n\n"
        "Visit our website through the links in our Telegram channel to receive your content!\n\n"
        "If you're having issues, make sure you:\n"
        "1. Click the link in our channel\n"
        "2. Wait 5 seconds on the website\n" 
        "3. Click the 'Get Your Video' button\n"
        "4. Come back here to receive your video automatically!"
    )

# Set up dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive updates from Telegram"""
    try:
        update = Update.de_json(request.get_json(), bot)
        dispatcher.process_update(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 400

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook for Telegram bot"""
    # EDIT THIS with your actual hosting URL
    webhook_url = "YOUR_RAILWAY_OR_RENDER_URL_HERE/webhook"
    
    try:
        success = bot.set_webhook(webhook_url)
        logger.info(f"Webhook set: {success} for URL: {webhook_url}")
        return jsonify({"success": success, "url": webhook_url})
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/')
def index():
    return "Bot is running and ready to serve videos! 🎬"

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to check if bot is working"""
    return jsonify({
        "status": "active",
        "videos_available": list(video_database.keys()),
        "video_count": len(video_database)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)