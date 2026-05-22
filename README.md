# 🛡️ Real-Time Banking Risk & Fraud Intelligence Platform
### *Enterprise-Grade Fraud Telemetry, Real-Time KQL Scoring, and Generative AI Incident Reasoner*

[![Fabric Capacity F2](https://img.shields.io/badge/Microsoft%20Fabric-F2%20Capacity-blue?logo=microsoft)](https://learn.microsoft.com/en-us/fabric/)
[![AI Models](https://img.shields.io/badge/AI%20Model-Random%20Forest-purple?logo=scikitlearn)](https://scikit-learn.org/)
[![GenAI Reasoner](https://img.shields.io/badge/GenAI-GPT--4o%20Reasoner-red?logo=openai)](https://openai.com/)
[![Operational Dashboard](https://img.shields.io/badge/UI-Streamlit%20Console-orange?logo=streamlit)](https://streamlit.io/)
[![Security Shield](https://img.shields.io/badge/Security-Credentials%20Protected-green?logo=gitlfs)](https://github.com/)

This solution accelerator delivers a complete, production-ready **Real-Time Banking Risk & Fraud Intelligence Platform** built on Microsoft Fabric and Generative AI. It continuously streams high-velocity transactions, executes sub-second real-time scoring with a dynamic machine learning ensemble classifier, triggers intelligent security responses, and provides AI-powered natural language incident reports.

---

## 🧭 Project Architecture & Data Flow

This platform links high-velocity event telemetry generation, micro-second stream routing, a real-time event database, dynamic AI scoring loops, and a glassmorphism executive control portal:

```
                            [ 🏦 Banking Clients (UPI / ATM / POS) ]
                                               │
                                               ▼  (Live Event Telemetry)
                       ┌───────────────────────────────────────────────┐
                       │   event_simulator.py (Indian Banking Context) │
                       └───────────────────────┬───────────────────────┘
                                               │
                                               ▼  (AMQP Binary Protocol / REST)
                       ┌───────────────────────────────────────────────┐
                       │   Microsoft Fabric Eventstream API Endpoint   │
                       └───────────────────────┬───────────────────────┘
                                               │
                                               ▼
                       ┌───────────────────────────────────────────────┐
                       │      Fabric Eventhouse (KQL Database DB)      │
                       └───────────────┬───────────────────────┬───────┘
                                       │                       │
         (Polled Scoped Raw Rows)      ▼                       ▼      (Direct REST Ingestion)
     ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
     │   local_scoring_loop.py Daemon    │           │     Streamlit Analytics Portal    │
     │  (Spark-free Random Forest + Rules)│          │            (src/dashboard/app.py) │
     └─────────────────┬─────────────────┘           └─────────────────▲─────────────────┘
                       │                                               │
                       └──────────────── (Scored Rows) ────────────────┘
```

---

## 🔒 Security First: Secrets & Connection Isolation

> [!IMPORTANT]
> **No Credentials in GitHub!** To ensure absolute compliance with security best practices, all active access keys, connection strings, and service principal secrets are fully decoupled from tracked code and isolated inside a local, Git-ignored environment configuration file.

### Secret Isolation System
1. **`.gitignore` Enforced Protection:**
   - The workspace includes a strict `.gitignore` file mapping `.env` and `*.env` patterns. These files are never committed or exposed on GitHub.
2. **Zero-Dependency Dynamic Loaders:**
   - The **Event Simulator (`event_simulator.py`)**, **Local Scoring Daemon (`local_scoring_loop.py`)**, **Streamlit Dashboard (`app.py`)**, and the **AI Notebook (`fraud_scoring_ai.ipynb`)** are fully equipped with custom environment loaders.
   - They dynamically check your local `.env` file first, falling back gracefully to non-sensitive placeholders.
3. **Generic Asset Configurations:**
   - Config file `config/accelerator-config.json` contains *only* non-sensitive resource IDs (e.g. location, capacitySku, databaseName).
   - Sensitive fields like `eventstreamCustomEndpoint` and `apiKey` are set to generic templates (`"YOUR_EVENTSTREAM_CUSTOM_ENDPOINT"`).

### Setting Up Your Local Environment Credentials
To enable live streaming or authenticated database queries, create a `.env` file at the root directory of the workspace using the provided template:

```bash
cp .env.example .env
```

Open the newly created `.env` file and supply your actual development credentials:
```env
# 1. Azure Service Principal (SPN) Credentials for Fabric API Authentication
AZURE_TENANT_ID="your-entra-tenant-id"
AZURE_CLIENT_ID="your-spn-application-id"
AZURE_CLIENT_SECRET="your-spn-client-secret"

# 2. Fabric Custom Eventstream Endpoint (Contains sensitive SharedAccessKey)
EVENTSTREAM_CUSTOM_ENDPOINT="Endpoint=sb://esehpnntzdoc9blu2kw2m0.servicebus.windows.net/;SharedAccessKeyName=key_xxx;SharedAccessKey=your_key_here=;EntityPath=esehpnntzdoc9blu2kw2m0_eh"

# 3. KQL Database Query Endpoint URI
KQL_QUERY_URI="https://trd-yourkustoid.location.kusto.fabric.microsoft.com"

# 4. OpenAI API Key for Live Fraud Explanations and Incident Reports
OPENAI_API_KEY="sk-proj-yourOpenAIKeyHere..."
```

---

## 🚀 Execution Pathways

Select one of the two execution paths to start exploring the accelerator:

* **Pathway A: Local Sandbox Mode (60-Second Run)** – Execute the transaction stream generator, local Random Forest model training, heuristic scoring loops, and the live dashboard completely offline with zero Azure setup.
* **Pathway B: Cloud Fabric Deployment (3-Minute Setup)** – Spin up your Azure Fabric compute capacity (`F2` capacity), auto-provision Fabric workspaces, and wire the live real-time KQL database.

---

### 💻 Pathway A: Local Sandbox Mode

Run a complete simulation loop locally on your machine.

#### 1. Setup Local Environment
Ensure you have Python 3.10+ installed. Install the solution dependencies:
```bash
pip install -r requirements.txt
```

#### 2. Seed Historical Dataset
Generate a high-fidelity historical card transaction database containing 10,000 pre-seeded entries with a 2.39% baseline anomaly rate to train your local models:
```bash
python data/generate_historical_data.py
```
*Output: `data/historical_credit_card_fraud.csv` (1.78 MB).*

#### 3. Launch the Interactive Telemetry Simulator
Stream simulated Indian retail banking UPI/ATM/POS transactions dynamically in your terminal:
```bash
python src/simulator/event_simulator.py --dry-run
```
- **Simulator Hotkeys (Keyboard Interactive):**
  - `+` / `-` : Instantly speed up or slow down the transaction rates (up to 30 events per second).
  - `1` : Inject a **High-Value Spike Anomaly** (₹2,50,000 POS transaction).
  - `2` : Inject a **Foreign Geolocation Anismatch** (impossible travel: Hyderabad to Moscow).
  - `3` : Inject a **Rapid ATM Cash-Out Burst** (skimming/card-cloning pattern).
  - `4` : Inject a **Midnight Takeover Anomaly** (3:00 AM bank transfer via a Tor exit node).
  - `q` : Terminate the simulator gracefully.

#### 4. Run the Dynamic AI Scoring Loop & Local Scoring Daemon
Run the local background scoring engine. It loads your serialized classification model (`models/fraud_forest_model.pkl`), evaluates raw incoming events, applies advanced rulesets, and outputs rich Markdown explanations:
```bash
# Trains model from historical data and runs one single scoring sweep
python src/simulator/local_scoring_loop.py

# Run continuously, checking for unscored transactions every 10 seconds
python src/simulator/local_scoring_loop.py --loop --interval 10
```

#### 5. Launch the Streamlit Operational Dashboard
Open a new terminal session and launch the Obsidian Glass executive dashboard:
```bash
streamlit run src/dashboard/app.py
```
Your browser will open to the dashboard. The app has high-fidelity mock fallbacks so you can interact with mock metrics, view live maps, trigger alerts, and run the Copilot even if not connected to live Fabric databases.

---

### ☁️ Pathway B: Cloud Fabric Deployment (Azure & Microsoft Fabric)

Orchestrate a fully wired real-time cloud data warehouse and streaming engine inside your Microsoft Fabric workspace.

#### 1. Log in to Azure Developer CLI & Azure CLI
Make sure you are authenticated to your Entra ID tenant containing your Microsoft Fabric development capacity:
```bash
az login
```

#### 2. Configure Your Capacity Properties
Open [config/accelerator-config.json](file:///c:/Users/015237/Desktop/MyTest/smart-banking-ai-powered/config/accelerator-config.json) and set your custom deployment parameters:
```json
{
  "subscriptionId": "YOUR_AZURE_SUBSCRIPTION_ID",
  "resourceGroup": "rg-banking-fraud-dev",
  "capacityName": "bankingfabriccapdev",
  "location": "CentralIndia"
}
```

#### 3. Automated One-Click Deployment via `azd`
If you have [Azure Developer CLI (`azd`)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) installed, provision the Azure compute capacity and deploy all Fabric workspace items in one click:
```bash
azd up
```
* **Under the Hood:** `azd` Bicep scripts deploy your F2 Capacity, create your workspace `SmartBankingRiskWorkspace`, provision OneLake Lakehouse storage, set up the Real-Time Eventhouse, deploy KQL schemas (`schema.kql`), and automatically upload the historical dataset!

#### 4. Step-by-Step Shell Deployment
If you do not have `azd` installed, execute the deployment stages using PowerShell:

```powershell
# A. Provision Fabric capacity in Azure via Bicep Template
.\infra\create-capacity.ps1

# B. Auto-deploy and wire workspace items via Fabric REST APIs
.\scripts\provision-fabric.ps1
```

#### 5. Connect the Live Eventstream & Stream Telemetry
1. Open the [Microsoft Fabric Portal](https://app.fabric.microsoft.com/).
2. Navigate to your new workspace `SmartBankingRiskWorkspace`.
3. Open `BankingTransactionStream`, select the **Custom App** source node, and copy the unique **REST API Endpoint URL**.
4. Paste this URL into your `.env` file under `EVENTSTREAM_CUSTOM_ENDPOINT`.
5. Run the live simulator without the `--dry-run` flag to start feeding Microsoft Fabric:
   ```bash
   python src/simulator/event_simulator.py
   ```
6. Paste the query endpoint URI of your KQL database into your `.env` file under `KQL_QUERY_URI`.
7. Start your local scoring loop daemon (`local_scoring_loop.py --loop`) or run the dashboard (`app.py`) to see real-time updates and interactive charts feed directly from your Fabric cloud database!

---

## 🤖 Real-Time Data Agents & Fabric Notebooks

The platform includes two powerful Synapse Spark notebooks that run directly inside Microsoft Fabric to orchestrate automated operations:

1. **`rti_notebook_smartbanking_data_agent.ipynb` (Fabric Data Agent):**
   - Implements the core real-time monitoring agent. It leverages Microsoft Fabric Real-Time Intelligence capabilities to poll incoming Eventstream telemetry, detect critical rule breaches (like midnight IP anomalies), and queue immediate security mitigation webhooks.
2. **`rti_notebook_myrealtimeaigmbe2.ipynb` (Model Evaluator & AI Orchestrator):**
   - Manages notebook-driven AI scoring. It reads streaming transaction data from Eventhouse Delta logs, invokes the Random Forest ML classifier, integrates with OpenAI API keys to generate natural language explanations of anomalies, and stores the completed records back into the KQL tables.

### Uploading Notebooks to Microsoft Fabric Workspace
1. In the Microsoft Fabric portal, select the **Synapse Data Engineering** experience.
2. Click **Import Notebook** in your workspace homepage.
3. Select `rti_notebook_smartbanking_data_agent.ipynb` and `rti_notebook_myrealtimeaigmbe2.ipynb` from the root directory of this repository to upload them.
4. Bind the notebooks to your newly created `BankingFraudLakehouse` to give them read/write access to your historical Delta tables.

---

## 🧼 Cleanup & Teardown

To prevent ongoing charges from your Azure subscription, clean up your resources when done:

- **Via `azd`:**
  ```bash
  azd down --purge --force
  ```
- **Manually:**
  1. Navigate to the Azure Portal, open your resource group (e.g., `rg-banking-fraud-dev`), and click **Delete Resource Group**.
  2. In the Microsoft Fabric portal, go to `SmartBankingRiskWorkspace` > **Workspace Settings** > **Other** and click **Remove this workspace**.

---

## 🎨 Design System & Customization

This accelerator is built around modular, well-structured building blocks that make it easy to adapt to other real-time analytics scenarios:
- **Retail Banking Context:** Customize `src/simulator/event_simulator.py` to stream alternative customer transactions and alert on payment channel compromises.
- **Logistics & Telematics:** Repurpose the schema in `src/definitions/kql/schema.kql` to represent fleet routing metrics (latitude, longitude, speed, fuel rate, brake temperature) to trigger real-time driver warnings.
- **Smart Grid Utilities:** Stream smart grid readings (voltage, load demand, transformer heat sensors) to predict local voltage drops or mechanical equipment failures.
