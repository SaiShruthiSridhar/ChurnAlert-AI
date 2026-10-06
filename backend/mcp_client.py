import os
import requests
import json
import hashlib
import base64
import secrets
from dotenv import load_dotenv, set_key

load_dotenv()

HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI")
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
HUBSPOT_BASE_URL = "https://api.hubapi.com"
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

# Global storage for PKCE code_verifier (used between /connect and /callback)
_pkce_code_verifier = None

def generate_pkce_pair():
    """Generates a PKCE code_verifier and code_challenge pair."""
    global _pkce_code_verifier
    code_verifier = secrets.token_urlsafe(64)
    _pkce_code_verifier = code_verifier
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

def get_pkce_verifier():
    """Returns the stored code_verifier for use in token exchange."""
    return _pkce_code_verifier

def get_access_token():
    token = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
    if not token:
        load_dotenv(ENV_PATH, override=True)
        token = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
    return token

def get_refresh_token():
    return os.getenv("HUBSPOT_REFRESH_TOKEN", "")

def save_tokens(access_token, refresh_token):
    os.environ["HUBSPOT_ACCESS_TOKEN"] = access_token
    os.environ["HUBSPOT_REFRESH_TOKEN"] = refresh_token
    try:
        set_key(ENV_PATH, "HUBSPOT_ACCESS_TOKEN", access_token)
        set_key(ENV_PATH, "HUBSPOT_REFRESH_TOKEN", refresh_token)
        print("[HubSpot MCP] Tokens saved to .env")
    except Exception as e:
        print(f"[HubSpot MCP] Could not save tokens to .env: {e}")

