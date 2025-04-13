import logging, re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from db import add_reminder_to_db, delete_reminder_from_db, delete_all_reminders_for_user, get_reminders_by_user
from utils import get_month_number

# Global variable to store active job queue entries
pending_jobs = {}  # key: user_id, value: list of jobs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🔔 *Reminder Bot* 🔔\n\n"
        "Welcome! This bot helps you set reminders for your important tasks.\n\n"
        "⏰ Reminders will be sent: 5d, 3d, 1d, 12h, 6h, 3h, 1h, 30m, exactly at deadline."
    )
    keyboard = [
        [InlineKeyboardButton("➕ Add Reminder", callback_data="add_reminder")],
        [InlineKeyboardButton("📋 View Reminders", callback_data="list_reminder")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def set_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tokens = update.message.text.split()
        if len(tokens) < 5:
            raise ValueError("Incorrect format")
        desc = " ".join(tokens[1:-3])
        day_str = tokens[-3]
        month_text = tokens[-2]
        time_token = tokens[-1]
        day = int(day_str)
        month = get_month_number(month_text)
        if not re.match(r'^\d{1,2}:\d{2}$', time_token):
            raise ValueError("Time must be in HH:MM format")
        hour, minute = map(int, time_token.split(':'))
        current_year = datetime.now().year
        deadline = datetime(current_year, month, day, hour, minute)
        if deadline < datetime.now():
            deadline = datetime(current_year + 1, month, day, hour, minute)
        user_id = update.effective_user.id

        job_list = []
        reminder_message = ""
        if context.job_queue is not None:
            reminder_intervals = [
                {"days": 1, "label": "1 day"},
                {"hours": 5, "label": "5 hours"},
                {"hours": 3, "label": "3 hours"},
                {"hours": 1, "label": "1 hour"},
                {"minutes": 30, "label": "30 minutes"},
                {"minutes": 15, "label": "15 minutes"}
            ]
            active_reminders = []
            for interval in reminder_intervals:
                kwargs = {}
                reminder_label = ""
                if "days" in interval:
                    kwargs["days"] = interval["days"]
                    reminder_label = interval["label"]
                elif "hours" in interval:
                    kwargs["hours"] = interval["hours"]
                    reminder_label = interval["label"]
                elif "minutes" in interval:
                    kwargs["minutes"] = interval["minutes"]
                    reminder_label = interval["label"]
                delta = timedelta(**kwargs)
                reminder_time = deadline - delta
                if reminder_time > datetime.now():
                    delay = (reminder_time - datetime.now()).total_seconds()
                    j = context.job_queue.run_once(
                        send_reminder,
                        when=delay,
                        chat_id=update.effective_chat.id,
                        name=f"{user_id}-{desc}-{reminder_time}",
                        data={
                            "desc": desc,
                            "deadline": deadline.strftime("%d-%B %H:%M"),
                            "interval": reminder_label,
                            "deadline_dt": deadline.timestamp()
                        }
                    )
                    job_list.append(j)
                    active_reminders.append(reminder_label)
            if active_reminders:
                reminder_message = f" Reminders will be sent {', '.join(active_reminders)} before the deadline."
            else:
                reminder_message = " (Deadline is too close for reminders)"
        else:
            reminder_message = " (Reminders are not active)"
        reminder_id = add_reminder_to_db(user_id, desc, deadline.strftime("%d-%B %H:%M"))
        if user_id in pending_jobs:
            pending_jobs[user_id].extend(job_list)
        else:
            pending_jobs[user_id] = job_list

        keyboard = [
            [InlineKeyboardButton("Add Reminder", callback_data="add_reminder")],
            [InlineKeyboardButton("List Reminder", callback_data="list_reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        short_message = "✅ Reminder Saved!"
        await update.message.reply_text(short_message, parse_mode='Markdown')
    except ValueError as e:
        await update.message.reply_text(
            f"Error: {str(e)}\nFormat: <description> DD Month HH:MM\nExample: Statistics 12 March 17:00"
        )
    except Exception as e:
        logging.error(f"Error in set_task: {e}")
        await update.message.reply_text("Something went wrong. Please verify your input format: <description> DD Month HH:MM")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    if isinstance(data, dict):
        desc = data["desc"]
        deadline = data["deadline"]
        indicator = "Deadline reached" if data["interval"] == "Deadline" else f"{data['interval']} before the deadline"
        message = (
            f"🔔 *REMINDER!*\n\n"
            f"📝 *{desc}*\n"
            f"⏰ Deadline: {deadline}\n"
            f"⚠️ {indicator}"
        )
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=message,
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"🔔 Reminder: {data}"
        )

async def selesai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in pending_jobs:
        for job in pending_jobs[user_id]:
            job.schedule_removal()
        del pending_jobs[user_id]
    delete_all_reminders_for_user(user_id)
    keyboard = [
        [InlineKeyboardButton("➕ Add New Reminder", callback_data="add_reminder")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ All reminders have been completed!", reply_markup=reply_markup)

async def add_tugas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🔸 *Reminder Input Format*\n\n"
        "Format: DD Month HH:MM\n"
        "Example: 15 April 14:30\n\n"
        "Month can be written in full or abbreviated."
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def lihat_tugas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reminders = get_reminders_by_user(user_id)
    msg = update.effective_message
    if reminders:
        await msg.reply_text("📋 *Your Reminders List*", parse_mode='Markdown')
        for (reminder_id, desc, deadline) in reminders:
            keyboard = [
                [InlineKeyboardButton("✅ Done", callback_data=f"done_{reminder_id}")],
                [InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{reminder_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            reminder_message = f"🔹 *{desc}*\n📅 Deadline: {deadline}"
            await msg.reply_text(reminder_message, reply_markup=reply_markup, parse_mode='Markdown')
        keyboard = [
            [InlineKeyboardButton("➕ Add Reminder", callback_data="add_reminder")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await msg.reply_text("What would you like to do next?", reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("➕ Add Reminder", callback_data="add_reminder")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await msg.reply_text("📭 *No Reminders Found*\n\nYou don't have any saved reminders yet.", reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_reminder":
        user_id = query.from_user.id
        context.user_data['state'] = {'state': 'waiting_for_desc'}
        cancel_message = (
            "📝 Please enter the reminder description.\n\n"
            "Example: Finish math homework\n\n"
            "Type /cancel to abort."
        )
        await query.message.reply_text(cancel_message, parse_mode='Markdown')
    elif query.data == "home":
        help_text = "🔔 *Reminder Bot* 🔔\n\nWhat would you like to do?"
        keyboard = [
            [InlineKeyboardButton("➕ Add Reminder", callback_data="add_reminder")],
            [InlineKeyboardButton("📋 View Reminders", callback_data="list_reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif query.data == "list_reminder":
        await lihat_tugas(update, context)
    elif query.data.startswith("done_"):
        reminder_id = int(query.data.split("_")[1])
        delete_reminder_from_db(reminder_id)
        await query.edit_message_text(
            f"✅ *DONE*\n\n{query.message.text}",
            parse_mode='Markdown'
        )
    elif query.data.startswith("delete_"):
        reminder_id = int(query.data.split("_")[1])
        delete_reminder_from_db(reminder_id)
        await query.edit_message_text(
            f"🗑️ *DELETED*\n\nReminder deleted.",
            parse_mode='Markdown'
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if 'state' not in context.user_data:
        return
    state = context.user_data['state']
    if state['state'] == 'waiting_for_desc':
        state['desc'] = update.message.text
        state['state'] = 'waiting_for_deadline'
        deadline_message = ("📅 *Enter the Deadline*\n\nFormat: DD Month HH:MM\nExample: 15 April 14:30\n\nType /cancel to abort.")
        await update.message.reply_text(deadline_message, parse_mode='Markdown')
    elif state['state'] == 'waiting_for_deadline':
        try:
            deadline_text = update.message.text
            parts = deadline_text.split()
            if len(parts) != 3:
                raise ValueError("Incorrect deadline format. Use: DD Month HH:MM")
            day_str, month_text, time_token = parts
            day = int(day_str)
            month = get_month_number(month_text)
            if not re.match(r'^\d{1,2}:\d{2}$', time_token):
                raise ValueError("Time must be in HH:MM format")
            hour, minute = map(int, time_token.split(':'))
            current_year = datetime.now().year
            deadline = datetime(current_year, month, day, hour, minute)
            if deadline < datetime.now():
                deadline = datetime(current_year + 1, month, day, hour, minute)
            desc = state['desc']
            job_list = []
            reminder_message = ""
            if context.job_queue is not None:
                reminder_intervals = [
                    {"days": 5, "label": "5 days"},
                    {"days": 3, "label": "3 days"},
                    {"days": 1, "label": "1 day"},
                    {"hours": 12, "label": "12 hours"},
                    {"hours": 6, "label": "6 hours"},
                    {"hours": 3, "label": "3 hours"},
                    {"hours": 1, "label": "1 hour"},
                    {"minutes": 30, "label": "30 minutes"},
                    {"minutes": 0, "label": "Deadline"}
                ]
                active_reminders = []
                for interval in reminder_intervals:
                    kwargs = {}
                    reminder_label = ""
                    if "days" in interval:
                        kwargs["days"] = interval["days"]
                        reminder_label = interval["label"]
                    elif "hours" in interval:
                        kwargs["hours"] = interval["hours"]
                        reminder_label = interval["label"]
                    elif "minutes" in interval:
                        kwargs["minutes"] = interval["minutes"]
                        reminder_label = interval["label"]
                    delta = timedelta(**kwargs)
                    reminder_time = deadline - delta
                    if reminder_time > datetime.now():
                        delay = (reminder_time - datetime.now()).total_seconds()
                        j = context.job_queue.run_once(
                            send_reminder,
                            when=delay,
                            chat_id=update.effective_chat.id,
                            name=f"{user_id}-{desc}-{reminder_time}",
                            data={
                                "desc": desc,
                                "deadline": deadline.strftime("%d-%B %H:%M"),
                                "interval": reminder_label,
                                "deadline_dt": deadline.timestamp()
                            }
                        )
                        job_list.append(j)
                        active_reminders.append(reminder_label)
                if active_reminders:
                    formatted_intervals = []
                    for r in active_reminders:
                        if r == "Deadline":
                            formatted_intervals.append("Exactly at the deadline")
                        else:
                            formatted_intervals.append(f"{r} before the deadline")
                    reminder_message = "⏰ Reminders will be sent:\n• " + "\n• ".join(formatted_intervals)
                else:
                    reminder_message = "⚠️ Deadline is too close for reminders"
            else:
                reminder_message = " (Reminders are not active: job-queue feature unavailable)"
            
            reminder_id = add_reminder_to_db(user_id, desc, deadline.strftime("%d-%B %H:%M"))
            if user_id in pending_jobs:
                pending_jobs[user_id].extend(job_list)
            else:
                pending_jobs[user_id] = job_list

            keyboard = [
                [InlineKeyboardButton("➕ Add Another Reminder", callback_data="add_reminder")],
                [InlineKeyboardButton("📋 View All Reminders", callback_data="list_reminder")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            short_message = "✅ Reminder Saved!"
            await update.message.reply_text(short_message, reply_markup=reply_markup, parse_mode='Markdown')
            del context.user_data['state']
        except ValueError as e:
            error_message = (
                f"❌ *Error:* {str(e)}\n\n"
                f"Use format: DD Month HH:MM\nExample: 1 April 17:00\n\nType /cancel to abort."
            )
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error in text_handler: {e}")
            await update.message.reply_text("Something went wrong. Try again with format DD Month HH:MM")
            del context.user_data['state']

async def help_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🔔 *Reminder Bot - Help* 🔔\n\n"
        "*List of Commands:*\n"
        "• /start - Start the bot\n"
        "• /help - Show this guide\n\n"
        "Use the buttons below for quick navigation:"
    )
    keyboard = [
        [InlineKeyboardButton("➕ Add Reminder", callback_data="add_reminder")],
        [InlineKeyboardButton("📋 View Reminders", callback_data="list_reminder")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' in context.user_data:
        del context.user_data['state']
    await update.message.reply_text("❌ Operation cancelled.", parse_mode='Markdown')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in pending_jobs:
        for job in pending_jobs[user_id]:
            job.schedule_removal()
        del pending_jobs[user_id]
    delete_all_reminders_for_user(user_id)
    await update.message.reply_text("❌ All your data has been removed from this bot.", parse_mode='Markdown')

async def setup_loaded_reminders(application):
    import sqlite3
    from db import DB_PATH
    from utils import get_month_number
    from datetime import datetime, timedelta
    import logging
    if not application.job_queue:
        logging.warning("Job queue unavailable, skipping reminder setup")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, description, deadline, id FROM reminders")
    rows = c.fetchall()
    conn.close()
    for user_id, desc, deadline_str, reminder_id in rows:
        try:
            day_part, month_time = deadline_str.split('-', 1)
            month_name, time_str = month_time.split(' ', 1)
            month = get_month_number(month_name)
            day = int(day_part)
            hour, minute = map(int, time_str.split(':'))
            current_year = datetime.now().year
            deadline = datetime(current_year, month, day, hour, minute)
            if deadline < datetime.now():
                deadline = datetime(current_year + 1, month, day, hour, minute)
            if deadline > datetime.now():
                reminder_intervals = [
                    {"days": 3, "label": "3 days"},
                    {"days": 1, "label": "1 day"},
                    {"hours": 12, "label": "12 hours"},
                    {"hours": 5, "label": "5 hours"},
                    {"hours": 3, "label": "3 hours"},
                    {"hours": 1, "label": "1 hour"},
                    {"minutes": 30, "label": "30 minutes"}
                ]
                for interval in reminder_intervals:
                    kwargs = {}
                    reminder_label = ""
                    if "days" in interval:
                        kwargs["days"] = interval["days"]
                        reminder_label = interval["label"]
                    elif "hours" in interval:
                        kwargs["hours"] = interval["hours"]
                        reminder_label = interval["label"]
                    elif "minutes" in interval:
                        kwargs["minutes"] = interval["minutes"]
                        reminder_label = interval["label"]
                    delta = timedelta(**kwargs)
                    reminder_time = deadline - delta
                    if reminder_time > datetime.now():
                        delay = (reminder_time - datetime.now()).total_seconds()
                        j = application.job_queue.run_once(
                            send_reminder,
                            when=delay,
                            chat_id=user_id,
                            name=f"{user_id}-{desc}-{reminder_time}",
                            data={
                                "desc": desc,
                                "deadline": deadline.strftime("%d-%B %H:%M"),
                                "interval": reminder_label
                            }
                        )
                        global pending_jobs
                        if user_id in pending_jobs:
                            pending_jobs[user_id].append(j)
                        else:
                            pending_jobs[user_id] = [j]
        except Exception as e:
            logging.error(f"Error setting up reminder from DB: {e}")
