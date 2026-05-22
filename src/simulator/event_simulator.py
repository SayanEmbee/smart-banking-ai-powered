import os
import sys
import json
import time
import random
import argparse
from datetime import datetime

# Check for Windows-specific keypress detection
try:
    import msvcrt
    WINDOWS_KEYBOARD = True
except ImportError:
    WINDOWS_KEYBOARD = False

# Try to import colorama for terminal formatting
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False
    # Fallback to empty strings if colorama is not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = WHITE = MAGENTA = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# Try to import requests for pushing to Fabric Eventstream
try:
    import requests
    HTTP_SUPPORT = True
except ImportError:
    HTTP_SUPPORT = False

# Try to import Azure Event Hub SDK dynamically
try:
    from azure.eventhub import EventHubProducerClient, EventData
    EVENTHUB_SUPPORT = True
except ImportError:
    EVENTHUB_SUPPORT = False

# Try to import Faker
try:
    from faker import Faker
    fake = Faker('en_IN')  # Use Indian locale
    FAKER_SUPPORT = True
except ImportError:
    FAKER_SUPPORT = False

# Fallback lists if Faker is not installed
INDIAN_NAMES = [
    "Aarav Sharma", "Aditya Patel", "Vihaan Rao", "Arjun Nair", "Sai Krishna", 
    "Reyansh Gupta", "Aanya Iyer", "Diya Sen", "Ananya Reddy", "Pari Deshmukh",
    "Ishaan Joshi", "Kabir Bhat", "Aaradhya Saxena", "Priya Verma", "Rohan Mehta"
]

payment_channels = ["UPI", "POS", "ATM", "Mobile Banking", "Internet Banking"]
transaction_type = "Debit"  # All outgoing transactions are debit type per schema

indian_cities = [
    {"city": "Mumbai", "state": "Maharashtra"},
    {"city": "Pune", "state": "Maharashtra"},
    {"city": "Bengaluru", "state": "Karnataka"},
    {"city": "Hyderabad", "state": "Telangana"},
    {"city": "Chennai", "state": "Tamil Nadu"},
    {"city": "New Delhi", "state": "Delhi"},
    {"city": "Kolkata", "state": "West Bengal"},
    {"city": "Ahmedabad", "state": "Gujarat"}
]

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

foreign_countries = [
    {"country": "Russia", "city": "Moscow"},
    {"country": "Nigeria", "city": "Lagos"},
    {"country": "Ukraine", "city": "Kyiv"},
    {"country": "United Arab Emirates", "city": "Dubai"}
]

devices = ["iPhone 15", "Samsung Galaxy S24", "MacBook Pro", "Windows Desktop", "Android Tablet"]
ip_subnets = ["192.168.1.", "103.45.21.", "49.206.12.", "223.189.43."]

# Pre-generate 100 customer records for simulation
customers = []
for i in range(1, 101):
    cust_id = f"CUST-{2000 + i}"
    acc_num = f"ACC-{random.randint(1000000000, 9999999999)}"
    
    if FAKER_SUPPORT:
        name = fake.name()
    else:
        name = random.choice(INDIAN_NAMES) + f" {random.randint(1,9)}"
        
    home_city = random.choice(indian_cities)
    home_device = random.choice(devices)
    customers.append({
        "customer_id": cust_id,
        "account_number": acc_num,
        "name": name,
        "home_city": home_city,
        "home_device": home_device
    })

