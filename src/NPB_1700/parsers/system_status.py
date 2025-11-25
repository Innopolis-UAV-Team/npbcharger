# fault_status.py
from enum import Flag, Enum
from .factories.status_factory import StatusParserFactory

class FaultStatus(Flag):
    RESERVED = 0
    OTP = 1 << 1
    OVP = 1 << 2  
    OLP = 1 << 3
    SHORT = 1 << 4
    AC_FAIL = 1 << 5
    OP_OFF = 1 << 6
    HI_TEMP = 1 << 7

class FaultSeverity(Enum):
    CRITICAL = "critical"
    INFO = "info"

# Configuration for fault status
FAULT_STATUS_CONFIG = {
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
    FaultStatus.OLP: {
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
        "description": "Output is turned off due to some issue",
        "severity": FaultSeverity.INFO,
    },
    FaultStatus.HI_TEMP: {
        "name": "High Temperature",
        "description": "Internal temperature abnormal",
        "severity": FaultSeverity.CRITICAL,
    }
}

# Create the parser using factory
FaultStatusParser = StatusParserFactory.create_parser(
    "FaultStatusParser",
    FAULT_STATUS_CONFIG, 
    FaultStatus
)
