from driver import NPB1700
from parsers.factory import ParserFactory
from commands import NPB1700Commands
from parsers.base import BaseParser

class NPB1700Service:
    def __init__(self, driver: NPB1700):
        self.driver = driver
        self.parser_factory = ParserFactory()
    
    def readParameter(self, command: NPB1700Commands) -> float:
        """Generic method to read any electric related parameter (constant voltage, constant amperage, floating amperage)"""
        response = self.driver.read(command)
        parser: BaseParser = self.parser_factory.get_parser(command)
        return parser.parseRead(response)
    
    def writeParameter (self, command: NPB1700Commands, param: float) -> None:
        """Generic method to set any electric related parameter (constant voltage, constant amperage, floating amperage)
           Returns:
                None since write methods do not echo anything in NPB
        """
        parser: BaseParser = self.parser_factory.get_parser(command)
        toSend = parser.parseWrite(param)
        self.driver.write(command, toSend)