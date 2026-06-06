from database import SessionLocal, engine
from models import Base, RuleThreshold
import datetime

def seed_thresholds():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    
    defaults = [
        {
            'rule_name': 'no_login_days',
            'value': 14.0,
            'label': 'No Login Days',
            'description': 'Flag account as HIGH risk if no login for this many days combined with renewal within window',
            'unit': 'days',
            'min_value': 5,
            'max_value': 60
        },
        {
            'rule_name': 'renewal_window_days',
            'value': 30.0,
            'label': 'Renewal Window',
            'description': 'Flag accounts with renewal approaching within this many days',
            'unit': 'days',
            'min_value': 7,
            'max_value': 90
        },
        {
            'rule_name': 'feature_adoption_critical',
            'value': 20.0,
            'label': 'Critical Feature Adoption',
            'description': 'Feature adoption below this percentage triggers critical flag',
            'unit': '%',
            'min_value': 5,
            'max_value': 50
        },
        {
            'rule_name': 'feature_adoption_low',
            'value': 50.0,
            'label': 'Low Feature Adoption',
            'description': 'Feature adoption below this percentage triggers low utilization flag',
            'unit': '%',
            'min_value': 20,
            'max_value': 80
        },
        {
            'rule_name': 'login_frequency_critical',
            'value': 3.0,
            'label': 'Critical Login Frequency',
            'description': 'Login frequency below this number triggers severe inactivity flag',
            'unit': 'logins',
            'min_value': 1,
            'max_value': 10
        },
        {
            'rule_name': 'login_frequency_low',
            'value': 10.0,
            'label': 'Low Login Frequency',
            'description': 'Login frequency below this number triggers declining engagement flag',
            'unit': 'logins',
            'min_value': 5,
            'max_value': 30
        },
        {
            'rule_name': 'session_duration_min',
            'value': 5.0,
            'label': 'Minimum Session Duration',
            'description': 'Average session below this duration in minutes triggers surface engagement flag',
            'unit': 'minutes',
            'min_value': 1,
            'max_value': 30
        },
        {
            'rule_name': 'negative_tickets_threshold',
            'value': 3.0,
            'label': 'Negative Tickets Threshold',
            'description': 'More than this many negative sentiment tickets triggers HIGH escalation',
            'unit': 'tickets',
            'min_value': 1,
            'max_value': 10
        },
        {
            'rule_name': 'high_value_contract',
            'value': 10000.0,
            'label': 'High Value Contract',
            'description': 'Contract value above this amount routes to senior CSM automatically',
            'unit': '$',
            'min_value': 1000,
            'max_value': 100000
        },
        {
            'rule_name': 'high_risk_score',
            'value': 70.0,
            'label': 'HIGH Risk Score Cutoff',
            'description': 'Risk score at or above this value is classified as HIGH risk',
            'unit': 'points',
            'min_value': 50,
            'max_value': 90
        },
        {
            'rule_name': 'medium_risk_score',
            'value': 35.0,
            'label': 'MEDIUM Risk Score Cutoff',
            'description': 'Risk score at or above this value is classified as MEDIUM risk',
            'unit': 'points',
            'min_value': 20,
            'max_value': 60
        },
        {
            'rule_name': 'tenure_critical',
            'value': 3.0,
            'label': 'Critical Tenure',
            'description': 'Accounts with tenure below this many months are flagged as critical early-stage',
            'unit': 'months',
            'min_value': 1,
            'max_value': 12
        },
        {
            'rule_name': 'tenure_early',
            'value': 6.0,
            'label': 'Early Tenure',
            'description': 'Accounts with tenure below this many months are flagged as early-stage',
            'unit': 'months',
            'min_value': 3,
            'max_value': 24
        },
    ]

    for d in defaults:
        existing = session.query(RuleThreshold).filter_by(rule_name=d['rule_name']).first()
        if not existing:
            threshold = RuleThreshold(
                rule_name=d['rule_name'],
                value=d['value'],
                label=d['label'],
                description=d['description'],
                unit=d['unit'],
                min_value=d['min_value'],
                max_value=d['max_value'],
                last_updated=datetime.datetime.utcnow()
            )
            session.add(threshold)
    
    session.commit()
    session.close()
    print(f"[Thresholds] Seeded {len(defaults)} rule thresholds.")

if __name__ == "__main__":
    seed_thresholds()
