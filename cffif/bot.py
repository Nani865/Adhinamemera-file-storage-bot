import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# Dictionary to store file_name: file_id mapping
file_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "Hi! I'm a file storage bot. Send me any file and I'll store it. "
        "To retrieve a file, just send me its name!\n\n"
        "Type /help to see all available commands."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    # Get the file information
    if update.message.document:
        file = update.message.document
        file_name = file.file_name
        if file_name is None:
            return
        # Clean up the filename by removing other channel names
        cleaned_name = file_name.replace("@ph_files", "").replace(" - -", "").strip()
        file_name = f"@adhi_na_meme_ra_{cleaned_name}"
        file_id = file.file_id
    elif update.message.photo:
        file = update.message.photo[-1]  # Get the highest quality photo
        file_name = f"@adhi_na_meme_ra_photo_{update.message.date.strftime('%Y%m%d_%H%M%S')}.jpg"
        file_id = file.file_id
    elif update.message.video:
        file = update.message.video
        file_name = file.file_name
        if file_name is None:
            file_name = f"@adhi_na_meme_ra_video_{update.message.date.strftime('%Y%m%d_%H%M%S')}.mp4"
        else:
            file_name = f"@adhi_na_meme_ra_{file_name}"
        file_id = file.file_id
    else:
        return

    # Store the file_id with the filename as key
    file_storage[file_name.lower()] = file_id
    await update.message.reply_text(f"File '{file_name}' has been stored!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return
    
    search_term = update.message.text.lower()
    
    # Find all matching files
    matching_files = [(filename, file_id) for filename, file_id in file_storage.items() 
                     if search_term in filename.lower()]
    
    if matching_files:
        for filename, file_id in matching_files:
            display_name = filename.replace("@adhi_na_meme_ra_", "")
            try:
                await update.message.reply_document(
                    document=file_id,
                    caption=f"🎬 {display_name}\n\n📢 @adhi_na_meme_ra"
                )
            except Exception as e:
                print(f"Error sending file: {str(e)}")
                await update.message.reply_text(f"❌ Failed to send: {display_name}")
    else:
        await update.message.reply_text("🔍 No files found matching your search.")

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    if not context.args:
        await update.message.reply_text("❌ Please provide a filename to delete!")
        return
    
    file_name = " ".join(context.args).lower()
    if file_name in file_storage:
        del file_storage[file_name]
        await update.message.reply_text(f"✅ File '{file_name}' has been deleted!")
    else:
        await update.message.reply_text("❌ File not found!")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
        
    if not file_storage:
        await update.message.reply_text("No files stored yet!")
        return
    
    file_list = "\n".join([f"📁 {filename}" for filename in file_storage.keys()])
    await update.message.reply_text(f"Stored Files:\n\n{file_list}")

async def file_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
        
    count = len(file_storage)
    await update.message.reply_text(f"📊 Total files stored: {count}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
        
    help_text = """
🤖 Bot Commands:
/start - Start the bot
/list - List all stored files
/count - Show total number of files
/delete [filename] - Delete a specific file
/help - Show this help message

To search for files, simply send the filename or part of it!
"""
    await update.message.reply_text(help_text)

def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
    application = Application.builder().token('5807271780:AAHv9njEnrvOjSLmpP--9sLJznNT6wIM03k').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("count", file_count))
    application.add_handler(CommandHandler("delete", delete_file))
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Print startup message
    print("🤖 Bot is running...")
    print("Press Ctrl+C to stop the bot")
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()