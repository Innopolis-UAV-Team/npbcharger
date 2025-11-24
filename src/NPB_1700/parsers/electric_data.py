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

    def parse_read(self, msg: Message) -> float:
        raw_data_address = msg.data
        if len(raw_data_address) < 4:
            raise ValueError("Fault status data too short")

        raw_data = raw_data_address[2:4]

        raw_value = int.from_bytes(raw_data, byteorder='little')
        return raw_value * self.scaling_factor

    def parse_write(self, data: float) -> bytearray:
        min_v = self.constraints.get('min')
        max_v = self.constraints.get('max')

        if min_v is not None:
            data = max(min_v, data)
        if max_v is not None:
            data = min(data, max_v)

        data = round(data, 2)
        raw_value = int(data / self.scaling_factor)
        return bytearray(raw_value.to_bytes(2, byteorder='little'))