def generate_transaction(inject_fraud=False, fraud_type=None):
    tx_id = f"TXN-{random.randint(100000, 999999)}"
    customer = random.choice(customers)
    
    country = "India"
    city = customer["home_city"]["city"]
    state = customer["home_city"]["state"]
    device = customer["home_device"]
    ip = random.choice(ip_subnets) + str(random.randint(2, 254))
    channel = random.choice(payment_channels)
    txtype = transaction_type  # Fixed as "Debit" per production schema
    
    # ISO-8601 UTC format: 2026-05-19T13:56:00.000Z
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    if not inject_fraud:
        # NORMAL TRANSACTION
        amount = round(random.uniform(50, 12000), 2)
        # UPI bias (40% chance of UPI small transaction)
        if random.random() < 0.4:
            channel = "UPI"
            txtype = transaction_type  # Always "Debit" per schema
            amount = round(random.uniform(10, 3000), 2)

        merchant = random.choice(merchants)
        merchant_name = merchant["name"]
        category = merchant["category"]
        risk_score = random.randint(1, 25)
        is_fraud = 0
    else:
        # INJECT FRAUD SCENARIO
        is_fraud = 1
        
        if fraud_type is None:
            fraud_type = random.choice([1, 2, 3, 4])
            
        if fraud_type == 1:
            # Pattern 1: High Value Spike
            amount = round(random.uniform(190000, 280000), 2)
            merchant = random.choice(suspicious_merchants)
            merchant_name = merchant["name"]
            category = merchant["category"]
            channel = random.choice(["Internet Banking", "POS"])
            risk_score = random.randint(85, 99)
            print(f"{Fore.RED}[FRAUD INJECTED]{Style.RESET_ALL} High Value Spike Pattern triggered!")
            
        elif fraud_type == 2:
            # Pattern 2: Foreign Country Transaction
            amount = round(random.uniform(12000, 45000), 2)
            foreign = random.choice(foreign_countries)
            country = foreign["country"]
            city = foreign["city"]
            state = "Overseas"
            merchant_name = "Offshore Retailer"
            category = "Travel & Leisure"
            device = "Unknown Linux Terminal"
            ip = f"{random.randint(80, 210)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            risk_score = random.randint(90, 99)
            print(f"{Fore.RED}[FRAUD INJECTED]{Style.RESET_ALL} Foreign Geolocation Transaction Pattern triggered!")
            
        elif fraud_type == 3:
            # Pattern 3: ATM Velocity Spike
            amount = round(random.uniform(45000, 60000), 2)
            channel = "ATM"
            txtype = transaction_type  # Keep as "Debit" per schema
            merchant_name = "Midnight Cash Outlet"
            category = "ATM Cash Out"
            risk_score = random.randint(82, 95)
            print(f"{Fore.RED}[FRAUD INJECTED]{Style.RESET_ALL} ATM Rapid Cash Withdrawal Burst Pattern triggered!")
            
        else:
            # Pattern 4: Suspicious Midnight Activity
            amount = round(random.uniform(35000, 75000), 2)
            merchant = random.choice(suspicious_merchants)
            merchant_name = merchant["name"]
            category = merchant["category"]
            channel = "Internet Banking"
            device = "Suspicious Mobile Device Model"
            ip = "185.220.101.44"  # Tor Node IP
            risk_score = random.randint(89, 98)
            print(f"{Fore.RED}[FRAUD INJECTED]{Style.RESET_ALL} Midnight Tor Account Takeover Pattern triggered!")

    return {
        "transaction_id": tx_id,
        "customer_id": customer["customer_id"],
        "account_number": customer["account_number"],
        "customer_name": customer["name"],
        "timestamp": timestamp,
        "amount": amount,
        "merchant": merchant_name,
        "merchant_category": category,
        "payment_channel": channel,
        "transaction_type": txtype,
        "country": country,
        "city": city,
        "state": state,
        "device_type": device,
        "ip_address": ip,
        "risk_score": 0,  # Unscored raw transaction telemetry (to be scored by AI notebook!)
        "is_fraud": 0     # Unscored raw transaction telemetry (to be scored by AI notebook!)
    }

def print_help():
    print("\n--- Key Commands ---")
    print("  [f] : Inject random fraud transaction")
    print("  [1] : Inject High Value Spike fraud pattern")
    print("  [2] : Inject Foreign Geolocation fraud pattern")
    print("  [3] : Inject ATM Velocity Burst fraud pattern")
    print("  [4] : Inject Midnight Tor login fraud pattern")
    print("  [+] : Increase transaction rate (speed up)")
    print("  [-] : Decrease transaction rate (slow down)")
    print("  [h] : Show this help guide")
    print("  [q] : Quit simulator")
    print("--------------------\n")

