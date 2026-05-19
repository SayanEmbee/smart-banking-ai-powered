# Real-Time Banking Risk & Fraud Intelligence Solution Accelerator

This solution accelerator delivers a complete, enterprise-grade **Real-Time Banking Risk & Fraud Intelligence Platform** built on Microsoft Fabric and Generative AI. It continuously analyzes live and historical banking transactions through interactive dashboards, detects suspicious activities and fraud patterns in real time, triggers intelligent alerts and automated responses, and provides AI-powered natural language investigation insights for proactive financial decision-making.

The architecture and framework are easily extendable across retail banking, fintech, insurance, payment systems, and commercial financial institutions for enterprise-scale adoption.

---

## 1. Key Business Use Cases

* **Real-Time Transaction Monitoring:** Continuous operational intelligence over transaction volumes, frequencies, and channels (UPI, POS, ATM, NetBanking).
* **Heuristics & Anomaly Identification:** Automated real-time detection of high-value spikes, rapid velocity bursts, and midnight accounts takeovers.
* **AI-Powered Risk Scoring & Explanations:** Predictive risk scores combined with rich, natural language summaries explaining *why* a transaction was flagged and recommending immediate remediation.
* **Geo-location & Device Monitoring:** Instantly detects when a transaction is initiated from a foreign country or unrecognized device hardware while the customer home profile indicates normal domestic activity.
* **Executive Command Dashboards:** Centralized monitoring for risk managers, compliance officers, and tier-2 fraud operations teams.

---

## 2. Technical Architecture & Data Flow

This accelerator coordinates real-time telemetry streaming and historical batch analytics:

```
                  +----------------------------------------------+
                  |  Python faker Live Telemetry Generator        |
                  +----------------------------------------------+
                                         |
                                         | (Continuous 1-5 events/sec)
                                         v
                  +----------------------------------------------+
                  |  Microsoft Fabric Eventstream API Endpoint   |
                  +----------------------------------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |  Fabric Eventhouse (KQL Database / Engine)   |
                  +----------------------------------------------+
                                   /            \
                       (KQL Direct Query)      (Real-time stream monitoring)
                                 /                \
                                v                  v
        +----------------------------+      +----------------------------+
        | Power BI Real-Time Board   |      | Fabric Activator Alerts    |
        +----------------------------+      +----------------------------+
                      ^                                    |
                      |                                    v
        +----------------------------+      +----------------------------+
        | AI Risk Scoring Notebook   |      | Automated Email Notification|
        +----------------------------+      +----------------------------+
```

---

## 3. Directory Layout

The workspace is organized to follow standard Microsoft Solution Accelerator governance practices:

```
smart-banking-ai-powered/
├── config/
│   └── accelerator-config.json      # Workspace orchestration settings
├── data/
│   ├── generate_historical_data.py  # Historical pre-seeded transactions generator
│   └── historical_credit_card_fraud.csv # 10k generated historical transactions
├── docs/
│   └── architecture.md              # Technical architecture details
├── src/
│   ├── definitions/
│   │   └── kql/
│   │       └── schema.kql           # KQL table schemas and queryset definitions
│   ├── notebooks/
│   │   └── fraud_scoring_ai.ipynb   # ML training, heuristics scoring, and AI reasoner
│   └── simulator/
│       └── event_simulator.py       # Live transaction stream simulator (Indian context)
├── requirements.txt                 # Project dependencies list
└── README.md                        # Master documentation (this file)
```

---

## 4. Getting Started & Running the Prototype

Follow these steps in order to set up your banking fraud intelligence environment.

### Step 1: Install Dependencies
Ensure you have Python 3.10+ installed. Install the accelerator requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Establish the Historical Fraud Dataset
Generate the 10,000 credit card transaction historical dataset seaded with anomalies:
```bash
python data/generate_historical_data.py
```
This writes `data/historical_credit_card_fraud.csv` automatically. You can load this file into your **Fabric Lakehouse** to power batch Power BI reports or machine learning models.

