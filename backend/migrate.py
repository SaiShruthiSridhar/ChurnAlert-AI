from sqlalchemy import create_engine, text
import os

DB_PATH = os.path.join(os.getcwd(), "churn_ai.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN intervention_date DATETIME;"))
            print("Added intervention_date")
        except Exception as e:
            print(f"Error adding intervention_date: {e}")
            
        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN outcome_date DATETIME;"))
            print("Added outcome_date")
        except Exception as e:
            print(f"Error adding outcome_date: {e}")
            
        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN was_successful BOOLEAN;"))
            print("Added was_successful")
        except Exception as e:
            print(f"Error adding was_successful: {e}")

        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN flagged_for_admin BOOLEAN DEFAULT 0;"))
            print("Added flagged_for_admin")
        except Exception as e:
            print(f"Error adding flagged_for_admin: {e}")

        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN flag_reason TEXT;"))
            print("Added flag_reason")
        except Exception as e:
            print(f"Error adding flag_reason: {e}")

        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hubspot_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    updated_at DATETIME
                );
            """))
            print("Created hubspot_tokens table (if not exists)")
        except Exception as e:
            print(f"Error creating hubspot_tokens: {e}")

        conn.commit()

if __name__ == "__main__":
    migrate()
