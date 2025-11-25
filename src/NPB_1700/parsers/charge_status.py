from enum import Flag
from .factories.status_factory import StatusParserFactory

class ChargeStatus(Flag):
    """Charging status flags"""
    NTCER = 1 << 10
    BTNC = 1 << 11
    CCTOF = 1 << 13
    CVTOF = 1 << 14
    FVTOF = 1 << 15
    FULLM = 1 << 0
    CCM = 1 << 1
    CVM = 1 << 2
    FVM = 1 << 3
    WAKEUP_STOP = 1 << 6

# Configuration for charge status
CHARGE_STATUS_CONFIG = {
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

# Create the parser using factory
ChargeStatusParser = StatusParserFactory.create_parser(
    "ChargeStatusParser", 
    CHARGE_STATUS_CONFIG, 
    ChargeStatus
)
