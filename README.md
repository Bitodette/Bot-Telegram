# Telegram Reminder Bot

This Telegram bot helps users set and manage reminders for important tasks. Reminders are automatically scheduled at various intervals before the deadline, ensuring that you never miss an important event.

## Features

- **Automatic Reminders:**  
  Notifications are sent at predefined intervals (e.g., 5 days, 3 days, 1 day, 12 hours, etc.) before the deadline.
- **Reminder Management:**  
  Users can add, view, complete, or delete reminders easily.
- **Interactive UI:**  
  Inline keyboards are used for quick navigation and interaction.
- **SQLite Database Integration:**  
  Reminders are stored in an SQLite database located in the `data` folder.
- **Additional SQLite Project:**  
  The `python-sqlite-project` folder contains supplementary examples or projects related to SQLite usage.

## Project Structure

- **bot.py**  
  Main file used to initialize the Telegram bot, check for dependencies (JobQueue), and register command handlers.
- **db.py**  
  Contains functions for initializing the SQLite database and performing CRUD operations on reminders. The database file (`reminders.db`) is created in the `data` folder.
- **handlers.py**  
  Implements all the command and message handlers to manage user interactions, reminder scheduling, and inline keyboard callbacks.
- **utils.py**  
  Provides auxiliary functions, such as converting month names to numbers.
- **python-sqlite-project**  
  Contains additional projects/examples related to SQLite for reference.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Bitodette/Bot-Telegram.git
   cd Bot-Telegram
   ```

2. **Set Up a Virtual Environment (Optional but Recommended):**

   ```bash
   python -m venv env
   env\Scripts\activate   # On Windows
   ```

3. **Install Dependencies:**

   The bot uses `python-telegram-bot` with the JobQueue feature. Install the necessary dependencies:

   ```bash
   pip install python-telegram-bot[job-queue]
   ```

4. **Configure Your Bot Token:**

   Open `bot.py` and replace `"YOUR_BOT_TOKEN"` with your actual Telegram bot token:

   ```python
   token = "YOUR_BOT_TOKEN"  # Replace with your bot token
   ```

5. **Run the Bot:**

   ```bash
   python bot.py
   ```

## Usage

- **Commands:**
  - `/start` - Start the bot and display a welcome message with available actions.
  - `/help` - Display help guidelines on how to use the bot.
  - `/cancel` - Cancel the current operation.

- **Reminder Input Format:**

  When adding a reminder, the expected format is:

  ```
  <description> DD Month HH:MM
  ```

  **Example:**

  ```
  Meeting 15 April 14:30
  ```

## Database

- The SQLite database file (`reminders.db`) is automatically created in the `data` folder upon first execution.
- Ensure that the `data` folder has the appropriate write permissions.

## Notes

- **JobQueue Dependency:**  
  The bot checks for the JobQueue module from `python-telegram-bot`. If it is not found, it will attempt to install the dependency automatically and prompt for a restart.
- **Security:**  
  Do not expose your bot token publicly. If you accidentally commit your token, rotate it immediately using BotFather and clean your repository history.

## License

Feel free to modify the repository license section as per your project requirements.
