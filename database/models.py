RESTS_TABLE = """
CREATE TABLE IF NOT EXISTS rests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    username TEXT,
    first_name TEXT,

    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,

    is_active INTEGER NOT NULL DEFAULT 1,
    reminded_for_end_date TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

RESTS_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS
idx_one_active_rest_per_user
ON rests(user_id)
WHERE is_active = 1;
"""

BOT_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS bot_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

APPEALS_TABLE = """
CREATE TABLE IF NOT EXISTS appeals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    admin_message_id INTEGER NOT NULL,
    admin_chat_id INTEGER NOT NULL,

    category TEXT NOT NULL,
    delivery_status TEXT NOT NULL DEFAULT 'received',

    created_at TEXT NOT NULL,

    UNIQUE(admin_chat_id, admin_message_id)
);
"""

APPEALS_USER_INDEX = """
CREATE INDEX IF NOT EXISTS idx_appeals_user
ON appeals(user_id);
"""
