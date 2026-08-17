# Composio 100-App Research Agent & Product Ops Case Study

An automated AI research pipeline and multi-pass verification loop evaluating developer access, authentication patterns, and buildability feasibility across 100 SaaS applications for Composio agent toolkits and MCP servers.

## 🔗 Live Deliverables
* **Live Case Study Dashboard:** `https://<your-username>.github.io/<your-repo-name>/`
* **Source Repository:** `https://github.com/<your-username>/<your-repo-name>`

---

## 🏗️ Architecture & Workflow

1. **Seed Dataset (`seed_apps.json`):** 100 target applications distributed across 10 distinct categories.
2. **Schema Definition (`schema.py`):** Pydantic contract enforcing structured outputs (`app_name`, `auth_method`, `access_model`, `api_surface`, `buildability_verdict`, `evidence_url`).
3. **Agent Research Pass (`research_agent.py`):** LLM-powered extraction pipeline using structured outputs to determine initial developer access patterns.
4. **Verification & Audit Loop (`verify_pipeline.py` & `patch_dataset.py`):**
   * Pings `evidence_url` endpoints to detect dead or broken doc links.
   * Multi-agent cross-examination comparing Pass 1 vs. Ground Truth to audit hallucinations (e.g., edge-case AI tools, CLI wrappers).
   * Measures accuracy progression from initial agent pass to verified ground truth.
5. **Dashboard Generation (`build_dashboard.py`):** Compiles the verified dataset, headline patterns, and architecture audit log into a standalone, scannable single-page case study (`index.html`).

---

## 🚀 How to Run Locally

### 1. Clone & Set Up Environment
```bash
git clone [https://github.com/](https://github.com/)<your-username>/<your-repo-name>.git
cd <your-repo-name>
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
