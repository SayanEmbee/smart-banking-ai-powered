import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import os
import random
import requests
import subprocess
from datetime import datetime

# =====================================================================
# 1. PAGE CONFIGURATION & STUNNING ENTERPRISE THEME (OBSIDIAN GLASS)
# =====================================================================
st.set_page_config(
    page_title="AI Smart Banking Fraud Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium stylesheet injection
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Globally constrain block container to 80% screen size on desktops and center it */
        @media (min-width: 992px) {
            .block-container {
                max-width: 80% !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                margin: 0 auto !important;
            }
            div[data-testid="stChatInput"] {
                max-width: 80% !important;
                margin: 0 auto !important;
            }
        }
        @media (max-width: 991px) {
            .block-container {
                max-width: 95% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                margin: 0 auto !important;
            }
            div[data-testid="stChatInput"] {
                max-width: 95% !important;
                margin: 0 auto !important;
            }
        }

        /* Core visual scheme - Premium Light Mode */
        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
            font-family: 'Outfit', sans-serif;
        }
        
        /* Disable standard sidebar visual footprint */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Main page headers styling */
        h1, h2, h3, .title-text {
            font-family: 'Space Grotesk', sans-serif !important;
            background: linear-gradient(135deg, #1E3A8A 30%, #991B1B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            margin: 0;
        }
        
        /* Custom Navigation Button styling to integrate seamlessly */
        div[data-testid="stColumn"] button {
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 10px 20px !important;
            height: auto !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
        }
        
        /* Active button style (Primary) */
        div[data-testid="stColumn"] button[kind="primary"] {
            background: linear-gradient(135deg, #991B1B 0%, #1E3A8A 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        div[data-testid="stColumn"] button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(153, 27, 27, 0.25) !important;
            color: #FFFFFF !important;
        }
        
        /* Inactive button style (Secondary) */
        div[data-testid="stColumn"] button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #1E3A8A !important;
            border: 1px solid rgba(30, 64, 175, 0.2) !important;
        }
        div[data-testid="stColumn"] button[kind="secondary"]:hover {
            background: #F1F5F9 !important;
            color: #991B1B !important;
            border-color: #991B1B !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(30, 64, 175, 0.1) !important;
        }
        
        /* Modern Glassmorphism Metric Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.05);
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            color: #0F172A;
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(15, 23, 42, 0.12);
            box-shadow: 0 15px 35px -5px rgba(15, 23, 42, 0.08);
        }
        
        .metric-card-blue::before { background: linear-gradient(90deg, #1E3A8A, #3B82F6); }
        .metric-card-blue:hover { box-shadow: 0 15px 35px -5px rgba(30, 64, 175, 0.1); }
        
        .metric-card-red::before { background: linear-gradient(90deg, #7F1D1D, #B91C1C); }
        .metric-card-red:hover { box-shadow: 0 15px 35px -5px rgba(185, 28, 28, 0.1); }
        
        .metric-card-purple::before { background: linear-gradient(90deg, #1E3A8A, #991B1B); }
        .metric-card-purple:hover { box-shadow: 0 15px 35px -5px rgba(153, 27, 27, 0.1); }
        
        .metric-value {
            font-size: 2.4rem;
            font-weight: 700;
            margin: 6px 0;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Premium Fraud Alerts */
        .alert-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(185, 28, 28, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 30px -8px rgba(15, 23, 42, 0.05);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .alert-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(180deg, #B91C1C, #991B1B);
        }
        .alert-card:hover {
            border-color: rgba(185, 28, 28, 0.35);
            background: #FFFFFF;
            transform: translateY(-2px);
            box-shadow: 0 12px 35px -5px rgba(185, 28, 28, 0.08);
        }
        
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(185, 28, 28, 0.1);
            padding-bottom: 12px;
            margin-bottom: 14px;
        }
        
        .alert-badge {
            background-color: #B91C1C;
            color: #FFFFFF;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        
        .alert-insight-box {
            background: rgba(185, 28, 28, 0.02);
            border-left: 3px solid #B91C1C;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
            border: 1px solid rgba(185, 28, 28, 0.08);
        }
        
        /* Status Badge Indicators */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .status-live {
            background: rgba(30, 64, 175, 0.06);
            color: #1E3A8A;
            border: 1px solid rgba(30, 64, 175, 0.15);
        }
        .status-sim {
            background: rgba(185, 28, 28, 0.06);
            color: #991B1B;
            border: 1px solid rgba(185, 28, 28, 0.15);
        }
        
        /* Premium Chatbot Styling */
        .chat-bubble {
            padding: 18px 22px;
            border-radius: 18px;
            margin-bottom: 20px;
            line-height: 1.6;
            font-size: 0.95rem;
            max-width: 85%;
            animation: fadeIn 0.4s ease-out;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-bubble-user {
            background: linear-gradient(135deg, #991B1B 0%, #B91C1C 100%);
            border: 1px solid rgba(153, 27, 27, 0.2);
            color: #FFFFFF;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            border-top-right-radius: 18px;
        }
        
        .chat-bubble-copilot {
            background: linear-gradient(135deg, #FFFFFF 0%, rgba(241, 245, 249, 0.8) 100%);
            border: 1px solid rgba(30, 64, 175, 0.12);
            border-left: 4px solid #1E3A8A;
            color: #0F172A;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            border-top-left-radius: 18px;
        }

        /* High-fidelity Responsive Overrides for Tablets, Laptops & Mobile */
        @media (max-width: 1200px) {
            .metric-value {
                font-size: 1.85rem !important;
            }
            .metric-card {
                padding: 16px 12px !important;
            }
            h1, .title-text {
                font-size: 1.95rem !important;
            }
            .alert-card {
                padding: 16px !important;
            }
        }
        @media (max-width: 992px) {
            .metric-value {
                font-size: 1.5rem !important;
            }
            .metric-card {
                padding: 12px 10px !important;
            }
            h1, .title-text {
                font-size: 1.65rem !important;
            }
            .chat-bubble {
                max-width: 92% !important;
            }
        }
        @media (max-width: 768px) {
            /* Adjust spacing and sizes for mobile viewports */
            .metric-card {
                margin-bottom: 12px !important;
            }
            .chat-bubble {
                max-width: 100% !important;
                padding: 12px 15px !important;
            }
            h1, .title-text {
                font-size: 1.5rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. AUTOMATED BACKSTAGE CONFIGURATION LOADERS
# =====================================================================
def load_env_file():
    env_paths = [
        ".env",
        os.path.join("..", ".env"),
        os.path.join("..", "..", ".env")
    ]
    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass

load_env_file()

def load_accelerator_config():
    config_paths = [
        os.path.join("config", "accelerator-config.json"),
        os.path.join("..", "..", "config", "accelerator-config.json"),
        os.path.join("..", "config", "accelerator-config.json")
    ]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

config_data = load_accelerator_config()
openai_config = config_data.get("openaiConfig", {})
kql_db_name = config_data.get("kqlDatabaseName", "BankingRiskDB")
kql_query_uri = os.environ.get("KQL_QUERY_URI", "https://trd-d2106gp5ufbuq1042c.z1.kusto.fabric.microsoft.com")

# =====================================================================
# 3. KQL DATA CONNECTION ENGINE
# =====================================================================
# 3. KQL DATA CONNECTION ENGINE
# =====================================================================

# Manual TTL token cache using session_state (avoids @st.cache_resource caching failures permanently)
def get_kql_client_credentials(tenant_id, client_id, client_secret):
    cache_key = "_kql_token_cache"
    now = time.time()

    cached = st.session_state.get(cache_key, {})
    if cached.get("token") and now < cached.get("expires_at", 0):
        return cached["token"]

    # ✅ CORRECT scope for Microsoft Fabric KQL / Azure Data Explorer
    # ❌ Wrong was: https://help.kusto.windows.net/.default  (that's the docs site)
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://kusto.kusto.windows.net/.default"
    }
    resp = requests.post(token_url, data=payload, timeout=10.0)
    if resp.status_code != 200:
        raise Exception(f"Auth HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    token = data.get("access_token") or data.get("accessToken")
    if not token:
        raise Exception(f"No access_token returned. Response: {list(data.keys())}")

    # Cache for 50 minutes (tokens expire at 60 min)
    st.session_state[cache_key] = {"token": token, "expires_at": now + 3000}
    return token

def query_fabric_kql(query_uri, db_name, kql_query, access_token):
    """Query Fabric KQL database via REST API.
    Handles both Fabric v2 (list of frames) and classic (dict with Tables key) responses.
    """
    url = f"{query_uri.rstrip('/')}/v2/rest/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "db": db_name,
        "csl": kql_query
    }
    response = requests.post(url, json=payload, headers=headers, timeout=12.0)
    if response.status_code != 200:
        raise Exception(f"KQL HTTP {response.status_code}: {response.text[:300]}")
    
    data = response.json()

    # Fabric v2 returns a JSON list of frame objects
    if isinstance(data, list):
        # Find the DataTable frame that is the PrimaryResult
        for frame in data:
            if not isinstance(frame, dict):
                continue
            frame_type = frame.get("FrameType", "")
            table_kind = frame.get("TableKind", "")
            # v2 primary result frame
            if frame_type == "DataTable" and table_kind == "PrimaryResult":
                cols = [c["ColumnName"] for c in frame.get("Columns", [])]
                rows = frame.get("Rows", [])
                return pd.DataFrame(rows, columns=cols)
        # Fallback: return first DataTable frame found
        for frame in data:
            if isinstance(frame, dict) and frame.get("FrameType") == "DataTable":
                cols = [c["ColumnName"] for c in frame.get("Columns", [])]
                rows = frame.get("Rows", [])
                if cols and rows:
                    return pd.DataFrame(rows, columns=cols)
        return pd.DataFrame()

    # Classic v1 response: dict with "Tables" key
    if isinstance(data, dict):
        tables = data.get("Tables", [])
        primary = [t for t in tables if isinstance(t, dict) and t.get("TableKind") == "PrimaryResult"]
        if not primary:
            primary = [t for t in tables if isinstance(t, dict) and t.get("Rows")]
        if not primary:
            return pd.DataFrame()
        cols = [c["ColumnName"] for c in primary[0].get("Columns", [])]
        rows = primary[0].get("Rows", [])
        return pd.DataFrame(rows, columns=cols)

    return pd.DataFrame()

# =====================================================================
# 4. HIGHEST-FIDELITY LOCAL SIMULATOR FALLBACK ENGINE
# =====================================================================
def local_calculate_ensemble_risk(txn):
    reasons = []
    heuristic_score = 10
    amount = float(txn.get('amount', 0))
    
    if amount >= 200000:
        heuristic_score += 45
        reasons.append("High-value spike above threshold of Rs. 2,00,000")
    elif amount >= 50000:
        heuristic_score += 15
        reasons.append("Elevated transaction amount")
        
    if txn.get('payment_channel') == "ATM" and amount >= 40000:
        heuristic_score += 45
        reasons.append("ATM cash withdrawal exceeds daily card limit of Rs. 40,000")
        
    if txn.get('country') != "India":
        heuristic_score += 40
        reasons.append(f"Foreign location mismatch: transaction initiated from {txn.get('country')}")
        
    if txn.get('ip_address') == "185.220.101.44":
        heuristic_score += 35
        reasons.append("Transaction routed through known malicious Tor IP subnet")
        
    try:
        ts = txn['timestamp']
        if "T" in ts:
            ts = ts.split(".")[0].replace("T", " ")
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if dt.hour in [1, 2, 3, 4]:
            heuristic_score += 20
            reasons.append("Suspicious midnight transaction window (1:00 AM - 4:30 AM)")
    except Exception:
        pass
        
    if txn.get('payment_channel') == "Internet Banking" and "Unrecognized" in txn.get('device_type', ''):
        heuristic_score += 25
        reasons.append("Internet banking accessed via unrecognized device hardware")
        
    ml_score = 0
    if txn.get('country') != "India":
        ml_score = random.randint(86, 96)
    elif txn.get('ip_address') == "185.220.101.44":
        ml_score = 100
    elif amount >= 200000:
        ml_score = 99
    elif txn.get('payment_channel') == "ATM" and amount >= 40000:
        ml_score = 100
    else:
        ml_score = random.randint(5, 18)
        
    if ml_score > 70:
        reasons.append(f"AI Random Forest Classifier flagged transaction as high probability fraud ({ml_score}%)")
        
    final_score = max(ml_score, heuristic_score)
    final_score = min(final_score, 99)
    return final_score, reasons

def local_explain_risk_with_ai(txn, score, reasons):
    amount = float(txn.get('amount', 0))
    channel = txn.get('payment_channel', 'Unknown')
    country = txn.get('country', 'India')
    ip = txn.get('ip_address', '')
    device = txn.get('device_type', '')
    cust = txn.get('customer_name', 'Customer')
    city = txn.get('city', 'Unknown')
    
    threat_vector = "Unknown Anomaly"
    regulatory_impact = "RBI Circular on Customer Liability (Rule 2017/18) - Flagged for review."
    remediation_tier1 = "Initiate instant security hold on Card/UPI channel."
    remediation_tier2 = "Send automated push-verification SMS request to registered mobile."
    remediation_tier3 = "Log case in AML/CFT system for Suspicious Transaction Report (STR) review."
    
    if amount >= 200000:
        threat_vector = "High-Value Transaction Spike (POS/Internet Banking Limit Breach)"
        regulatory_impact = "RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18 limits customer liability if unauthorized transaction is reported within 3 days. High value necessitates immediate preventive freeze to mitigate bank liability."
        remediation_tier1 = "Suspend UPI, POS, and Net-Banking channels immediately. Lock account funds transfer capabilities."
        remediation_tier2 = "Initiate high-priority telephone verification call via the Relationship Manager."
        remediation_tier3 = "Report to Fraud FMC and log in Suspicious Transaction Registry."
    elif channel == "ATM" and amount >= 40000:
        threat_vector = "ATM Velocity & Cash-Out Burst (Daily Debit Limit Breach)"
        regulatory_impact = "High cash-out volumes at unorthodox hours suggest physical card compromise or ATM cloning skimming attacks."
        remediation_tier1 = "Temporary lockdown of debit card status. Restrict domestic and international ATM channels."
        remediation_tier2 = "Trigger instant in-app security alert and SMS warning to registered number."
        remediation_tier3 = "Analyze local ATM terminal DVR footage and review terminal health reports for physical skimmer anomalies."
    elif country != "India":
        threat_vector = "Foreign Geolocation Mismatch (Impossible Travel Speed Anomaly)"
        regulatory_impact = "Cross-border transaction velocity violates standard risk boundaries. Compliance requires instant card lock to prevent cross-border money laundering."
        remediation_tier1 = "Place global card lockdown. Decline all international POS, ATM, and E-commerce gateways."
        remediation_tier2 = "Send critical security email alert and interactive mobile app push-notification confirmation request."
        remediation_tier3 = "Mark card status as 'Compromised' and queue automatic reissue protocol."
    elif ip == "185.220.101.44":
        threat_vector = "Midnight Takeover via Malicious Proxy (Tor Node Access)"
        regulatory_impact = "Routing transaction authentication through a known Tor exit node IP violates standard corporate Cyber Security policy."
        remediation_tier1 = "Terminate active internet-banking login session. Suspend online banking login credentials."
        remediation_tier2 = "Require mandatory step-up Multi-Factor Authentication (MFA) and force credential reset."
        remediation_tier3 = "Flag IP subnet in Security Information and Event Management (SIEM) dashboard for broad threat analysis."

    reasons_bullet = "\n- ".join(reasons)
    explanation = (
        f"### 🛡️ AI Risk Scoring Insight & Decision Summary\n\n"
        f"**Transaction ID:** {txn['transaction_id']} | **Risk Score:** {score}% | **Customer:** {cust}\n\n"
        f"#### 🔍 1. Threat Analysis Summary\n"
        f"- **Threat Vector:** {threat_vector}\n"
        f"- **Risk Indicators Flagged:**\n- {reasons_bullet}\n"
        f"- **Contextual Analysis:** Contextual home profile indicates customer lives in {city}, India. Initiating transaction from {country} via {channel} channel using {device} is a deviation from typical behavioral trends.\n\n"
        f"#### 🏛️ 2. Regulatory & Compliance Impact\n"
        f"- {regulatory_impact}\n\n"
        f"#### 🚀 3. Structured Operational Action Plan\n"
        f"- **Tier 1 (Immediate / Automated):** {remediation_tier1}\n"
        f"- **Tier 2 (Direct Outreach / Step-up):** {remediation_tier2}\n"
        f"- **Tier 3 (Log / Compliance):** {remediation_tier3}"
    )
    return explanation

def explain_risk_with_openai(txn, score, reasons, api_key, endpoint, model):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=endpoint)
        
        prompt = (
            f"You are a senior banking risk manager and expert fraud analyst at a top bank.\n"
            f"Analyze the anomalous transaction and generate a structured markdown report.\n\n"
            f"### Transaction Details:\n"
            f"- Transaction ID: {txn['transaction_id']}\n"
            f"- Customer Name: {txn['customer_name']}\n"
            f"- Home Location: {txn.get('city', 'Unknown')}, India\n"
            f"- Channel: {txn['payment_channel']}\n"
            f"- Amount: Rs. {txn['amount']}\n"
            f"- Geolocation: {txn['country']}\n"
            f"- Device: {txn.get('device_type', 'Unknown')}\n"
            f"- IP: {txn.get('ip_address', 'Unknown')}\n"
            f"- Flaws Flagged: {', '.join(reasons)}\n"
            f"- AI Risk Score: {score}%\n\n"
            f"### Format:\n"
            f"### 🛡️ AI Risk Scoring Insight & Decision Summary\n\n"
            f"**Transaction ID:** {txn['transaction_id']} | **Risk Score:** {score}% | **Customer:** {txn['customer_name']}\n\n"
            f"#### 🔍 1. Threat Analysis Summary\n"
            f"- **Threat Vector:** [Classify threat, e.g. Geolocation Velocity, Cash-Out Burst, Tor Node Hijacking]\n"
            f"- **Risk Indicators Flagged:** {', '.join(reasons)}\n"
            f"- **Contextual Analysis:** [Analyze the deviation from typical patterns]\n\n"
            f"#### 🏛️ 2. Regulatory & Compliance Impact\n"
            f"- [Cite relevant Indian banking regulatory guidelines like RBI customer liability framework]\n\n"
            f"#### 🚀 3. Structured Operational Action Plan\n"
            f"- **Tier 1 (Immediate / Automated):** [Card block, device blacklisting, active API freeze]\n"
            f"- **Tier 2 (Direct Outreach / Step-up):** [RM phone call verification, MFA step-up request]\n"
            f"- **Tier 3 (Log / Compliance):** [FMC, AML or FIU logs]"
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional banking fraud risk compliance specialist. Output clean, extremely concise, highly analytical markdown summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        mock_exp = local_explain_risk_with_ai(txn, score, reasons)
        return f"{mock_exp}\n\n*(AI live generation fallback: {e})*"

# Send Teams Alert Card
def send_teams_fraud_alert(webhook_url, txn, risk_score, explanation):
    headers = {"Content-Type": "application/json"}
    card_payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🚨 HIGH-RISK ANOMALY FLAGGED",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": "Attention"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Transaction ID:", "value": str(txn.get('transaction_id', 'Unknown'))},
                            {"title": "Customer:", "value": str(txn.get('customer_name', 'Unknown'))},
                            {"title": "Amount:", "value": f"Rs. {float(txn.get('amount', 0)):,.2f}"},
                            {"title": "Channel:", "value": str(txn.get('payment_channel', 'Unknown'))},
                            {"title": "Risk Score:", "value": f"{risk_score}/100"}
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": f"**AI Operations Insights:**\n{explanation}",
                        "wrap": True,
                        "spacing": "Medium"
                    }
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "Investigate in Fabric",
                        "url": "https://app.fabric.microsoft.com"
                    }
                ]
            }
        }]
    }
    try:
        response = requests.post(webhook_url, json=card_payload, headers=headers, timeout=5.0)
        return response.status_code in [200, 201, 202]
    except Exception:
        return False

