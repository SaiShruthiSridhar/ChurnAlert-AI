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
        
        conn.commit()

if __name__ == "__main__":
    migrate()