def get_oauth_url():
    code_verifier, code_challenge = generate_pkce_pair()
    url = (
        f"https://mcp-na2.hubspot.com/oauth/authorize/user"
        f"?client_id={HUBSPOT_CLIENT_ID}"
        f"&redirect_uri={HUBSPOT_REDIRECT_URI}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    return url

def exchange_code_for_tokens(code):
    try:
        code_verifier = get_pkce_verifier()
        if not code_verifier:
            print("[HubSpot MCP] No PKCE code_verifier found. Please restart OAuth flow.")
            return False, None

        payload = {
            "grant_type": "authorization_code",
            "client_id": HUBSPOT_CLIENT_ID,
            "client_secret": HUBSPOT_CLIENT_SECRET,
            "redirect_uri": HUBSPOT_REDIRECT_URI,
            "code": code,
            "code_verifier": code_verifier
        }
        response = requests.post(HUBSPOT_TOKEN_URL, data=payload)
        data = response.json()
        if "access_token" in data:
            save_tokens(data["access_token"], data.get("refresh_token", ""))
            print("[HubSpot MCP] OAuth tokens obtained successfully with PKCE.")
            return True, data["access_token"]
        else:
            print(f"[HubSpot MCP] Token exchange failed: {data}")
            return False, None
    except Exception as e:
        print(f"[HubSpot MCP] Token exchange error: {e}")
        return False, None

def refresh_access_token():
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("[HubSpot MCP] No refresh token available.")
        return False
    try:
        response = requests.post(HUBSPOT_TOKEN_URL, data={
            "grant_type": "refresh_token",
            "client_id": HUBSPOT_CLIENT_ID,
            "client_secret": HUBSPOT_CLIENT_SECRET,
            "refresh_token": refresh_token
        })
        data = response.json()
        if "access_token" in data:
            save_tokens(data["access_token"], data.get("refresh_token", refresh_token))
            print("[HubSpot MCP] Access token refreshed successfully.")
            return True
        else:
            print(f"[HubSpot MCP] Token refresh failed: {data}")
            return False
    except Exception as e:
        print(f"[HubSpot MCP] Token refresh error: {e}")
        return False

def hubspot_get(endpoint, params=None):
    access_token = get_access_token()
    if not access_token:
        print("[HubSpot MCP] No access token. Run OAuth flow first.")
        return None
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{HUBSPOT_BASE_URL}{endpoint}", headers=headers, params=params)
        if response.status_code == 401:
            print("[HubSpot MCP] Token expired. Refreshing...")
            if refresh_access_token():
                headers["Authorization"] = f"Bearer {get_access_token()}"
                response = requests.get(f"{HUBSPOT_BASE_URL}{endpoint}", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[HubSpot MCP] API error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[HubSpot MCP] Request error: {e}")
        return None

def fetch_companies():
    print("[HubSpot MCP] Fetching companies with full custom properties...")
    properties = [
        "name", "domain", "industry", "annualrevenue",
        "numberofemployees", "city", "country", "description",
        "hs_lastmodifieddate", "createdate",
        "assigned_csm", "contract_type", "tenure_months",
        "monthly_charges", "feature_adoption_pct", "login_frequency",
        "session_duration_avg", "renewal_date", "last_login_date"
    ]
    params = {
        "limit": 100,
        "properties": ",".join(properties)
    }
    data = hubspot_get("/crm/v3/objects/companies", params=params)
    if not data:
        return []
    companies = []
    for result in data.get("results", []):
        props = result.get("properties", {})
        companies.append({
            "id": f"HS-{result.get('id', 'unknown')}",
            "hubspot_id": result.get("id"),
            "name": props.get("name", "Unknown"),
            "domain": props.get("domain", ""),
            "industry": props.get("industry", ""),
            "annual_revenue": props.get("annualrevenue", 0),
            "city": props.get("city", ""),
            "country": props.get("country", ""),
            "description": props.get("description", ""),
            "last_modified": props.get("hs_lastmodifieddate", ""),
            "created_date": props.get("createdate", ""),
            "assigned_csm": props.get("assigned_csm", "Unassigned"),
            "contract_type": props.get("contract_type", "Month-to-month"),
            "tenure": int(float(props.get("tenure_months") or 0)),
            "monthly_charges": float(props.get("monthly_charges") or 0),
            "contract_value": float(props.get("monthly_charges") or 0) * 12,
            "feature_adoption_pct": float(props.get("feature_adoption_pct") or 0),
            "login_frequency": int(float(props.get("login_frequency") or 0)),
            "session_duration_avg": float(props.get("session_duration_avg") or 0),
            "renewal_date": props.get("renewal_date", ""),
            "last_login_date": props.get("last_login_date", ""),
            "status": "Active",
            "source": "hubspot"
        })
    print(f"[HubSpot MCP] Fetched {len(companies)} companies with full data.")
    return companies

def fetch_company_details(hubspot_company_id):
    print(f"[HubSpot MCP] Fetching details for company {hubspot_company_id}...")
    properties = [
        "name", "domain", "industry", "annualrevenue",
        "numberofemployees", "city", "country", "description",
        "hs_lastmodifieddate", "createdate", "notes_last_contacted",
        "closedate", "hs_num_open_deals"
    ]
    params = {"properties": ",".join(properties)}
    data = hubspot_get(f"/crm/v3/objects/companies/{hubspot_company_id}", params=params)
    if not data:
        return None
    props = data.get("properties", {})
    return {
        "id": f"HS-{hubspot_company_id}",
        "hubspot_id": hubspot_company_id,
        "name": props.get("name", "Unknown"),
        "domain": props.get("domain", ""),
        "industry": props.get("industry", ""),
        "annual_revenue": float(props.get("annualrevenue", 0) or 0),
        "city": props.get("city", ""),
        "country": props.get("country", ""),
        "description": props.get("description", ""),
        "last_contacted": props.get("notes_last_contacted", ""),
        "close_date": props.get("closedate", ""),
        "open_deals": props.get("hs_num_open_deals", 0)
    }

def is_hubspot_connected():
    token = get_access_token()
    if not token:
        return False
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            "https://api.hubapi.com/crm/v3/objects/companies?limit=1&properties=name",
            headers=headers
        )
        if response.status_code == 200:
            return True
        print(f"[HubSpot] Connection check failed: {response.status_code}: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"[HubSpot] Connection check error: {e}")
        return False

def find_company_by_name(company_name):
    """Search HubSpot for a company by name and return its HubSpot ID."""
    try:
        params = {
            "limit": 5,
            "properties": "name,domain",
            "filterGroups": json.dumps([{
                "filters": [{
                    "propertyName": "name",
                    "operator": "CONTAINS_TOKEN",
                    "value": company_name
                }]
            }])
        }
        data = hubspot_get("/crm/v3/objects/companies/search", params=None)
        if data is None:
            search_payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "name",
                        "operator": "CONTAINS_TOKEN",
                        "value": company_name
                    }]
                }],
                "properties": ["name", "domain"],
                "limit": 5
            }
            access_token = get_access_token()
            if not access_token:
                return None
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{HUBSPOT_BASE_URL}/crm/v3/objects/companies/search",
                headers=headers,
                json=search_payload
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0].get("id")
            return None
        results = data.get("results", [])
        if results:
            return results[0].get("id")
        return None
    except Exception as e:
        print(f"[HubSpot MCP] Company search error: {e}")
        return None

