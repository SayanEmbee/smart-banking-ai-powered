import os
import csv
import random
from datetime import datetime, timedelta

def main():
    print("Starting Historical Data Generator...")
    print("Generating 10,000 realistic bank transactions with seaded fraud patterns...")

    # Seed for deterministic generation
    random.seed(42)

    # 1. Configuration
    total_records = 10000
    fraud_rate = 0.022  # ~2.2% fraud
    
    payment_channels = ["UPI", "POS", "ATM", "Mobile Banking", "Internet Banking"]
    transaction_types = ["Transfer", "Withdrawal", "Purchase", "Bill Payment"]
    
    indian_cities = [
        {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
        {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
        {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
        {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867},
        {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
        {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
        {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714}
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
        {"name": "Apollo Pharmacy", "category": "Healthcare"},
        {"name": "DMart Supermarket", "category": "Groceries"}
    ]

    suspicious_merchants = [
        {"name": "Unknown Forex Broker", "category": "Investment"},
        {"name": "Suspicious Shell Co", "category": "Miscellaneous"},
        {"name": "Cryptocurrency Exchange Malta", "category": "Crypto"},
        {"name": "Luxury Watches Dubai", "category": "Luxury Shopping"},
        {"name": "Midnight Cash Outlet", "category": "ATM Cash Out"}
    ]

    foreign_countries = [
        {"country": "Russia", "city": "Moscow", "lat": 55.7558, "lon": 37.6173},
        {"country": "Nigeria", "city": "Lagos", "lat": 6.5244, "lon": 3.3792},
        {"country": "Ukraine", "city": "Kyiv", "lat": 50.4501, "lon": 30.5234},
        {"country": "United Arab Emirates", "city": "Dubai", "lat": 25.2048, "lon": 55.2708}
    ]

    devices = ["iPhone 15", "Samsung Galaxy S24", "MacBook Pro", "Windows Desktop", "Android Tablet"]
    ip_subnets = ["192.168.1.", "103.45.21.", "49.206.12.", "223.189.43."]

    # Create directory if not exists
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "historical_credit_card_fraud.csv")

    # Generate customer base
    customers = []
    for i in range(1, 401):  # 400 distinct customers
        cust_id = f"CUST-{1000 + i}"
        account_num = f"ACC-{random.randint(1000000000, 9999999999)}"
        name = f"Customer {i}"
        home_city = random.choice(indian_cities)
        home_device = random.choice(devices)
        customers.append({
            "customer_id": cust_id,
            "account_number": account_num,
            "name": name,
            "home_city": home_city,
            "home_device": home_device
        })

    # Start writing CSV
    headers = [
        "transaction_id", "customer_id", "account_number", "customer_name",
        "timestamp", "amount", "merchant", "merchant_category",
        "payment_channel", "transaction_type", "country", "city", "state",
        "device_type", "ip_address", "risk_score", "is_fraud"
    ]

    # Timeframe: Last 30 days
    base_time = datetime.now() - timedelta(days=30)

    transactions = []
    fraud_count = 0

    print("Generating records...")
    for idx in range(1, total_records + 1):
        tx_id = f"TXN-{100000 + idx}"
        
        # Decide if this transaction is a pre-seeded fraud event
        should_be_fraud = random.random() < fraud_rate
        
        customer = random.choice(customers)
        cust_id = customer["customer_id"]
        acc_num = customer["account_number"]
        cust_name = customer["name"]
        
        # Time distribution: transactions spread randomly across 30 days
        tx_time = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Home location
        country = "India"
        city = customer["home_city"]["city"]
        state = customer["home_city"]["state"]
        device = customer["home_device"]
        ip = random.choice(ip_subnets) + str(random.randint(2, 254))
        channel = random.choice(payment_channels)
        txtype = random.choice(transaction_types)

        if not should_be_fraud:
            # NORMAL TRANSACTION
            amount = round(random.uniform(50, 15000), 2)
            # Add bias toward standard UPI transactions
            if random.random() < 0.4:
                channel = "UPI"
                txtype = "Purchase" if random.random() < 0.7 else "Transfer"
                amount = round(random.uniform(10, 4000), 2)

            merchant = random.choice(merchants)
            merchant_name = merchant["name"]
            category = merchant["category"]
            
            # Risk score low for normal events
            risk_score = random.randint(1, 29)
            is_fraud = 0

        else:
            # FRAUD TRANSACTION (Simulate specific patterns)
            is_fraud = 1
            fraud_count += 1
            pattern = random.randint(1, 5)

            if pattern == 1:
                # Pattern 1: High Value Spike
                amount = round(random.uniform(180000, 295000), 2)
                merchant = random.choice(suspicious_merchants)
                merchant_name = merchant["name"]
                category = merchant["category"]
                channel = random.choice(["Internet Banking", "POS"])
                risk_score = random.randint(85, 99)

            elif pattern == 2:
                # Pattern 2: Foreign Country Transaction
                amount = round(random.uniform(5000, 45000), 2)
                foreign = random.choice(foreign_countries)
                country = foreign["country"]
                city = foreign["city"]
                state = "Overseas"
                merchant_name = "International Retailer"
                category = "Travel & Leisure"
                device = "Unknown Linux Terminal"
                ip = f"{random.randint(80, 210)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                risk_score = random.randint(90, 99)

            elif pattern == 3:
                # Pattern 3: Velocity Spike (Adjust timestamp specifically to be within seconds)
                # For historical representation we just give it a high risk score and velocity flag indicator
                amount = round(random.uniform(45000, 95000), 2)
                channel = "ATM"
                txtype = "Withdrawal"
                merchant_name = "Midnight Cash Outlet"
                category = "ATM Cash Out"
                risk_score = random.randint(80, 95)

            elif pattern == 4:
                # Pattern 4: Midnight Activity
                amount = round(random.uniform(25000, 85000), 2)
                # Set hour specifically to early morning
                tx_time = tx_time.replace(hour=3, minute=random.randint(5, 55))
                merchant = random.choice(suspicious_merchants)
                merchant_name = merchant["name"]
                category = merchant["category"]
                channel = "Internet Banking"
                device = "New Unrecognized Mobile Device"
                ip = "185.220.101.44"  # Suspicious Tor IP range
                risk_score = random.randint(88, 98)

            else:
                # Pattern 5: ATM Withdrawal Burst
                amount = round(random.uniform(20000, 40000), 2)
                channel = "ATM"
                txtype = "Withdrawal"
                merchant_name = "Offsite ATM Bangalore"
                category = "ATM Cash Out"
                risk_score = random.randint(75, 92)

        transactions.append({
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "account_number": acc_num,
            "customer_name": cust_name,
            "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
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
            "risk_score": risk_score,
            "is_fraud": is_fraud
        })

    # Sort transactions by timestamp so they read naturally
    transactions.sort(key=lambda x: x["timestamp"])

    # Write to CSV
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)

    print(f"Success! Historical file created at: {output_path}")
    print(f"Total Transactions: {len(transactions)}")
    print(f"Fraud Transactions: {fraud_count} ({round((fraud_count/len(transactions))*100, 2)}% of total)")

if __name__ == "__main__":
    main()
