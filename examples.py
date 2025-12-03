#!/usr/bin/env python3

from npbcharger.driver import NPB1700
from npbcharger.services import NPB1700Service


if __name__ == "__main__":
    # Example: create service with custom address
    with NPB1700(channel="/dev/ttyACM0", device_id=0x000C0100) as npb_custom:
        serivce_custom = NPB1700Service(npb_custom)

    # Example: create service which will broadcast messages
    with NPB1700(channel="/dev/ttyACM0", device_id=0x000C01FF) as npb_broadcast:
        serivce_broadcast = NPB1700Service(npb_broadcast)

    # Example: create service with default address
    # NOTE: it's better to use NPB1700 with "with" so context manager of driver
    # would shutdown slcan on it's own
    # But you still may use it without bus.shutdown()
    with NPB1700("/dev/ttyACM0") as npb_default:
        service_default = NPB1700Service(npb_default)

        # Read configs
        print (service_default.get_curve_config())
        print (service_default.get_system_config())

        # Read statuses
        print (service_default.get_fault_status())
        print (service_default.get_charge_status())
        print (service_default.get_system_status())

        # Write into config. For setting config values refer to docs - fields have same name
        # service_default.set_system_config({"EEP_OFF":True})
        # For multivalue fields in config provide integer corresponding to bin code (refer to manual)
        # service_default.set_curve_config({"TCS":1})

        # Read real time voltage & amperage
        print (service_default.get_voltage_current())
        print(service_default.get_constant_current())

        # Read curve voltage & amperage & float voltage values
        print(service_default.get_constant_voltage_curve())
        print(service_default.get_constant_current_curve())
        print(service_default.get_float_voltage_curve())

        # Set curve values
        # Set amperage of curve to 15 A
        # service_default.set_constant_current_curve(15)
        # Set voltage of curve to 32 V
        # service_default.set_constant_voltage_curve(32)
        print(service_default.get_model_id())