### Step 3: Run the Live Transaction Simulator (Console/Dry-Run)
Run the generator in **dry-run mode** to see simulated Indian banking transactions stream dynamically in your console:
```bash
python src/simulator/event_simulator.py --dry-run
```
* **Speed:** Default is 2.0 transactions/second.
* **Payment Channels Simulated:** UPI (Google Pay/PhonePe style), POS, ATM, Mobile Banking, Internet Banking.
* **Indian Profiles:** Indian names, home cities (Mumbai, Bengaluru, Delhi, etc.), and UPI transaction bounds.

### Step 4: Interact & Inject Live Fraud During Demo
While the simulator is running in your console, press these hotkeys to trigger dynamic anomalies:
* Press **`f`** : Inject a random fraud transaction.
* Press **`1`** : Inject a **High Value Spike** pattern (e.g. ₹2,50,000 POS transaction).
* Press **`2`** : Inject a **Foreign Location** pattern (Hyderabad customer transacting in Russia).
* Press **`3`** : Inject an **ATM Velocity Burst** pattern (rapid high-value ATM withdrawals).
* Press **`4`** : Inject **Midnight Tor Login** pattern (3:00 AM transaction via Tor node IP).
* Press **`+`** : Increase transaction rate (up to 30 TPS) to simulate peak spikes.
* Press **`-`** : Slow down transaction rate.
* Press **`q`** : Exit simulator safely.

### Step 5: Explore ML Scoring & AI Explanations
Open the notebook `src/notebooks/fraud_scoring_ai.ipynb` in VS Code or upload it to your **Fabric Workspace**:
* It loads the historical CSV from OneLake.
* Trains a `Random Forest Classifier` in scikit-learn.
* Executes a heuristic-based risk evaluation ruleset.
* Connects to **OpenAI / Generative AI** to write natural language explanations explaining *why* a transaction was flagged as risky and suggesting mitigation steps (card block, Tier-2 analyst routing).

---

## 5. 100% Automated Deployment & Provisioning (Azure & Microsoft Fabric)

We have provided complete PowerShell deployment automation matching the architecture of the Microsoft accelerators:

### Prerequisites for Automation:
1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
2. Authenticate to your Azure/Fabric tenant:
   ```bash
   az login
   ```

### Step 1: Assign Resource Names in Configuration
Open [config/accelerator-config.json](file:///C:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/config/accelerator-config.json) and customize your names:
* `"resourceGroup"`: The Azure resource group to create.
* `"capacityName"`: The name of the Fabric F2 capacity to deploy.
* `"location"`: The Azure region (e.g. `CentralIndia` or `EastUS`).

### Step 2: Provision Azure & Fabric Capacity
Execute the capacity provisioning script in PowerShell:
```powershell
.\infra\create-capacity.ps1
```
This script signs in via the active CLI credentials, creates your Azure Resource Group, provisions a Fabric F2 capacity, and saves the resolved Capacity ID back to your configuration automatically.

### Step 3: Automatically Provision Fabric Workspace & Assets
Run the primary Fabric orchestrator script:
```powershell
.\scripts\provision-fabric.ps1
```
This script connects via Fabric Entra tokens and:
1. Automatically discovers or creates your workspace `SmartBankingRiskWorkspace`.
2. Automatically assigns the workspace to the Fabric capacity.
3. Automatically provisions your Lakehouse (`BankingFraudLakehouse`), KQL Database (`BankingRiskDB`), and Eventstream (`BankingTransactionStream`).
4. Automatically uploads the generated 1.78 MB historical CSV dataset directly to OneLake Storage.
5. Populates all resolved item IDs back to your local config file!

### Step 4: Complete Mappings & Connect Stream
To connect the live simulator to your newly created Eventstream:
1. Open the [Microsoft Fabric Portal](https://app.fabric.microsoft.com/).
2. Navigate to your new workspace `SmartBankingRiskWorkspace`.
3. Open `BankingTransactionStream` and select the **Custom App** source to retrieve the REST API URL endpoint.
4. Paste this REST API URL into `"eventstreamCustomEndpoint"` in `config/accelerator-config.json`.
5. Execute the simulator to stream live transactions directly to Fabric:
   ```bash
   python src/simulator/event_simulator.py
   ```

