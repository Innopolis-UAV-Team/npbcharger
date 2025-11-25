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

        parsers: dict[NPB1700Commands, BaseParser] = {
            NPB1700Commands.CURVE_CC: ElectricDataParser(constraints={'min': 10.0, 'max': 50.0}),
            NPB1700Commands.CURVE_CV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}),
            NPB1700Commands.CURVE_FV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}),
            NPB1700Commands.FAULT_STATUS: FaultStatusParser(),
            NPB1700Commands.CHG_STATUS: ChargeStatusParser(),
            NPB1700Commands.CURVE_CONFIG: CurveConfigParser(),
        }
        
        if command not in parsers:
            raise ValueError(
                f"No parser available for command {command.name} (0x{command.value.hex()})")

        return parsers[command]