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

## 4. Execution Pathways

Choose **one** of the two pathways below depending on your goal:
* **Pathway A: Local Sandbox Mode** (Get running locally in 60 seconds with no Azure setup required).
* **Pathway B: Automated Cloud Deployment** (Provision complete Azure capacity and Fabric workspace items in under 3 minutes).

---

### Pathway A: Local Sandbox Mode (60-Second Setup)

This mode runs the entire transaction generator and AI notebook locally on your PC. No Azure subscription or active Fabric capacity is needed.

#### Step 1: Install Local Python Packages
Ensure you have Python 3.10+ installed. Open your terminal in the project root and run:
```bash
pip install -r requirements.txt
```

#### Step 2: Generate the Historical Transaction Database
Create the 10,000 credit card transaction historical CSV containing 2.39% pre-seeded anomalies:
```bash
python data/generate_historical_data.py
```
*Output file: `data/historical_credit_card_fraud.csv` (1.78 MB).*

#### Step 3: Launch the Interactive Live Simulator
Stream simulated Indian banking UPI/ATM/POS transactions directly inside your command line:
```bash
python src/simulator/event_simulator.py --dry-run
```

* **Speed Controls:** Press `+` to accelerate up to 30 TPS, or `-` to slow it down.
* **Live Fraud Injection Keys:** While the simulator is streaming in the terminal, press any of these keys to inject specific fraud profiles instantly:
  * Press `1` : Inject a **High-Value Spike** (₹2,50,000 POS transaction).
  * Press `2` : Inject a **Foreign Location Mismatch** (Hyderabad customer transacting in Moscow).
  * Press `3` : Inject an **ATM Velocity Burst** (rapid high-value ATM cash-outs).
  * Press `4` : Inject a **Midnight Account Takeover** (3:00 AM transaction via a Tor node IP).
  * Press `q` : Safely terminate the stream.

#### Step 4: Run the AI Risk-Scoring & Explanations Notebook
Open `src/notebooks/fraud_scoring_ai.ipynb` in VS Code or Jupyter:
* Runs machine learning classification using `scikit-learn`.
* Scores live transactions using combined rules + probability matrices.
* Generates plain-language fraud operations reasoning blocks (mock reasonings are automatically generated if you do not have an active OpenAI API key).

---

### Pathway B: Automated Cloud Deployment (Azure & Microsoft Fabric)

Use this pathway to deploy the entire, production-grade real-time streaming pipeline inside your active Microsoft Fabric workspace.

```
[Azure CLI Login] ──> [.\infra\create-capacity.ps1] ──> [.\scripts\provision-fabric.ps1] ──> [Stream Live Events!]
```

#### Step 1: Authenticate to Your Azure Tenant
Make sure you have [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed. Open your terminal and sign in:
```bash
az login
```

#### Step 2: Configure Your Resource Names
Open [config/accelerator-config.json](file:///C:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/config/accelerator-config.json) and set your custom names:
```json
{
  "subscriptionId": "YOUR_AZURE_SUBSCRIPTION_ID",
  "resourceGroup": "rg-banking-fraud-dev",
  "capacityName": "bankingfabriccapdev",
  "location": "CentralIndia"
}
```

#### Step 3: Provision Azure Fabric Capacity
Open a PowerShell terminal and run the capacity provisioner script:
```powershell
.\infra\create-capacity.ps1
```
> **What this does:** Automatically logs in, creates your Azure Resource Group, provisions a dedicated Fabric F2 capacity (`Sku: F2`), and saves the resolved Capacity ID back to your local config.

#### Step 4: Deploy All Fabric Workspace Items
Run the primary Fabric orchestrator script:
```powershell
.\scripts\provision-fabric.ps1
```
> **What this does:** Runs fully authenticated Entra ID Fabric REST API calls to:
> 1. Create or locate the workspace `SmartBankingRiskWorkspace` and bind it to your capacity.
> 2. Deploy your Lakehouse (`BankingFraudLakehouse`), KQL Database (`BankingRiskDB`), and Eventstream (`BankingTransactionStream`).
> 3. Stream the 1.78 MB historical CSV dataset directly into OneLake Storage (`Files/` directory).
> 4. Save all newly resolved Fabric item IDs back to your config file.

#### Step 5: Connect Your Live Stream & Run
Now that your cloud environment is ready, hook up your local generator:
1. Open the [Microsoft Fabric Portal](https://app.fabric.microsoft.com/).
2. Open your new `SmartBankingRiskWorkspace`.
3. Open `BankingTransactionStream` and select the **Custom App** source node to copy your unique REST API endpoint URL.
4. Open `config/accelerator-config.json` and paste that URL into the `"eventstreamCustomEndpoint"` field.
5. Run the simulator to stream live transactions directly into Microsoft Fabric:
   ```bash
   python src/simulator/event_simulator.py
   ```
6. Open your KQL Database (`BankingRiskDB`), execute the query scripts inside [schema.kql](file:///C:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/src/definitions/kql/schema.kql), and start visualizing sub-second operational data!
