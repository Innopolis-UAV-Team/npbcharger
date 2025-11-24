from time import sleep
import can
from can import BusABC
from commands import NPB1700Commands
from exceptions import NPBCommunicationError
import sys



class NPB1700:
    # Private can communication related
    __interface: str = "slcan"
    __channel: str = "/dev/ttyACMx"
    __ttyBaudrate: int = 1000000
    __bitrate: int = 250000
    __id: int = 0x000C0103
    __canBus: BusABC

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
            self.__canBus = can.Bus(interface=self.__interface, channel=self.__channel,
                                    ttyBaudrate=self.__ttyBaudrate, bitrate=self.__bitrate)
        except can.exceptions.CanInitializationError as e:
            print(f"Failed to initialize CAN bus on {self.__channel}: {e}")
            sys.exit(1)
        except Exception as e:  # Catch any other unexpected error during instantiation
            print(
                f"An unexpected error occurred while creating NPB1700 instance: {e}")
            sys.exit(1)

    def spin(self, msg: can.Message, timeout: float, have_responce: bool = True) -> can.Message:
        self.__canBus.send(msg)
        # For debug purposes
        # print(f"Message sent on {self.__canBus.channel_info}")
        if have_responce:
            recMsg: can.Message | None  = self.__canBus.recv(timeout=2.0)
            if recMsg is not None:
                # For debug purposes
                # print(f"Message received on {self.__canBus.channel_info}")
                return recMsg
            return can.Message(error_state_indicator=True)
        sleep(timeout)
        return can.Message()

    def _createMsg(self, command: NPB1700Commands, params: bytearray = bytearray()) -> can.Message:
        dlc: int = len(command.value) + len(params)
        data: bytearray = command.value + params
        return can.Message(arbitration_id=self.__id, dlc=dlc, data=data, is_extended_id=True, check=True)

    def read(self, command: NPB1700Commands) -> can.Message:
        canMsg: can.Message = self._createMsg(command)

        # Send message and check if it failed
        recMsg: can.Message = self.spin(canMsg, 0.01)
        if recMsg.error_state_indicator == True:
            raise NPBCommunicationError
        return recMsg

    def write(self, command: NPB1700Commands, params: bytearray) -> can.Message:
        canMsg: can.Message = self._createMsg(command, params)
        recMsg: can.Message = self.spin(canMsg, 0.01, False)
        if recMsg.error_state_indicator == True:
            raise NPBCommunicationError
        return recMsg
