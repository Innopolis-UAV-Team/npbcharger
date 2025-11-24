from typing import Any, Dict, Optional
from can import Message
from .base import BaseParser


class ElectricDataParser(BaseParser):
    scaling_factor: float

    def __init__(self,
                 scaling_factor: float = 0.01,
                 constraints: Optional[Dict[str, Any]] = None):
        self.scaling_factor = scaling_factor
        self.constraints = constraints or {}

    def parseRead(self, msg: Message) -> float:
        rawDataAddress = msg.data
        if len(rawDataAddress) < 4:
            raise ValueError("Fault status data too short")

        rawData = rawDataAddress[2:4]

        raw_value = int.from_bytes(rawData, byteorder='little')
        return raw_value * self.scaling_factor

    def parseWrite(self, data: float) -> bytearray:
        min_v = self.constraints.get('min')
        max_v = self.constraints.get('max')

        if min_v is not None:
            data = max(min_v, data)
        if max_v is not None:
            data = min(data, max_v)

        data = round(data, 2)
        raw_value = int(data / self.scaling_factor)
        return bytearray(raw_value.to_bytes(2, byteorder='little'))
