"""
IntelliChain v2 — AI-Driven Self-Evolving Blockchain
Main Streamlit Application

Run with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import time, random, json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from modules.network_monitor   import NetworkMonitor
from modules.prediction_engine import PredictionEngine
from modules.consensus_engine  import AdaptiveConsensusEngine, get_mechanism_color
from modules.blockchain        import Blockchain
from modules.block_creator     import BlockCreator
from analytics.tracker         import AnalyticsTracker
from analytics.charts import (
    chart_consensus_distribution,
    chart_performance_trends,
    chart_latency_vs_throughput,
    chart_consensus_timeline,
    chart_threat_heatmap,
    chart_network_radar,
    chart_scoring_matrix,
    chart_confidence_trend,
    sparkline,
)
from utils.helpers import threat_label, efficiency_color

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IntelliChain",
    page_icon="⛓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Cyberpunk CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

:root {
    --bg:      #080D08;
    --panel:   #0C1410;
    --panel2:  #0E1A0E;
    --green:   #00FF9C;
    --mid:     #00CC7A;
    --dark:    #003322;
    --accent:  #7DFFB3;
    --text:    #C8F0D8;
    --muted:   #4A7A5A;
    --amber:   #FFB800;
    --red:     #FF3C5A;
    --blue:    #00BFFF;
    --purple:  #C87FFF;
    --border:  #1A3A20;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Exo 2', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070C07 0%, #050A05 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3 { color: var(--green) !important; }
h1 { font-family: 'Share Tech Mono', monospace !important; letter-spacing: 3px; }
h3 { letter-spacing: 1px; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--panel), var(--panel2)) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    position: relative;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--green);
    border-radius: 8px 0 0 8px;
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-size: 10px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--green) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 22px !important;
}

.stButton>button {
    background: linear-gradient(135deg, #002A1A, #005533) !important;
    color: var(--green) !important;
    border: 1px solid var(--green) !important;
    border-radius: 5px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 13px !important;
    letter-spacing: 2px !important;
    padding: 10px 24px !important;
    transition: all 0.25s !important;
    text-transform: uppercase !important;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #003A22, #007744) !important;
    box-shadow: 0 0 20px rgba(0,255,156,0.35) !important;
}

hr { border-color: var(--border) !important; opacity: 0.4 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--panel) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--green) !important;
    border-bottom: 2px solid var(--green) !important;
    background: rgba(0,255,156,0.04) !important;
}

code, pre { background: #0A1A0A !important; color: var(--accent) !important; font-family: 'Share Tech Mono', monospace !important; }
[data-testid="stExpander"] { background: var(--panel) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* ── Custom components ── */
.intel-box {
    background: linear-gradient(135deg, #0B1A0C, #0E200E);
    border: 1px solid #1E3A22;
    border-left: 3px solid var(--green);
    border-radius: 6px;
    padding: 16px 20px;
    margin: 8px 0;
    font-family: 'Share Tech Mono', monospace;
}
.intel-box.danger { border-left-color: var(--red)    !important; }
.intel-box.warn   { border-left-color: var(--amber)  !important; }
.intel-box.info   { border-left-color: var(--blue)   !important; }
.intel-box.purple { border-left-color: var(--purple) !important; }

.block-card {
    background: linear-gradient(135deg, #0B1A0C, #0D1C0D);
    border: 1px solid #1E3A22;
    border-radius: 8px;
    padding: 16px;
    margin: 6px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    line-height: 1.7;
}
.block-id   { color: #00FF9C; font-size: 15px; font-weight: bold; letter-spacing: 1px; }
.hash-text  { color: #3A6A4A; word-break: break-all; font-size: 10px; }

.chain-link {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
    padding: 10px 14px;
    background: #0C180C;
    border: 1px solid #1A3A1A;
    border-radius: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
}

.stat-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 10px;
    font-family: 'Share Tech Mono', monospace;
    margin: 2px;
    border: 1px solid;
}

.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #4A7A5A;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1A3A1A;
}

.score-display {
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    padding: 16px;
    border: 1px solid #1A3A1A;
    border-radius: 8px;
    background: linear-gradient(135deg, #0B1A0C, #0E200E);
}

.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00FF9C;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.4s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,255,156,0.4); }
    50%       { opacity: 0.6; box-shadow: 0 0 0 5px rgba(0,255,156,0); }
}

.banner {
    background: linear-gradient(90deg, #080D08 0%, #0C1C10 50%, #080D08 100%);
    border: 1px solid #1A3A20;
    border-radius: 10px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00FF9C, transparent);
}
</style>
""", unsafe_allow_html=True)


