# ⛓ IntelliChain
### AI-Driven Self-Evolving Blockchain with Adaptive Consensus

> *"A blockchain that is not fixed, but self-evolving, optimizing security, scalability, and performance dynamically."*

---

## 🚀 Overview

**IntelliChain** is a hackathon-grade intelligent blockchain simulation that dynamically selects, switches, and evolves consensus mechanisms in real time based on AI-predicted network conditions.

Instead of a static consensus protocol, IntelliChain uses a **machine-learning prediction engine** and a rule-based **Adaptive Consensus Engine (ACE)** to switch between:

| Consensus | Best For |
|---|---|
| **PoW** — Proof of Work | Low-node networks, maximum trust |
| **PoS** — Proof of Stake | High throughput, low latency conditions |
| **PBFT** — Byzantine Fault Tolerance | High attack risk, security-critical states |
| **Hybrid** (PoS+PBFT / PoW+PoS) | Mixed or uncertain conditions |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| UI / Dashboard | Streamlit |
| AI Prediction | scikit-learn (Decision Tree) |
| Visualization | Matplotlib, Seaborn |
| Blockchain | Custom Python Classes |
| Hashing | SHA-256 (hashlib) |
| Data | Pandas, NumPy, JSON |

---

## 📁 Project Structure

```
intelli_chain/
│
├── app.py                        ← Main Streamlit app (entry point)
│
├── modules/
│   ├── network_monitor.py        ← Real-time network simulation
│   ├── prediction_engine.py      ← ML-based traffic & attack prediction
│   ├── consensus_engine.py       ← Adaptive Consensus Engine (ACE)
│   ├── blockchain.py             ← Block and Blockchain classes
│   └── block_creator.py          ← Block assembly and chain addition
│
├── analytics/
│   ├── tracker.py                ← Metadata tracking & efficiency scoring
│   └── charts.py                 ← Dark-theme visualization suite
│
├── utils/
│   ├── hashing.py                ← SHA-256 block hashing
│   └── helpers.py                ← Shared utilities
│
├── data/
│   └── blockchain_data.json      ← Auto-generated analytics output
│
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone / Download

```bash
git clone <repo-url>
cd intelli_chain
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🎮 Simulation Scenarios

### Scenario 1 — Normal Operations
- Nodes: 25, TX Rate: 150, Attack: OFF
- Expected consensus: PoS (efficient for medium load)

### Scenario 2 — High Traffic Spike
- Nodes: 50, TX Rate: 400, Attack: OFF
- Expected consensus: PoS or Hybrid (PoW+PoS)

### Scenario 3 — Active Attack Simulation
- Nodes: 30, TX Rate: 200, Attack: ON
- Expected consensus: PBFT or Hybrid (PoS+PBFT)

### Scenario 4 — Sparse Network
- Nodes: 5, TX Rate: 50, Attack: OFF
- Expected consensus: PoW (max trust on small network)

### Scenario 5 — Full Stress Test
- Nodes: 100, TX Rate: 500, Attack: ON, Blocks: 30
- Expected: Frequent consensus switching, threat events logged

---

## 🧠 How the AI Works

1. **NetworkMonitor** samples real-time (simulated) metrics including nodes, TX rate, latency, and threat signals
2. **PredictionEngine** uses a Decision Tree trained on synthetic data to predict:
   - Congestion level (Low / Medium / High)
   - Traffic spike probability
   - Attack risk probability
3. **AdaptiveConsensusEngine (ACE)** applies rule-based logic on top of predictions to select the optimal consensus

---

## 📊 Analytics Dashboard

The Analytics tab shows:
- **Consensus Distribution** — donut chart of how often each consensus was used
- **Performance Trends** — latency, TX rate, and efficiency over time
- **Latency vs Throughput** — scatter plot with trend line
- **Consensus Switching Timeline** — when and why the system changed consensus
- **Threat Heatmap** — visual threat level across all blocks
- **Switch Log** — tabular consensus change events
- **Threat Log** — all detected threat events and system responses

---

## 🔐 Block Structure

Each block contains:
```json
{
  "block_id": 5,
  "previous_hash": "abc123...",
  "hash": "sha256...",
  "timestamp": "2024-01-01T12:00:00",
  "transactions": ["TX-123456", "TX-789012"],
  "consensus": "PBFT",
  "block_time": 1.47,
  "latency": 134.2,
  "tx_count": 87
}
```

---

## 🎨 Design Theme

IntelliChain uses a **Cyberpunk Dark** aesthetic:
- Primary palette: Rich Black, Neon Green, Caribbean Green
- Fonts: Share Tech Mono (display), Exo 2 (body)
- Glow accents, dark panels, futuristic typography

---

## 📄 License

MIT License — open for hackathon submission and educational use.

---

*Built for the future of decentralized, intelligent infrastructure.*
