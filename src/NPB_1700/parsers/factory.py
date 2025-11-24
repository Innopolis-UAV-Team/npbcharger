from .electricData import ElectricDataParser
from .fault_status import FaultStatusParser
from .chg_status import ChargeStatusParser
from .base import BaseParser
from commands import NPB1700Commands


class ParserFactory:
    @staticmethod
    def get_parser(command: NPB1700Commands) -> BaseParser:
        parsers: dict[NPB1700Commands, BaseParser] = {
            NPB1700Commands.CURVE_CC: ElectricDataParser(constraints={'min': 10.0, 'max': 50.0}),
            NPB1700Commands.CURVE_CV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}),
            NPB1700Commands.CURVE_FV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}),
            NPB1700Commands.FAULT_STATUS: FaultStatusParser(),
            NPB1700Commands.CHG_STATUS: ChargeStatusParser(),
        }
        if command not in parsers:
            raise ValueError(
                f"No parser available for command {command.name} (0x{command.value.hex()})")

        return parsers[command]
