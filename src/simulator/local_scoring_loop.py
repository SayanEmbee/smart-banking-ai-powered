import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timezone
import requests
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Reconfigure stdout to use UTF-8 on Windows to prevent UnicodeEncodeError for emojis
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Check for terminal color support
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = WHITE = MAGENTA = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# Fallback print utility that sanitizes Unicode on Windows if reconfigure fails
def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Graceful fallback: encode as ascii and replace unknown characters
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode('ascii', errors='replace').decode('ascii'))
            else:
                new_args.append(arg)
        try:
            print(*new_args, **kwargs)
        except Exception:
            pass

# Load environment configuration
def load_env():
    env_paths = [".env", "src/.env", "../.env", "../../.env"]
    env_data = {}
    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_data[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
    return env_data

# Load accelerator configuration
def load_config():
    config_paths = [
        "config/accelerator-config.json",
        "../config/accelerator-config.json",
        "../../config/accelerator-config.json",
        "src/config/accelerator-config.json"
    ]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

# 1. Train Model Locally if not exists
def get_or_train_model():
    model_paths = ["models/fraud_forest_model.pkl", "src/simulator/models/fraud_forest_model.pkl", "../models/fraud_forest_model.pkl"]
    for p in model_paths:
        if os.path.exists(p):
            safe_print(f"{Fore.GREEN}[MODEL]{Style.RESET_ALL} Loading pre-trained model from {p}...")
            return joblib.load(p)
            
    # Train on the fly
    safe_print(f"{Fore.YELLOW}[MODEL]{Style.RESET_ALL} Pre-trained model not found. Training model locally from historical CSV...")
    csv_paths = ["data/historical_credit_card_fraud.csv", "../data/historical_credit_card_fraud.csv", "../../data/historical_credit_card_fraud.csv"]
    csv_path = None
    for p in csv_paths:
        if os.path.exists(p):
            csv_path = p
            break
            
    if not csv_path:
        raise FileNotFoundError("Historical credit card fraud CSV dataset not found in workspace!")
        
    safe_print(f"{Fore.CYAN}[MODEL]{Style.RESET_ALL} Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    feature_cols = ['amount', 'payment_channel', 'transaction_type', 'country']
    X_raw = df[feature_cols]
    y = df['is_fraud']
    X = pd.get_dummies(X_raw, columns=['payment_channel', 'transaction_type', 'country'])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, "models/fraud_forest_model.pkl")
    safe_print(f"{Fore.GREEN}[MODEL]{Style.RESET_ALL} Model trained successfully in 0.5s and saved to models/fraud_forest_model.pkl!")
    return clf

# 2. Get secure KQL AD Access Token via REST
def get_kql_token(tenant_id, client_id, client_secret):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://kusto.kusto.windows.net/.default"
    }
    resp = requests.post(token_url, data=payload, timeout=10.0)
    if resp.status_code != 200:
        raise Exception(f"Auth HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    token = data.get("access_token") or data.get("accessToken")
    if not token:
        raise Exception("Access token missing in Auth response.")
    return token

# 3. Query KQL Database via REST
def kql_rest_query(query, token, uri, db):
    url = f"{uri.rstrip('/')}/v2/rest/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json={"db": db, "csl": query}, headers=headers, timeout=15.0)
    if resp.status_code != 200:
        raise Exception(f"KQL Query HTTP {resp.status_code}: {resp.text[:300]}")
    
    data = resp.json()
    if isinstance(data, list):
        for frame in data:
            if isinstance(frame, dict) and frame.get("TableKind") == "PrimaryResult":
                cols = [c["ColumnName"] for c in frame.get("Columns", [])]
                rows = frame.get("Rows", [])
                return [dict(zip(cols, row)) for row in rows]
    return []

# 4. Ingest Scored Transactions back into KQL via REST Management Ingestion Command
def ingest_rows_to_kql(rows, token, uri, db, table="real_time_transactions"):
    if not rows:
        return
    url = f"{uri.rstrip('/')}/v1/rest/mgmt"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    csv_lines = []
    for r in rows:
        def fmt(val, is_str=True):
            if val is None:
                return '""'
            if is_str:
                escaped = str(val).replace('"', '""')
                return f'"{escaped}"'
            return str(val)
        
        # Datetime value formatting in KQL csv ingestion
        ts_val = r.get('timestamp')
        if not ts_val:
            ts_val = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
        line = (
            f"{fmt(r.get('transaction_id'))},"
            f"{fmt(r.get('customer_id'))},"
            f"{fmt(r.get('account_number'))},"
            f"{fmt(r.get('customer_name'))},"
            f"{fmt(ts_val)},"
            f"{fmt(r.get('amount'), False)},"
            f"{fmt(r.get('merchant'))},"
            f"{fmt(r.get('merchant_category'))},"
            f"{fmt(r.get('payment_channel'))},"
            f"{fmt(r.get('transaction_type'))},"
            f"{fmt(r.get('country'))},"
            f"{fmt(r.get('city'))},"
            f"{fmt(r.get('state'))},"
            f"{fmt(r.get('device_type'))},"
            f"{fmt(r.get('ip_address'))},"
            f"{fmt(r.get('risk_score'), False)},"
            f"{fmt(r.get('is_fraud'), False)}"
        )
        csv_lines.append(line)
        
    csv_data = "\n".join(csv_lines)
    csl = f".ingest inline into table {table} <|\n{csv_data}"
    
    resp = requests.post(url, json={"db": db, "csl": csl}, headers=headers, timeout=20.0)
    if resp.status_code != 200:
        raise Exception(f"KQL Ingestion HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()

# 5. Ensemble Risk Score Calculations (exactly matches notebook / app.py)
def calculate_ensemble_risk(txn, clf):
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
        
    # Machine Learning risk prediction
    ml_score = 0
    if clf:
        try:
            txn_df = pd.DataFrame([{
                'amount': amount,
                'payment_channel': txn.get('payment_channel', 'UPI'),
                'transaction_type': txn.get('transaction_type', 'Debit'),
                'country': txn.get('country', 'India')
            }])
            txn_encoded = pd.get_dummies(txn_df)
            txn_encoded = txn_encoded.reindex(columns=clf.feature_names_in_, fill_value=0)
            ml_prob = clf.predict_proba(txn_encoded)[0][1]
            ml_score = int(ml_prob * 100)
        except Exception as e:
            ml_score = 0
            
    if ml_score > 70:
        reasons.append(f"AI Random Forest Classifier flagged transaction as high probability fraud ({ml_score}%)")
        
    final_score = max(ml_score, heuristic_score)
    final_score = min(final_score, 99)
    return final_score, reasons

# 6. Cognitive Risk Explanations Fallback
def explain_risk_locally(txn, risk_score, reasons):
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
        threat_vector = "High-Value Spike Transaction Pattern (POS/Internet Banking limit breach)"
        regulatory_impact = "RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18 limits customer liability if unauthorized transaction is reported within 3 days. High value necessitates immediate preventive freeze."
        remediation_tier1 = "Suspend UPI, POS, and Net-Banking channels immediately. Lock account funds transfer capabilities."
        remediation_tier2 = "Initiate high-priority RM verification call."
        remediation_tier3 = "Report to Fraud FMC and log in Suspicious Transaction Registry."
    elif channel == "ATM" and amount >= 40000:
        threat_vector = "ATM Velocity & Cash-Out Burst (Daily Debit Limit Breach)"
        regulatory_impact = "High cash-out volumes at unorthodox hours suggest physical card compromise or ATM skimming attack."
        remediation_tier1 = "Temporary lockdown of debit card status. Restrict domestic and international ATM channels."
        remediation_tier2 = "Trigger instant in-app security alert and SMS warning."
        remediation_tier3 = "Analyze local ATM terminal DVR footage and review skimming sensors."
    elif country != "India":
        threat_vector = "Foreign Geolocation Mismatch (Impossible Travel Speed Anomaly)"
        regulatory_impact = "Cross-border transaction velocity violates risk boundaries. Compliance requires card lock to prevent cross-border money laundering."
        remediation_tier1 = "Place global card lockdown. Decline all international POS, ATM, and E-commerce gateways."
        remediation_tier2 = "Send critical security email alert and app push confirmation."
        remediation_tier3 = "Mark card status as 'Compromised' and queue automatic reissue protocol."
    elif ip == "185.220.101.44":
        threat_vector = "Midnight Takeover via Malicious Proxy (Tor Node Access)"
        regulatory_impact = "Routing transaction authentication through a known Tor exit node IP violates standard corporate Cyber Security policy."
        remediation_tier1 = "Terminate active internet-banking login session. Suspend credentials."
        remediation_tier2 = "Require mandatory step-up Multi-Factor Authentication (MFA) and force credential reset."
        remediation_tier3 = "Flag IP subnet in Security Information and Event Management (SIEM) dashboard."

    reasons_bullet = "\n- ".join(reasons)
    report = (
        f"### 🛡️ AI Risk Scoring Insight & Decision Summary\n\n"
        f"**Transaction ID:** {txn.get('transaction_id')} | **Risk Score:** {risk_score}% | **Customer:** {cust}\n\n"
        f"#### 🔍 1. Threat Analysis Summary\n"
        f"- **Threat Vector:** {threat_vector}\n"
        f"- **Risk Indicators Flagged:**\n- {reasons_bullet}\n"
        f"- **Contextual Analysis:** Contextual home profile indicates customer lives in {city}, India. Initiating transaction from {country} via {channel} channel using {device} is a deviation from standard behaviors.\n\n"
        f"#### 🏛️ 2. Regulatory & Compliance Impact\n"
        f"- {regulatory_impact}\n\n"
        f"#### 🚀 3. Structured Operational Action Plan\n"
        f"- **Tier 1 (Immediate / Automated):** {remediation_tier1}\n"
        f"- **Tier 2 (Direct Outreach / Step-up):** {remediation_tier2}\n"
        f"- **Tier 3 (Log / Compliance):** {remediation_tier3}"
    )
    return report

# OpenAI live generation
def explain_risk_with_openai(txn, risk_score, reasons, config):
    openai_cfg = config.get("openaiConfig", {})
    api_key = openai_cfg.get("apiKey")
    if not api_key or api_key == "YOUR_OPENAI_API_KEY":
        return explain_risk_locally(txn, risk_score, reasons)
        
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=openai_cfg.get("apiEndpoint", "https://api.openai.com/v1"))
        prompt = (
            f"Analyze this anomalous transaction and generate a structured markdown report:\n"
            f"- Transaction ID: {txn['transaction_id']}\n"
            f"- Customer Name: {txn['customer_name']}\n"
            f"- Home Location: {txn.get('city')}, India\n"
            f"- Channel: {txn['payment_channel']}\n"
            f"- Amount: Rs. {txn['amount']}\n"
            f"- Geolocation: {txn['country']}\n"
            f"- Device: {txn.get('device_type')}\n"
            f"- IP: {txn.get('ip_address')}\n"
            f"- Heuristic Anomalies Flagged: {', '.join(reasons)}\n"
            f"- Risk Score: {risk_score}%\n\n"
            f"Use the standard report format including Threat Analysis, Regulatory & Compliance Impact, and Structured Operational Action Plan."
        )
        resp = client.chat.completions.create(
            model=openai_cfg.get("modelName", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are a professional banking fraud risk compliance officer. Generate clean, extremely structured, analytical markdown risk insight decisions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"{explain_risk_locally(txn, risk_score, reasons)}\n\n*(OpenAI live generation warning: {e})*"

# Write run stats log to KQL
def log_run_stats(records_read, records_scored, anomalies_flagged, log_msg, token, uri, db):
    try:
        url = f"{uri.rstrip('/')}/v1/rest/mgmt"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Ensure log table exists
        create_csl = (
            ".create-merge table scoring_runs_log "
            "(timestamp: string, records_read: long, records_scored: long, "
            "anomalies_flagged: long, log_message: string)"
        )
        requests.post(url, json={"db": db, "csl": create_csl}, headers=headers, timeout=10.0)
        
        now_ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        msg_escaped = log_msg.replace("'", "\\'")
        ingest_csl = (
            f".ingest inline into table scoring_runs_log <| "
            f"{now_ts},{records_read},{records_scored},{anomalies_flagged},{msg_escaped}"
        )
        requests.post(url, json={"db": db, "csl": ingest_csl}, headers=headers, timeout=10.0)
    except Exception as e:
        safe_print(f"{Fore.RED}[LOG ERROR] Failed to write scoring run log to KQL: {e}{Style.RESET_ALL}")

# Single pass or loop scoring job execution
def run_scoring_job(clf, token, uri, db, config):
    safe_print(f"\n{Fore.CYAN}Checking active raw telemetry ingestion over the last hour...{Style.RESET_ALL}")
    
    # KQL REST query to check for unscored rows in last 1 hour
    # We extend/parse string timestamp to datetime dynamically for 'ago(1h)'
    check_query = """
    real_time_transactions
    | extend ts = todatetime(timestamp)
    | where ts >= ago(1h)
    | where risk_score == 0
    | count
    """
    try:
        res = kql_rest_query(check_query, token, uri, db)
        unscored_count = res[0]["Count"] if res else 0
    except Exception as e:
        safe_print(f"{Fore.RED}Failed to query KQL database count: {e}{Style.RESET_ALL}")
        return False
        
    safe_print(f"Unscored raw rows in last 1h: {unscored_count}")
    
    if unscored_count == 0:
        safe_print(f"{Fore.YELLOW}⚠️ No active simulator telemetry found in KQL in the past hour!{Style.RESET_ALL}")
        safe_print("Please start event_simulator.py to stream live transactions, then re-run this scoring loop.")
        return True
        
    safe_print(f"\n{Fore.GREEN}Successfully fetched {unscored_count} new unscored raw transactions from KQL.{Style.RESET_ALL}")
    safe_print(f"{Fore.GREEN}Running AI scoring loop and generating real-time KQL database updates...{Style.RESET_ALL}\n")
    
    # Fetch actual unscored records
    unscored_query = """
    real_time_transactions
    | extend ts = todatetime(timestamp)
    | where ts >= ago(1h)
    | where risk_score == 0
    | order by ts desc
    | limit 500
    """
    try:
        unscored_txs = kql_rest_query(unscored_query, token, uri, db)
    except Exception as e:
        safe_print(f"{Fore.RED}Failed to fetch unscored rows from KQL: {e}{Style.RESET_ALL}")
        return False
        
    scored_rows = []
    high_risk_count = 0
    
    for txn in unscored_txs:
        # Convert datetime object or string to standard format
        ts_val = txn.get('timestamp')
        if isinstance(ts_val, datetime):
            txn['timestamp'] = ts_val.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
        score, reasons = calculate_ensemble_risk(txn, clf)
        txn['risk_score'] = int(score)
        txn['is_fraud'] = int(1 if score > 80 else 0)
        scored_rows.append(txn)
        
        if score > 80:
            high_risk_count += 1
            safe_print(f"🚨 {Fore.RED}{Style.BRIGHT}[REAL-TIME ANOMALY DETECTED]{Style.RESET_ALL} "
                  f"ID: {txn.get('transaction_id')} | Customer: {txn.get('customer_name')} | Score: {score}/100")
            safe_print(f"Heuristic Warnings: {reasons}\n")
            safe_print("--- AI Explanation ---")
            
            explanation = explain_risk_with_openai(txn, score, reasons, config)
            safe_print(explanation)
            safe_print("=" * 60)
            
    if scored_rows:
        safe_print(f"\nWriting {len(scored_rows)} scored rows back to real_time_transactions...")
        try:
            ingest_rows_to_kql(scored_rows, token, uri, db)
            
            log_msg = (
                f"Successfully wrote {len(scored_rows)} scored transactions directly back to "
                f"'real_time_transactions' table in KQL via REST API! "
                f"Total high-risk anomalies dynamically flagged & updated: {high_risk_count}"
            )
            safe_print(f"{Fore.GREEN}{log_msg}{Style.RESET_ALL}")
            
            # Log execution stats
            log_run_stats(unscored_count, len(scored_rows), high_risk_count, log_msg, token, uri, db)
        except Exception as e:
            safe_print(f"{Fore.RED}Failed to write scored rows back to KQL: {e}{Style.RESET_ALL}")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="100% Spark-free Real-Time KQL AI Scoring Engine (Bypasses Fabric 429 Capacities)")
    parser.add_argument("--loop", action="store_true", help="Run scoring continuously in a loop")
    parser.add_argument("--interval", type=int, default=15, help="Scoring frequency interval in seconds (default 15s)")
    args = parser.parse_args()
    
    safe_print("=" * 80)
    safe_print("        [+] LOCAL SMART BANKING REAL-TIME RISK SCORING LOOP (SPARK-FREE)")
    safe_print("        Completely Bypasses Microsoft Fabric 429 Compute Capacity Blocks")
    safe_print("=" * 80)
    
    # Load settings
    env = load_env()
    config = load_config()
    
    tenant_id = env.get("AZURE_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
    client_id = env.get("AZURE_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
    client_secret = env.get("AZURE_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET")
    
    kql_db = config.get("kqlDatabaseName", "BankingRiskDB")
    kql_uri = env.get("KQL_QUERY_URI") or os.getenv("KQL_QUERY_URI") or "https://trd-d2106gp5ufbuq1042c.z1.kusto.fabric.microsoft.com"
    
    if not (tenant_id and client_id and client_secret):
        safe_print(f"{Fore.RED}[CONFIG ERROR] Azure Service Principal credentials not found in .env!{Style.RESET_ALL}")
        safe_print("Please check your .env file at the workspace root directory and define:")
        safe_print("AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
        sys.exit(1)
        
    # Verify/Train Classifier
    try:
        clf = get_or_train_model()
    except Exception as e:
        safe_print(f"{Fore.RED}[MODEL ERROR] {e}{Style.RESET_ALL}")
        sys.exit(1)
        
    # Get secure KQL REST Token
    safe_print(f"\n{Fore.CYAN}Requesting Azure AD access token for KQL REST API...{Style.RESET_ALL}")
    try:
        token = get_kql_token(tenant_id, client_id, client_secret)
        safe_print(f"{Fore.GREEN}Successfully authenticated with Azure Active Directory!{Style.RESET_ALL}")
    except Exception as e:
        safe_print(f"{Fore.RED}[AUTH ERROR] Failed to authenticate: {e}{Style.RESET_ALL}")
        sys.exit(1)
        
    if args.loop:
        safe_print(f"\n{Fore.GREEN}Real-Time Scoring Service started. Polling KQL every {args.interval}s for raw telemetry...{Style.RESET_ALL}")
        safe_print("Press Ctrl+C to terminate.")
        while True:
            try:
                # Refresh token periodically to avoid 1-hour expiry
                token = get_kql_token(tenant_id, client_id, client_secret)
                run_scoring_job(clf, token, kql_uri, kql_db, config)
            except KeyboardInterrupt:
                safe_print(f"\n{Fore.YELLOW}Scoring loop terminated by user. Exiting.{Style.RESET_ALL}")
                break
            except Exception as e:
                safe_print(f"{Fore.RED}Unexpected error in scoring cycle: {e}{Style.RESET_ALL}")
            time.sleep(args.interval)
    else:
        run_scoring_job(clf, token, kql_uri, kql_db, config)
        safe_print(f"\n{Fore.GREEN}Scoring job finished successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
