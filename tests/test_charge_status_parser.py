# test_charge_status_parser.py
import unittest
import sys
import os
from can import Message

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from NPB_1700.parsers.charge_status import ChargeStatusParser, ChargeStatus
from NPB_1700.parsers.factories.status_factory import Severity

class TestChargeStatusParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = ChargeStatusParser()
    
    def _create_message(self, status_word: int) -> Message:
        """Helper to create CAN message with charge status command header"""
        # Command: 0xB800 (little endian) + status bytes
        status_bytes = status_word.to_bytes(2, byteorder='little')
        return Message(data=bytearray([0xB8, 0x00]) + bytearray(status_bytes))
    
    def test_parse_read_normal_status(self):
        """Test parsing when no charge status flags are active"""
        msg = self._create_message(0x0000)
        result = self.parser.parse_read(msg)
        
        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["status"], ChargeStatus(0))
        self.assertEqual(len(result["active_states"]), 0)
        self.assertFalse(result["has_critical"])
        self.assertFalse(result["has_warnings"])
    
    def test_parse_read_all_single_flags(self):
        """Test each flag individually"""
        test_cases = [
            # (flag, expected_severity, expected_name)
            (ChargeStatus.NTCER, Severity.CRITICAL, "NTC Short Circuit"),
            (ChargeStatus.BTNC, Severity.CRITICAL, "No Battery"),
            (ChargeStatus.CCTOF, Severity.WARNING, "CC Mode Timeout"),
            (ChargeStatus.CVTOF, Severity.WARNING, "CV Mode Timeout"),
            (ChargeStatus.FVTOF, Severity.WARNING, "Float Mode Timeout"),
            (ChargeStatus.FULLM, Severity.INFO, "Fully Charged"),
            (ChargeStatus.CCM, Severity.INFO, "Constant Current Mode"),
            (ChargeStatus.CVM, Severity.INFO, "Constant Voltage Mode"),
            (ChargeStatus.FVM, Severity.INFO, "Float Mode"),
            (ChargeStatus.WAKEUP_STOP, Severity.INFO, "Wakeup Active"),
        ]
        
        for flag, expected_severity, expected_name in test_cases:
            with self.subTest(flag=flag, severity=expected_severity):
                msg = self._create_message(flag.value)
                result = self.parser.parse_read(msg)
                
                # Check flag is active
                self.assertTrue(flag in result["status"])
                self.assertEqual(result["raw_value"], flag.value)
                self.assertEqual(len(result["active_states"]), 1)
                
                # Check metadata
                active_state = result["active_states"][0]
                self.assertEqual(active_state["state"], flag)
                self.assertEqual(active_state["name"], expected_name)
                self.assertEqual(active_state["severity"], expected_severity)
                
                # Check severity detection
                if expected_severity == Severity.CRITICAL:
                    self.assertTrue(result["has_critical"])
                elif expected_severity == Severity.WARNING:
                    self.assertTrue(result["has_warnings"])
    
    def test_parse_read_severity_groups(self):
        """Test groups of flags by severity"""
        severity_groups = {
            "critical": ChargeStatus.NTCER | ChargeStatus.BTNC,
            "warning": ChargeStatus.CCTOF | ChargeStatus.CVTOF | ChargeStatus.FVTOF,
            "info": ChargeStatus.FULLM | ChargeStatus.CCM | ChargeStatus.CVM | ChargeStatus.FVM | ChargeStatus.WAKEUP_STOP,
        }
        
        for severity_name, flags in severity_groups.items():
            with self.subTest(severity=severity_name):
                msg = self._create_message(flags.value)
                result = self.parser.parse_read(msg)
                
                # Verify all expected flags are active
                for flag in ChargeStatus:
                    if flag.value & flags.value:
                        self.assertTrue(flag in result["status"])
                
                # Verify severity detection
                if severity_name == "critical":
                    self.assertTrue(result["has_critical"])
                elif severity_name == "warning":
                    self.assertTrue(result["has_warnings"])
    
    def test_parse_read_common_charging_scenarios(self):
        """Test realistic charging scenarios"""
        scenarios = [
            # (scenario_name, status_bits, expected_active_count, has_critical, has_warnings)
            ("CC Charging", ChargeStatus.CCM.value, 1, False, False),
            ("CV Charging", ChargeStatus.CVM.value, 1, False, False),
            ("Float Charging", ChargeStatus.FVM.value, 1, False, False),
            ("Fully Charged", ChargeStatus.FULLM.value, 1, False, False),
            ("CC Timeout", ChargeStatus.CCTOF.value, 1, False, True),
            ("Multiple Timeouts", 
             ChargeStatus.CCTOF.value | ChargeStatus.CVTOF.value, 2, False, True),
            ("Critical Fault", ChargeStatus.NTCER.value, 1, True, False),
            ("Mixed Critical and Warning", 
             ChargeStatus.NTCER.value | ChargeStatus.CCTOF.value, 2, True, True),
            ("All Charging Modes", 
             ChargeStatus.CCM.value | ChargeStatus.CVM.value | ChargeStatus.FVM.value, 3, False, False),
        ]
        
        for scenario_name, status_bits, expected_count, expected_critical, expected_warnings in scenarios:
            with self.subTest(scenario=scenario_name):
                msg = self._create_message(status_bits)
                result = self.parser.parse_read(msg)
                
                self.assertEqual(len(result["active_states"]), expected_count)
                self.assertEqual(result["has_critical"], expected_critical)
                self.assertEqual(result["has_warnings"], expected_warnings)
                self.assertEqual(result["raw_value"], status_bits)
    
    def test_severity_detection_helpers(self):
        """Test the severity detection helper methods with various combinations"""
        test_combinations = [
            (ChargeStatus.NTCER, True, False, False),   # Single critical
            (ChargeStatus.CCTOF, False, True, False),   # Single warning  
            (ChargeStatus.CCM, False, False, False),    # Single info
            (ChargeStatus.NTCER | ChargeStatus.BTNC, True, False, False),  # Multiple critical
            (ChargeStatus.CCTOF | ChargeStatus.CVTOF, False, True, False), # Multiple warnings
            (ChargeStatus.NTCER | ChargeStatus.CCTOF, True, True, False),  # Mixed
        ]
        
        for flags, expected_critical, expected_warnings, expected_errors in test_combinations:
            with self.subTest(flags=flags):
                self.assertEqual(self.parser._has_critical(flags), expected_critical)
                self.assertEqual(self.parser._has_warnings(flags), expected_warnings)
    
    def test_parse_write_not_implemented(self):
        """Test that write parsing raises NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.parser.parse_write("some_data")
    
    def test_invalid_data_length(self):
        """Test handling of messages that are too short"""
        short_msg = Message(data=bytearray(b'\xB8\x00'))  # Only command bytes
        with self.assertRaises(ValueError):
            self.parser.parse_read(short_msg)


if __name__ == '__main__':
    unittest.main()