import unittest
import sys
import os
from can import Message

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from NPB_1700.parsers.fault_status import FaultStatusParser, FaultStatus, FaultSeverity


class TestFaultStatusParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = FaultStatusParser()
    
    def test_parse_read_normal_status(self):
        # Message data: command echo (0x4000) + status bytes (0x0000)
        msg = Message(data=bytearray(b'\x40\x00\x00\x00'))
        result = self.parser.parse_read(msg)
        
        # Verify dictionary structure
        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["status"], FaultStatus(0))  # Empty flags
        self.assertEqual(len(result["active_states"]), 0)
        self.assertFalse(result["has_critical"])
        self.assertFalse(result["has_errors"])
        self.assertFalse(result["has_warnings"])
    
    def test_parse_read_single_fault(self):
        # Simulate OTP fault (bit 1 = 0x0002)
        # status_word = 0b00000010 = 2
        msg = Message(data=bytearray(b'\x40\x00\x02\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertEqual(result["raw_value"], 2)  # Should be 2, not 1
        self.assertTrue(FaultStatus.OTP in result["status"])
        self.assertEqual(len(result["active_states"]), 1)
        self.assertTrue(result["has_critical"])  # OTP is CRITICAL
        
        # Check active state metadata
        active_state = result["active_states"][0]
        self.assertEqual(active_state["state"], FaultStatus.OTP)
        self.assertEqual(active_state["name"], "Over Temperature Protection")
        self.assertEqual(active_state["severity"], FaultSeverity.CRITICAL)
    
    def test_parse_read_output_off(self):
        # Simulate OP_OFF fault (bit 6 = 0x0040)
        # status_word = 0b01000000 = 64
        msg = Message(data=bytearray(b'\x40\x00\x40\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertTrue(FaultStatus.OP_OFF in result["status"])
        self.assertFalse(result["has_critical"])  # OP_OFF is INFO severity
        self.assertFalse(result["has_errors"])
        
        # Check that OP_OFF is correctly identified as INFO severity
        op_off_state = next(s for s in result["active_states"] if s["state"] == FaultStatus.OP_OFF)
        self.assertEqual(op_off_state["severity"], FaultSeverity.INFO)
    
    def test_parse_read_multiple_faults(self):
        """Test parsing when multiple faults are active"""
        # Simulate OTP + OVP faults (bits 1 + 2 = 0x0006)
        # status_word = 0b00000110 = 6
        msg = Message(data=bytearray(b'\x40\x00\x06\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertTrue(FaultStatus.OTP in result["status"])
        self.assertTrue(FaultStatus.OVP in result["status"])
        self.assertEqual(len(result["active_states"]), 2)
        self.assertTrue(result["has_critical"])  # Both are CRITICAL
        
        # Verify both faults are critical
        critical_states = [s for s in result["active_states"] if s["severity"] == FaultSeverity.CRITICAL]
        self.assertEqual(len(critical_states), 2)
    
    def test_active_states_metadata_structure(self):
        """Test that active states have correct dictionary structure"""
        # Create a message with OTP + OP_OFF faults (bits 1 + 6 = 0x0042)
        # OTP (bit1=0x02) + OP_OFF (bit6=0x40) = 0x42
        msg = Message(data=bytearray(b'\x40\x00\x42\x00'))
        result = self.parser.parse_read(msg)
        active_states = result["active_states"]
        
        # Should have 2 active states (OTP and OP_OFF)
        self.assertEqual(len(active_states), 2)
        
        # Check OTP fault metadata
        otp_state = next(s for s in active_states if s["state"] == FaultStatus.OTP)
        self.assertEqual(otp_state["name"], "Over Temperature Protection")
        self.assertEqual(otp_state["description"], "Internal temperature abnormal")
        self.assertEqual(otp_state["severity"], FaultSeverity.CRITICAL)
        
        # Check OP_OFF fault metadata
        op_off_state = next(s for s in active_states if s["state"] == FaultStatus.OP_OFF)
        self.assertEqual(op_off_state["name"], "Output Disabled")
        self.assertEqual(op_off_state["description"], "Output is turned off")
        self.assertEqual(op_off_state["severity"], FaultSeverity.INFO)
    
    def test_severity_detection_methods(self):
        """Test the severity detection helper methods"""
        # Create a parser instance to test methods
        parser = FaultStatusParser()
        
        # Test with critical fault (OTP)
        critical_status = FaultStatus.OTP
        self.assertTrue(parser._has_critical(critical_status))
        self.assertFalse(parser._has_errors(critical_status))
        self.assertFalse(parser._has_warnings(critical_status))
        
        # Test with info fault (OP_OFF)  
        info_status = FaultStatus.OP_OFF
        self.assertFalse(parser._has_critical(info_status))
        self.assertFalse(parser._has_errors(info_status))
        self.assertFalse(parser._has_warnings(info_status))
    
    def test_parse_read_all_critical_faults(self):
        """Test detection when multiple critical faults are active"""
        # OTP(bit1=0x02) + OVP(bit2=0x04) + OLP(bit3=0x08) + SHORT(bit4=0x10) + AC_FAIL(bit5=0x20) + HI_TEMP(bit7=0x80)
        # = 0x02 + 0x04 + 0x08 + 0x10 + 0x20 + 0x80 = 0xBE
        msg = Message(data=bytearray(b'\x40\x00\xBE\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertTrue(result["has_critical"])
        self.assertEqual(len(result["active_states"]), 6)  # 6 faults total
    
    def test_parse_write_not_implemented(self):
        """Test that write parsing raises NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.parser.parse_write("some_data")
    
    def test_invalid_data_length(self):
        """Test handling of messages that are too short"""
        short_msg = Message(data=bytearray(b'\x40\x00'))  # Only 2 bytes
        with self.assertRaises(ValueError):
            self.parser.parse_read(short_msg)


if __name__ == '__main__':
    unittest.main()