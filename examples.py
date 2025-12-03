#!/usr/bin/env python3
import argparse
import os
from npbcharger.driver import NPB1700
from npbcharger.services import NPB1700Service



if __name__ == "__main__":
    # Initialise usging argparse
    default_channel = "COM3@1000000" if os.name == "nt" else "/dev/ttyACM0"
    parser = argparse.ArgumentParser(description="Mean Well NPB-1700 Control Tool")
    parser.add_argument(
        "--channel",
        type=str,
        default=default_channel,
        help=f"Channel for NPB1700 (default: {default_channel})",
    )
    parser.add_argument(
        "--iface",
        type=str,
        default='slcan',
        help=f"Interface for NPB1700 (default: {default_channel})",
    )

    args = parser.parse_args()

    # Example: create service with default address
    # NOTE: it's better to use NPB1700 with "with" so context manager of driver
    # would shutdown slcan on it's own
    # But you still may use it without bus.shutdown()
    with NPB1700(channel=args.channel, interface=args.iface, device_id=0x000C01FF) as npb_default:
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
