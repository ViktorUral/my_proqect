import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class BarChartWidget(QWidget):
    def __init__(self, data, name, value, name_graph, parent=None):
        super().__init__(parent)
        self.initUI(data, name, value, name_graph)

    def initUI(self, data, name, value, name_graph):
        pairs = [(data[0], data[1])]
        x_positions = [1, 2]
        heights = [val for pair in pairs for val in pair]
        labels = name

        bar_graph = pg.BarGraphItem(x=x_positions, height=heights, width=0.8, brush="blue")

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addItem(bar_graph)
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setTitle(name_graph)
        self.plot_widget.setLabel("left", value)

        x_axis = self.plot_widget.getPlotItem().getAxis("bottom")
        ticks = [(x_positions[i], labels[i]) for i in range(len(x_positions))]
        x_axis.setTicks([ticks])

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
