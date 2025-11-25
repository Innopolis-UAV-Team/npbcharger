from .factories.status_factory import StatusParserFactory, FieldType

# Configuration for charge settings - no Flag enum needed!
CURVE_CONFIG = {
    # High byte fields
    "constant_voltage_timeout_enable": {
        "type": FieldType.FLAG,
        "bit": 8,  # Bit 0 of high byte (byte 1, bit 0)
        "name": "Constant Voltage Timeout Enable",
        "description": "Constant voltage stage timeout indication enable"
    },
    "constant_current_timeout_enable": {
        "type": FieldType.FLAG, 
        "bit": 9,  # Bit 1 of high byte (byte 1, bit 1)
        "name": "Constant Current Timeout Enable",
        "description": "Constant current stage timeout indication enable"
    },
    "restart_charge_enable": {
        "type": FieldType.FLAG,
        "bit": 11,  # Bit 3 of high byte (byte 1, bit 3)
        "name": "Restart Charge Enable", 
        "description": "Restart to charge after the battery is full enable"
    },
    "cv_timeout_status_selection": {
        "type": FieldType.FLAG,
        "bit": 13,  # Bit 5 of high byte (byte 1, bit 5)
        "name": "CV Timeout Status Selection",
        "description": "CV Timeout Status Selection Enable"
    },
    
    # Low byte fields  
    "charge_curve_setting": {
        "type": FieldType.BITS,
        "mask": 0x03,  # Bits 0-1 of low byte
        "shift": 0,
        "name": "Charge Curve Setting",
        "description": "Charge curve setting",
        "values": {
            0: "Customized charging curve",
            1: "Preset charging curve #1", 
            2: "Preset charging curve #2",
            3: "Preset charging curve #3"
        }
    },
    "temperature_compensation": {
        "type": FieldType.BITS,
        "mask": 0x0C,  # Bits 2-3 of low byte
        "shift": 2,
        "name": "Temperature Compensation",
        "description": "Temperature compensation setting",
        "values": {
            0: "Disabled",
            1: "-3mV/°C/cell",
            2: "-4mV/°C/cell", 
            3: "-5mV/°C/cell"
        }
    },
    "charge_curve_enable": {
        "type": FieldType.FLAG,
        "bit": 7,  # Bit 7 of low byte
        "name": "Charge Curve Enable",
        "description": "Charge curve function enable"
    }
}

# Create the parser - no Flag enum needed!
CurveConfigParser = StatusParserFactory.create_parser(
    "CurveConfigParser",
    CURVE_CONFIG
    # No enum_class parameter for field-based parsers
)