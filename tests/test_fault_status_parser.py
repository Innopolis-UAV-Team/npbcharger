import unittest
import sys
import os
from can import Message

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from NPB_1700.parsers.fault_status import FaultStatusParser


class TestFaultStateDataParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = FaultStatusParser()

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
        """Test parsing when no faults are active (all zeros)"""
        # Message data: command echo (0x4000) + status bytes (0x0000)
        msg = Message(data=bytearray(b'\x40\x00\x00\x00'))
        result = self.parser.parse_read(msg)
        
        # Verify dictionary structure
        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["fault_status"], FaultStatus.RESERVED)
        self.assertEqual(len(result["active_faults"]), 0)
        self.assertFalse(result["has_critical_faults"])
        self.assertTrue(result["output_enabled"])
    
    def test_parse_read_single_fault(self):
        """Test parsing when one fault is active"""
        # Simulate OTP fault (bit 1)
        # status_word = 0b00000010 = 2
        msg = Message(data=bytearray(b'\x40\x00\x02\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertEqual(result["raw_value"], 2)
        self.assertTrue(FaultStatus.OTP in result["fault_status"])
        self.assertEqual(len(result["active_faults"]), 1)
        self.assertTrue(result["has_critical_faults"])
        self.assertTrue(result["output_enabled"])
        
        self.skipTest("Need actual byte values from device")
    
    def test_parse_read_output_off(self):
        """Test parsing when output is turned off"""
        # Simulate OP_OFF fault (bit 6)
        # status_word = 0b01000000 = 64
        msg = Message(data=bytearray(b'\x40\x00\x40\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertTrue(FaultStatus.OP_OFF in result["fault_status"])
        self.assertFalse(result["output_enabled"])
        self.assertFalse(result["has_critical_faults"])  # OP_OFF is INFO severity
        
        self.skipTest("Need actual byte values from device")
    
    def test_parse_read_multiple_faults(self):
        """Test parsing when multiple faults are active"""
        # Simulate OTP + OVP faults
        # status_word = 0b00000110 = 6 (bit 1 + bit 2)
        msg = Message(data=bytearray(b'\x40\x00\x06\x00'))
        result = self.parser.parse_read(msg)
        
        self.assertTrue(FaultStatus.OTP in result["fault_status"])
        self.assertTrue(FaultStatus.OVP in result["fault_status"])
        self.assertEqual(len(result["active_faults"]), 2)
        self.assertTrue(result["has_critical_faults"])
        
        self.skipTest("Need actual byte values from device")
    
    def test_active_faults_metadata_structure(self):
        """Test that active faults have correct dictionary structure"""
        # Create a test fault status
        test_status = FaultStatus.OTP | FaultStatus.OP_OFF
        
        active_faults = self.parser._get_active_faults(test_status)
        
        # Should have 2 active faults (OTP and OP_OFF)
        self.assertEqual(len(active_faults), 2)
        
        # Check OTP fault metadata
        otp_fault = next(f for f in active_faults if f["fault"] == FaultStatus.OTP)
        self.assertEqual(otp_fault["name"], "Over Temperature Protection")
        self.assertEqual(otp_fault["description"], "Internal temperature abnormal")
        self.assertEqual(otp_fault["severity"], FaultSeverity.CRITICAL)
        self.assertIn("bit_position", otp_fault)
        
        # Check OP_OFF fault metadata
        op_off_fault = next(f for f in active_faults if f["fault"] == FaultStatus.OP_OFF)
        self.assertEqual(op_off_fault["name"], "Output Disabled")
        self.assertEqual(op_off_fault["severity"], FaultSeverity.INFO)
    
    def test_has_critical_faults_detection(self):
        """Test critical fault detection logic"""
        # Test with critical faults
        test_status_critical = FaultStatus.OTP | FaultStatus.OVP
        active_faults_critical = self.parser._get_active_faults(test_status_critical)
        self.assertTrue(self.parser._has_critical_faults(active_faults_critical))
        
        # Test with only info-level faults
        test_status_info = FaultStatus.OP_OFF
        active_faults_info = self.parser._get_active_faults(test_status_info)
        self.assertFalse(self.parser._has_critical_faults(active_faults_info))
        
        # Test with no faults
        test_status_none = FaultStatus.RESERVED
        active_faults_none = self.parser._get_active_faults(test_status_none)
        self.assertFalse(self.parser._has_critical_faults(active_faults_none))
    
    def test_output_enabled_calculation(self):
        """Test output enabled status calculation"""
        # Output should be enabled when OP_OFF is NOT present
        status_enabled = FaultStatus.OTP  # Any fault except OP_OFF
        result = self.parser.parse_read(Message(data=bytearray(b'\x40\x00\x02\x00')))
        # This will depend on the actual byte values
        
        # Output should be disabled when OP_OFF IS present
        status_disabled = FaultStatus.OP_OFF
        # Test would go here with actual byte values


    

if __name__ == '__main__':
    unittest.main()