# ─── Session state ────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "blockchain": None, "tracker": None, "ace": None,
        "sim_run": False, "total_blocks": 0,
        "last_snapshot": None, "last_pred": None,
        "last_consensus": None, "last_block": None,
        "last_efficiency": 0.0, "all_snapshots": [],
        "all_preds": [], "all_consensus": [],
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 8px;'>
        <div style='font-family:Share Tech Mono,monospace; font-size:20px; color:#00FF9C; letter-spacing:3px;'>⛓ INTELLICHAIN</div>
        <div style='font-size:10px; color:#3A6A4A; letter-spacing:2px; margin-top:4px;'>v2.0 · ADAPTIVE CONSENSUS</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div class='section-header'>Simulation Parameters</div>", unsafe_allow_html=True)
    num_nodes  = st.slider("Active Nodes",           5,  100, 25,  5)
    tx_rate    = st.slider("Transaction Rate (TX/s)", 10, 500, 150, 10)
    num_blocks = st.slider("Blocks to Simulate",      1,  50,  8)
    attack_on  = st.toggle("⚠  Simulate Attack", value=False)

    st.markdown("<div class='section-header'>Animation</div>", unsafe_allow_html=True)
    animate    = st.toggle("Live block animation", value=True)
    anim_delay = st.slider("Animation speed (ms)", 50, 500, 120, 10) if animate else 120

    st.markdown("---")
    run_btn   = st.button("▶  RUN SIMULATION",  use_container_width=True)
    reset_btn = st.button("↺  RESET CHAIN",     use_container_width=True)

    if reset_btn:
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        _init()
        st.rerun()

    if st.session_state["sim_run"]:
        tr = st.session_state["tracker"]
        ace_obj = st.session_state["ace"]
        st.markdown("---")
        st.markdown("<div class='section-header'>Live Stats</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-family:Share Tech Mono,monospace; font-size:11px; line-height:2;'>
        <span style='color:#4A7A5A'>Blocks:</span> <span style='color:#00FF9C'>{st.session_state['total_blocks']}</span><br>
        <span style='color:#4A7A5A'>Switches:</span> <span style='color:#FFB800'>{len(tr.switching_events)}</span><br>
        <span style='color:#4A7A5A'>Threats:</span> <span style='color:#FF3C5A'>{len(tr.threat_events)}</span><br>
        <span style='color:#4A7A5A'>Stability:</span> <span style='color:#7DFFB3'>{ace_obj.stability_score():.0%}</span><br>
        <span style='color:#4A7A5A'>Avg Conf:</span> <span style='color:#00BFFF'>{ace_obj.avg_confidence():.0%}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:9px; color:#2A4A2A; font-family:Share Tech Mono,monospace; line-height:1.8;'>
    CONSENSUS: PoW · PoS · PBFT · HYBRID<br>
    AI ENGINE: Decision Tree + z-score<br>
    HASH: SHA-256 · CHAIN: Linked<br>
    BUILD: IntelliChain v2.0
    </div>
    """, unsafe_allow_html=True)


# ─── Header banner ────────────────────────────────────────────────────────────
st.markdown("""
<div class='banner'>
    <div style='font-family:Share Tech Mono,monospace; font-size:26px; color:#00FF9C; letter-spacing:4px;'>
        ⛓ INTELLICHAIN
    </div>
    <div style='font-size:11px; color:#4A7A5A; letter-spacing:3px; margin-top:6px;'>
        AI-DRIVEN SELF-EVOLVING BLOCKCHAIN  ·  ADAPTIVE CONSENSUS ENGINE  ·  REAL-TIME THREAT DETECTION
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "⛓  Blockchain Simulation",
    "📊  Analytics Dashboard",
    "🔍  Chain Explorer",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    if run_btn:
        # Fresh objects — accumulate if chain already exists
        if st.session_state["blockchain"] is None:
            blockchain = Blockchain()
            tracker    = AnalyticsTracker()
            ace        = AdaptiveConsensusEngine()
        else:
            blockchain = st.session_state["blockchain"]
            tracker    = st.session_state["tracker"]
            ace        = st.session_state["ace"]

        monitor   = NetworkMonitor(base_nodes=num_nodes, base_tx_rate=tx_rate, attack_mode=attack_on)
        predictor = PredictionEngine()
        creator   = BlockCreator(blockchain)

        # ── Live animation container ──────────────────────────────────────
        progress   = st.progress(0, text="Initializing IntelliChain...")
        live_area  = st.empty()
        block_feed = st.empty()

        for i in range(num_blocks):
            pct = int((i / num_blocks) * 100)
            progress.progress(pct, text=f"Mining block {blockchain.length}/{blockchain.length + num_blocks - i - 1 + 1}…")

            snap = monitor.sample()
            pred = predictor.predict(snap, monitor.history[:-1])
            cons = ace.select(snap, pred)
            blk  = creator.create_block(cons, snap["tx_rate"], snap["latency"])
            eff  = tracker.compute_efficiency(cons, snap)
            tracker.record_block(blk.to_dict(), snap, pred, eff, cons)

            st.session_state["all_snapshots"].append(snap)
            st.session_state["all_preds"].append(pred)
            st.session_state["all_consensus"].append(cons)

            # Live display
            if animate:
                badge_color = get_mechanism_color(cons.mechanism)
                threat_color = {"Low": "#00FF9C", "Medium": "#FFB800",
                                "High": "#FF7733", "Critical": "#FF3C5A"}.get(snap["threat_label"], "#00FF9C")
                live_area.markdown(f"""
                <div class='intel-box {"danger" if snap["threat_label"] == "Critical" else "warn" if snap["threat_label"] == "High" else ""}'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <span style='color:#4A7A5A; font-size:10px; letter-spacing:1px;'>MINING BLOCK</span>
                            <span style='color:#00FF9C; font-size:18px; margin-left:10px; font-weight:bold;'>#{blk.block_id}</span>
                        </div>
                        <div style='color:{badge_color}; font-size:14px;'>{cons.mechanism}</div>
                    </div>
                    <div style='margin-top:10px; display:flex; gap:20px; font-size:11px;'>
                        <span>Nodes: <b style='color:#7DFFB3'>{snap['nodes']}</b></span>
                        <span>TX/s: <b style='color:#00FF9C'>{snap['tx_rate']}</b></span>
                        <span>Latency: <b style='color:#FFB800'>{snap['latency']}ms</b></span>
                        <span>Threat: <b style='color:{threat_color}'>{snap['threat_label']}</b></span>
                        <span>Efficiency: <b style='color:#7DFFB3'>{eff:.2f}</b></span>
                        <span>Confidence: <b style='color:#00BFFF'>{cons.confidence:.0%}</b></span>
                    </div>
                    <div style='margin-top:8px; font-size:10px; color:#3A6A4A;'>
                        {cons.rule_triggered}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                time.sleep(anim_delay / 1000)

        progress.progress(100, text="✓ Simulation complete")
        time.sleep(0.4)
        progress.empty()
        live_area.empty()

        # Save state
        st.session_state.update({
            "blockchain":     blockchain,
            "tracker":        tracker,
            "ace":            ace,
            "sim_run":        True,
            "total_blocks":   blockchain.length - 1,
            "last_snapshot":  snap,
            "last_pred":      pred,
            "last_consensus": cons,
            "last_block":     blk,
            "last_efficiency": eff,
        })
        tracker.save_to_disk()

    # ── Results display ────────────────────────────────────────────────────
    if st.session_state["sim_run"]:
        snap  = st.session_state["last_snapshot"]
        pred  = st.session_state["last_pred"]
        cons  = st.session_state["last_consensus"]
        blk   = st.session_state["last_block"]
        eff   = st.session_state["last_efficiency"]
        bc    = st.session_state["blockchain"]
        tr    = st.session_state["tracker"]
        ace   = st.session_state["ace"]

        # ── Section: Network State ─────────────────────────────────────────
        st.markdown("<div class='section-header'>🌐 Real-Time Network State</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Active Nodes",  snap["nodes"])
        c2.metric("TX Rate",       f"{snap['tx_rate']} /s")
        c3.metric("Latency",       f"{snap['latency']} ms")
        c4.metric("Threat Level",  snap["threat_label"],
                  delta=f"Risk {snap['threat']:.0%}", delta_color="inverse")
        c5.metric("Total Blocks",  bc.length - 1)

        # Sparkline row
        if len(tr.records) >= 3:
            series = tr.performance_series()
            sp1, sp2, sp3, sp4, sp5 = st.columns(5)
            for col, vals, color, label in [
                (sp1, series["latencies"],  "#FFB800", "latency trend"),
                (sp2, series["tx_rates"],   "#00FF9C", "tx trend"),
                (sp3, series["efficiencies"], "#7DFFB3", "efficiency"),
                (sp4, series["threats"],    "#FF3C5A",  "threat"),
                (sp5, series["block_times"], "#00BFFF", "block time"),
            ]:
                fig = sparkline(vals, color=color)
                col.pyplot(fig, use_container_width=True)
                col.caption(label)
                plt.close(fig)

        st.markdown("---")

        # ── Section: AI Predictions + Radar ───────────────────────────────
        st.markdown("<div class='section-header'>🤖 AI Prediction Engine</div>", unsafe_allow_html=True)
        pred_col, radar_col = st.columns([2, 1])

        with pred_col:
            p1, p2, p3 = st.columns(3)
            spike_pct  = int(pred["traffic_spike_prob"] * 100)
            attack_pct = int(pred["attack_risk_prob"]   * 100)

            p1.metric("Traffic Spike",   f"{spike_pct}%",
                      delta="Alert" if spike_pct > 60 else "Normal",
                      delta_color="inverse" if spike_pct > 60 else "normal")
            p2.metric("Attack Risk",     f"{attack_pct}%",
                      delta="THREAT" if attack_pct > 50 else "Safe",
                      delta_color="inverse" if attack_pct > 50 else "normal")
            p3.metric("Congestion",      pred["congestion_level"])

            # Scoring matrix chart
            scoring = ace.get_scoring_matrix(snap, pred)
            fig = chart_scoring_matrix(scoring)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with radar_col:
            fig = chart_network_radar(snap, pred)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.markdown("---")

        # ── Section: ACE Decision ──────────────────────────────────────────
        st.markdown("<div class='section-header'>⚙️ Adaptive Consensus Engine (ACE)</div>", unsafe_allow_html=True)
        ace_left, ace_right = st.columns([1, 2])

        badge_color = get_mechanism_color(cons.mechanism)
        with ace_left:
            st.markdown(f"""
            <div class='intel-box {"purple" if cons.is_hybrid else ""}'>
                <div style='font-size:10px; color:#4A7A5A; letter-spacing:2px; margin-bottom:8px;'>SELECTED CONSENSUS</div>
                <div style='font-size:24px; color:{badge_color}; font-weight:bold; letter-spacing:1px;'>{cons.mechanism}</div>
                <div style='margin-top:12px; font-size:10px; color:#4A7A5A; line-height:2;'>
                    Block Time &nbsp;·&nbsp; <span style='color:#FFB800'>~{cons.block_time_estimate}s</span><br>
                    Security   &nbsp;·&nbsp; <span style='color:#00BFFF'>{cons.security_score:.0%}</span><br>
                    Throughput &nbsp;·&nbsp; <span style='color:#00FF9C'>{cons.throughput_score:.0%}</span><br>
                    ACE Confidence &nbsp;·&nbsp; <span style='color:#7DFFB3'>{cons.confidence:.0%}</span>
                </div>
                {"<div style='margin-top:10px; padding:6px 10px; background:#1A0A2A; border:1px solid #C87FFF; border-radius:4px; font-size:10px; color:#C87FFF;'>⚡ HYBRID: " + " + ".join(cons.base_mechanisms) + "</div>" if cons.is_hybrid else ""}
            </div>

            <div class='intel-box info' style='margin-top:8px;'>
                <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px; margin-bottom:6px;'>ACE RULE TRIGGERED</div>
                <div style='color:#00BFFF; font-size:11px; line-height:1.5;'>{cons.rule_triggered}</div>
            </div>
            """, unsafe_allow_html=True)

            # ACE stats
            st.markdown(f"""
            <div style='display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;'>
                <span class='stat-pill' style='border-color:#00FF9C; color:#00FF9C;'>Stability {ace.stability_score():.0%}</span>
                <span class='stat-pill' style='border-color:#FFB800; color:#FFB800;'>Avg Conf {ace.avg_confidence():.0%}</span>
                <span class='stat-pill' style='border-color:#FF3C5A; color:#FF3C5A;'>Switches {len(tr.switching_events)}</span>
            </div>
            """, unsafe_allow_html=True)

        with ace_right:
            box_cls = "danger" if pred["attack_risk_prob"] > 0.65 else ("warn" if pred["attack_risk_prob"] > 0.40 else "intel-box")
            st.markdown(f"""
            <div class='intel-box {box_cls}'>
                <div style='font-size:10px; color:#4A7A5A; letter-spacing:2px; margin-bottom:8px;'>DECISION RATIONALE</div>
                <div style='color:#C8F0D8; font-size:13px; line-height:1.7;'>{cons.reason}</div>
            </div>
            """, unsafe_allow_html=True)

            # All-time consensus breakdown
            dist = tr.consensus_distribution()
            if dist:
                st.markdown("""
                <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px; margin:12px 0 6px;'>CONSENSUS USAGE (ALL BLOCKS)</div>
                """, unsafe_allow_html=True)
                total_b = sum(dist.values())
                for mech, count in sorted(dist.items(), key=lambda x: -x[1]):
                    pct = count / total_b
                    mcolor = get_mechanism_color(mech)
                    bar_w = int(pct * 200)
                    st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:10px; margin:4px 0; font-family:Share Tech Mono,monospace; font-size:11px;'>
                        <span style='color:{mcolor}; width:140px; white-space:nowrap;'>{mech}</span>
                        <div style='background:#0C1410; border:1px solid #1A3A1A; border-radius:3px; height:12px; flex:1; overflow:hidden;'>
                            <div style='background:{mcolor}; width:{bar_w}px; max-width:100%; height:100%; border-radius:3px; opacity:0.8;'></div>
                        </div>
                        <span style='color:#4A7A5A; width:50px; text-align:right;'>{count} / {pct:.0%}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Section: Latest Block ──────────────────────────────────────────
        st.markdown("<div class='section-header'>📦 Latest Block</div>", unsafe_allow_html=True)
        bdict = blk.to_dict()
        bl1, bl2 = st.columns([1, 2])

        with bl1:
            st.markdown(f"""
            <div class='block-card'>
                <div class='block-id'>⛓ BLOCK #{bdict['block_id']}</div>
                <div style='color:#1E3A22; margin:10px 0 8px;'>{'─' * 28}</div>
                <div>Consensus&nbsp; <span style='color:{get_mechanism_color(bdict["consensus"])};'>{bdict['consensus']}</span></div>
                <div>Block Time <span style='color:#FFB800;'>{bdict['block_time']}s</span></div>
                <div>Transactions <span style='color:#7DFFB3;'>{bdict['tx_count']}</span></div>
                <div>Latency&nbsp;&nbsp;&nbsp; <span style='color:#C8F0D8;'>{bdict['latency']} ms</span></div>
                <div style='margin-top:10px; color:#3A6A4A; font-size:9px;'>{bdict['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

        with bl2:
            st.markdown(f"""
            <div class='block-card'>
                <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px; margin-bottom:4px;'>BLOCK HASH · SHA-256</div>
                <div class='hash-text'>{bdict['hash']}</div>
                <div style='margin-top:10px; font-size:10px; color:#4A7A5A; letter-spacing:1px;'>PREVIOUS HASH</div>
                <div class='hash-text'>{bdict['previous_hash']}</div>
                <div style='margin-top:10px; font-size:10px; color:#4A7A5A; letter-spacing:1px;'>TRANSACTIONS ({bdict['tx_count']})</div>
                <div style='color:#00CC7A; font-size:10px; line-height:1.8; margin-top:4px;'>
                    {' &nbsp;·&nbsp; '.join(bdict['transactions'][:8])}{'&nbsp;···' if len(bdict['transactions']) > 8 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Section: Efficiency KPIs ───────────────────────────────────────
        st.markdown("<div class='section-header'>📈 Efficiency & Chain Health</div>", unsafe_allow_html=True)
        e1, e2, e3, e4, e5, e6 = st.columns(6)
        series = tr.performance_series()
        avg_eff  = float(np.mean(series["efficiencies"])) if series else 0
        avg_lat  = float(np.mean(series["latencies"]))    if series else 0
        avg_bt   = float(np.mean(series["block_times"]))  if series else 0

        e1.metric("Last Efficiency",  f"{eff:.2f}",    delta="Optimal" if eff > 0.75 else "Low")
        e2.metric("Avg Efficiency",   f"{avg_eff:.2f}")
        e3.metric("Chain Valid",      "✓ YES" if bc.is_chain_valid() else "✗ NO")
        e4.metric("Avg Latency",      f"{avg_lat:.0f}ms")
        e5.metric("Avg Block Time",   f"{avg_bt:.2f}s")
        e6.metric("ACE Stability",    f"{ace.stability_score():.0%}")

        # Confidence trend
        if len(tr.records) >= 3:
            st.markdown("---")
            fig = chart_confidence_trend(tr.records)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    else:
        # Welcome screen
        st.markdown("""
        <div style='text-align:center; padding:70px 20px; border:1px dashed #1A3A1A; border-radius:12px; margin:20px 0;'>
            <div style='font-size:52px; margin-bottom:16px;'>⛓</div>
            <div style='font-family:Share Tech Mono,monospace; font-size:22px; color:#00FF9C; letter-spacing:3px; margin-bottom:10px;'>INTELLICHAIN READY</div>
            <div style='font-family:Share Tech Mono,monospace; font-size:11px; color:#4A7A5A; line-height:2.2;'>
                Configure parameters in the sidebar &nbsp;·&nbsp; Press <b style='color:#00CC7A'>RUN SIMULATION</b><br>
                CONSENSUS MODES: PoW &nbsp;·&nbsp; PoS &nbsp;·&nbsp; PBFT &nbsp;·&nbsp; HYBRID<br>
                AI ENGINE: Decision Tree + Probabilistic Signals<br>
                HASH ALGORITHM: SHA-256 &nbsp;·&nbsp; CHAIN: Linked Blocks
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    tr = st.session_state.get("tracker")

    if not tr or not tr.records:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; border:1px dashed #1A3A1A; border-radius:12px; margin:20px 0;'>
            <div style='font-size:40px;'>📊</div>
            <div style='font-family:Share Tech Mono,monospace; font-size:16px; color:#00FF9C; margin:12px 0;'>NO ANALYTICS DATA</div>
            <div style='font-size:12px; color:#4A7A5A; font-family:Share Tech Mono,monospace;'>Run a simulation to populate the dashboard.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        dist    = tr.consensus_distribution()
        series  = tr.performance_series()
        records = tr.records
        ace     = st.session_state["ace"]

        # KPI row
        st.markdown("<div class='section-header'>📊 Session Overview</div>", unsafe_allow_html=True)
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Total Blocks",    len(records))
        k2.metric("Avg Efficiency",  f"{np.mean(series['efficiencies']):.2f}")
        k3.metric("Avg Latency",     f"{np.mean(series['latencies']):.0f} ms")
        k4.metric("ACE Switches",    len(tr.switching_events))
        k5.metric("Threat Events",   len(tr.threat_events))
        k6.metric("ACE Stability",   f"{ace.stability_score():.0%}")

        st.markdown("---")

        # Charts row 1
        st.markdown("<div class='section-header'>Consensus & Network</div>", unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            fig = chart_consensus_distribution(dist)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with ch2:
            fig = chart_latency_vs_throughput(series, records)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.markdown("---")
        st.markdown("<div class='section-header'>Performance Trends</div>", unsafe_allow_html=True)
        fig = chart_performance_trends(series)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")
        st.markdown("<div class='section-header'>Consensus Switching Timeline</div>", unsafe_allow_html=True)
        fig = chart_consensus_timeline(records)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")
        st.markdown("<div class='section-header'>Threat Detection Heatmap</div>", unsafe_allow_html=True)
        fig = chart_threat_heatmap(records)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")
        st.markdown("<div class='section-header'>Efficiency vs ACE Confidence</div>", unsafe_allow_html=True)
        fig = chart_confidence_trend(records)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")

        # Logs
        if tr.switching_events:
            st.markdown("<div class='section-header'>Consensus Switch Log</div>", unsafe_allow_html=True)
            df = pd.DataFrame([{
                "Block": e["block_id"], "From": e["from"],
                "To": e["to"], "Time": e["timestamp"][:19],
            } for e in tr.switching_events])
            st.dataframe(df, use_container_width=True, hide_index=True)

        if tr.threat_events:
            st.markdown("<div class='section-header'>Threat Event Log</div>", unsafe_allow_html=True)
            df = pd.DataFrame([{
                "Block": e["block_id"], "Level": e["threat_level"],
                "Score": f"{e['threat_score']:.2%}",
                "Attack Risk": f"{e['attack_risk']:.2%}",
                "Response": e["consensus_chosen"],
                "Time": e["timestamp"][:19],
            } for e in tr.threat_events])
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Download
        with st.expander("💾 Export Analytics Data (JSON)", expanded=False):
            payload = {
                "records": records,
                "switching_events": tr.switching_events,
                "threat_events": tr.threat_events,
                "ace_evolution": ace.evolution_history,
            }
            st.download_button(
                "Download blockchain_data.json",
                data=json.dumps(payload, indent=2),
                file_name="intellichain_data.json",
                mime="application/json",
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHAIN EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    bc = st.session_state.get("blockchain")

    if not bc or bc.length <= 1:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; border:1px dashed #1A3A1A; border-radius:12px; margin:20px 0;'>
            <div style='font-size:40px;'>🔍</div>
            <div style='font-family:Share Tech Mono,monospace; font-size:16px; color:#00FF9C; margin:12px 0;'>CHAIN EXPLORER</div>
            <div style='font-size:12px; color:#4A7A5A; font-family:Share Tech Mono,monospace;'>Run a simulation to populate the chain.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        blocks = bc.get_blocks_as_dicts()
        tr     = st.session_state["tracker"]

        # Chain integrity banner
        valid = bc.is_chain_valid()
        banner_color = "#00FF9C" if valid else "#FF3C5A"
        st.markdown(f"""
        <div style='background:{"#0B1A0C" if valid else "#1A0B0C"}; border:1px solid {"#1E3A22" if valid else "#3A1E1E"};
                    border-left:3px solid {banner_color}; border-radius:6px; padding:14px 20px; margin-bottom:16px;
                    font-family:Share Tech Mono,monospace; display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span style='color:#4A7A5A; font-size:10px; letter-spacing:2px;'>CHAIN INTEGRITY</span>
                <span style='color:{banner_color}; font-size:16px; margin-left:16px;'>{"✓ VALID — All block hashes verified" if valid else "✗ CORRUPTED — Hash mismatch detected"}</span>
            </div>
            <div style='color:#4A7A5A; font-size:11px;'>{len(blocks)} total blocks (incl. genesis)</div>
        </div>
        """, unsafe_allow_html=True)

        # Search / filter
        st.markdown("<div class='section-header'>Block Search</div>", unsafe_allow_html=True)
        sf1, sf2 = st.columns([2, 1])
        with sf1:
            search_id = st.number_input("Jump to Block ID", min_value=0,
                                        max_value=len(blocks)-1, value=len(blocks)-1)
        with sf2:
            filter_cons = st.selectbox("Filter by Consensus", ["All"] + list(set(b["consensus"] for b in blocks[1:])))

        # Single block deep-dive
        if 0 <= search_id < len(blocks):
            b = blocks[search_id]
            st.markdown("<div class='section-header'>Block Detail</div>", unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"""
                <div class='block-card'>
                    <div class='block-id'>⛓ BLOCK #{b['block_id']} {"· GENESIS" if b['block_id']==0 else ""}</div>
                    <div style='color:#1E3A22; margin:8px 0;'>{'─'*28}</div>
                    <div style='line-height:2;'>
                        <div>Consensus &nbsp;<span style='color:{get_mechanism_color(b["consensus"])};'>{b['consensus']}</span></div>
                        <div>Block Time <span style='color:#FFB800;'>{b['block_time']}s</span></div>
                        <div>TX Count &nbsp;<span style='color:#7DFFB3;'>{b['tx_count']}</span></div>
                        <div>Latency &nbsp;&nbsp;<span style='color:#C8F0D8;'>{b['latency']} ms</span></div>
                        <div>Timestamp</div>
                        <div style='color:#3A6A4A; font-size:10px;'>{b['timestamp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with d2:
                st.markdown(f"""
                <div class='block-card'>
                    <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px;'>BLOCK HASH</div>
                    <div class='hash-text' style='margin-bottom:10px;'>{b['hash']}</div>
                    <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px;'>PREVIOUS HASH</div>
                    <div class='hash-text' style='margin-bottom:10px;'>{b['previous_hash']}</div>
                    <div style='font-size:10px; color:#4A7A5A; letter-spacing:1px;'>HASH VALID</div>
                    <div style='color:{"#00FF9C" if b["block_id"]==0 else "#00FF9C" if bc.chain[b["block_id"]].is_valid() else "#FF3C5A"};'>
                        {"✓ YES" if b["block_id"]==0 or bc.chain[b["block_id"]].is_valid() else "✗ NO"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Full transactions list
            if b['transactions'] and b['transactions'] != ['GENESIS']:
                with st.expander(f"📋 All {b['tx_count']} Transactions in Block #{b['block_id']}", expanded=False):
                    tx_df = pd.DataFrame({"#": range(1, len(b['transactions'])+1),
                                          "Transaction ID": b['transactions']})
                    st.dataframe(tx_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Full chain table
        st.markdown("<div class='section-header'>Full Chain Ledger</div>", unsafe_allow_html=True)
        display_blocks = blocks[1:] if filter_cons == "All" else [b for b in blocks[1:] if b["consensus"] == filter_cons]

        rows = [{
            "Block #":        b["block_id"],
            "Consensus":      b["consensus"],
            "TX Count":       b["tx_count"],
            "Block Time (s)": b["block_time"],
            "Latency (ms)":   b["latency"],
            "Hash (prefix)":  b["hash"][:20] + "…",
            "Prev (prefix)":  b["previous_hash"][:12] + "…",
            "Timestamp":      b["timestamp"][:19],
        } for b in display_blocks]

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("---")

        # Visual chain diagram (last 10 blocks)
        st.markdown("<div class='section-header'>Visual Chain (last 10 blocks)</div>", unsafe_allow_html=True)
        recent = blocks[-10:]
        chain_html = "<div style='overflow-x:auto; white-space:nowrap; padding:10px 0;'>"
        for i, b in enumerate(recent):
            color = get_mechanism_color(b["consensus"])
            arrow = "<span style='color:#1E3A22; font-size:18px; margin:0 4px;'>→</span>" if i > 0 else ""
            chain_html += (
                f"{arrow}"
                f"<div style='display:inline-block; vertical-align:top; background:#0C1810; border:1px solid {color}33;"
                f"            border-top:2px solid {color}; border-radius:6px; padding:10px 14px; min-width:120px;"
                f"            font-family:Share Tech Mono,monospace; font-size:10px;'>"
                f"    <div style='color:{color}; font-weight:bold; font-size:12px;'>#{b['block_id']}</div>"
                f"    <div style='color:#4A7A5A; margin:4px 0;'>{b['consensus'][:12]}</div>"
                f"    <div style='color:#3A6A4A;'>{b['tx_count']} TX</div>"
                f"    <div style='color:#2A5A3A; font-size:9px; margin-top:4px;'>{b['hash'][:8]}…</div>"
                f"</div>"
            )
        chain_html += "</div>"
        st.markdown(chain_html, unsafe_allow_html=True)
