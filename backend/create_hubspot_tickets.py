import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# HIGH risk company HubSpot IDs and their ticket data
# These match the 7 HIGH risk companies we imported
ticket_data = [
    {
        "company_name": "Quantum Dynamics",
        "tickets": [
            {"subject": "Platform keeps crashing during peak hours", "sentiment": "negative"},
            {"subject": "Cannot access reporting module for 3 days", "sentiment": "negative"},
            {"subject": "Billing discrepancy on last invoice", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "Orbit Software",
        "tickets": [
            {"subject": "Onboarding support has been unresponsive", "sentiment": "negative"},
            {"subject": "Features promised during sales not available", "sentiment": "negative"},
            {"subject": "API integration keeps failing", "sentiment": "negative"},
            {"subject": "Response time from support team is very slow", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "Stellar Systems",
        "tickets": [
            {"subject": "Considering switching to competitor", "sentiment": "negative"},
            {"subject": "Product does not meet expectations", "sentiment": "negative"},
            {"subject": "Data export feature is broken", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "Apex Innovations",
        "tickets": [
            {"subject": "Dashboard loading very slowly", "sentiment": "negative"},
            {"subject": "Need urgent support for integration issue", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "CipherCore",
        "tickets": [
            {"subject": "Security alert not working as expected", "sentiment": "negative"},
            {"subject": "Cannot generate compliance reports", "sentiment": "negative"},
            {"subject": "Team members unable to login", "sentiment": "negative"},
            {"subject": "Price increase not communicated in advance", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "NovaBridge Tech",
        "tickets": [
            {"subject": "Integration with our CRM keeps disconnecting", "sentiment": "negative"},
            {"subject": "Support ticket response taking over 5 days", "sentiment": "negative"},
            {"subject": "Feature we rely on was removed without notice", "sentiment": "negative"}
        ]
    },
    {
        "company_name": "VortexAI",
        "tickets": [
            {"subject": "AI model giving inaccurate results", "sentiment": "negative"},
            {"subject": "Platform downtime affecting our operations", "sentiment": "negative"}
        ]
    }
]

def get_company_id_by_name(company_name):
    search_payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "name",
                "operator": "EQ",
                "value": company_name
            }]
        }],
        "properties": ["name"],
        "limit": 1
    }
    response = requests.post(
        "https://api.hubapi.com/crm/v3/objects/companies/search",
        headers=headers,
        json=search_payload
    )
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0].get("id")
    return None

def create_ticket(company_id, subject, sentiment):
    ticket_payload = {
        "properties": {
            "subject": subject,
            "hs_pipeline": "0",
            "hs_pipeline_stage": "1",
            "hs_ticket_priority": "HIGH" if sentiment == "negative" else "MEDIUM"
        }
    }
    response = requests.post(
        "https://api.hubapi.com/crm/v3/objects/tickets",
        headers=headers,
        json=ticket_payload
    )
    if response.status_code in [200, 201]:
        ticket_id = response.json().get("id")
        # Associate ticket with company
        requests.put(
            f"https://api.hubapi.com/crm/v3/objects/tickets/{ticket_id}/associations/companies/{company_id}/ticket_to_company",
            headers=headers
        )
        return ticket_id
    else:
        print(f"  Failed to create ticket: {response.status_code} {response.text[:100]}")
        return None

for company_data in ticket_data:
    company_name = company_data["company_name"]
    print(f"\nProcessing {company_name}...")
    company_id = get_company_id_by_name(company_name)
    if not company_id:
        print(f"  Company not found in HubSpot: {company_name}")
        continue
    print(f"  Found company ID: {company_id}")
    for ticket in company_data["tickets"]:
        ticket_id = create_ticket(company_id, ticket["subject"], ticket["sentiment"])
        if ticket_id:
            print(f"  Created ticket: {ticket['subject'][:50]}")

print("\nDone creating tickets.")
