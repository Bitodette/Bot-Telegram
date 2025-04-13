import logging, sys, subprocess
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from db import init_db
from handlers import (start, set_task, selesai, add_tugas as original_add_tugas, lihat_tugas,
                      help_commands, cancel, button_callback, text_handler, setup_loaded_reminders)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Check & install job-queue
try:
    from telegram.ext import JobQueue
    job_queue_available = True
except ImportError:
    job_queue_available = False
    logging.warning("JobQueue is not available. Reminders will not be sent.")
    try:
        logging.info("Attempting to install python-telegram-bot[job-queue]...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot[job-queue]"])
        logging.info("Installation successful. Please restart the bot.")
        print("Job-queue dependency installed. Restart bot to enable reminders.")
    except Exception as e:
        logging.error(f"Failed to install dependency: {e}")
        print("Reminder feature needs job-queue; install with: pip install 'python-telegram-bot[job-queue]' and restart.")

# Override add_tugas handler to send short confirmation message
def add_tugas(update, context):
    result = original_add_tugas(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Reminder Saved!")
    return result

def main():
    token = "8127018084:AAE-kLjh0S2_wJJ6tTeArIkzsTD4WTK2JSg"  # Replace with your bot token
    init_db()
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setreminder", set_task))
    app.add_handler(CommandHandler("selesai", selesai))
    app.add_handler(CommandHandler("addreminder", add_tugas))
    app.add_handler(CommandHandler("lihatreminder", lihat_tugas))
    app.add_handler(CommandHandler("custom", help_commands))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("help", help_commands))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CommandHandler("stop", cancel))  # or your stop handler as imported, if applicable
    app.job_queue.run_once(lambda context: setup_loaded_reminders(app), when=1)
    app.run_polling()

if __name__ == "__main__":
    main()