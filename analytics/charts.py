"""
IntelliChain - Analytics Charts v2
Visually powerful dark cyberpunk charts using matplotlib and seaborn.

New in v2:
  - Network health radar chart
  - Confidence score trend line
  - Consensus score bar chart (scoring matrix)
  - Mini inline sparklines
  - Improved aesthetics throughout
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import numpy as np
from collections import Counter

# ─── Color Palette ────────────────────────────────────────────────────────────
BG_COLOR    = "#080D08"
PANEL_COLOR = "#0C1410"
NEON_GREEN  = "#00FF9C"
MID_GREEN   = "#00CC7A"
DARK_GREEN  = "#005533"
ACCENT      = "#7DFFB3"
WARN_AMBER  = "#FFB800"
DANGER_RED  = "#FF3C5A"
INFO_BLUE   = "#00BFFF"
PURPLE      = "#C87FFF"
GRID_COLOR  = "#162216"
TEXT_COLOR  = "#C8F0D8"
MUTED_COLOR = "#3A6A4A"
SPINE_COLOR = "#1A3020"

CONSENSUS_COLORS = {
    "PoW":  WARN_AMBER,
    "PoS":  NEON_GREEN,
    "PBFT": INFO_BLUE,
}

def _get_consensus_color(label: str) -> str:
    if "Hybrid" in label:
        if "PoS" in label and "PBFT" in label:
            return PURPLE
        return "#FF7F50"
    for key, color in CONSENSUS_COLORS.items():
        if key in label:
            return color
    return NEON_GREEN


def _apply_dark_style(fig, axes):
    """Apply IntelliChain cyberpunk dark theme to all axes."""
    fig.patch.set_facecolor(BG_COLOR)
    if not hasattr(axes, '__iter__'):
        axes = [axes]
    for ax in axes:
        if ax is None:
            continue
        ax.set_facecolor(PANEL_COLOR)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8.5)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(NEON_GREEN)
        for spine in ax.spines.values():
            spine.set_edgecolor(SPINE_COLOR)
        ax.grid(True, color=GRID_COLOR, linewidth=0.5, linestyle="--", alpha=0.7)


def _empty_chart(message: str, size=(6, 3)) -> plt.Figure:
    fig, ax = plt.subplots(figsize=size)
    ax.text(0.5, 0.5, message, ha="center", va="center",
            color=NEON_GREEN, fontsize=11, transform=ax.transAxes,
            fontfamily="monospace")
    _apply_dark_style(fig, [ax])
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig


# ─── Chart 1: Consensus Distribution (Donut) ─────────────────────────────────
def chart_consensus_distribution(distribution: dict) -> plt.Figure:
    if not distribution:
        return _empty_chart("No data yet")

    labels = list(distribution.keys())
    sizes  = list(distribution.values())
    colors = [_get_consensus_color(l) for l in labels]

    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, _, autotexts = ax.pie(
        sizes, labels=None, autopct="%1.1f%%", startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.58, edgecolor=BG_COLOR, linewidth=2.5),
        pctdistance=0.77,
    )
    for t in autotexts:
        t.set_color(BG_COLOR)
        t.set_fontsize(9)
        t.set_fontweight("bold")

    # Center annotation
    total = sum(sizes)
    ax.text(0, 0, f"{total}\nblocks", ha="center", va="center",
            color=NEON_GREEN, fontsize=10, fontfamily="monospace",
            fontweight="bold")

    ax.legend(wedges, labels, loc="lower center", ncol=2,
              facecolor=PANEL_COLOR, edgecolor=SPINE_COLOR,
              labelcolor=TEXT_COLOR, fontsize=8,
              bbox_to_anchor=(0.5, -0.10))
    ax.set_title("Consensus Distribution", fontsize=13, fontweight="bold",
                 color=NEON_GREEN, pad=14)

    _apply_dark_style(fig, [ax])
    fig.tight_layout()
    return fig


# ─── Chart 2: Performance Trends (3-panel) ───────────────────────────────────
def chart_performance_trends(series: dict) -> plt.Figure:
    if not series or not series.get("block_ids"):
        return _empty_chart("No performance data yet", size=(9, 6))

    ids        = series["block_ids"]
    latencies  = series["latencies"]
    tx_rates   = series["tx_rates"]
    efficiency = series["efficiencies"]
    threats    = series.get("threats", [0] * len(ids))

    fig, axes = plt.subplots(4, 1, figsize=(9, 9), sharex=True,
                              gridspec_kw={"height_ratios": [1.5, 1.5, 1.5, 0.8]})

    # Panel 1: Latency
    axes[0].plot(ids, latencies, color=WARN_AMBER, lw=2.0, marker="o", ms=3.5, zorder=5)
    axes[0].fill_between(ids, latencies, alpha=0.15, color=WARN_AMBER)
    axes[0].set_ylabel("Latency (ms)", color=TEXT_COLOR, fontsize=9)
    axes[0].set_title("Network Performance & Efficiency Trends", color=NEON_GREEN, fontsize=12, pad=10)

    # Panel 2: TX Rate
    axes[1].plot(ids, tx_rates, color=NEON_GREEN, lw=2.0, marker="o", ms=3.5, zorder=5)
    axes[1].fill_between(ids, tx_rates, alpha=0.12, color=NEON_GREEN)
    axes[1].set_ylabel("TX / sec", color=TEXT_COLOR, fontsize=9)

    # Panel 3: Efficiency
    axes[2].plot(ids, efficiency, color=ACCENT, lw=2.2, marker="o", ms=3.5, zorder=5)
    axes[2].fill_between(ids, efficiency, alpha=0.15, color=ACCENT)
    axes[2].set_ylim(0, 1.08)
    axes[2].axhline(0.75, color=NEON_GREEN, lw=0.8, ls="--", alpha=0.5, label="Target 0.75")
    axes[2].set_ylabel("Efficiency", color=TEXT_COLOR, fontsize=9)
    axes[2].legend(facecolor=PANEL_COLOR, edgecolor=SPINE_COLOR,
                   labelcolor=TEXT_COLOR, fontsize=7)

    # Panel 4: Threat bar
    bar_colors = [DANGER_RED if t > 0.6 else (WARN_AMBER if t > 0.35 else MID_GREEN)
                  for t in threats]
    axes[3].bar(ids, threats, color=bar_colors, width=0.7, alpha=0.85)
    axes[3].set_ylim(0, 1.1)
    axes[3].set_ylabel("Threat", color=TEXT_COLOR, fontsize=9)
    axes[3].set_xlabel("Block ID", color=TEXT_COLOR, fontsize=9)

    _apply_dark_style(fig, axes)
    fig.tight_layout(h_pad=0.6)
    return fig


# ─── Chart 3: Latency vs Throughput (Scatter) ────────────────────────────────
def chart_latency_vs_throughput(series: dict, records: list = None) -> plt.Figure:
    if not series or not series.get("block_ids"):
        return _empty_chart("No data yet")

    latencies = series["latencies"]
    tx_rates  = series["tx_rates"]

    # Color points by efficiency if available
    effs = series.get("efficiencies", [0.7] * len(latencies))
    cmap_vals = np.array(effs)

    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(latencies, tx_rates, c=cmap_vals, cmap="YlGn",
                    vmin=0.3, vmax=1.0, alpha=0.85, s=55,
                    edgecolors=DARK_GREEN, linewidth=0.6, zorder=5)

    cbar = plt.colorbar(sc, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label("Efficiency", color=TEXT_COLOR, fontsize=9)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR, fontsize=8)
    cbar.outline.set_edgecolor(SPINE_COLOR)

    if len(latencies) >= 3:
        z = np.polyfit(latencies, tx_rates, 1)
        p = np.poly1d(z)
        xl = np.linspace(min(latencies), max(latencies), 100)
        ax.plot(xl, p(xl), "--", color=ACCENT, lw=1.3, alpha=0.7, label="Trend")
        ax.legend(facecolor=PANEL_COLOR, edgecolor=SPINE_COLOR,
                  labelcolor=TEXT_COLOR, fontsize=8)

    ax.set_xlabel("Latency (ms)", color=TEXT_COLOR)
    ax.set_ylabel("Transaction Rate (TX/s)", color=TEXT_COLOR)
    ax.set_title("Latency vs Throughput", color=NEON_GREEN, fontsize=12)
    _apply_dark_style(fig, [ax])
    fig.tight_layout()
    return fig


# ─── Chart 4: Consensus Switching Timeline ───────────────────────────────────
def chart_consensus_timeline(records: list) -> plt.Figure:
    if not records:
        return _empty_chart("No timeline data yet", size=(9, 4))

    block_ids  = [r["block_id"] for r in records]
    mechanisms = [r["consensus"] for r in records]
    unique     = sorted(set(mechanisms))
    y_map      = {m: i for i, m in enumerate(unique)}

    fig, ax = plt.subplots(figsize=(9, 4))

    # Draw connecting lines first
    for i in range(1, len(block_ids)):
        x0, x1 = block_ids[i-1], block_ids[i]
        y0, y1 = y_map[mechanisms[i-1]], y_map[mechanisms[i]]
        color = _get_consensus_color(mechanisms[i])
        ax.plot([x0, x1], [y0, y1], color=color, lw=1.5, alpha=0.45, zorder=3)

    # Draw points on top
    for bid, mech in zip(block_ids, mechanisms):
        color = _get_consensus_color(mech)
        ax.scatter(bid, y_map[mech], color=color, s=70, zorder=6,
                   edgecolors=BG_COLOR, linewidth=0.8)

    # Highlight switches
    for i in range(1, len(mechanisms)):
        if mechanisms[i] != mechanisms[i-1]:
            ax.axvline(block_ids[i], color=DANGER_RED, lw=0.8, ls=":", alpha=0.5)

    ax.set_yticks(list(y_map.values()))
    ax.set_yticklabels(list(y_map.keys()), color=TEXT_COLOR, fontsize=9)
    ax.set_xlabel("Block ID", color=TEXT_COLOR)
    ax.set_title("Consensus Switching Timeline  ┆  dashed red = switch event",
                 color=NEON_GREEN, fontsize=11)

    _apply_dark_style(fig, [ax])
    fig.tight_layout()
    return fig


# ─── Chart 5: Threat Heatmap ─────────────────────────────────────────────────
def chart_threat_heatmap(records: list) -> plt.Figure:
    if len(records) < 3:
        return _empty_chart("Need ≥ 3 blocks for threat heatmap", size=(9, 2))

    threats = np.array([r["threat"] for r in records]).reshape(1, -1)
    x_labels = [str(r["block_id"]) for r in records]

    fig, ax = plt.subplots(figsize=(9, 1.8))
    sns.heatmap(threats, ax=ax, cmap="RdYlGn_r", vmin=0, vmax=1,
                cbar_kws={"shrink": 0.7, "label": "Threat"},
                xticklabels=x_labels, yticklabels=["Threat Level"],
                linewidths=0.3, linecolor=BG_COLOR)

    ax.set_title("Threat Level Heatmap Across Blocks", color=NEON_GREEN, fontsize=11, pad=8)
    ax.tick_params(colors=TEXT_COLOR, labelsize=7.5)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.collections[0].colorbar.set_label("Threat", color=TEXT_COLOR, fontsize=8)
    ax.collections[0].colorbar.ax.tick_params(colors=TEXT_COLOR)

    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(PANEL_COLOR)
    fig.tight_layout()
    return fig


# ─── Chart 6: Radar Chart — Network Health ───────────────────────────────────
def chart_network_radar(snapshot: dict, prediction: dict) -> plt.Figure:
    """Radar / spider chart showing current network health dimensions."""
    categories = ["Security", "Throughput", "Stability", "Decentralization", "Resilience"]
    N = len(categories)

    attack  = prediction["attack_risk_prob"]
    spike   = prediction["traffic_spike_prob"]
    cong    = {"Low": 0.9, "Medium": 0.6, "High": 0.3}.get(prediction["congestion_level"], 0.5)
    nodes   = min(snapshot["nodes"] / 50.0, 1.0)
    latency = max(0.0, 1.0 - snapshot["latency"] / 400.0)

    values = [
        round(1.0 - attack, 3),          # Security (inverse of attack risk)
        round(cong, 3),                   # Throughput (inverse of congestion)
        round(latency, 3),                # Stability (inverse of latency)
        round(nodes, 3),                  # Decentralization (node density)
        round(max(0, 1.0 - spike), 3),   # Resilience (inverse of spike)
    ]
    values_plot = values + [values[0]]  # Close the polygon

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))

    # Fill area
    ax.fill(angles, values_plot, color=NEON_GREEN, alpha=0.18)
    ax.plot(angles, values_plot, color=NEON_GREEN, lw=2.0, marker="o", ms=5)

    # Draw threshold ring at 0.6
    threshold = [0.6] * (N + 1)
    ax.plot(angles, threshold, color=WARN_AMBER, lw=0.8, ls="--", alpha=0.5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color=TEXT_COLOR, fontsize=9.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.0"], color=MUTED_COLOR, fontsize=7)
    ax.grid(color=GRID_COLOR, linewidth=0.6)
    ax.set_facecolor(PANEL_COLOR)
    ax.spines["polar"].set_edgecolor(SPINE_COLOR)
    ax.tick_params(colors=TEXT_COLOR)

    fig.patch.set_facecolor(BG_COLOR)
    ax.set_title("Network Health Radar", color=NEON_GREEN, fontsize=12,
                 pad=18, fontfamily="monospace")
    fig.tight_layout()
    return fig


# ─── Chart 7: Consensus Scoring Bar Chart ────────────────────────────────────
def chart_scoring_matrix(scoring: dict) -> plt.Figure:
    """Horizontal grouped bar chart showing multi-factor scores per consensus."""
    if not scoring:
        return _empty_chart("No scoring data", size=(6, 4))

    mechanisms = list(scoring.keys())
    factors    = ["score", "security", "throughput", "decentralization"]
    factor_labels = ["Overall Score", "Security", "Throughput", "Decentralization"]
    colors_f   = [NEON_GREEN, INFO_BLUE, WARN_AMBER, PURPLE]

    x      = np.arange(len(mechanisms))
    width  = 0.18
    fig, ax = plt.subplots(figsize=(7, 4))

    for i, (factor, label, color) in enumerate(zip(factors, factor_labels, colors_f)):
        vals = [scoring[m][factor] for m in mechanisms]
        bars = ax.bar(x + i * width, vals, width, label=label,
                      color=color, alpha=0.85, edgecolor=BG_COLOR, linewidth=0.5)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    f"{val:.2f}", ha="center", va="bottom",
                    color=color, fontsize=7, fontfamily="monospace")

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(mechanisms, color=TEXT_COLOR, fontsize=10)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Score (0–1)", color=TEXT_COLOR)
    ax.set_title("ACE Consensus Scoring Matrix", color=NEON_GREEN, fontsize=12)
    ax.legend(facecolor=PANEL_COLOR, edgecolor=SPINE_COLOR,
              labelcolor=TEXT_COLOR, fontsize=8, loc="upper right")

    _apply_dark_style(fig, [ax])
    fig.tight_layout()
    return fig


# ─── Chart 8: Confidence + Efficiency Dual Axis ──────────────────────────────
def chart_confidence_trend(records: list) -> plt.Figure:
    """Dual-axis chart: ACE confidence score vs efficiency per block."""
    if len(records) < 2:
        return _empty_chart("Need ≥ 2 blocks", size=(8, 4))

    ids        = [r["block_id"] for r in records]
    efficiency = [r["efficiency"] for r in records]
    confidence = [r.get("confidence", 0.8) for r in records]

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2 = ax1.twinx()

    ax1.plot(ids, efficiency, color=NEON_GREEN, lw=2.2, marker="o", ms=4, label="Efficiency")
    ax1.fill_between(ids, efficiency, alpha=0.12, color=NEON_GREEN)
    ax1.set_ylabel("Efficiency Score", color=NEON_GREEN, fontsize=9)
    ax1.tick_params(axis="y", colors=NEON_GREEN)
    ax1.set_ylim(0, 1.1)

    ax2.plot(ids, confidence, color=WARN_AMBER, lw=1.8, marker="s",
             ms=3.5, ls="--", label="ACE Confidence", alpha=0.85)
    ax2.set_ylabel("ACE Confidence", color=WARN_AMBER, fontsize=9)
    ax2.tick_params(axis="y", colors=WARN_AMBER)
    ax2.set_ylim(0, 1.1)

    ax1.set_xlabel("Block ID", color=TEXT_COLOR, fontsize=9)
    ax1.set_title("Efficiency vs ACE Confidence Trend", color=NEON_GREEN, fontsize=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               facecolor=PANEL_COLOR, edgecolor=SPINE_COLOR,
               labelcolor=TEXT_COLOR, fontsize=8, loc="lower right")

    for ax in [ax1, ax2]:
        ax.set_facecolor(PANEL_COLOR)
        for spine in ax.spines.values():
            spine.set_edgecolor(SPINE_COLOR)
        ax.tick_params(axis="x", colors=TEXT_COLOR, labelsize=8.5)

    ax1.grid(True, color=GRID_COLOR, linewidth=0.5, linestyle="--", alpha=0.6)
    fig.patch.set_facecolor(BG_COLOR)
    fig.tight_layout()
    return fig


# ─── Sparkline (mini chart for inline display) ───────────────────────────────
def sparkline(values: list, color: str = NEON_GREEN, size=(3, 0.8)) -> plt.Figure:
    """Tiny sparkline chart for inline embedding."""
    fig, ax = plt.subplots(figsize=size)
    if len(values) >= 2:
        ax.plot(values, color=color, lw=1.5)
        ax.fill_between(range(len(values)), values, alpha=0.2, color=color)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor("none")
    fig.patch.set_facecolor("none")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig
