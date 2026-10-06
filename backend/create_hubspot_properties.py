import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
PORTAL_ID = "246294698"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

properties = [
    {"name": "assigned_csm", "label": "Assigned CSM", "type": "string", "fieldType": "text", "groupName": "companyinformation"},
    {"name": "contract_type", "label": "Contract Type", "type": "string", "fieldType": "text", "groupName": "companyinformation"},
    {"name": "tenure_months", "label": "Tenure Months", "type": "number", "fieldType": "number", "groupName": "companyinformation"},
    {"name": "monthly_charges", "label": "Monthly Charges", "type": "number", "fieldType": "number", "groupName": "companyinformation"},
    {"name": "feature_adoption_pct", "label": "Feature Adoption Pct", "type": "number", "fieldType": "number", "groupName": "companyinformation"},
    {"name": "login_frequency", "label": "Login Frequency", "type": "number", "fieldType": "number", "groupName": "companyinformation"},
    {"name": "session_duration_avg", "label": "Session Duration Avg", "type": "number", "fieldType": "number", "groupName": "companyinformation"},
    {"name": "renewal_date", "label": "Renewal Date", "type": "date", "fieldType": "date", "groupName": "companyinformation"},
    {"name": "last_login_date", "label": "Last Login Date", "type": "date", "fieldType": "date", "groupName": "companyinformation"},
]

for prop in properties:
    response = requests.post(
        "https://api.hubapi.com/crm/v3/properties/companies",
        headers=headers,
        json=prop
    )
    if response.status_code in [200, 201]:
        print(f"Created: {prop['name']}")
    elif response.status_code == 409:
        print(f"Already exists: {prop['name']}")
    else:
        print(f"Failed {prop['name']}: {response.status_code} {response.text[:100]}")

print("Done.")
