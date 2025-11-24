from driver import NPB1700
from parsers.factory import ParserFactory
from commands import NPB1700Commands
from parsers.base import BaseParser


class NPB1700Service:
    def __init__(self, driver: NPB1700):
        self.driver = driver
        self.parser_factory = ParserFactory()

    def read_parameter(self, command: NPB1700Commands) -> float:
        """Generic method to read any electric related parameter"""
        response = self.driver.read(command)
        parser: BaseParser = self.parser_factory.get_parser(command)
        return parser.parse_read(response)

    def write_parameter(self, command: NPB1700Commands, param: float) -> None:
        """Generic method to set any electric related parameter"""
        parser: BaseParser = self.parser_factory.get_parser(command)
        to_send = parser.parse_write(param)
        self.driver.write(command, to_send)
