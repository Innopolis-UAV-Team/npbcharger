from enum import Flag, Enum
from typing import Any, Dict, List, Type, Union, Tuple
from can import Message
from ..base import BaseParser

class Severity(Enum):
    CRITICAL = "critical"
    INFO = "info"
    WARNING = "warning"

class FieldType(Enum):
    FLAG = "flag"           # Single bit flag
    BITS = "bits"           # Multi-bit field
    VALUE = "value"         # Direct value

class StatusParserFactory:
    """Factory for creating status parsers from configuration"""
    
    @classmethod
    def create_parser(cls, parser_name: str, status_config: Dict, enum_class: Type[Flag] = None) -> Type[BaseParser]:
        """
        Create a parser class from configuration
        Supports both Flag enums and field-based configurations
        """
        
        class DynamicStatusParser(BaseParser):
            STATUS_CONFIG = status_config
            STATUS_ENUM = enum_class
            
            def parse_read(self, msg: Message) -> Dict:
                if len(msg.data) < 4:
                    raise ValueError(f"{parser_name} data too short")

                status_bytes = msg.data[2:4]
                status_word = int.from_bytes(status_bytes, byteorder='little')
                
                result = {}
                    
                # Add Flag enum support if provided
                if enum_class:
                    status_flags = enum_class(0)
                    for flag in enum_class:
                        if status_word & flag.value:
                            status_flags |= flag
                    
                    result = ({
                            "raw_value": status_word,
                            "status": status_flags,
                            "active_states": self._get_active_states(status_flags),
                            "has_errors": self._has_errors(status_flags),
                            "has_warnings": self._has_warnings(status_flags),
                            "has_critical": self._has_critical(status_flags),
                        })
                else:
                    result = {
                        "raw_value": status_word,
                        "fields": self._parse_fields(status_word),
                    }
                
                return result

            def _parse_fields(self, status_word: int) -> Dict:
                """Parse all configured fields from the status word"""
                fields = {}
                
                for field_name, config in self.STATUS_CONFIG.items():
                    field_type = config.get("type", FieldType.FLAG)
                    
                    if field_type == FieldType.FLAG:
                        # Single bit flag
                        bit_position = config["bit"]
                        fields[field_name] = bool(status_word & (1 << bit_position))
                        
                    elif field_type == FieldType.BITS:
                        # Multi-bit field
                        bit_mask = config["mask"]
                        bit_shift = config.get("shift", 0)
                        field_value = (status_word & bit_mask) >> bit_shift
                        
                        # Map to human-readable values if mapping provided
                        value_map = config.get("values", {})
                        fields[field_name] = value_map.get(field_value, field_value)
                        
                    elif field_type == FieldType.VALUE:
                        # Direct value extraction
                        bit_mask = config["mask"]
                        bit_shift = config.get("shift", 0)
                        fields[field_name] = (status_word & bit_mask) >> bit_shift
                
                return fields

            def _get_active_states(self, status: Flag) -> List[Dict]:
                """Get all active states with metadata (for Flag enums)"""
                if not self.STATUS_ENUM:
                    return []
                    
                active_states = []
                for state in self.STATUS_ENUM:
                    if state in status:
                        metadata = self.STATUS_CONFIG.get(state, {})
                        active_states.append({
                            "state": state,
                            "name": metadata.get("name", state.name),
                            "description": metadata.get("description", ""),
                            "severity": metadata.get("severity")
                        })
                return active_states

            def _has_errors(self, status: Flag) -> bool:
                return self._check_severity(status, "error")

            def _has_warnings(self, status: Flag) -> bool:
                return self._check_severity(status, "warning")

            def _has_critical(self, status: Flag) -> bool:
                return self._check_severity(status, "critical")

            def _check_severity(self, status: Flag, target_severity: str) -> bool:
                if not self.STATUS_ENUM:
                    return False
                    
                for state in self.STATUS_ENUM:
                    if state in status:
                        metadata = self.STATUS_CONFIG.get(state, {})
                        state_severity = metadata.get("severity")
                        
                        if isinstance(state_severity, Enum):
                            state_severity = state_severity.value
                        
                        if state_severity == target_severity:
                            return True
                return False

            def parse_write(self, data: Any) -> bytearray:
                raise NotImplementedError(f"{parser_name} is read-only")

        DynamicStatusParser.__name__ = parser_name
        return DynamicStatusParser