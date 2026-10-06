import pandas as pd
import os
from rules_engine import calculate_risk

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_accounts():
    df = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    # Merge with risk tier (simplified for list view)
    return df.to_dict(orient="records")

def get_account_details(account_id):
    df_accounts = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    df_metrics = pd.read_csv(os.path.join(DATA_DIR, "metrics.csv"))
    df_tickets = pd.read_csv(os.path.join(DATA_DIR, "tickets.csv"))
    
    account = df_accounts[df_accounts["id"] == account_id]
    if account.empty:
        return None
    
    acc_dict = account.iloc[0].to_dict()
    
    # Get metrics
    metrics = df_metrics[df_metrics["account_id"] == account_id].sort_values("timestamp", ascending=False).to_dict(orient="records")
    
    # Get tickets
    tickets = df_tickets[df_tickets["account_id"] == account_id].sort_values("created_at", ascending=False).to_dict(orient="records")
    
    acc_dict["usage_metrics"] = metrics
    acc_dict["support_tickets"] = tickets
    
    return acc_dict

def get_portfolio_insights():
    df_accounts = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    all_reasons = []
    
    for _, acc in df_accounts.iterrows():
        details = get_account_details(acc['id'])
        _, _, reasons = calculate_risk(details)
        all_reasons.extend(reasons)
    
    # Return top unique reasons
    from collections import Counter
    counts = Counter(all_reasons)
    return counts.most_common(5)

def add_account(account_data):
    """
    Appends a new account to accounts.csv and generates initial metrics/tickets.
    """
    accounts_path = os.path.join(DATA_DIR, "accounts.csv")
    metrics_path = os.path.join(DATA_DIR, "metrics.csv")
    tickets_path = os.path.join(DATA_DIR, "tickets.csv")

    # Load existing to check for ID collision
    df_accounts = pd.read_csv(accounts_path)
    if account_data['id'] in df_accounts['id'].values:
        return False, "Account ID already exists"

    # 1. Append to accounts.csv
    acc_cols = ["id","name","tenure","monthly_charges","contract_type","assigned_csm","status","last_login_date","renewal_date","contract_value"]
    new_acc = {
        "id": account_data['id'],
        "name": account_data['name'],
        "tenure": account_data['tenure'],
        "monthly_charges": account_data['monthly_charges'],
        "contract_type": account_data['contract_type'],
        "assigned_csm": account_data['assigned_csm'],
        "status": "Active",
        "last_login_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "renewal_date": (pd.Timestamp.now() + pd.DateOffset(months=12)).strftime("%Y-%m-%d"),
        "contract_value": account_data['contract_value']
    }
    pd.DataFrame([new_acc])[acc_cols].to_csv(accounts_path, mode='a', header=False, index=False)

    # 2. Append to metrics.csv
    met_cols = ["account_id","login_frequency","feature_adoption_pct","session_duration_avg","timestamp"]
    new_metric = {
        "account_id": account_data['id'],
        "login_frequency": 5,
        "feature_adoption_pct": 20.0,
        "session_duration_avg": 15,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d")
    }
    pd.DataFrame([new_metric])[met_cols].to_csv(metrics_path, mode='a', header=False, index=False)

    # 3. Append to tickets.csv
    tkt_cols = ["account_id","subject","sentiment","is_resolved","created_at"]
    new_ticket = {
        "account_id": account_data['id'],
        "subject": "Initial onboarding setup",
        "sentiment": "neutral",
        "is_resolved": "true",
        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d")
    }
    pd.DataFrame([new_ticket])[tkt_cols].to_csv(tickets_path, mode='a', header=False, index=False)

    return True, "Success"

def load_accounts():
    return get_accounts()

def load_metrics(account_id):
    df_metrics = pd.read_csv(os.path.join(DATA_DIR, "metrics.csv"))
    return df_metrics[df_metrics["account_id"] == account_id].sort_values("timestamp", ascending=False).to_dict(orient="records")

def load_tickets(account_id):
    df_tickets = pd.read_csv(os.path.join(DATA_DIR, "tickets.csv"))
    return df_tickets[df_tickets["account_id"] == account_id].sort_values("created_at", ascending=False).to_dict(orient="records")

if __name__ == "__main__":
    # Test
    accs = get_accounts()
    print(f"Loaded {len(accs)} accounts")
    if accs:
        details = get_account_details(accs[0]["id"])
        print(f"Details for {accs[0]['name']}: {len(details['usage_metrics'])} metrics, {len(details['support_tickets'])} tickets")
