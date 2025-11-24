from enum import Enum, Flag
from typing import Any, Dict, List
from can import Message
from .base import BaseParser


class FaultStatus(Flag):
    """Fault status flags using Python Flag enum for bitwise operations"""
    RESERVED = 0
    OTP = 1 << 1        # Over temperature protection
    OVP = 1 << 2        # Output over voltage protection
    OCP = 1 << 3        # Output over current protection
    SHORT = 1 << 4      # Output short circuit protection
    AC_FAIL = 1 << 5    # AC abnormal flag
    OP_OFF = 1 << 6     # Output turned off
    HI_TEMP = 1 << 7    # Internal high temperature protection


class FaultSeverity(Enum):
    CRITICAL = "critical"
    INFO = "info"


class FaultStatusParser(BaseParser):
    # Fault metadata took from manual
    FAULT_METADATA = {
        FaultStatus.OTP: {
            "name": "Over Temperature Protection",
            "description": "Internal temperature abnormal",
            "severity": FaultSeverity.CRITICAL,
        },
        FaultStatus.OVP: {
            "name": "Over Voltage Protection",
            "description": "Output voltage exceeded maximum limit",
            "severity": FaultSeverity.CRITICAL,
        },
        FaultStatus.OCP: {
            "name": "Over Current Protection",
            "description": "Output current exceeded maximum limit",
            "severity": FaultSeverity.CRITICAL,
        },
        FaultStatus.SHORT: {
            "name": "Short Circuit Protection",
            "description": "Output short circuit detected",
            "severity": FaultSeverity.CRITICAL,
        },
        FaultStatus.AC_FAIL: {
            "name": "AC Input Failure",
            "description": "AC input voltage abnormal or missing",
            "severity": FaultSeverity.CRITICAL,
        },
        FaultStatus.OP_OFF: {
            "name": "Output Disabled",
            "description": "Output is turned off due to some issue, look chg_status to elaborate",
            "severity": FaultSeverity.INFO,
        },
        FaultStatus.HI_TEMP: {
            "name": "High Temperature",
            "description": "Internal temperature abnormal",
            "severity": FaultSeverity.CRITICAL,
        }
    }

    def parseRead(self, msg: Message) -> Dict:
        """
        Parse fault status response into structured data
        Returns:
            Dict with fault status, active faults, and summary
        """
        rawDataAddress = msg.data
        if len(rawDataAddress) < 4:
            raise ValueError("Fault status data too short")

        rawData = rawDataAddress[2:4]

        # Convert to integer (little-endian)
        status_word = int.from_bytes(rawData, byteorder='little')
        fault_status = FaultStatus(status_word)

        active_faults = self._get_active_faults(fault_status)

        return {
            "raw_value": status_word,
            "fault_status": fault_status,
            "active_faults": active_faults,
            "has_critical_faults": self._has_critical_faults(active_faults),
            "output_enabled": FaultStatus.OP_OFF not in fault_status
        }

    def _get_active_faults(self, fault_status: FaultStatus) -> List[Dict]:
        """Extract active faults with metadata"""
        active_faults = []

        for fault in FaultStatus:
            if fault in fault_status:
                metadata = self.FAULT_METADATA.get(fault, {})
                active_faults.append({
                    "fault": fault,
                    "name": metadata.get("name", fault.name),
                    "description": metadata.get("description"),
                    "severity": metadata.get("severity"),
                    "bit_position": fault.value.bit_length() - 1 if fault.value > 0 else 0
                })

        return active_faults

    def _has_critical_faults(self, active_faults: List[Dict]) -> bool:
        """Check if any critical faults are active"""
        return any(
            fault["severity"] == FaultSeverity.CRITICAL
            for fault in active_faults
        )

    def parseWrite(self, data: Any) -> bytearray:
        raise NotImplementedError("Fault status is read only")
