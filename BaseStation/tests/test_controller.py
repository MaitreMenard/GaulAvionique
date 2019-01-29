import unittest
from unittest.mock import Mock, MagicMock, call

from src.consumer import Consumer
from src.controller import Controller
from src.data_producer import DataProducer
from src.message_listener import MessageListener
from src.message_type import MessageType
from src.ui.data_widget import DataWidget
from tests.builders.config_builder import ConfigBuilder


class ControllerTest(unittest.TestCase):

    MESSAGE = "A MESSAGE"
    MESSAGE_TYPE = MessageType.INFO
    ALTITUDE = 9000
    APOGEE = 10000
    EASTING = 32
    NORTHING = 52
    VOLTAGE = 3.3
    BOARD_STATE_1 = True
    BOARD_STATE_2 = True
    BOARD_STATE_3 = False
    POWER_SUPPLY_STATE_1 = True
    POWER_SUPPLY_STATE_2 = False
    PAYLOAD_BOARD_STATE_1 = True
    TEMPERATURE = 100
    QUATERNION = (1, 2, 3, 4)

    def setUp(self):
        self.data_widget = Mock(spec=DataWidget)
        self.data_producer = Mock(spec=DataProducer)
        self.consumer = MagicMock(spec=Consumer)

        self.message_listener1 = MessageListener()
        self.message_listener1.notify = Mock()
        self.message_listener2 = MessageListener()
        self.message_listener2.notify = Mock()

        config = ConfigBuilder().build()

        self.controller = Controller(self.data_widget, self.data_producer, self.consumer, config)

    def test_register_message_listener_should_add_listener_in_list(self):
        self.controller.register_message_listener(self.message_listener1)
        self.controller.register_message_listener(self.message_listener2)

        num_listeners = len(self.controller.message_listeners)
        self.assertEqual(num_listeners, 2)

    def test_notify_all_message_listeners_should_call_notify_on_each_listeners(self):
        self.controller.register_message_listener(self.message_listener1)
        self.controller.register_message_listener(self.message_listener2)

        self.controller.notify_all_message_listeners(self.MESSAGE, self.MESSAGE_TYPE)

        self.message_listener1.notify.assert_called_with(self.MESSAGE, self.MESSAGE_TYPE)
        self.message_listener2.notify.assert_called_with(self.MESSAGE, self.MESSAGE_TYPE)

    def test_update_should_update_consumer(self):
        self.controller.update()

        self.consumer.update.assert_called_with()

    def test_update_should_update_plots_when_consumer_has_data(self):
        self.consumer.has_data.return_value = True
        self.setup_consumer_data()

        self.controller.update()

        self.data_widget.draw_altitude.assert_called_with(self.ALTITUDE)
        self.data_widget.draw_apogee.assert_called_with(self.APOGEE)
        self.data_widget.draw_map.assert_called_with(self.EASTING, self.NORTHING)
        self.data_widget.draw_voltage.assert_called_with(self.VOLTAGE)

    def test_update_should_update_leds_when_consumer_has_data(self):
        self.consumer.has_data.return_value = True
        self.setup_consumer_data()

        self.controller.update()

        self.assert_leds_updated()

    def test_update_should_update_thermometer_when_consumer_has_data(self):
        self.consumer.has_data.return_value = True
        self.consumer.get_average_temperature.return_value = self.TEMPERATURE

        self.controller.update()

        self.data_widget.set_thermometer_value.assert_called_with(self.TEMPERATURE)

    def test_update_should_update_3d_model_when_consumer_has_data(self):
        self.consumer.has_data.return_value = True
        self.consumer.get_rocket_rotation.return_value = self.QUATERNION

        self.controller.update()

        self.data_widget.rotate_rocket_model.assert_called_with(self.QUATERNION[0], self.QUATERNION[1],
                                                                self.QUATERNION[2], self.QUATERNION[3])

    def test_update_should_not_update_ui_when_consumer_has_no_data(self):
        self.consumer.has_data.return_value = False

        self.controller.update()

        self.assert_ui_not_updated()

    def test_update_should_clear_consumer(self):
        self.controller.update()

        self.consumer.clear.assert_called_with()

    def setup_consumer_data(self):
        data = {"altitude_feet": self.ALTITUDE, "apogee": self.APOGEE, "easting": self.EASTING,
                "northing": self.NORTHING, "voltage": self.VOLTAGE, "acquisition_board_state_1": [self.BOARD_STATE_1],
                "acquisition_board_state_2": [self.BOARD_STATE_2], "acquisition_board_state_3": [self.BOARD_STATE_3],
                "power_supply_state_1": [self.POWER_SUPPLY_STATE_1],
                "power_supply_state_2": [self.POWER_SUPPLY_STATE_2],
                "payload_board_state_1": [self.PAYLOAD_BOARD_STATE_1]}
        self.consumer.__getitem__.side_effect = lambda arg: data[arg]

    def assert_leds_updated(self):
        calls = [call(1, self.BOARD_STATE_1), call(2, self.BOARD_STATE_2), call(3, self.BOARD_STATE_3),
                 call(4, self.POWER_SUPPLY_STATE_1), call(5, self.POWER_SUPPLY_STATE_2),
                 call(6, self.PAYLOAD_BOARD_STATE_1)]
        self.data_widget.set_led_state.assert_has_calls(calls, any_order=True)

    def assert_ui_not_updated(self):
        self.data_widget.draw_altitude.assert_not_called()
        self.data_widget.draw_apogee.assert_not_called()
        self.data_widget.draw_map.assert_not_called()
        self.data_widget.draw_voltage.assert_not_called()
        self.data_widget.set_led_state.assert_not_called()
        self.data_widget.set_thermometer_value.assert_not_called()
        self.data_widget.rotate_rocket_model.assert_not_called()
