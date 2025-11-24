from abc import ABC, abstractmethod
from can import Message
from typing import Any

class BaseParser(ABC):
    """Abstract base class for all parsers"""
    
    @abstractmethod
    def parseRead(self, msg: Message) -> Any:
        """Parse response message into meaningful data"""
        pass
    
    @abstractmethod 
    def parseWrite(self, data: Any) -> bytearray:
        """Convert data to bytearray for sending"""
        pass