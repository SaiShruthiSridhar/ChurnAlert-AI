import pandas as pd
import random
import uuid
import os
from datetime import datetime, timedelta

# Create directory if not exists
os.makedirs("data", exist_ok=True)

# 1. Accounts Dataset
account_data = []
csm_names = ["Sarah Jenkins", "Michael Chen", "Emily Rodriguez", "David Park", "Jessica Taylor"]
contract_types = ["Month-to-month", "One year", "Two year"]

companies = [
    "Quantum Dynamics", "Nebula Systems", "Vertex Solutions", "Apex Logic", "Solaris Tech",
    "Stellar Soft", "Prism Interactive", "Flux Networks", "Zenith Global", "Ember Analytics",
    "Oracle Cloud (SMB)", "ByteScale", "CloudPulse", "DataStream", "InfiniLink",
    "NetGlow", "SwiftScale", "Terraform Tech", "Velocify", "WaveForm",
    "BlueHorizon", "DeepLogic", "EcoSystem", "FireFly", "GreenLeaf",
    "IronForge", "Krypton", "LunarLabs", "Matrix", "Nova"
]

for i, name in enumerate(companies):
    acc_id = f"ACC-{1000 + i}"
    tenure = random.randint(2, 48)
    charges = round(random.uniform(49.0, 499.0), 2)
    contract = random.choice(contract_types)
    
    account_data.append({
        "id": acc_id,
        "name": name,
        "tenure": tenure,
        "monthly_charges": charges,
        "contract_type": contract,
        "assigned_csm": random.choice(csm_names),
        "status": "Active",
        "last_login_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
        "renewal_date": (datetime.now() + timedelta(days=random.randint(10, 365))).strftime("%Y-%m-%d"),
        "contract_value": round(charges * (12 if contract != "Month-to-month" else 1), 2)
    })

df_accounts = pd.DataFrame(account_data)
df_accounts.to_csv("data/accounts.csv", index=False)

# 2. Metrics Dataset (8 weeks per account)
metrics_data = []
for acc in account_data:
    for w in range(8):
        metrics_data.append({
            "account_id": acc["id"],
            "login_frequency": random.randint(1, 20) if w > 2 else random.randint(0, 5), # Simulate some dropping usage
            "feature_adoption_pct": round(random.uniform(10, 95), 2),
            "session_duration_avg": random.randint(5, 60),
            "timestamp": (datetime.now() - timedelta(weeks=w)).strftime("%Y-%m-%d")
        })

df_metrics = pd.DataFrame(metrics_data)
df_metrics.to_csv("data/metrics.csv", index=False)

# 3. Tickets Dataset (Realistic Business Scenarios)
ticket_templates = [
    {"subject": "Cannot export Q4 financial reports", "sentiment": "negative", "is_resolved": False},
    {"subject": "API documentation is missing examples for Node.js", "sentiment": "neutral", "is_resolved": True},
    {"subject": "Considering switching to competitor due to pricing", "sentiment": "negative", "is_resolved": False},
    {"subject": "Great support from the CSM team on onboarding", "sentiment": "positive", "is_resolved": True},
    {"subject": "Dashboard loading very slowly during peak hours", "sentiment": "negative", "is_resolved": True},
    {"subject": "New integration request for Slack/Teams", "sentiment": "neutral", "is_resolved": False},
    {"subject": "Billing discrepancy on last month's invoice", "sentiment": "negative", "is_resolved": True},
    {"subject": "How to enable SSO for our organization?", "sentiment": "neutral", "is_resolved": True},
    {"subject": "Feature request: Dark mode for the portal", "sentiment": "positive", "is_resolved": False},
    {"subject": "Platform downtime cost us 2 hours of productivity", "sentiment": "negative", "is_resolved": True}
]

tickets_data = []
for acc in account_data:
    # Randomly assign 0-4 tickets per account
    num_tickets = random.randint(1, 4)
    selected = random.sample(ticket_templates, num_tickets)
    for t in selected:
        tickets_data.append({
            "account_id": acc["id"],
            "subject": t["subject"],
            "sentiment": t["sentiment"],
            "is_resolved": t["is_resolved"],
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
        })

df_tickets = pd.DataFrame(tickets_data)
df_tickets.to_csv("data/tickets.csv", index=False)

print("CSVs generated successfully in data/ folder.")
