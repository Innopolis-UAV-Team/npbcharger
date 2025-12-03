from functools import wraps
from typing import Any, Dict, Callable
from .driver import NPB1700
from .parsers import ParserFactory
from .commands import NPB1700Commands


def command_reader(command: NPB1700Commands, method_type: str = 'electric'):
    """
    Decorator to handle reading from the driver.
    :param method_type: 'electric', 'bytes', 'status', 'config'
    """
    def decorator(func: Callable) -> Callable:
         # @wrap substitutes function signature instead of "wrapper" func
         # leaving body as it is and saving the access to argument through *args, **kwargs
        @wraps(func)
        def wrapper(self: 'NPB1700Service', *args, **kwargs):
            if method_type == 'electric':
                return self._read_electric(command)
            elif method_type == 'bytes':
                # For byte reads that need decoding
                raw = self._read_bytes(command)
                return func(self, raw, *args, **kwargs)
            elif method_type == 'status':
                return self._read_status(command)
            elif method_type == 'config':
                return self._read_config(command)
            else:
                raise ValueError(f"Unknown read method type: {method_type}")
        return wrapper
    return decorator

def command_writer(command: NPB1700Commands, method_type: str = 'electric'):
    """
    Decorator to handle writing to the driver.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: 'NPB1700Service', value: Any, *args, **kwargs):
            if method_type == 'electric':
                return self._write_electric(command, value)
            elif method_type == 'config':
                return self._write_config(command, value)
            else:
                raise ValueError(f"Unknown write method type: {method_type}")
        return wrapper
    return decorator

# Service Class
class NPB1700Service:
    def __init__(self, driver: NPB1700):
        self.driver = driver
        self.parser_factory = ParserFactory()

    # Electrical Domain
    @command_writer(NPB1700Commands.CURVE_CC)
    def set_constant_current_curve(self, current: float) -> None:
        """Set constant charge current"""
        pass

    @command_reader(NPB1700Commands.CURVE_CC)
    def get_constant_current_curve(self) -> float:
        """Get constant charge current"""
        pass

    @command_writer(NPB1700Commands.CURVE_CV)
    def set_constant_voltage_curve(self, voltage: float) -> None:
        """Set constant charge voltage"""
        pass

    @command_reader(NPB1700Commands.CURVE_CV)
    def get_constant_voltage_curve(self) -> float:
        """Get constant charge voltage"""
        pass

    @command_writer(NPB1700Commands.CURVE_FV)
    def set_float_voltage_curve(self, voltage: float) -> None:
        pass

    @command_reader(NPB1700Commands.CURVE_FV)
    def get_float_voltage_curve(self) -> float:
        pass

    @command_writer(NPB1700Commands.CHG_RST_VBAT)
    def set_charge_restart_vbat(self, voltage: float) -> None: pass

    @command_reader(NPB1700Commands.CHG_RST_VBAT)
    def get_charge_restart_vbat(self) -> float: pass


    @command_writer(NPB1700Commands.CURVE_CC_TIMEOUT)
    def set_cc_timeout(self, time_in_minutes: int) -> None: pass

    @command_reader(NPB1700Commands.CURVE_CC_TIMEOUT)
    def get_cc_timeout(self) -> int: pass

    @command_reader(NPB1700Commands.READ_IOUT)
    def get_constant_current(self) -> float: pass

    @command_reader(NPB1700Commands.READ_VOUT)
    def get_voltage_current(self) -> float: pass

    @command_reader(NPB1700Commands.READ_TEMPERATURE_1)
    def get_temperature_1(self) -> float: pass

    # Status Domain
    @command_reader(NPB1700Commands.FAULT_STATUS, method_type='status')
    def get_fault_status(self) -> Dict[str, Any]: pass

    @command_reader(NPB1700Commands.CHG_STATUS, method_type='status')
    def get_charge_status(self) -> Dict[str, Any]: pass

    @command_reader(NPB1700Commands.SYSTEM_STATUS, method_type='status')
    def get_system_status(self) -> Dict[str, Any]: pass

    # Configuration Domain
    @command_reader(NPB1700Commands.CURVE_CONFIG, method_type='config')
    def get_curve_config(self) -> Dict[str, Any]: pass

    @command_writer(NPB1700Commands.CURVE_CONFIG, method_type='config')
    def set_curve_config(self, config_fields: Dict[str, Any]) -> None: pass

    @command_reader(NPB1700Commands.SYSTEM_CONFIG, method_type='config')
    def get_system_config(self) -> Dict[str, Any]: pass

    @command_writer(NPB1700Commands.SYSTEM_CONFIG, method_type='config')
    def set_system_config(self, config_fields: Dict[str, Any]) -> None: pass

    # Special cases that are not handled by decorator
    def set_operation_status(self, status: bool) -> None:
        self._write_electric(NPB1700Commands.OPERATION, float(status))
    
    def get_model_id(self) -> str:
        low = self._read_bytes(NPB1700Commands.MFR_MODEL_B0B5)
        high = self._read_bytes(NPB1700Commands.MFR_MODEL_B6B11)
        return (low + high).decode('utf-8')

    def get_operation_status(self) -> bool:
        return bool(self._read_electric(NPB1700Commands.OPERATION))
    

    # Private Helpers
    def _read_electric(self, command: NPB1700Commands) -> float:
        response = self.driver.read(command)
        parser = self.parser_factory.get_parser(command)
        return parser.parse_read(response)

    def _read_bytes(self, command: NPB1700Commands) -> bytearray:
        response = self.driver.read(command)
        parser = self.parser_factory.get_parser(command)
        return parser.parse_read(response)

    def _write_electric(self, command: NPB1700Commands, value: float) -> None:
        parser = self.parser_factory.get_parser(command)
        to_send = parser.parse_write(value)
        self.driver.write(command, to_send)

    def _read_status(self, command: NPB1700Commands) -> Dict[str, Any]:
        response = self.driver.read(command)
        parser = self.parser_factory.get_parser(command)
        return parser.parse_read(response)

    def _read_config(self, command: NPB1700Commands) -> Dict[str, Any]:
        response = self.driver.read(command)
        parser = self.parser_factory.get_parser(command)
        return parser.parse_read(response)

    def _write_config(self, command: NPB1700Commands, config_data: Dict[str, Any]) -> None:
        parser = self.parser_factory.get_parser(command)
        current_config = self._read_config(NPB1700Commands.CURVE_CONFIG)
        current_raw = current_config["raw_value"]
        
        if not hasattr(parser, 'parse_write_update'):
             raise TypeError(f"Parser for {command} does not support partial updates")
             
        to_send = parser.parse_write_update(config_data, current_raw)
        self.driver.write(command, to_send)
