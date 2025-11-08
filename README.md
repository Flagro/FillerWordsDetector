# Filler Words Detector Bot

A Telegram bot that detects and tracks filler words in group chat messages. The bot monitors conversations, notifies users when filler words are detected, and provides detailed usage statistics over time.

## Features

- **Real-time Detection**: Monitors all messages and detects filler words instantly
- **Multiple Words Support**: Detects multiple filler words within a single message
- **Persistent Storage**: Uses SQLite database to track usage over time
- **Comprehensive Statistics**: View stats for today, last 30 days, or all-time
- **Per-User Tracking**: Statistics are tied to user ID and chat ID pairs
- **Access Control**: Optional whitelist for allowed users and administrators
- **Configurable Words**: Define your own list of filler words via environment variables

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file based on `.env-example`:
```bash
cp .env-example .env
```

3. Configure your `.env` file:
```
TELEGRAM_BOT_TOKEN=your_token_here
FILLER_WORDS=um,uh,like,you know,actually,basically,literally
ALLOWED_HANDLES=  # Optional: comma-separated list of allowed usernames
ADMIN_HANDLES=    # Optional: comma-separated list of admin usernames
DATABASE_PATH=filler_words.db  # Optional: path to SQLite database
```

4. Run the bot:
```bash
poetry run python main.py
```

## Commands

- `/start` - Start tracking filler words in the current chat (admin only if admins configured)
- `/stop` - Stop tracking filler words in the current chat (admin only if admins configured)
- `/stats` - View your filler words usage statistics

## Usage Examples

### 1. Starting the Bot

```
Admin: /start
Bot: 👋 Hello! I'm a Filler Words Detector Bot!
     I track filler words in your messages and provide statistics.
     [...]
```

### 2. Filler Words Detection

```
User: Um, I think we should, like, actually move forward with this.
Bot: 🔔 Filler word detected: *um*, *like*, *actually*
```

### 3. Viewing Statistics

```
User: /stats
Bot: 📊 Filler Words Statistics

     📅 Today's Stats:
     Total: 5
       • um: 2
       • like: 2
       • actually: 1

     📆 Last 30 Days:
     Total: 47
       • like: 15
       • um: 12
       • actually: 10
       • basically: 6
       • literally: 4

     🕐 All-Time Stats:
     Total: 203
       • like: 68
       • um: 52
       • actually: 35
       • basically: 28
       • literally: 20
```

## How It Works

### Detection Algorithm

The bot uses regex word boundary matching to detect filler words:

1. **Message Processing**: Each message is analyzed for configured filler words
2. **Word Boundary Matching**: Uses `\b` regex boundaries to match whole words only
3. **Multiple Detection**: Counts each occurrence, even if the same word appears multiple times
4. **Case-Insensitive**: Detects filler words regardless of capitalization

### Database Schema

The bot uses SQLite with the following schema:

```sql
CREATE TABLE filler_words_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Access Control

- **Allowed Users**: If `ALLOWED_HANDLES` is configured, only listed users' messages are monitored
- **Admin Control**: If `ADMIN_HANDLES` is configured, only admins can start/stop the bot
- **Open Access**: Leave both empty to allow all users

### Statistics Tracking

Statistics are tracked per (user_id, chat_id) pair:
- **Daily**: Stats from midnight today
- **Monthly**: Stats from last 30 days
- **All-Time**: Complete historical data

## Configuration

### Filler Words

Configure filler words as a comma-separated list in the `FILLER_WORDS` environment variable:

```
FILLER_WORDS=um,uh,like,you know,actually,basically,literally,sort of,kind of
```

**Common filler words to track:**
- Verbal pauses: um, uh, er, ah
- Hedge words: like, sort of, kind of, I mean
- Intensifiers: actually, basically, literally, seriously
- Discourse markers: you know, I guess, I think, so
- Filler phrases: at the end of the day, to be honest

### Access Control

**Allowed Users** (optional):
```
ALLOWED_HANDLES=@user1,user2,@user3
```

**Admin Users** (optional):
```
ADMIN_HANDLES=@admin1,admin2
```

Note: Handles can be specified with or without the `@` prefix.

## Docker Support

A Dockerfile is included for containerized deployment:

```bash
docker build -t filler-words-bot .
docker run -d --env-file .env filler-words-bot
```

## Technical Details

- **Language**: Python 3.10+
- **Framework**: python-telegram-bot 20.1
- **Database**: SQLite3
- **Configuration**: python-decouple

## License

See LICENSE file for details.