def create_hubspot_note(company_id, note_body, csm_name="ChurnAlert AI"):
    """Create a note on a HubSpot company record to log the outreach message."""
    try:
        access_token = get_access_token()
        if not access_token:
            print("[HubSpot MCP] No access token for note creation.")
            return False
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        import datetime
        note_payload = {
            "properties": {
                "hs_note_body": f"[ChurnAlert AI Outreach — Approved by {csm_name}]\n\n{note_body}",
                "hs_timestamp": str(int(datetime.datetime.utcnow().timestamp() * 1000))
            },
            "associations": [
                {
                    "to": {"id": str(company_id)},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 190}]
                }
            ]
        }
        response = requests.post(
            f"{HUBSPOT_BASE_URL}/crm/v3/objects/notes",
            headers=headers,
            json=note_payload
        )
        if response.status_code in [200, 201]:
            print(f"[HubSpot MCP] Note created successfully on company {company_id}.")
            return True
        else:
            print(f"[HubSpot MCP] Note creation failed: {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[HubSpot MCP] Note creation error: {e}")
        return False

def fetch_company_tickets(hubspot_company_id):
    """Fetch support tickets associated with a HubSpot company."""
    try:
        access_token = get_access_token()
        if not access_token:
            return []
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        # Get tickets associated with the company
        response = requests.get(
            f"{HUBSPOT_BASE_URL}/crm/v3/objects/companies/{hubspot_company_id}/associations/tickets",
            headers=headers
        )
        if response.status_code != 200:
            return []
        ticket_ids = [r.get("id") for r in response.json().get("results", [])]
        if not ticket_ids:
            return []
        tickets = []
        for ticket_id in ticket_ids[:10]:
            t_response = requests.get(
                f"{HUBSPOT_BASE_URL}/crm/v3/objects/tickets/{ticket_id}",
                headers=headers,
                params={"properties": "subject,hs_ticket_priority,hs_pipeline_stage,createdate"}
            )
            if t_response.status_code == 200:
                props = t_response.json().get("properties", {})
                subject = props.get("subject", "Support ticket")
                priority = props.get("hs_ticket_priority", "MEDIUM")
                stage = props.get("hs_pipeline_stage", "1")
                sentiment = "negative" if priority == "HIGH" else "neutral"
                is_resolved = stage in ["4", "closed"]
                createdate = props.get("createdate")
                if not createdate:
                    import datetime
                    createdate = datetime.datetime.utcnow().isoformat() + "Z"
                tickets.append({
                    "subject": subject,
                    "sentiment": sentiment,
                    "is_resolved": is_resolved,
                    "created_at": createdate
                })
        print(f"[HubSpot MCP] Fetched {len(tickets)} tickets for company {hubspot_company_id}.")
        return tickets
    except Exception as e:
        print(f"[HubSpot MCP] Ticket fetch error: {e}")
        return []
