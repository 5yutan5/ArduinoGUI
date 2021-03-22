from collections import deque

import pyqtgraph as pg
from PySide6.QtWidgets import QApplication


class RealTimeCurve:
    def __init__(self, plot_widget: pg.PlotWidget, max_len: int) -> None:
        self.plot_data_item = plot_widget.plot()
        self.x_data, self.y_data = deque(maxlen=max_len), deque(maxlen=max_len)

    def set_data(self, x_data: list, y_data: list) -> None:
        self.x_data = deque(x_data)
        self.y_data = deque(y_data)
        self.plot_data_item.setData(x_data, y_data)

    def append_data(self, x_data: int, y_data: int) -> None:
        self.x_data.append(x_data)
        self.y_data.append(y_data)
        self.plot_data_item.setData(self.x_data, self.y_data)


class RealTimePlotWidget(pg.PlotWidget):
    def __init__(
        self,
        x_min,
        x_max,
        y_min,
        y_max,
        title="no name",
        x_label="no name",
        y_label="no name",
        curve_name="no name",
    ):
        super().__init__()
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max
        self.curve_name = curve_name
        self.curve = RealTimeCurve(self, x_max - x_min + 1)

        # setup
        self.setXRange(x_min, x_max)
        self.setYRange(y_min, y_max)
        self.plotItem.setTitle(title)
        self.plotItem.setLabel("left", y_label)
        self.plotItem.setLabel("bottom", x_label)
        self.plotItem.hideButtons()
        self.plotItem.setMenuEnabled(False)
        self.plotItem.setMouseEnabled(False, False)
        self.enableMouse(False)

    def clear_curve(self):
        self.plotItem.clear()
        self.setXRange(self.x_min, self.x_max)
        self.curve = RealTimeCurve(self, self.x_max - self.x_min + 1)


def main():
    import sys

    app = QApplication(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
