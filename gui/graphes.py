"""graphes.py — Tracés matplotlib (thème sombre) à partir des CSV du benchmark C."""
import math
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import theme as T
import data

matplotlib.rcParams.update({
    "figure.facecolor": T.CARTE, "axes.facecolor": T.CARTE2, "axes.edgecolor": T.BORDURE,
    "axes.labelcolor": T.TEXTE, "text.color": T.TEXTE, "xtick.color": T.TEXTE2, "ytick.color": T.TEXTE2,
    "grid.color": "#353b50", "legend.facecolor": T.CARTE, "legend.edgecolor": T.BORDURE,
    "font.size": 8.5, "axes.titlesize": 10, "axes.titleweight": "bold",
})


class Toile:
    """Figure matplotlib intégrée dans un cadre Tk, avec barre d'outils (zoom, export)."""

    def __init__(self, parent, l=10, h=6, outils=True):
        self.fig = Figure(figsize=(l, h), dpi=96)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        if outils:
            barre = NavigationToolbar2Tk(self.canvas, parent, pack_toolbar=False)
            barre.update()
            barre.pack(side="bottom", fill="x")
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def dessiner(self):
        self.fig.tight_layout()
        self.canvas.draw_idle()


def tracer_serie(ax, op, series, logy=False, theorie=True, logx=False, xlabel="n"):
    """series : [(nom_csv, légende, théorie ou None)]. Pleins = mesures ; pointillés = théorie ajustée."""
    xs, ser = data.charger(op)
    if not xs:
        ax.text(0.5, 0.5, "Pas de données :\nlancer l'étude expérimentale", ha="center", va="center",
                transform=ax.transAxes, color=T.TEXTE2)
        return
    for i, (nom, leg, th) in enumerate(series):
        if nom not in ser:
            continue
        ys = ser[nom]
        c = T.SERIES[i % len(T.SERIES)]
        ax.plot(xs, ys, "o-", color=c, lw=1.8, ms=3.5, label=leg)
        if theorie and th:
            a = data.ajuster(xs, ys, th)
            xf = [xs[0] + (xs[-1] - xs[0]) * k / 60 for k in range(61)]
            ax.plot(xf, [a * data.THEORIE[th](x) for x in xf], "--", color=c, lw=1, alpha=0.8,
                    label=f"  théorie {data.NOM_THEORIE[th]}")
    if logy:
        ax.set_yscale("log")
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(data.UNITES.get(op, ""))
    ax.grid(True, alpha=0.6)
    ax.legend(fontsize=6.8, loc="best")
