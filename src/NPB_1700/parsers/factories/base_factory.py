# base_factory.py
from commands import NPB1700Commands
from ..base import BaseParser


class ParserFactory:
    @staticmethod
    def get_parser(command: NPB1700Commands) -> BaseParser:
        # Local imports to avoid circular dependencies and ensure classes are fully created
        from ..electric_data import ElectricDataParser
        from ..fault_status import FaultStatusParser
        from ..charge_status import ChargeStatusParser
        from ..curve_config import CurveConfigParser
        from ..system_config import SystemConfigParser
        from ..system_status import SystemStatusParser

        parsers: dict[NPB1700Commands, BaseParser] = {

            NPB1700Commands.CURVE_CC: ElectricDataParser(constraints={'min': 10.0, 'max': 50.0}, scaling_factor=0.01),
            NPB1700Commands.READ_IOUT: ElectricDataParser(constraints={'min': 0.0, 'max': 60.0}, scaling_factor=0.01),

            NPB1700Commands.CHG_RST_VBAT: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
            NPB1700Commands.CURVE_CV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
            NPB1700Commands.CURVE_FV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
            NPB1700Commands.READ_VOUT: ElectricDataParser(constraints={'min': 0.0, 'max': 42.0}, scaling_factor=0.01),

            NPB1700Commands.READ_TEMPERATURE_1: ElectricDataParser(constraints={'min': -40.0, 'max': 110.0}, scaling_factor=0.1),
            
            NPB1700Commands.CURVE_CC_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),
            NPB1700Commands.CURVE_CV_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),
            NPB1700Commands.CURVE_FV_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),
           
            NPB1700Commands.OPERATION: ElectricDataParser(constraints={'min': 0.0, 'max': 1.0}, scaling_factor=1, raw_data_len=3),

            NPB1700Commands.FAULT_STATUS: FaultStatusParser(),
            NPB1700Commands.CHG_STATUS: ChargeStatusParser(),
            NPB1700Commands.SYSTEM_STATUS: SystemStatusParser(),
            
            NPB1700Commands.CURVE_CONFIG: CurveConfigParser(),
            NPB1700Commands.SYSTEM_CONFIG: SystemConfigParser(),
        }
        
        if command not in parsers:
            raise ValueError(
                f"No parser available for command {command.name} (0x{command.value.hex()})")

        return parsers[command]
