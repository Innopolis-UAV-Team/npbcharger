from typing import Any, Dict, TypeGuard
from .driver import NPB1700
from .parsers import ParserFactory
from .commands import NPB1700Commands
from .parsers import BaseParser


def _is_config_parser(parser: BaseParser) -> TypeGuard[Any]:
    """Type guard to check if parser has parse_write_update method"""
    return hasattr(parser, 'parse_write_update')

class NPB1700Service:
    def __init__(self, driver: NPB1700):
        self.driver = driver
        self.parser_factory = ParserFactory()

    # Electrical domain
    def set_constant_current_curve(self, current: float) -> None:
        """Set constant charge current"""
        self._write_electric(NPB1700Commands.CURVE_CC, current)
    def get_constant_current_curve(self) -> float:
        """Get constant charge current"""
        return self._read_electric(NPB1700Commands.CURVE_CC)

    def set_constant_voltage_curve(self, voltage: float) -> None:
        """Set constant charge voltage"""
        self._write_electric(NPB1700Commands.CURVE_CV, voltage)
    def get_constant_voltage_curve(self) -> float:
        """Get constant charge voltage"""
        return self._read_electric(NPB1700Commands.CURVE_CV)
    
    def set_float_voltage_curve(self, voltage: float) -> None:
        """Set float charge voltage"""
        self._write_electric(NPB1700Commands.CURVE_FV, voltage)
    def get_float_voltage_curve(self) -> float:
        """Get float charge voltage"""
        return self._read_electric(NPB1700Commands.CURVE_FV)
    
    def set_operation_status(self, status: bool) -> None:
        self._write_electric(NPB1700Commands.OPERATION, float(status))
    def get_operation_status(self) -> bool:
        return bool(self._read_electric(NPB1700Commands.OPERATION))
    
    def set_charge_restart_vbat(self, voltage: float) -> None:
        return self._write_electric(NPB1700Commands.CHG_RST_VBAT, voltage)
    def get_charge_restart_vbat(self) -> float:
        return self._read_electric(NPB1700Commands.CHG_RST_VBAT)
    
    def set_cc_timeout(self, timeInMinutes: int) -> None:
        return self._write_electric(NPB1700Commands.CURVE_CC_TIMEOUT, timeInMinutes)
    def get_cc_timeout(self) -> int:
        return int(self._read_electric(NPB1700Commands.CURVE_CC_TIMEOUT))
    
    def set_cv_timeout(self, timeInMinutes: int) -> None:
        return self._write_electric(NPB1700Commands.CURVE_CV_TIMEOUT, timeInMinutes)
    def get_cv_timeout(self) -> int:
        return int(self._read_electric(NPB1700Commands.CURVE_CV_TIMEOUT))
    
    def set_fv_timeout(self, timeInMinutes: int) -> None:
        return self._write_electric(NPB1700Commands.CURVE_FV_TIMEOUT, timeInMinutes)
    def get_fv_timeout(self) -> int:
        return int(self._read_electric(NPB1700Commands.CURVE_FV_TIMEOUT))
    
    def get_constant_current(self) -> float:
        """Get constant charge current"""
        return self._read_electric(NPB1700Commands.READ_IOUT)
    
    def get_voltage_current(self) -> float:
        """Get voltage charge current"""
        return self._read_electric(NPB1700Commands.READ_VOUT)
    
    def get_temperature_1 (self) -> float:
        return self._read_electric(NPB1700Commands.READ_TEMPERATURE_1)
    


    # Status domain
    def get_fault_status(self) -> Dict[str, Any]:
        """Get current fault status"""
        return self._read_status(NPB1700Commands.FAULT_STATUS)

    def get_charge_status(self) -> Dict[str, Any]:
        """Get current charge status"""
        return self._read_status(NPB1700Commands.CHG_STATUS)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return self._read_status(NPB1700Commands.SYSTEM_STATUS)

    # Configuration domain
    def get_curve_config(self) -> Dict[str, Any]:
        """Get curve configuration"""
        return self._read_config(NPB1700Commands.CURVE_CONFIG)

    def set_curve_config(self, config_fields: Dict[str, Any]) -> None:
        """Set curve configuration using keyword arguments"""
        self._write_config(NPB1700Commands.CURVE_CONFIG, config_fields)
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self._read_config(NPB1700Commands.SYSTEM_CONFIG)

    def set_system_config(self, config_fields: Dict[str, Any]) -> None:
        """Set system configuration using keyword arguments"""
        self._write_config(NPB1700Commands.SYSTEM_CONFIG, config_fields)
    
    # Private helpers
    def _read_electric(self, command: NPB1700Commands) -> float:
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
        if not _is_config_parser(parser):
            raise TypeError(f"Parser for {command} does not support partial updates")
        to_send = parser.parse_write_update(config_data, current_raw)
        self.driver.write(command, to_send)
