# Real-Time Banking Risk & Fraud Intelligence Solution Accelerator

This solution accelerator delivers a complete, enterprise-grade **Real-Time Banking Risk & Fraud Intelligence Platform** built on Microsoft Fabric and Generative AI. It continuously analyzes live and historical banking transactions through interactive dashboards, detects suspicious activities and fraud patterns in real time, triggers intelligent alerts and automated responses, and provides AI-powered natural language investigation insights for proactive financial decision-making.

The architecture and framework are easily extendable across retail banking, fintech, insurance, payment systems, and commercial financial institutions for enterprise-scale adoption.

---

## 1. Key Business Use Cases & Simulated Attack Vectors

This solution accelerator simulates a high-fidelity retail banking scenario and detects five distinct real-time financial attack vectors:

| Attack Vector | Simulated Scenario | Risk Flag Trigger | Operational Remediation |
| :--- | :--- | :--- | :--- |
| **High Value Spike** | Sudden transaction of ₹2,50,000 via a POS channel | Amount exceeding 10x customer standard deviation | Instant transaction hold; automatic analyst alert |
| **Foreign Geolocation** | Mumbai customer initiating card transactions from Moscow | Concurrent active sessions across disparate countries | Card block; push-notification request to customer app |
| **ATM Cash Out Burst** | 5 rapid ATM withdrawals totaling ₹95,000 within 2 minutes | High transaction count velocity per minute bounds | Device restriction; temporary card lockdown |
| **Midnight Account Takeover** | 3:00 AM mobile bank login and transfer from unrecognized IP | Unorthodox login hour + transaction sequence | Multi-factor authorization request to account phone |
| **New Device Transfer** | IMPS transaction from unregistered device hardware ID | New device signature with high-value velocity | Step-up security confirmation request |

---

## 2. Infrastructure Topology (Bicep Provisioned)

The accelerator automatically deploys and wires up the following enterprise footprint inside Microsoft Fabric and Azure:

| Resource Name | Service Type | SKU / Tier | Purpose |
| :--- | :--- | :--- | :--- |
| **`bankingfabriccapdev`** | Microsoft Fabric Capacity | `F2` | Azure host computing all workspace, Lakehouse, and streaming pipelines |
| **`SmartBankingRiskWorkspace`** | Microsoft Fabric Workspace | `Standard` | Container organizing all banking assets, notebooks, and database schemas |
| **`BankingFraudLakehouse`** | Microsoft Fabric Lakehouse | `Delta Lake` | Ingests and registers historical data for batch reporting and ML model training |
| **`BankingRiskDB`** | Fabric Eventhouse (KQL Database) | `Kusto Engine` | Performs sub-second real-time queries and KPI summaries over transaction streams |
| **`BankingTransactionStream`** | Fabric Eventstream | `Standard` | Dynamic stream capturing, routing, and filtering simulator telemetry events |

---

## 3. Technical Architecture & Data Flow

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

## 4. Directory Structure

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

## 5. Execution Pathways

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

Use this pathway to deploy the entire, production-grade real-time streaming pipeline inside your active Microsoft Fabric workspace. You can choose to deploy either **automatically via the Azure Developer CLI (`azd`)** or **step-by-step via PowerShell**.

```
[Azure CLI Login] ──> [azd up (One-Click Deploy)] ──> [Stream Live Events!]
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

---

#### Option 1: One-Click deployment via Azure Developer CLI (Recommended)
If you have [Azure Developer CLI (`azd`)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) installed, you can provision and deploy the entire environment with a single command:
```bash
azd up
```
> **What this does:** `azd` reads the [azure.yaml](file:///C:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/azure.yaml) file, executes `infra/create-capacity.ps1` as a `preprovision` hook to spin up your Bicep F2 capacity, and then runs `scripts/provision-fabric.ps1` as a `postprovision` hook to orchestrate all Fabric assets and OneLake files!

---

#### Option 2: Step-by-Step PowerShell deployment
If you do not have `azd` installed, execute the steps sequentially in PowerShell:

##### A. Provision Azure Fabric Capacity
```powershell
.\infra\create-capacity.ps1
```
> **What this does:** Validates your Resource Group, deploys the Microsoft Fabric F2 capacity using your custom **Azure Bicep template** ([infra/main.bicep](file:///C:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/infra/main.bicep)), and writes the resolved Capacity ID to your configuration.

##### B. Deploy All Fabric Workspace Items
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

---

## 6. Teardown & Resource Cleanup

To avoid ongoing charges and keep your subscription clean, you can completely teardown the deployed resources:

### Option 1: Automatic Teardown via Azure Developer CLI
If you deployed your environment using `azd`, simply run:
```bash
azd down --purge --force
```
> **What this does:** Automatically deletes all Azure and Fabric capacity objects provisioned under Bicep, cleans up resource records, and purges deployment metadata.

### Option 2: Manual Teardown via CLI & Fabric Portal
1. **Delete Azure Capacity:**
   ```bash
   az group delete --name rg-banking-fraud-dev --yes --no-wait
   ```
2. **Delete Fabric Workspace:**
   * Open the Microsoft Fabric portal.
   * Navigate to `SmartBankingRiskWorkspace` > **Workspace Settings** > **Other** > **Remove this workspace**.

---

## 7. Customization & Industry Extendability

This solution accelerator was built as a modular blueprint. You can easily adapt its architecture and codebase to support other industry telemetry scenarios:

* **Retail & E-commerce:** Update `src/simulator/event_simulator.py` to stream shopping cart events (customer_id, checkout_amount, product_category, discount_codes) and trigger alerts on checkout drop-offs or payment processing delays.
* **Smart Grid & Utilities:** Adjust telemetry fields to represent grid sensor data (meter_id, voltage, current_frequency, grid_temperature) and configure KQL queries to identify local transformer faults or voltage sags.
* **Fleet Logistics:** Repurpose the schema to capture real-time route details (vehicle_id, latitude, longitude, speed, fuel_rate, brake_status) to proactively flag dangerous driver behavior or engine overheating.

