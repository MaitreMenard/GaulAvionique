import os

from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QStackedWidget, QFileDialog, QWidget

from src.controller_factory import ControllerFactory
from src.message_type import MessageType
from src.realtime.rocket_packet_parser_factory import RocketPacketVersionException
from src.ui import utils
from src.ui.console_message_listener import ConsoleMessageListener
from src.ui.homewidget import HomeWidget
from src.ui.menu_bar import MenuBar
from src.ui.real_time_widget import RealTimeWidget
from src.ui.replay_widget import ReplayWidget
from src.ui.status_bar import StatusBar
from src.ui.configdialog import ConfigDialog


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.home_widget = HomeWidget(self.new_acquisition, self.load_flight_data, self)
        self.real_time_widget = RealTimeWidget(self)
        self.replay_widget = ReplayWidget(self)
        self.central_widget.addWidget(self.home_widget)
        self.central_widget.addWidget(self.real_time_widget)
        self.central_widget.addWidget(self.replay_widget)

        self.controller_factory = ControllerFactory()
        self.active_controller = None
        self.real_time_controller = None
        self.replay_controller = None

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        self.menu_bar = self.create_menu_bar()
        self.config_dialog = None
        self.console = ConsoleMessageListener(self)
        self.console.hide()

        self.setWindowIcon(QIcon("src/resources/logo.jpg"))
        self.setWindowTitle("GAUL BaseStation")
        self.set_stylesheet("src/resources/mainwindow.css")

    def resizeEvent(self, *args, **kwargs):
        self.console.adjust_console(self.width(), self.height())

    def create_menu_bar(self):
        menu_bar = MenuBar(self)

        menu_bar.set_new_acquisition_callback(self.new_acquisition)
        menu_bar.set_save_as_callback(self.save_as)
        menu_bar.set_load_flight_data_callback(self.load_flight_data)
        menu_bar.set_open_simulation_callback(self.add_simulation)
        menu_bar.set_console_callback(self.open_close_console)
        menu_bar.set_edit_preferences_callback(self.open_preferences)
        menu_bar.set_on_exit_callback(self.close)

        self.setMenuBar(menu_bar)

        return menu_bar

    def new_acquisition(self):
        deactivated = True
        if self.active_controller is not None:
            deactivated = self.active_controller.deactivate()

        if deactivated:
            try:
                self.open_real_time()
                self.active_controller.activate("")
            except RocketPacketVersionException as error:
                self.status_bar.notify(str(error), MessageType.ERROR)

    def save_as(self):  # TODO
        pass

    def load_flight_data(self):
        filename, _ = QFileDialog.getOpenFileName(caption="Open File", directory="./src/resources/",
                                                  filter="All Files (*);; CSV Files (*.csv)")
        if filename:
            deactivated = True
            if self.active_controller is not None:
                deactivated = self.active_controller.deactivate()

            if deactivated:
                self.open_replay()
                self.active_controller.activate(filename)

    def add_simulation(self):
        filename, _ = QFileDialog.getOpenFileName(caption="Open File", directory="./src/resources/",
                                                  filter="All Files (*);; CSV Files (*.csv)")
        if filename:
            self.active_controller.add_open_rocket_simulation(filename)

    def open_preferences(self):
        config_path = os.path.join(os.getcwd(), "config.ini")
        if self.config_dialog is None:
            self.config_dialog = ConfigDialog(self)
        self.config_dialog.open(config_path)

    def open_real_time(self):
        if self.real_time_controller is None:
            self.real_time_controller = self.controller_factory.create_real_time_controller(self.real_time_widget,
                                                                                            self.console)
            self.real_time_controller.register_message_listener(self.status_bar)

        self.active_controller = self.real_time_controller
        self.open_widget(self.real_time_widget)
        self.menu_bar.set_real_time_mode()

    def open_replay(self):
        if self.replay_controller is None:
            self.replay_controller = self.controller_factory.create_replay_controller(self.replay_widget)
            self.replay_controller.register_message_listener(self.status_bar)

        self.active_controller = self.replay_controller
        self.open_widget(self.replay_widget)
        self.menu_bar.set_replay_mode()

    def open_widget(self, widget: QWidget):
        self.central_widget.setCurrentWidget(widget)
        self.set_stylesheet("src/resources/data_widget.css")
        self.showMaximized()
        self.status_bar.clear()

    def open_close_console(self):
        if self.console.show_console:
            self.console.hide()
            self.console.show_console = False
        else:
            self.console.show()
            self.console.show_console = True

    def set_stylesheet(self, stylesheet_path):
        stylesheet = utils.read_stylesheet(stylesheet_path)
        self.setStyleSheet(stylesheet)

    def closeEvent(self, event: QCloseEvent):
        if self.active_controller is not None:
            self.active_controller.on_close(event)
        else:
            event.accept()

    def center(self):
        window_geometry = self.frameGeometry()
        screen_center_point = QDesktopWidget().screenGeometry(self).center()
        window_geometry.moveCenter(screen_center_point)
        self.move(window_geometry.topLeft())
