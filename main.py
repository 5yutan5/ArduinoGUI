from collections import deque
from typing import Union

import pyqtgraph as pg
import serial
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QComboBox, QMainWindow, QTabWidget, QToolBar
from serial.serialutil import SerialException
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class RealTimeCurve:
    def __init__(self, plot_widget: pg.PlotWidget, max_len: int) -> None:
        self.plot_data_item = plot_widget.plot()
        self.x_data, self.y_data = deque(maxlen=max_len), deque(maxlen=max_len)

    def set_data(self, x_data: list[float], y_data: list[float]) -> None:
        self.x_data = deque(x_data)
        self.y_data = deque(y_data)
        self.plot_data_item.setData(x_data, y_data)

    def append_data(self, x_data: float, y_data: float) -> None:
        self.x_data.append(x_data)
        self.y_data.append(y_data)
        self.plot_data_item.setData(self.x_data, self.y_data)


class RealTimePlotWidget(pg.PlotWidget):
    def __init__(
        self,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
        x_label: str,
        y_label: str,
        curve_name: str,
        title: str = "",
    ) -> None:
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

    def clear_curve(self) -> None:
        self.plotItem.clear()
        self.setXRange(self.x_min, self.x_max)
        self.curve = RealTimeCurve(self, self.x_max - self.x_min + 1)


class PortCombobox(QComboBox):
    def __init__(self, filter: str = None) -> None:
        super().__init__()
        self._port_infos = []
        self._default_text = "Select Port"
        self.filter = "" if filter is None else filter
        self.addItem(self._default_text)

    def get_current_port_info(self) -> Union[ListPortInfo, None]:
        return (
            None
            if len(self._port_infos) == 0
            else self._port_infos[self.currentIndex()]
        )

    def showPopup(self) -> None:
        self._port_infos.clear()
        self.clear()
        self._port_infos = [
            port
            for port in list_ports.comports()
            if self.filter in str(port.description)
        ]
        if len(self._port_infos) == 0:
            self.addItem(self._default_text)
        else:
            self.addItems([str(port.description) for port in self._port_infos])
        width = self.view().sizeHintForColumn(0)
        self.view().setMinimumWidth(width)
        super().showPopup()


class MainWindowUI:
    def setup_ui(self, win: QMainWindow) -> None:
        self.toolbar = QToolBar("main", parent=win)
        self.port_combobox = PortCombobox("Arduino")
        self.tab_graph = QTabWidget()
        self.graph_voltage = RealTimePlotWidget(
            0, 30, 0, 5, "Time[s]", "Voltage[V]", "voltage", "Voltage"
        )
        self.graph_resistance = RealTimePlotWidget(
            0, 30, 0, 100, "Time[s]", "Resistance[kΩ]", "Resistance", "Resistance"
        )

        # setup_widget
        self.tab_graph.addTab(self.graph_voltage, "Voltage")  # type:ignore
        self.tab_graph.addTab(self.graph_resistance, "Resistance")  # type:ignore

        # setup_layout
        win.setCentralWidget(self.tab_graph)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = MainWindowUI()

        # action
        self.action_run = QAction(parent=self, text="Run")
        self.action_stop = QAction(parent=self, text="Stop")

        # setup ui
        self.ui.setup_ui(self)

        # setup toolbar
        self.addToolBar(self.ui.toolbar)
        self.ui.toolbar.addAction(self.action_run)  # type:ignore
        self.ui.toolbar.addSeparator()
        self.ui.toolbar.addAction(self.action_stop)  # type:ignore
        self.ui.toolbar.addSeparator()
        self.ui.toolbar.addWidget(self.ui.port_combobox)

    def start_plot(self):
        self.action_run.setEnabled(False)
        self.action_stop.setEnabled(True)
        port = self.ui.port_combobox.get_current_port_info().device
        with serial.Serial(port, 9600, parity=serial.PARITY_ODD) as ser:
            ser.close()
            ser.parity = serial.PARITY_NONE
            ser.open()
            time = 0
            try:
                while self.action_stop.isEnabled():
                    time = time + 0.1
                    analog_value = ser.readline().decode().rstrip()
                    voltage = int(analog_value) * 5 / 1024
                    self.ui.graph_voltage.curve.append_data(voltage, time)
            except (SerialException, ValueError) as e:
                print(e.with_traceback)

    def stop_plot(self):
        self.action_run.setEnabled(True)
        self.action_stop.setEnabled(False)


def main():
    import sys

    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
