import datetime

def get_thresholds():
    try:
        from database import SessionLocal
        from models import RuleThreshold
        session = SessionLocal()
        thresholds = session.query(RuleThreshold).all()
        session.close()
        return {t.rule_name: t.value for t in thresholds}
    except Exception:
        return {}

def calculate_risk(account):
    t = get_thresholds()

    NO_LOGIN_DAYS = t.get('no_login_days', 14)
    RENEWAL_WINDOW = t.get('renewal_window_days', 30)
    ADOPTION_CRITICAL = t.get('feature_adoption_critical', 20)
    ADOPTION_LOW = t.get('feature_adoption_low', 50)
    LOGIN_CRITICAL = t.get('login_frequency_critical', 3)
    LOGIN_LOW = t.get('login_frequency_low', 10)
    SESSION_MIN = t.get('session_duration_min', 5)
    NEGATIVE_TICKETS = t.get('negative_tickets_threshold', 3)
    HIGH_VALUE = t.get('high_value_contract', 10000)
    HIGH_SCORE = t.get('high_risk_score', 70)
    MEDIUM_SCORE = t.get('medium_risk_score', 35)
    TENURE_CRITICAL = t.get('tenure_critical', 3)
    TENURE_EARLY = t.get('tenure_early', 6)

    contract_score = 0
    usage_score = 0
    support_score = 0
    reasons = []

    # 1. Contract & Tenure (Max 25 pts)
    if account.get('contract_type') == "Month-to-month":
        contract_score += 15
        reasons.append("High-risk Month-to-month contract")

    tenure = account.get('tenure', 0)
    if tenure < TENURE_CRITICAL:
        contract_score += 10
        reasons.append(f"Critical early-stage tenure (< {int(TENURE_CRITICAL)}m)")
    elif tenure < TENURE_EARLY:
        contract_score += 5
        reasons.append(f"Early-stage tenure (< {int(TENURE_EARLY)}m)")

    renewal_date = account.get('renewal_date')
    last_login = account.get('last_login_date')
    if renewal_date and last_login:
        try:
            if isinstance(renewal_date, str):
                renewal_dt = datetime.datetime.strptime(renewal_date[:10], '%Y-%m-%d')
            else:
                renewal_dt = renewal_date
            if isinstance(last_login, str):
                login_dt = datetime.datetime.strptime(last_login[:10], '%Y-%m-%d')
            else:
                login_dt = last_login
            days_to_renewal = (renewal_dt - datetime.datetime.utcnow()).days
            days_since_login = (datetime.datetime.utcnow() - login_dt).days
            if days_since_login >= NO_LOGIN_DAYS and days_to_renewal <= RENEWAL_WINDOW:
                contract_score += 20
                reasons.append(f"No login in {days_since_login} days with renewal in {days_to_renewal} days — immediate HIGH risk")
            elif days_to_renewal <= RENEWAL_WINDOW:
                contract_score += 10
                reasons.append(f"Renewal approaching in {days_to_renewal} days")
        except Exception:
            pass

    # 2. Usage & Adoption (Max 40 pts)
    metrics = account.get('usage_metrics', [])
    if metrics:
        latest = metrics[0]
        adoption = latest.get('feature_adoption_pct', 100)
        if adoption < ADOPTION_CRITICAL:
            usage_score += 20
            reasons.append(f"Critically low feature adoption (< {int(ADOPTION_CRITICAL)}%)")
        elif adoption < ADOPTION_LOW:
            usage_score += 10
            reasons.append("Under-utilization of platform features")

        freq = latest.get('login_frequency', 30)
        if freq < LOGIN_CRITICAL:
            usage_score += 15
            reasons.append("Severe inactivity (low login frequency)")
        elif freq < LOGIN_LOW:
            usage_score += 5
            reasons.append("Declining engagement frequency")

        duration = latest.get('session_duration_avg', 30)
        if duration < SESSION_MIN:
            usage_score += 5
            reasons.append("Surface-level sessions (low duration)")
    else:
        usage_score += 30
        reasons.append("No usage data recorded")

    # 3. Support & Sentiment (Max 35 pts)
    tickets = account.get('support_tickets', [])
    negative_tickets = [t for t in tickets if t.get('sentiment') == "negative"]
    unresolved_tickets = [t for t in tickets if not t.get('is_resolved')]

    if negative_tickets:
        neg_count = len(negative_tickets)
        if neg_count > NEGATIVE_TICKETS:
            support_score += 25
            reasons.append(f"HIGH escalation — {neg_count} negative sentiment tickets (exceeds threshold of {int(NEGATIVE_TICKETS)})")
        else:
            support_score += min(20, neg_count * 10)
            reasons.append(f"Detected {neg_count} negative sentiment ticket(s)")

    if unresolved_tickets:
        unres_count = len(unresolved_tickets)
        support_score += min(10, unres_count * 5)
        reasons.append(f"{unres_count} unresolved support ticket(s) outstanding")

    total_score = contract_score + usage_score + support_score
    final_score = min(100, total_score)

    contract_value = account.get('contract_value', 0)
    try:
        contract_value = float(contract_value)
    except (ValueError, TypeError):
        contract_value = 0
    if contract_value > HIGH_VALUE and total_score > 0:
        final_score = min(100, final_score + 10)
        reasons.append(f"High-value account (${contract_value:,.0f}) — escalate to senior CSM")

    if final_score >= HIGH_SCORE:
        tier = "HIGH"
    elif final_score >= MEDIUM_SCORE:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    reasons = reasons[:5]
    return final_score, tier, reasons