def load_env(env_path=".env"):
    """Lightweight, zero-dependency .env file loader."""
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        os.environ[key] = val
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Real-Time Banking Transaction Stream Simulator")
    parser.add_argument("--endpoint", type=str, help="Fabric Eventstream API Endpoint URL")
    parser.add_argument("--dry-run", action="store_true", help="Print transactions to console without sending network requests")
    parser.add_argument("--speed", type=float, default=2.0, help="Initial transaction speed in events per second")
    args = parser.parse_args()

    # Load environment variables from local .env
    load_env()

    # Determine endpoint from CLI arg, environment, or config
    endpoint = args.endpoint
    if not endpoint and not args.dry_run:
        # Try environment first
        endpoint = os.environ.get("EVENTSTREAM_CUSTOM_ENDPOINT")
        
        # Try config file fallback
        if not endpoint or "YOUR_EVENTSTREAM" in endpoint or "<your-custom" in endpoint:
            config_path = os.path.join("config", "accelerator-config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as cfg:
                        config = json.load(cfg)
                        endpoint = config.get("eventstreamCustomEndpoint")
                        if endpoint and ("YOUR_EVENTSTREAM" in endpoint or "<your-custom" in endpoint):
                            endpoint = None
                except Exception:
                    endpoint = None
                
    # If no valid endpoint, default to dry-run
    dry_run = args.dry_run or (endpoint is None)


    print("==================================================")
    print("   REAL-TIME BANKING FRAUD TELEMETRY SIMULATOR    ")
    print("==================================================")
    
    if FAKER_SUPPORT:
        print("Faker engine: ACTIVE (Locale: en_IN)")
    else:
        print("Faker engine: INACTIVE (using fallback profiles)")

    if dry_run:
        print(f"Ingestion Mode: {Fore.YELLOW}DRY RUN (Writing to Console Only){Style.RESET_ALL}")
    else:
        print(f"Ingestion Mode: {Fore.GREEN}STREAMING (Sending events to Fabric Eventstream){Style.RESET_ALL}")
        print(f"Endpoint: {endpoint}")

    print(f"Initial Speed: {args.speed} Transactions/Sec (TPS)")
    print_help()

    tps = args.speed
    running = True
    
    while running:
        # Non-blocking keypress check for Windows
        if WINDOWS_KEYBOARD and msvcrt.kbhit():
            key = msvcrt.getch().decode("utf-8").lower()
            if key == 'q':
                print("\nExiting simulator. Goodbye!")
                running = False
                break
            elif key == 'f':
                tx = generate_transaction(inject_fraud=True)
                send_tx(tx, endpoint, dry_run)
            elif key in ['1', '2', '3', '4']:
                tx = generate_transaction(inject_fraud=True, fraud_type=int(key))
                send_tx(tx, endpoint, dry_run)
            elif key == '+':
                tps = min(tps + 2, 30)
                print(f"\n{Fore.CYAN}[SPEED UP]{Style.RESET_ALL} Speed increased to {tps} TPS")
            elif key == '-':
                tps = max(tps - 0.5, 0.5)
                print(f"\n{Fore.CYAN}[SLOW DOWN]{Style.RESET_ALL} Speed decreased to {tps} TPS")
            elif key == 'h':
                print_help()

        # Generate random standard transaction
        tx = generate_transaction(inject_fraud=False)
        send_tx(tx, endpoint, dry_run)
        
        # Sleep according to target TPS
        time.sleep(1.0 / tps)

def generate_sas_token(uri, sas_name, sas_key, expiry=3600):
    import time
    import urllib.parse
    import hmac
    import hashlib
    import base64
    
    target_uri = urllib.parse.quote_plus(uri)
    sas = sas_key.encode('utf-8')
    expiry_time = str(int(time.time() + expiry))
    string_to_sign = (target_uri + '\n' + expiry_time).encode('utf-8')
    signed_hmac = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = urllib.parse.quote(base64.b64encode(signed_hmac.digest()))
    return f"SharedAccessSignature sr={target_uri}&sig={signature}&se={expiry_time}&skn={sas_name}"

_producer_client = None

def send_tx(tx, endpoint, dry_run):
    global _producer_client
    # Print to console colorfully
    color = Fore.WHITE
    if tx["is_fraud"] == 1:
        color = Fore.RED + Style.BRIGHT
    elif tx["payment_channel"] == "UPI":
        color = Fore.GREEN
    elif tx["payment_channel"] == "ATM":
        color = Fore.YELLOW

    tx_str = (
        f"[{tx['timestamp']}] "
        f"transaction_id: {tx['transaction_id']} | "
        f"customer_id: {tx['customer_id']} | "
        f"account_number: {tx['account_number']} | "
        f"customer_name: {tx['customer_name']:<20} | "
        f"amount: Rs.{tx['amount']:<10} | "
        f"merchant: {tx['merchant']:<22} | "
        f"merchant_category: {tx['merchant_category']:<18} | "
        f"payment_channel: {tx['payment_channel']:<16} | "
        f"transaction_type: {tx['transaction_type']:<8} | "
        f"country: {tx['country']:<6} | "
        f"city: {tx['city']:<14} | "
        f"state: {tx['state']:<18} | "
        f"device_type: {tx['device_type']:<22} | "
        f"ip_address: {tx['ip_address']:<15} | "
        f"risk_score: {tx['risk_score']:<3} | "
        f"is_fraud: {tx['is_fraud']}"
    )
    print(color + tx_str)

    # Perform actual push if not dry-run
    if not dry_run and endpoint:
        # Check if it is a standard Event Hub connection string
        if endpoint.startswith("Endpoint=sb://"):
            if not EVENTHUB_SUPPORT:
                print(f"{Fore.RED}[SDK ERROR] azure-eventhub package is missing! Please install it by running: pip install azure-eventhub{Style.RESET_ALL}")
                return
            
            try:
                if _producer_client is None:
                    _producer_client = EventHubProducerClient.from_connection_string(endpoint)
                
                event_data = EventData(json.dumps(tx))
                # Send the event via secure AMQP binary protocol (completely immune to HTTP/WCF 500 dispatcher bugs!)
                _producer_client.send_event(event_data)
            except Exception as e:
                print(f"{Fore.RED}[EVENT HUB SEND FAILED] {e}{Style.RESET_ALL}")
                _producer_client = None # Clear client to retry connection next time
        else:
            if HTTP_SUPPORT:
                try:
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(endpoint, data=json.dumps(tx), headers=headers, timeout=3.0)
                    if response.status_code != 200 and response.status_code != 201 and response.status_code != 202:
                        print(f"{Fore.RED}[NETWORK ERROR] Status: {response.status_code} - {response.text}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[NETWORK CONNECTION FAILED] {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[HTTP ERROR] requests package missing. Please install dependencies.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulator interrupted by user. Exiting.")
        sys.exit(0)
