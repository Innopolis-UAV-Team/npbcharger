import can
import enum
import sys

class NPB1700Commands(enum.Enum):
    """CAN Command Codes for Mean Well NPB-1700 Series in Little Endian Format."""
    # pylint: disable=invalid-name

    # --- Control Commands ---
    OPERATION = bytearray([0x00, 0x00])        # R/W, 1 byte - ON/OFF control
    VOUT_SET = bytearray([0x20, 0x00])         # R/W, 2 bytearray - Output voltage setting (F=0.01)
    IOUT_SET = bytearray([0x30, 0x00])         # R/W, 2 bytearray - Output current setting (F=0.01)

    # --- Status/Read Commands ---
    FAULT_STATUS = bytearray([0x40, 0x00])     # R, 2 bytearray - Abnormal status
    READ_VIN = bytearray([0x50, 0x00])         # R, 2 bytearray - Input voltage read value
    READ_VOUT = bytearray([0x60, 0x00])        # R, 2 bytearray - Output voltage read value (F=0.01)
    READ_IOUT = bytearray([0x61, 0x00])        # R, 2 bytearray - Output current read value (F=0.01)
    READ_TEMPERATURE_1 = bytearray([0x62, 0x00]) # R, 2 bytearray - Internal ambient temperature (F=0.1)

    # --- Manufacturer Info Commands ---
    MFR_ID_B0B5 = bytearray([0x80, 0x00])      # R, 6 bytearray - Manufacturer's name
    MFR_ID_B6B11 = bytearray([0x81, 0x00])     # R, 6 bytearray - Manufacturer's name
    MFR_MODEL_B0B5 = bytearray([0x82, 0x00])   # R, 6 bytearray - Manufacturer's model name
    MFR_MODEL_B6B11 = bytearray([0x83, 0x00])  # R, 6 bytearray - Manufacturer's model name
    MFR_REVISION_B0B5 = bytearray([0x84, 0x00]) # R, 6 bytearray - Firmware revision
    MFR_LOCATION_B0B2 = bytearray([0x85, 0x00]) # R/W, 3 bytearray - Manufacturer's factory location
    MFR_DATE_B0B5 = bytearray([0x86, 0x00])    # R/W, 6 bytearray - Manufacturer date
    MFR_SERIAL_B0B5 = bytearray([0x87, 0x00])  # R/W, 6 bytearray - Product serial number
    MFR_SERIAL_B6B11 = bytearray([0x88, 0x00]) # R/W, 6 bytearray - Product serial number

    # --- Charging Curve Commands (Charger Mode) ---
    CURVE_CC = bytearray([0xB0, 0x00])         # R/W, 2 bytearray - Constant current setting (F=0.01)
    CURVE_CV = bytearray([0xB1, 0x00])         # R/W, 2 bytearray - Constant voltage setting (F=0.01)
    CURVE_FV = bytearray([0xB2, 0x00])         # R/W, 2 bytearray - Floating voltage setting (F=0.01)
    CURVE_TC = bytearray([0xB3, 0x00])         # R/W, 2 bytearray - Taper current setting (F=0.01)
    CURVE_CONFIG = bytearray([0xB4, 0x00])     # R/W, 2 bytearray - Configuration setting of charge curve
    CURVE_CC_TIMEOUT = bytearray([0xB5, 0x00]) # R/W, 2 bytearray - CC charge timeout setting
    CURVE_CV_TIMEOUT = bytearray([0xB6, 0x00]) # R/W, 2 bytearray - CV charge timeout setting
    CURVE_FV_TIMEOUT = bytearray([0xB7, 0x00]) # R/W, 2 bytearray - FV charge timeout setting
    CHG_STATUS = bytearray([0xB8, 0x00])       # R, 2 bytearray - Charging status reporting
    CHG_RST_VBAT = bytearray([0xB9, 0x00])     # R/W, 2 bytearray - Voltage to restart charging after full

    # --- System Commands ---
    SCALING_FACTOR = bytearray([0xC0, 0x00])   # R, 2 bytearray - Scaling ratio
    SYSTEM_STATUS = bytearray([0xC1, 0x00])    # R, 2 bytearray - System status
    SYSTEM_CONFIG = bytearray([0xC2, 0x00])    # R/W, 2 bytearray - System configuration


class NPB1700:
    # Private can communication related
    __interface: str = "slcan"
    __channel: str = "/dev/ttyACMx"
    __ttyBaudrate: int = 1000000
    __bitrate: int = 250000
    __id: int = 0x000C0103
    __canBus: can.Bus

    """ Initializes npb1700 can bus instance & id
    
    :param channel: path to device which connected by CAN to NPB-1700
    :param ttyBaudrate: baudrate of your ... -> CAN adapter
    :param id: id of NPB-1700 read documentation to set correct id
    """
    def __init__(self, channel: str, ttyBaudrate: int = 1000000, id: int = 0x000C0103):
        self.__channel = channel
        self.__ttyBaudrate = ttyBaudrate
        self.__id = id
        try:
            self.__canBus = can.Bus(interface = self.__interface, channel = self.__channel, ttyBaudrate = self.__ttyBaudrate, bitrate = self.__bitrate)
        except can.exceptions.CanInitializationError as e:
            print(f"Failed to initialize CAN bus on {self.__channel}: {e}")
            sys.exit(1)
        except Exception as e: # Catch any other unexpected error during instantiation
            print(f"An unexpected error occurred while creating NPB1700 instance: {e}")
            sys.exit(1)


    def spin (self, msg: can.Message, have_responce:bool = True) -> can.Message:
        self.__canBus.send(msg)
        print(f"Message sent on {self.__canBus.channel_info}")
        if (have_responce):
            recMsg: can.Message = self.__canBus.recv(timeout=2.0)
            if recMsg is not None:
                # For debug purposes
                # print(f"Message received on {self.__canBus.channel_info}")
                return recMsg
            return can.Message(error_state_indicator=True)
        return can.Message()
            
    def _createMsg (self, command:NPB1700Commands, params:bytearray = bytearray()) -> can.Message:
        dlc:int = len(command.value) + len(params)
        print (dlc)
        data: bytearray = command.value + params
        return can.Message(arbitration_id=self.__id, dlc=dlc, data=data, is_extended_id=True, check=True)

    def read (self, command:NPB1700Commands) -> can.Message:
        canMsg: can.Message = self._createMsg(command)
        
        # Send message and check if it failed
        recMsg: can.Message = self.spin(canMsg)
        if recMsg.error_state_indicator == True:
            raise NPBCommunicationError
        # TODO (ilyha_dev): parse result data
        return recMsg
    
    def write (self, command:NPB1700Commands, params:bytearray) -> can.Message:
        canMsg: can.Message = self._createMsg(command, params)
        recMsg: can.Message = self.spin(canMsg, False)
        if recMsg.error_state_indicator == True:
            raise NPBCommunicationError
        return recMsg
    
class NPBCommunicationError(Exception):
    """
    Exception which handles loss of communication with NPB-1700
    """
    pass