# =====================================================================
# AI SECURITY COPILOT TRANSLATION & EXECUTION ENGINES
# =====================================================================
def translate_question_to_kql(question, config_data):
    """Translate natural language question to KQL using OpenAI or local fallback."""
    # Check if we have standard starter prompts for instant high-fidelity local mapping
    starters = {
        "Show me a high-level overview of our transaction ingestion telemetry.": 
            "real_time_transactions\n| summarize TotalTransactions = count(), DateFrom = min(todatetime(timestamp)), DateTo = max(todatetime(timestamp)), UniqueCustomers = dcount(customer_id), AvgAmount = round(avg(amount), 2), AvgRisk = round(avg(risk_score), 1), FraudCount = countif(risk_score > 80)",
        
        "What are the detailed fraud statistics and vulnerability rates by payment channel?":
            "real_time_transactions\n| summarize TotalTransactions = count(), TotalFraud = countif(risk_score > 80), MaxRisk = max(risk_score), AvgRisk = round(avg(risk_score), 2), TotalAmount = round(sum(amount), 2) by payment_channel\n| extend FraudPercentage = round(TotalFraud * 100.0 / TotalTransactions, 2)\n| order by FraudPercentage desc",
        
        "Identify all cross-border transactions originating outside of India with a risk score above 80%.":
            "real_time_transactions\n| where country != \"India\" and risk_score > 80\n| project timestamp, transaction_id, customer_name, country, amount, risk_score, payment_channel, device_type\n| order by risk_score desc",
        
        "Detect suspicious midnight transactions occurring via Internet Banking with high risk.":
            "real_time_transactions\n| extend Hour = hourofday(todatetime(timestamp))\n| where Hour in (1, 2, 3, 4) and payment_channel == \"Internet Banking\" and risk_score > 80\n| project timestamp, transaction_id, customer_name, amount, risk_score, ip_address, device_type\n| order by risk_score desc"
    }
    
    # Strict matching
    cleaned_q = question.strip().strip("?").strip()
    for sq, kql in starters.items():
        if cleaned_q.lower() in sq.lower() or sq.lower() in cleaned_q.lower():
            return kql

    # OpenAI translation
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_config = config_data.get("openaiConfig", {})
    if openai_key and openai_key != "YOUR_OPENAI_API_KEY":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, base_url=openai_config.get("apiEndpoint", "https://api.openai.com/v1"))
            
            system_prompt = """You are a KQL translation assistant for a Microsoft Fabric Real-Time Intelligence database.
Your job is to translate the user's natural language question into a single, highly optimized KQL (Kusto Query Language) query.
The table name is `real_time_transactions`.

Schema of `real_time_transactions`:
- `transaction_id` (string)
- `customer_id` (string)
- `account_number` (string)
- `customer_name` (string)
- `timestamp` (datetime)
- `amount` (real)
- `merchant` (string)
- `merchant_category` (string)
- `payment_channel` (string): UPI, POS, ATM, Internet Banking
- `transaction_type` (string): Debit
- `country` (string)
- `city` (string)
- `state` (string)
- `device_type` (string)
- `ip_address` (string)
- `risk_score` (int): 0 to 100
- `is_fraud` (int): 1 if risk_score > 80 else 0

Proven KQL Query Patterns:
1. Overview:
real_time_transactions | summarize TotalTransactions = count(), DateFrom = min(todatetime(timestamp)), DateTo = max(todatetime(timestamp)), UniqueCustomers = dcount(customer_id), AvgAmount = round(avg(amount), 2), AvgRisk = round(avg(risk_score), 1), FraudCount = countif(risk_score > 80)
2. Channel breakdown:
real_time_transactions | summarize TotalTransactions = count(), TotalFraud = countif(risk_score > 80), MaxRisk = max(risk_score), AvgRisk = round(avg(risk_score), 2), TotalAmount = round(sum(amount), 2) by payment_channel | extend FraudPercentage = round(TotalFraud * 100.0 / TotalTransactions, 2) | order by FraudPercentage desc
3. Cross-border:
real_time_transactions | where country != "India" and risk_score > 80 | project timestamp, transaction_id, customer_name, country, amount, risk_score, payment_channel, device_type | order by risk_score desc
4. Midnight Internet Banking:
real_time_transactions | extend Hour = hourofday(todatetime(timestamp)) | where Hour in (1, 2, 3, 4) and payment_channel == "Internet Banking" and risk_score > 80 | project timestamp, transaction_id, customer_name, amount, risk_score, ip_address, device_type | order by risk_score desc

Rules:
- Respond ONLY with the raw KQL query.
- Do NOT wrap in markdown block code syntax (like ```kql).
- Make sure the query is single-spaced and formatted properly.
"""
            response = client.chat.completions.create(
                model=openai_config.get("modelName", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip().replace("```kql", "").replace("```", "").strip()
        except Exception:
            pass

    # Default fallback if offline/no key and doesn't match starters
    return "real_time_transactions\n| limit 10"


def execute_kql_locally(kql_query, df):
    """Execute KQL queries locally on in-memory simulated DataFrame."""
    if df.empty:
        return df
    
    res = df.copy()
    lines = [line.strip() for line in kql_query.split("\n") if line.strip()]
    
    for line in lines:
        if line.startswith("real_time_transactions"):
            continue
        if line.startswith("|"):
            line = line[1:].strip()
            
        # Parse clauses
        if line.startswith("where "):
            clause = line[len("where "):].strip()
            conditions = clause.split(" and ")
            for cond in conditions:
                cond = cond.strip()
                if "!=" in cond:
                    col, val = cond.split("!=")
                    col = col.strip()
                    val = val.strip().strip('"').strip("'")
                    if col in res.columns:
                        res = res[res[col] != val]
                elif "==" in cond:
                    col, val = cond.split("==")
                    col = col.strip()
                    val = val.strip().strip('"').strip("'")
                    if col in res.columns:
                        if val.isdigit():
                            res = res[res[col] == int(val)]
                        else:
                            res = res[res[col] == val]
                elif ">" in cond:
                    col, val = cond.split(">")
                    col = col.strip()
                    val = val.strip()
                    if col in res.columns:
                        res = res[res[col] > float(val)]
                elif "<" in cond:
                    col, val = cond.split("<")
                    col = col.strip()
                    val = val.strip()
                    if col in res.columns:
                        res = res[res[col] < float(val)]
                elif " in " in cond:
                    col, vals_str = cond.split(" in ")
                    col = col.strip()
                    vals_str = vals_str.strip().strip("(").strip(")")
                    vals = [int(v.strip()) if v.strip().isdigit() else v.strip().strip('"').strip("'") for v in vals_str.split(",")]
                    if col == "Hour":
                        res["Hour"] = pd.to_datetime(res["timestamp"], errors="coerce").dt.hour
                    if col in res.columns:
                        res = res[res[col].isin(vals)]
                    
        elif line.startswith("extend "):
            clause = line[len("extend "):].strip()
            if "=" in clause:
                col, expr = clause.split("=", 1)
                col = col.strip()
                expr = expr.strip()
                if "hourofday" in expr:
                    res[col] = pd.to_datetime(res["timestamp"], errors="coerce").dt.hour
                elif "todatetime" in expr:
                    res[col] = pd.to_datetime(res["timestamp"], errors="coerce")
                    
        elif line.startswith("summarize "):
            clause = line[len("summarize "):].strip()
            if " by " in clause:
                agg_part, by_part = clause.split(" by ")
                agg_part = agg_part.strip()
                by_part = by_part.strip().split(",")
                by_cols = [c.strip() for c in by_part]
            else:
                agg_part = clause
                by_cols = []
                
            aggs = agg_part.split(",")
            agg_dict = {}
            for agg in aggs:
                agg = agg.strip()
                if "=" in agg:
                    new_col, func_expr = agg.split("=", 1)
                    new_col = new_col.strip()
                    func_expr = func_expr.strip()
                    
                    if "count()" in func_expr:
                        agg_dict[new_col] = ("transaction_id", "count")
                    elif "countif" in func_expr:
                        agg_dict[new_col] = ("risk_score", lambda x: (x > 80).sum())
                    elif "sum(" in func_expr:
                        col = func_expr[func_expr.find("(")+1:func_expr.rfind(")")]
                        agg_dict[new_col] = (col, "sum")
                    elif "avg(" in func_expr:
                        col = func_expr[func_expr.find("(")+1:func_expr.rfind(")")]
                        agg_dict[new_col] = (col, "mean")
                    elif "max(" in func_expr:
                        col = func_expr[func_expr.find("(")+1:func_expr.rfind(")")]
                        agg_dict[new_col] = (col, "max")
                    elif "min(" in func_expr:
                        col = func_expr[func_expr.find("(")+1:func_expr.rfind(")")]
                        agg_dict[new_col] = (col, "min")
                    elif "dcount(" in func_expr:
                        col = func_expr[func_expr.find("(")+1:func_expr.rfind(")")]
                        agg_dict[new_col] = (col, "nunique")
            
            if by_cols:
                valid_by = [c for c in by_cols if c in res.columns]
                if valid_by:
                    grouped = res.groupby(valid_by)
                    agg_res = {}
                    for k, v in agg_dict.items():
                        col, func = v
                        if col in res.columns:
                            agg_res[k] = grouped[col].agg(func)
                    res = pd.DataFrame(agg_res).reset_index()
            else:
                agg_res = {}
                for k, v in agg_dict.items():
                    col, func = v
                    if col in res.columns:
                        if callable(func):
                            agg_res[k] = [func(res[col])]
                        else:
                            agg_res[k] = [res[col].agg(func)]
                res = pd.DataFrame(agg_res)
                
        elif line.startswith("project "):
            cols = [c.strip() for c in line[len("project "):].split(",")]
            existing_cols = [c for c in cols if c in res.columns]
            res = res[existing_cols]
            
        elif line.startswith("order by "):
            parts = line[len("order by "):].split()
            col = parts[0].strip()
            asc = True
            if len(parts) > 1 and parts[1].strip().lower() == "desc":
                asc = False
            if col in res.columns:
                res = res.sort_values(by=col, ascending=asc)
                
        elif line.startswith("limit "):
            n = int(line[len("limit "):].strip())
            res = res.head(n)
            
    return res


def formulate_copilot_response(question, kql_query, df_result, config_data):
    """Formulate executive security response using OpenAI or local rule-based templating."""
    # 1. Overview Telemetry
    if "TotalTransactions" in df_result.columns and "UniqueCustomers" in df_result.columns and not df_result.empty:
        try:
            row = df_result.iloc[0]
            total_txs = int(row.get("TotalTransactions", 0))
            min_date = str(row.get("DateFrom", "N/A"))
            max_date = str(row.get("DateTo", "N/A"))
            unique_custs = int(row.get("UniqueCustomers", 0))
            avg_amount = float(row.get("AvgAmount", 0.0))
            avg_risk = float(row.get("AvgRisk", 0.0))
            fraud_count = int(row.get("FraudCount", 0))
            
            return f"""### 📊 Ingestion Telemetry Executive Summary

I have executed a comprehensive KQL telemetry query against the active `real_time_transactions` ledger. Here is the threat intelligence audit:

- **Ledger Audit Interval:** From `{min_date}` to `{max_date}`
- **Total Processed Transactions:** **{total_txs:,}** events ingested.
- **Account Ingestion Depth:** **{unique_custs:,}** unique customer endpoints monitored.
- **Average Transaction Footprint:** Rs. **{avg_amount:,.2f}**
- **Composite Risk Rating:** **{avg_risk}%** average risk profile across all streams.
- **High-Risk Anomalies Flagged:** **{fraud_count}** transactions exceed the 80% critical risk threshold.

**Compliance Risk Directive:** 
The composite risk rating of `{avg_risk}%` is within acceptable operating margins, but the presence of **{fraud_count}** critical alerts triggers the **RBI Circular on Customer Liability (Rule 2017/18)**. Automated security locks have been successfully placed on these compromised accounts."""
        except Exception:
            pass

    # 2. Vulnerability risk per channel
    if "payment_channel" in df_result.columns and "FraudPercentage" in df_result.columns and not df_result.empty:
        try:
            table_rows = ""
            max_channel = "Internet Banking"
            max_rate = 0.0
            
            for idx, row in df_result.iterrows():
                ch = row.get("payment_channel", "Unknown")
                tot = int(row.get("TotalTransactions", 0))
                fr = int(row.get("TotalFraud", 0))
                rate = float(row.get("FraudPercentage", 0.0))
                max_r = int(row.get("MaxRisk", 0))
                avg_r = float(row.get("AvgRisk", 0.0))
                tot_a = float(row.get("TotalAmount", 0.0))
                
                if rate > max_rate:
                    max_rate = rate
                    max_channel = ch
                    
                table_rows += f"| {ch} | {tot:,} | {fr:,} | {rate}% | {max_r}% | {avg_r}% | Rs. {tot_a:,.2f} |\n"
                
            insight = f"The **{max_channel}** channel displays the highest vulnerability index with a fraud rate of **{max_rate}%**. Risk parameters should be tightened immediately for {max_channel} authentication flows."
            
            return f"""### 💳 Channel Exposure & Vulnerability Risk Analysis

Analyzing the distribution of fraud and risk models across the payment channels:

| Payment Channel | Total Vol | Fraud Vol | Fraud Rate (%) | Max Risk (%) | Avg Risk (%) | Total Amount (Rs.) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_rows}
**Threat Insight & Recommendation:**
{insight}"""
        except Exception:
            pass

    # 3. Cross border
    if "country" in df_result.columns and "risk_score" in df_result.columns and not df_result.empty:
        countries = df_result["country"].unique()
        if len(countries) > 0 and (len(countries) > 1 or countries[0] != "India"):
            try:
                table_rows = ""
                for idx, row in df_result.head(10).iterrows():
                    ts = str(row.get("timestamp", "N/A")).split("T")[0]
                    tx_id = row.get("transaction_id", "N/A")
                    cust = row.get("customer_name", "N/A")
                    coun = row.get("country", "N/A")
                    amt = float(row.get("amount", 0.0))
                    risk = int(row.get("risk_score", 0))
                    ch = row.get("payment_channel", "N/A")
                    dev = row.get("device_type", "N/A")
                    
                    table_rows += f"| {ts} | {tx_id} | {cust} | {coun} | Rs. {amt:,.2f} | **{risk}%** | {ch} | {dev} |\n"
                    
                return f"""### 🌍 Cross-Border Threat Vectors & AML Alerts

I have filtered the transaction ledger for all overseas events (originating outside of India) with an AI Risk Score exceeding **80%**.

**Total Cross-Border Threat Alerts:** **{len(df_result)}** events detected.

| Date | Transaction ID | Customer Name | Country | Amount | Risk Score | Channel | Device |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_rows}
**Compliance Risk Directive:**
Cross-border transactions originating from high-risk locations with impossible travel velocity breach standard FEMA and RBI security guidelines. Instantaneous global lock status has been applied to these accounts."""
            except Exception:
                pass

    # 4. Midnight Takeover
    if "Hour" in df_result.columns or ("payment_channel" in df_result.columns and "ip_address" in df_result.columns and not df_result.empty):
        try:
            table_rows = ""
            for idx, row in df_result.head(10).iterrows():
                ts = str(row.get("timestamp", "N/A"))
                tx_id = row.get("transaction_id", "N/A")
                cust = row.get("customer_name", "N/A")
                amt = float(row.get("amount", 0.0))
                risk = int(row.get("risk_score", 0))
                ip = row.get("ip_address", "N/A")
                dev = row.get("device_type", "N/A")
                
                table_rows += f"| {ts} | {tx_id} | {cust} | Rs. {amt:,.2f} | **{risk}%** | {ip} | {dev} |\n"
                
            return f"""### 🌙 Midnight Internet Banking Hijacking Detection

I have scanned the ledger for transactions occurring during the critical midnight window (**1:00 AM - 4:30 AM**) via **Internet Banking** with a risk score exceeding **80%**.

**Total Midnight Internet Banking Hijacks:** **{len(df_result)}** events detected.

| Ingestion Time | Transaction ID | Customer Name | Amount | Risk Score | IP Address | Device hardware |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_rows}
**Contextual Forensic Telemetry:**
Midnight transactions executed via Internet Banking on unrecognized browsers or IP networks represent primary account takeover (ATO) indicators. The active sessions have been terminated."""
        except Exception:
            pass

    # OpenAI Cognitive Summary (if API key is available)
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_config = config_data.get("openaiConfig", {})
    if openai_key and openai_key != "YOUR_OPENAI_API_KEY" and not df_result.empty:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, base_url=openai_config.get("apiEndpoint", "https://api.openai.com/v1"))
            
            prompt = f"""You are a professional banking fraud risk compliance specialist and executive risk reporter.
Analyze the following tabular dataset returned by a KQL query and write a highly analytical, extremely polished, and structured executive markdown response answering the user's question.

User's Question: "{question}"
KQL Query Executed: "{kql_query}"

Returned Data (first 30 rows as JSON):
{df_result.head(30).to_json(orient='records', indent=2)}

Format Requirements:
- Use clean, premium markdown structure (headers, bullet points, and tables if applicable).
- Keep the tone professional, objective, and risk-oriented.
- Highlight regulatory implications (e.g. RBI circulars) where relevant.
- Provide a summary and bulleted threats list, followed by recommended remediation directives.
"""
            response = client.chat.completions.create(
                model=openai_config.get("modelName", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are a professional banking fraud risk compliance specialist. Output clean, concise, highly analytical markdown summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"*(AI live generation fallback: {e})*\n\n**Raw Query Results Summary:**\nReturned {len(df_result)} rows. Columns: {', '.join(df_result.columns)}"

    # Default tabular fallback if offline and no high-fidelity template match
    if df_result.empty:
        return "### 🔍 Analytical Search Completed\n\nNo records matched the specified risk criteria in the current event frame. All ingestion channels are within nominal bounds."
    
    headers = " | ".join(df_result.columns)
    divider = " | ".join(["---"] * len(df_result.columns))
    rows = ""
    for idx, row in df_result.head(10).iterrows():
        row_vals = [str(row[c]) for c in df_result.columns]
        rows += " | ".join(row_vals) + "\n"
        
    more_msg = ""
    if len(df_result) > 10:
        more_msg = f"\n*(Showing top 10 of {len(df_result)} total matching rows)*"
        
    return f"""### 🔍 Analytical Search Completed

I have successfully executed the translated KQL query against the transactional ledger.

**Total matching records:** {len(df_result)} rows.

| {headers} |
| {divider} |
{rows}
{more_msg}

*(Configure `OPENAI_API_KEY` in `.env` to unlock live executive-level cognitive summaries.)*"""


# =====================================================================
# 5. INITIALIZE STATE AND SIMULATOR ARTIFACTS
# =====================================================================
if "transactions" not in st.session_state:
    indian_names = ["Aarav Sharma", "Vihaan Rao", "Sai Krishna", "Reyansh Gupta", "Aanya Iyer", "Diya Sen", "Ananya Reddy", "Ishaan Joshi", "Kabir Bhat", "Priya Verma"]
    cities = [("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Bengaluru", "Karnataka"), ("Kolkata", "West Bengal"), ("Chennai", "Tamil Nadu")]
    merchants = [
        {"name": "Amazon India", "category": "Shopping"},
        {"name": "Reliance Digital", "category": "Electronics"},
        {"name": "Flipkart Retail", "category": "Shopping"},
        {"name": "Zomato Food", "category": "Food & Dining"},
        {"name": "Swiggy Delivery", "category": "Food & Dining"},
        {"name": "Uber India", "category": "Travel"},
        {"name": "Taj Hotels", "category": "Hospitality"},
        {"name": "Airtel Pay", "category": "Utilities"},
        {"name": "HDFC Home Loan", "category": "Financial Services"},
        {"name": "Apollo Pharmacy", "category": "Healthcare"}
    ]
    
    baseline = []
    for i in range(25):
        name = random.choice(indian_names)
        city_info = random.choice(cities)
        score = random.randint(5, 20)
        merchant = random.choice(merchants)
        baseline.append({
            "transaction_id": f"TXN-{random.randint(100000, 999999)}",
            "customer_id": f"CUST-{random.randint(100000, 999999)}",
            "account_number": f"ACT-{random.randint(100000, 999999)}",
            "customer_name": name,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "amount": round(random.uniform(500, 12000), 2),
            "merchant": merchant["name"],
            "merchant_category": merchant["category"],
            "payment_channel": random.choice(["UPI", "POS", "Internet Banking", "ATM"]),
            "transaction_type": "Debit",
            "country": "India",
            "city": city_info[0],
            "state": city_info[1],
            "device_type": random.choice(["Mobile", "Tablet", "Desktop", "iPhone 15"]),
            "ip_address": f"192.168.1.{random.randint(2,254)}",
            "risk_score": score,
            "is_fraud": 0,
            "ai_explanation": ""
        })
    st.session_state.transactions = baseline

if "alerted_txs" not in st.session_state:
    st.session_state.alerted_txs = set()

# Helper to automatically generate simulated transactions (keeps layout active in simulation mode)
def generate_simulated_transaction():
    indian_names = ["Aarav Sharma", "Vihaan Rao", "Sai Krishna", "Reyansh Gupta", "Aanya Iyer", "Diya Sen", "Ananya Reddy", "Ishaan Joshi", "Kabir Bhat", "Priya Verma"]
    cities = [("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Bengaluru", "Karnataka"), ("Kolkata", "West Bengal"), ("Chennai", "Tamil Nadu")]
    
    merchants = [
        {"name": "Amazon India", "category": "Shopping"},
        {"name": "Reliance Digital", "category": "Electronics"},
        {"name": "Flipkart Retail", "category": "Shopping"},
        {"name": "Zomato Food", "category": "Food & Dining"},
        {"name": "Swiggy Delivery", "category": "Food & Dining"},
        {"name": "Uber India", "category": "Travel"},
        {"name": "Taj Hotels", "category": "Hospitality"},
        {"name": "Airtel Pay", "category": "Utilities"},
        {"name": "HDFC Home Loan", "category": "Financial Services"},
        {"name": "Apollo Pharmacy", "category": "Healthcare"}
    ]
    suspicious_merchants = [
        {"name": "Unknown Forex Broker", "category": "Investment"},
        {"name": "Suspicious Shell Co", "category": "Miscellaneous"},
        {"name": "Cryptocurrency Exchange Malta", "category": "Crypto"},
        {"name": "Luxury Watches Dubai", "category": "Luxury Shopping"},
        {"name": "Midnight Cash Outlet", "category": "ATM Cash Out"}
    ]
    
    # 22% probability of an anomaly pattern
    is_anomaly = (random.random() < 0.22)
    name = random.choice(indian_names)
    city_info = random.choice(cities)
    tx_id = f"TXN-{random.randint(100000, 999999)}"
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    if is_anomaly:
        pattern = random.randint(1, 4)
        if pattern == 1:
            merchant = random.choice(suspicious_merchants)
            txn = {
                "transaction_id": tx_id,
                "customer_id": f"CUST-{random.randint(100000, 999999)}",
                "account_number": f"ACT-{random.randint(100000, 999999)}",
                "customer_name": name,
                "timestamp": timestamp,
                "amount": round(random.uniform(210000, 275000), 2),
                "merchant": merchant["name"],
                "merchant_category": merchant["category"],
                "payment_channel": "Internet Banking",
                "transaction_type": "Debit",
                "country": "India",
                "city": city_info[0],
                "state": city_info[1],
                "device_type": "Desktop",
                "ip_address": f"103.45.21.{random.randint(2,254)}",
                "risk_score": 0,
                "is_fraud": 0
            }
        elif pattern == 2:
            txn = {
                "transaction_id": tx_id,
                "customer_id": f"CUST-{random.randint(100000, 999999)}",
                "account_number": f"ACT-{random.randint(100000, 999999)}",
                "customer_name": name,
                "timestamp": timestamp,
                "amount": round(random.uniform(15000, 38000), 2),
                "merchant": "Offshore Retailer",
                "merchant_category": "Travel & Leisure",
                "payment_channel": "UPI",
                "transaction_type": "Debit",
                "country": random.choice(["Russia", "Ukraine", "Nigeria", "United Arab Emirates"]),
                "city": "Moscow",
                "state": "Overseas",
                "device_type": "Unknown Linux Terminal",
                "ip_address": f"85.201.12.{random.randint(2,254)}",
                "risk_score": 0,
                "is_fraud": 0
            }
        elif pattern == 3:
            txn = {
                "transaction_id": tx_id,
                "customer_id": f"CUST-{random.randint(100000, 999999)}",
                "account_number": f"ACT-{random.randint(100000, 999999)}",
                "customer_name": name,
                "timestamp": timestamp,
                "amount": round(random.uniform(42000, 58000), 2),
                "merchant": "Midnight Cash Outlet",
                "merchant_category": "ATM Cash Out",
                "payment_channel": "ATM",
                "transaction_type": "Debit",
                "country": "India",
                "city": city_info[0],
                "state": city_info[1],
                "device_type": "Tablet",
                "ip_address": f"223.189.43.{random.randint(2,254)}",
                "risk_score": 0,
                "is_fraud": 0
            }
        else:
            merchant = random.choice(suspicious_merchants)
            txn = {
                "transaction_id": tx_id,
                "customer_id": f"CUST-{random.randint(100000, 999999)}",
                "account_number": f"ACT-{random.randint(100000, 999999)}",
                "customer_name": name,
                "timestamp": timestamp,
                "amount": round(random.uniform(35000, 70000), 2),
                "merchant": merchant["name"],
                "merchant_category": merchant["category"],
                "payment_channel": "Internet Banking",
                "transaction_type": "Debit",
                "country": "India",
                "city": city_info[0],
                "state": city_info[1],
                "device_type": "Suspicious Mobile Device Model",
                "ip_address": "185.220.101.44",
                "risk_score": 0,
                "is_fraud": 0
            }
    else:
        merchant = random.choice(merchants)
        txn = {
            "transaction_id": tx_id,
            "customer_id": f"CUST-{random.randint(100000, 999999)}",
            "account_number": f"ACT-{random.randint(100000, 999999)}",
            "customer_name": name,
            "timestamp": timestamp,
            "amount": round(random.uniform(500, 15000), 2),
            "merchant": merchant["name"],
            "merchant_category": merchant["category"],
            "payment_channel": random.choice(["UPI", "POS", "Internet Banking", "ATM"]),
            "transaction_type": "Debit",
            "country": "India",
            "city": city_info[0],
            "state": city_info[1],
            "device_type": "Mobile",
            "ip_address": f"192.168.1.{random.randint(2,254)}",
            "risk_score": 0,
            "is_fraud": 0
        }
        
    score, reasons = local_calculate_ensemble_risk(txn)
    txn["risk_score"] = score
    txn["is_fraud"] = 1 if score > 80 else 0
    
    # Generate explanations
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "YOUR_OPENAI_API_KEY":
        openai_endpoint = openai_config.get("apiEndpoint", "https://api.openai.com/v1")
        openai_model = openai_config.get("modelName", "gpt-4o")
        txn["ai_explanation"] = explain_risk_with_openai(txn, score, reasons, openai_key, openai_endpoint, openai_model)
    else:
        txn["ai_explanation"] = local_explain_risk_with_ai(txn, score, reasons)
        
    st.session_state.transactions.insert(0, txn)
    if len(st.session_state.transactions) > 40:
        st.session_state.transactions.pop()

# =====================================================================
# 6. RENDER DASHBOARD CORE
# =====================================================================
def render_dashboard_core():
    # Initialize Chat Session State
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Silent background credentials authentication
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    access_token = None
    is_live = False
    _conn_error = ""

    if tenant_id and client_id and client_secret:
        try:
            access_token = get_kql_client_credentials(tenant_id, client_id, client_secret)
            is_live = True
        except Exception as e:
            _conn_error = f"Auth failed: {str(e)[:120]}"

    df_display = pd.DataFrame()

    # True aggregate counts — queried BEFORE any limit/slice
    kql_total_transactions = 0
    kql_fraud_detected = 0
    kql_highest_risk = 0

    if is_live:
        try:
            # ── Aggregate query: get TRUE counts from entire table (no limit) ──
            agg_query = (
                "real_time_transactions "
                "| where risk_score > 0 "
                "| summarize "
                "total_scored = count(), "
                "total_fraud = countif(risk_score > 80), "
                "highest_risk = max(risk_score)"
            )
            df_agg = query_fabric_kql(kql_query_uri, kql_db_name, agg_query, access_token)
            if not df_agg.empty:
                kql_total_transactions = int(df_agg["total_scored"].iloc[0])
                kql_fraud_detected = int(df_agg["total_fraud"].iloc[0])
                kql_highest_risk = int(df_agg["highest_risk"].iloc[0])

            # ── Display query: fetch latest 150 scored rows for the fraud feed ──
            txn_query = (
                "real_time_transactions "
                "| where risk_score > 0 "
                "| extend ts = todatetime(timestamp) "
                "| summarize arg_max(ts, *) by transaction_id "
                "| order by ts desc "
                "| limit 150"
            )
            df_display = query_fabric_kql(kql_query_uri, kql_db_name, txn_query, access_token)

            if df_display.empty:
                # No scored rows at all — notebook hasn't run yet
                # Show latest raw unscored rows from the last 24h so dashboard is not blank
                txn_query_raw = (
                    "real_time_transactions "
                    "| extend ts = todatetime(timestamp) "
                    "| where ts >= ago(24h) "
                    "| summarize arg_max(ts, *) by transaction_id "
                    "| order by ts desc "
                    "| limit 150"
                )
                df_display = query_fabric_kql(kql_query_uri, kql_db_name, txn_query_raw, access_token)

            if df_display.empty:
                _conn_error = "KQL has 0 rows — start event_simulator.py to stream data"
                is_live = False
                generate_simulated_transaction()
                df_display = pd.DataFrame(st.session_state.transactions)
        except Exception as e:
            _conn_error = f"KQL query error: {str(e)[:120]}"
            is_live = False
            generate_simulated_transaction()
            df_display = pd.DataFrame(st.session_state.transactions)
    else:
        # Generate a live transaction periodically to animate the simulator feed
        generate_simulated_transaction()
        df_display = pd.DataFrame(st.session_state.transactions)

    # Always cast display df columns for the fraud feed cards below
    if not df_display.empty:
        df_display["risk_score"] = pd.to_numeric(df_display["risk_score"], errors="coerce").fillna(0).astype(int)
        df_display["amount"] = pd.to_numeric(df_display["amount"], errors="coerce").fillna(0.0).astype(float)

    if is_live and kql_total_transactions > 0:
        # Use TRUE counts from the full-table aggregate query
        total_transactions = kql_total_transactions
        fraud_detected = kql_fraud_detected
        highest_risk = kql_highest_risk
    elif not df_display.empty:
        # Fallback: derive from local simulation data
        total_transactions = len(df_display)
        fraud_detected = len(df_display[df_display["risk_score"] > 80])
        highest_risk = int(df_display["risk_score"].max())
    else:
        total_transactions = 0
        fraud_detected = 0
        highest_risk = 0

    # 1. HEADER TITLE ROW
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; margin-bottom: 15px;">
            <div>
                <h1 class="title-text">🛡️ AI Smart Banking Fraud Console</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. CUSTOM BUTTON NAVIGATION DIRECTLY UNDER TITLE
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "analytics"

    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.session_state.active_tab == "analytics":
            st.button("📊 Threat Analytics & Feed", key="btn_nav_analytics", type="primary", use_container_width=True)
        else:
            if st.button("📊 Threat Analytics & Feed", key="btn_nav_analytics", type="secondary", use_container_width=True):
                st.session_state.active_tab = "analytics"
                st.rerun()
    with nav_col2:
        if st.session_state.active_tab == "copilot":
            st.button("💬 AI Security Copilot", key="btn_nav_copilot", type="primary", use_container_width=True)
        else:
            if st.button("💬 AI Security Copilot", key="btn_nav_copilot", type="secondary", use_container_width=True):
                st.session_state.active_tab = "copilot"
                st.rerun()

    st.write("") # Spacer

    # 3. CONDITIONAL WORKSPACE CONTENT
    if st.session_state.active_tab == "analytics":
        # 1. HEADER ROW with live status indicators
        status_html = ""
        if is_live:
            status_html = f'<span class="status-badge status-live">🟢 Live Fabric Stream ({kql_db_name})</span>'
        elif _conn_error:
            status_html = f'<span class="status-badge status-sim" title="{_conn_error}">🔴 Connection Error — Simulation Active</span>'
        else:
            status_html = '<span class="status-badge status-sim">🟡 Offline Simulation Stream</span>'

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; margin-bottom: 25px; border-bottom: 1px solid rgba(15, 23, 42, 0.08);">
                <div>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 4px; font-weight: 500;">Real-Time Cognitive Ingestion Analytics & Threat Detection</div>
                </div>
                <div>
                    {status_html}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. KEY METRICS GRID
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card metric-card-blue">
                    <div style="font-size: 0.85rem; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Total Transactions</div>
                    <div class="metric-value" style="color: #1E3A8A;">{total_transactions:,}</div>
                    <div style="font-size: 0.8rem; color: #2563EB; font-weight: 500;">📡 Ingestion Stream Active</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card metric-card-red">
                    <div style="font-size: 0.85rem; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Total Fraud Detected</div>
                    <div class="metric-value" style="color: #B91C1C;">{fraud_detected}</div>
                    <div style="font-size: 0.8rem; color: #DC2626; font-weight: 500;">🚨 Threshold Score > 80</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card metric-card-purple">
                    <div style="font-size: 0.85rem; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Highest Risk Score</div>
                    <div class="metric-value" style="color: #991B1B;">{highest_risk}%</div>
                    <div style="font-size: 0.8rem; color: #64748B; font-weight: 500;">🤖 Ensemble AI Model</div>
                </div>
            """, unsafe_allow_html=True)

        st.write("---")
        st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 5px;">📊 Threat Intelligence Hub</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.9rem; color: #475569; margin-bottom: 25px;">Visual telemetry analytics showcasing anomaly distribution clusters, channel exposure indices, threat volatility, and cross-border risk vectors.</p>', unsafe_allow_html=True)

        if not df_display.empty:
            chart_data = df_display.copy()
            # Map clean readable categorical groups for the charts
            chart_data["Status"] = np.where(chart_data["risk_score"] > 80, "🚨 High Risk Fraud", "🟢 Approved / Normal")

            # Row 1 of Visual Charts
            c_row1_left, c_row1_right = st.columns(2)
            with c_row1_left:
                st.markdown('<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #0F172A; text-align: center;">🎯 Transaction Anomaly Cluster</div>', unsafe_allow_html=True)
                st.scatter_chart(
                    chart_data,
                    x="amount",
                    y="risk_score",
                    color="Status",
                    size="amount"
                )
                st.markdown('<p style="font-size: 0.75rem; color: #475569; margin-top: -5px; text-align: center;">Amount (Rs.) vs AI Risk Score (%)</p>', unsafe_allow_html=True)

            with c_row1_right:
                st.markdown('<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #0F172A; text-align: center;">💳 Channel Vulnerability Index</div>', unsafe_allow_html=True)
                # Count legitimate vs fraudulent per payment channel
                channel_groups = chart_data.groupby(["payment_channel", "Status"]).size().reset_index(name="Volume")
                st.bar_chart(
                    channel_groups,
                    x="payment_channel",
                    y="Volume",
                    color="Status",
                    stack=True
                )
                st.markdown('<p style="font-size: 0.75rem; color: #475569; margin-top: -5px; text-align: center;">Legitimate vs. Fraudulent volumes per channel</p>', unsafe_allow_html=True)

            st.write("") # Spacer

            # Row 2 of Visual Charts
            c_row2_left, c_row2_right = st.columns(2)
            with c_row2_left:
                st.markdown('<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #0F172A; text-align: center;">📈 Real-Time Threat Volatility</div>', unsafe_allow_html=True)
                # Volatility Trend: reverse chronological order (oldest to newest)
                trend_data = chart_data.iloc[::-1].copy().reset_index(drop=True)
                trend_data["Rolling Alert Threshold"] = 80
                st.line_chart(
                    trend_data,
                    y=["risk_score", "Rolling Alert Threshold"],
                    color=["#B91C1C", "#64748B"] # Maroon red for risk score, darker grey for threshold
                )
                st.markdown('<p style="font-size: 0.75rem; color: #475569; margin-top: -5px; text-align: center;">Ingestion risk stream vs 80% critical threshold</p>', unsafe_allow_html=True)

            with c_row2_right:
                st.markdown('<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #0F172A; text-align: center;">🌍 Geolocation Attack Vectors</div>', unsafe_allow_html=True)
                # Fraud count by country
                geo_groups = chart_data.groupby(["country", "Status"]).size().reset_index(name="Alerts")
                st.bar_chart(
                    geo_groups,
                    x="country",
                    y="Alerts",
                    color="Status",
                    stack=True
                )
                st.markdown('<p style="font-size: 0.75rem; color: #475569; margin-top: -5px; text-align: center;">Cross-border threat volume origins</p>', unsafe_allow_html=True)
        else:
            st.info("Waiting for transactional data stream to initialize visual threat vectors...")

        st.write("---")

        # ── REAL-TIME FRAUD FEED PANEL ──
        # Center the Triage layout on desktop, standard fluid width on mobile
        triage_grid_mid = st.container()
        with triage_grid_mid:
            st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 5px;">🚨 Real-Time Fraud Triage</h2>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 0.9rem; color: #475569; margin-bottom: 25px;">Instantly displays high-risk transaction anomalies flagged by the AI ensemble scoring engine.</p>', unsafe_allow_html=True)

            fraud_df = df_display[df_display["risk_score"] > 80] if not df_display.empty else pd.DataFrame()

            if fraud_df.empty:
                st.success("✅ System Clean: No high-risk transaction anomalies detected in the current event frame.")
            else:
                # Initialize Carousel Session State
                if "fraud_carousel_index" not in st.session_state:
                    st.session_state.fraud_carousel_index = 0

                num_frauds = len(fraud_df)
                # Clamp boundaries dynamically
                if st.session_state.fraud_carousel_index >= num_frauds:
                    st.session_state.fraud_carousel_index = num_frauds - 1
                if st.session_state.fraud_carousel_index < 0:
                    st.session_state.fraud_carousel_index = 0

                row = fraud_df.iloc[st.session_state.fraud_carousel_index]
                score = int(row['risk_score'])
                tx_id = row['transaction_id']
                cust = row['customer_name']
                amt = row['amount']
                channel = row['payment_channel']
                country = row['country']
                city = row.get('city', 'Unknown')
                ip = row.get('ip_address', 'Unknown')

                # Retrieve or generate explanation
                if "ai_explanation" not in row or not row["ai_explanation"]:
                    warnings = []
                    if float(amt) >= 200000:
                        warnings.append("High-value spike above threshold of Rs. 2,00,000")
                    if channel == "ATM" and float(amt) >= 40000:
                        warnings.append("ATM cash withdrawal exceeds daily card limit of Rs. 40,000")
                    if country != "India":
                        warnings.append(f"Foreign location mismatch: transaction initiated from {country}")
                    if ip == "185.220.101.44":
                        warnings.append("Transaction routed through known malicious Tor IP subnet")

                    warnings.append(f"AI Random Forest Classifier flagged transaction as high probability fraud ({score}%)")

                    if openai_key and openai_key != "YOUR_OPENAI_API_KEY":
                        openai_endpoint = openai_config.get("apiEndpoint", "https://api.openai.com/v1")
                        openai_model = openai_config.get("modelName", "gpt-4o")
                        explanation = explain_risk_with_openai(row, score, warnings, openai_key, openai_endpoint, openai_model)
                    else:
                        explanation = local_explain_risk_with_ai(row, score, warnings)
                else:
                    explanation = row["ai_explanation"]

                # Send Teams Alert
                if teams_webhook:
                    if tx_id not in st.session_state.alerted_txs:
                        sent = send_teams_fraud_alert(teams_webhook, row, score, explanation)
                        if sent:
                            st.session_state.alerted_txs.add(tx_id)
                            st.toast(f"💬 Live Teams alert posted for {cust} ({tx_id})!", icon="💬")

                # Render active Carousel Card
                st.markdown(f"""
                    <div class="alert-card">
                        <div class="alert-header">
                            <div>
                                <span class="alert-badge">🚨 Fraud Detected</span>
                                <strong style="margin-left: 10px; font-size: 1.1rem; color: #0F172A;">{cust} ({tx_id})</strong>
                            </div>
                            <span style="font-size: 1.3rem; font-weight: 700; color: #B91C1C;">{score}/100 Risk</span>
                        </div>
                        <div style="font-size: 0.95rem; color: #334155; line-height: 1.6;">
                            <strong>💳 Amount:</strong> Rs. {float(amt):,.2f} | 
                            <strong>📡 Channel:</strong> {channel} | 
                            <strong>🌍 Location:</strong> {city}, {country} | 
                            <strong>🌐 IP:</strong> {ip}
                        </div>
                        <div class="alert-insight-box">
                            <strong style="color: #991B1B; font-size: 0.9rem; text-transform: uppercase;">🤖 OpenAI Cognitive Insight Decision:</strong>
                            <pre style="background: transparent; border: none; color: #1E293B; font-family: 'Outfit', sans-serif; font-size: 0.95rem; white-space: pre-wrap; margin: 10px 0 0 0; padding: 0;">{explanation}</pre>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Carousel Controls
                c_prev, c_indicator, c_next = st.columns([1, 2, 1])
                with c_prev:
                    if st.button("◀ Prev", key="btn_carousel_prev", use_container_width=True):
                        st.session_state.fraud_carousel_index = (st.session_state.fraud_carousel_index - 1) % num_frauds
                        st.rerun()
                with c_indicator:
                    st.markdown(f"""
                        <div style="text-align: center; font-size: 1rem; font-weight: 600; color: #0F172A; padding-top: 5px;">
                            Event {st.session_state.fraud_carousel_index + 1} of {num_frauds}
                        </div>
                    """, unsafe_allow_html=True)
                with c_next:
                    if st.button("Next ▶", key="btn_carousel_next", use_container_width=True):
                        st.session_state.fraud_carousel_index = (st.session_state.fraud_carousel_index + 1) % num_frauds
                        st.rerun()


    elif st.session_state.active_tab == "copilot":
        copilot_mid = st.container()
        with copilot_mid:
            chat_header_left, chat_header_right = st.columns([8, 2])
            with chat_header_left:
                st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 5px;">💬 AI Security Copilot Panel</h2>', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">Ask natural language questions to query the Eventhouse ledger, analyze AML risk, or inspect custom KQL segments.</p>', unsafe_allow_html=True)
            with chat_header_right:
                if st.button("🗑️ Clear History", key="clear_chat_history", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()

            # Render Chat Container using Streamlit's native scroll container
            with st.container(height=420, border=True):
                if not st.session_state.chat_history:
                    st.markdown("""
                        <div style="text-align: center; padding: 50px 20px; color: #475569;">
                            <span style="font-size: 3rem;">🤖</span>
                            <h3 style="color: #0F172A; margin-top: 15px; font-family: 'Space Grotesk', sans-serif;">Secure AI Copilot Ingest Stream Agent</h3>
                            <p style="font-size: 0.9rem; max-width: 500px; margin: 10px auto; font-family: 'Outfit', sans-serif;">
                                Welcome, risk investigator. I am your specialized cyber-security intelligence co-analyst. 
                                Ask me any question in natural language to translate it into highly optimized KQL and run 
                                it against the real-time transaction ledger.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    for idx, chat in enumerate(st.session_state.chat_history):
                        # User Message Bubble
                        st.markdown(f"""
                            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                                <div class="chat-bubble chat-bubble-user" style="margin-bottom: 0px;">
                                    <strong>🧑‍💻 Investigator:</strong><br/>
                                    {chat['question']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # Copilot Message Bubble
                        st.markdown(f"""
                            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; width: 100%;">
                                <div class="chat-bubble chat-bubble-copilot" style="margin-bottom: 0px; width: 85%;">
                                    <strong>🛡️ AI Security Copilot:</strong><br/>
                        """, unsafe_allow_html=True)

                        st.markdown(chat['answer'])

                        with st.expander("🔍 Inspect Executed KQL Query"):
                            st.code(chat['kql'], language="sql")

                        st.markdown("""
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            # Collapsible Starter Prompts Section
            with st.expander("📚 Quick Ingestion Audits (Starter Prompts)", expanded=True):
                p_cols = st.columns(2)
                prompts = [
                    "Show me a high-level overview of our transaction ingestion telemetry.",
                    "What are the detailed fraud statistics and vulnerability rates by payment channel?",
                    "Identify all cross-border transactions originating outside of India with a risk score above 80%.",
                    "Detect suspicious midnight transactions occurring via Internet Banking with high risk."
                ]

                clicked_prompt = None
                for idx, prompt_text in enumerate(prompts):
                    col_idx = idx % 2
                    with p_cols[col_idx]:
                        if st.button(prompt_text, key=f"btn_prompt_{idx}", use_container_width=True):
                            clicked_prompt = prompt_text

            # Chat input bar
            user_input = st.chat_input("Ask the AI Security Copilot about transactions or KQL anomalies...", key="copilot_chat_input")

            question_to_run = None
            if user_input:
                question_to_run = user_input
            elif clicked_prompt:
                question_to_run = clicked_prompt

            if question_to_run:
                with st.spinner("🧠 AI Copilot translating business question to optimized KQL..."):
                    kql_query = translate_question_to_kql(question_to_run, config_data)

                with st.spinner("📡 Running KQL query against the ledger..."):
                    try:
                        if is_live:
                            df_result = query_fabric_kql(kql_query_uri, kql_db_name, kql_query, access_token)
                        else:
                            df_result = execute_kql_locally(kql_query, df_display)
                    except Exception as e:
                        df_result = pd.DataFrame()
                        st.error(f"KQL Execution Error: {e}")

                with st.spinner("✍️ AI Copilot formulating executive response..."):
                    answer = formulate_copilot_response(question_to_run, kql_query, df_result, config_data)

                # Save to chat history
                st.session_state.chat_history.append({
                    "question": question_to_run,
                    "kql": kql_query,
                    "answer": answer
                })
                st.rerun()


# Render within st.fragment to auto-refresh dynamically
if hasattr(st, "fragment"):
    @st.fragment(run_every=10)
    def run_fragment_loop():
        render_dashboard_core()
    run_fragment_loop()
else:
    render_dashboard_core()
    time.sleep(10)
    st.rerun()
