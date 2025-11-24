from enum import Flag
from typing import Any, Dict, List
from can import Message
from .base import BaseParser


class ChargeStatus(Flag):
    """Charging status flags"""
    # High byte flags
    NTCER = 1 << 10   # Bit 2: Temperature compensation short circuit
    BTNC = 1 << 11   # Bit 3: No battery detected
    CCTOF = 1 << 13   # Bit 5: Constant current mode timeout
    CVTOF = 1 << 14   # Bit 6: Constant voltage mode timeout
    FVTOF = 1 << 15   # Bit 7: Float mode timeout

    # Low byte flags
    FULLM = 1 << 0   # Bit 0: Fully charged
    CCM = 1 << 1   # Bit 1: Constant current mode active
    CVM = 1 << 2   # Bit 2: Constant voltage mode active
    FVM = 1 << 3   # Bit 3: Float mode active
    WAKEUP_STOP = 1 << 6   # Bit 6: Wakeup in progress


class ChargeStatusParser(BaseParser):
    """Parser for battery charging status (0xB800 command)
    """

    STATUS_METADATA = {
        ChargeStatus.NTCER: {
            "name": "NTC Short Circuit",
            "description": "Temperature compensation circuit shorted",
            "severity": "ERROR"
        },
        ChargeStatus.BTNC: {
            "name": "No Battery",
            "description": "Battery not detected",
            "severity": "ERROR"
        },
        ChargeStatus.CCTOF: {
            "name": "CC Mode Timeout",
            "description": "Constant current charging timed out",
            "severity": "WARNING"
        },
        ChargeStatus.CVTOF: {
            "name": "CV Mode Timeout",
            "description": "Constant voltage charging timed out",
            "severity": "WARNING"
        },
        ChargeStatus.FVTOF: {
            "name": "Float Mode Timeout",
            "description": "Float charging timed out",
            "severity": "WARNING"
        },

        ChargeStatus.FULLM: {
            "name": "Fully Charged",
            "description": "Battery charging complete",
            "severity": "INFO"
        },
        ChargeStatus.CCM: {
            "name": "Constant Current Mode",
            "description": "Charging with constant current",
            "severity": "INFO"
        },
        ChargeStatus.CVM: {
            "name": "Constant Voltage Mode",
            "description": "Charging with constant voltage",
            "severity": "INFO"
        },
        ChargeStatus.FVM: {
            "name": "Float Mode",
            "description": "Maintaining battery with float voltage",
            "severity": "INFO"
        },
        ChargeStatus.WAKEUP_STOP: {
            "name": "Wakeup Active",
            "description": "Battery wakeup sequence in progress",
            "severity": "INFO"
        }
    }

    def parse_read(self, msg: Message) -> Dict:
        """Parse charge status response"""
        if len(msg.data) < 4:
            raise ValueError("Charge status data too short")

        status_bytes = msg.data[2:4]
        status_word = int.from_bytes(status_bytes, byteorder='little')
        charge_status = ChargeStatus(status_word)

        return {
            "raw_value": status_word,
            "charge_status": charge_status,
            "active_states": self._get_active_states(charge_status),
            "has_errors": self._has_errors(charge_status),
            "has_timeouts": self._has_timeouts(charge_status),
            "is_charging": self._is_charging(charge_status),
            "is_complete": ChargeStatus.FULLM in charge_status
        }

    def _get_active_states(self, status: ChargeStatus) -> List[Dict]:
        """Get all active charge states with metadata"""
        # Generate describtion for all states
        return [
            {
                "state": state,
                "name": self.STATUS_METADATA[state]["name"],
                "description": self.STATUS_METADATA[state]["description"],
                "severity": self.STATUS_METADATA[state]["severity"]
            }
            for state in ChargeStatus
            if state in status
        ]

    def _has_errors(self, status: ChargeStatus) -> bool:
        errors = {ChargeStatus.NTCER, ChargeStatus.BTNC}
        return any(error in status for error in errors)

    def _has_timeouts(self, status: ChargeStatus) -> bool:
        timeouts = {ChargeStatus.CCTOF, ChargeStatus.CVTOF, ChargeStatus.FVTOF}
        return any(timeout in status for timeout in timeouts)

    def _is_charging(self, status: ChargeStatus) -> bool:
        charging_modes = {
            ChargeStatus.CCM,
            ChargeStatus.CVM,
            ChargeStatus.FVM
        }
        return any(mode in status for mode in charging_modes)

    def parse_write(self, data: Any) -> bytearray:
        raise NotImplementedError("Charge status is read-only")
