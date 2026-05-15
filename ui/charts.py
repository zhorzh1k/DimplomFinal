from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatsCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(4, 3))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#121212")
        self.ax.set_facecolor("#121212")
        
    def update_chart(self, stats):
        self.ax.clear()
        self.ax.set_facecolor("#121212")
        self.fig.patch.set_facecolor("#121212")

        if not stats:
            self.ax.text(
                0.5,
                0.5,
                "No detections yet",
                color="white",
                ha="center",
                va="center",
                fontsize=12
            )
            self.draw()
            return
        categories = list(stats.keys())
        values = list(stats.values())
        total = sum(values)
        
        percentages = [
            (v / total) * 100
            for v in values
        ]
        colors = [
            "#ff6b6b",
            "#ffd93d",
            "#6c5ce7",
            "#4ecdc4",
            "#45b7d1",
            "#00cec9"
        ]
        bars = self.ax.bar(
            categories,
            values,
            color=colors[:len(categories)]
        )
        for bar, val, pct in zip(
            bars,
            values,
            percentages
        ):
            self.ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val} ({pct:.1f}%)",
                ha='center',
                va='bottom',
                color='white',
                fontsize=9
            )
        self.ax.set_title(
            "Waste Distribution",
            color='white',
            fontsize=13
        )
        self.ax.set_ylabel(
            "Detected Objects",
            color='white'
        )
        self.ax.tick_params(
            axis='x',
            rotation=20,
            colors='white'
        )
        self.ax.tick_params(
            axis='y',
            colors='white'
        )
        self.ax.grid(
            True,
            linestyle='--',
            alpha=0.2
        )
        self.fig.tight_layout()
        self.draw()