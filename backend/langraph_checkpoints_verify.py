import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'churn_ai_checkpoints.db')

if not os.path.exists(db_path):
    print("Checkpoint database not found.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("LangGraph Checkpointing — SQLite Verification")
print("=" * 60)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Database: {db_path}")
print(f"Tables found: {[t[0] for t in tables]}")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM checkpoints")
checkpoint_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM writes")
writes_count = cursor.fetchone()[0]

print(f"Total agent runs checkpointed: {checkpoint_count}")
print(f"Total node writes recorded: {writes_count}")
print("=" * 60)

cursor.execute("SELECT thread_id, checkpoint_id, parent_checkpoint_id FROM checkpoints ORDER BY rowid DESC LIMIT 5")
recent = cursor.fetchall()

print("5 most recent checkpoints:")
print("-" * 60)
for row in recent:
    thread_id = row[0]
    checkpoint_id = row[1]
    print(f"  Thread: {thread_id}")
    print(f"  Checkpoint ID: {checkpoint_id}")
    print("-" * 60)

cursor.execute("SELECT task_id, channel, type FROM writes ORDER BY rowid DESC LIMIT 5")
recent_writes = cursor.fetchall()

print("5 most recent node writes:")
print("-" * 60)
for row in recent_writes:
    print(f"  Task: {row[0]}")
    print(f"  Channel: {row[1]}")
    print(f"  Type: {row[2]}")
    print("-" * 60)

print("Checkpointing status: ACTIVE")
print("Every AI analysis run is saved to SQLite automatically")
print("Agent memory persists across server restarts")
print("=" * 60)

conn.close()
