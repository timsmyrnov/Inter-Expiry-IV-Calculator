# visualizer.py
import matplotlib.pyplot as plt
import numpy as np

def plot(atm_ivs, interval_ivs=None):
    if not atm_ivs:
        print("Nothing to plot.")
        return

    expiry_days = sorted(atm_ivs.keys())
    atm_vals = [atm_ivs[d] for d in expiry_days]

    fig, ax = plt.subplots(figsize=(9, 4.8))

    if len(expiry_days) >= 2:
        min_gap = max(min(np.diff(expiry_days)), 1)
    else:
        min_gap = 1
    atm_width = 0.2 * min_gap

    if interval_ivs:
        for (t1, t2), v in sorted(interval_ivs.items()):
            if v is None or t2 <= t1:
                continue
            ax.bar(
                t1, v,
                width=t2 - t1, align='edge',
                color="#A7A7A7", alpha=0.3,
                edgecolor="#444", linewidth=0.4,
                label="Interval IV" if (t1, t2) == next(iter(sorted(interval_ivs.keys()))) else None,
                zorder=1
            )
            ax.text(
                (t1 + t2) / 2, v * 0.02,
                f"({t1},{t2})", ha="center", va="bottom",
                fontsize=8, color="#444", alpha=0.8
            )

    ax.bar(
        expiry_days, atm_vals,
        width=atm_width,
        color="#1F3C88",
        label="ATM IV",
        zorder=2
    )

    ax.set_xticks(expiry_days)
    ax.set_xticklabels([str(x) for x in expiry_days])
    ax.set_xlabel("Days to expiry", labelpad=6)
    ax.set_ylabel("Implied Volatility", labelpad=6)
    ax.set_title("Implied Volatilities at and Between Expiries", pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    handles, labels = ax.get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    ax.legend(uniq.values(), uniq.keys(), frameon=False)

    yvals = atm_vals + [v for v in interval_ivs.values()] if interval_ivs else atm_vals
    ax.set_ylim(0, max(yvals) + 0.05)

    plt.tight_layout()
    plt.show()