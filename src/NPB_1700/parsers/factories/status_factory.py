from enum import Flag, Enum
from typing import Any, Dict, List, Type, Optional
from can import Message
from ..base import StatusParser


class StatusParserFactory:
    """ NOTE: status parsers are READ ONLY"""
    @classmethod
    def create_parser(cls, parser_name: str, status_config: Dict, enum_class: Type[Flag]) -> Type[StatusParser]:
        """
        Create a parser class from configuration
        
        Args:
            parser_name: Name for the parser class
            status_config: Dictionary mapping status flags to metadata
            enum_class: The Flag enum class to use
            
        Returns:
            Created parser class
        """
        
        class DynamicStatusParser(StatusParser):
            STATUS_METADATA = status_config
            STATUS_ENUM = enum_class
            
            def parse_read(self, msg: Message) -> Dict:
                if len(msg.data) < 4:
                    raise ValueError(f"{parser_name} data too short")

                status_bytes = msg.data[2:4]
                status_word = int.from_bytes(status_bytes, byteorder='little')
                status_flags = enum_class(status_word)

                return {
                    "raw_value": status_word,
                    "status": status_flags,
                    "active_states": self._get_active_states(status_flags),
                    "has_errors": self._has_errors(status_flags),
                    "has_warnings": self._has_warnings(status_flags),
                    "has_critical": self._has_critical(status_flags)
                }

            def _get_active_states(self, status: Flag) -> List[Dict]:
                return [
                    {
                        "state": state,
                        "name": self.STATUS_METADATA[state]["name"],
                        "description": self.STATUS_METADATA[state]["description"],
                        "severity": self.STATUS_METADATA[state]["severity"]
                    }
                    for state in enum_class
                    if state in status and state in self.STATUS_METADATA
                ]

            def _has_errors(self, status: Flag) -> bool:
                return self._check_severity(status, "ERROR")

            def _has_warnings(self, status: Flag) -> bool:
                return self._check_severity(status, "WARNING")

            def _has_critical(self, status: Flag) -> bool:
                return self._check_severity(status, "CRITICAL")

            def _check_severity(self, status: Flag, severity: str) -> bool:
                return any(
                    state in status and 
                    self.STATUS_METADATA.get(state, {}).get("severity") == severity
                    for state in enum_class
                )

            def parse_write(self, data: Any) -> bytearray:
                raise NotImplementedError(f"{parser_name} is read-only")

        # Set the class name
        DynamicStatusParser.__name__ = parser_name
        return DynamicStatusParser