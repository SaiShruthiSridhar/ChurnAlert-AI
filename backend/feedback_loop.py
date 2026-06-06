from database import SessionLocal
from models import Account, RuleWeight
import datetime

def run_feedback_loop():
    db = SessionLocal()
    
    # Analyze recent outcomes
    successful = db.query(Account).filter(Account.was_successful == True).count()
    failed = db.query(Account).filter(Account.was_successful == False).count()
    
    # Logic: If failure rate is high for certain categories, adjust weights
    # This is a simplified simulation
    weights = db.query(RuleWeight).all()
    for w in weights:
        if failed > successful:
            # Increase weight if we are missing churners
            w.weight *= 1.05
        else:
            # Decrease weight if we are over-predicting
            w.weight *= 0.95
        w.last_adjusted = datetime.datetime.utcnow()
    
    db.commit()
    print(f"Feedback loop processed: {successful} successes, {failed} failures. Weights updated.")
    db.close()

if __name__ == "__main__":
    run_feedback_loop()
