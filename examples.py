from npbcharger.driver import NPB1700
from npbcharger.services import NPB1700Service


npb = NPB1700("/dev/ttyACM0")
service = NPB1700Service(npb)

# NOTE: RTSE and CVTSSE strange behaviour. When i sent 0x{010C03}{4}{B40084FF} (set whole h byte to 1's to check bits that can be written)
# I then read B4008407 which proves that we can't write to RSTE and CVTSSE bits
# Since that work with r/w of CHG_RST_VBAT causes connection error!
# Manual p. 59 reports:
# The following two conditions need to be met in order for
# this function [CHG_RST_VBAT] to take effect:
# NPB is in curve charging mode, and this setting value is applicable to all
# 4 charging curves;
# The bit3: RSTE value of 0x00B4 (CURVE_CONFIG) High byte is 1;

# However it's still important to mention that charger does not respond even to simple read messages on B9! 0x{010C03}{2}{B900} doesn't get any answer!
# Such behaviour is really strange and it's worth investigating

#print(service.get_temperature_1())
# print(service.get_operation_status())
#print(service.set_operation_status(False))
# print(service.get_operation_status())
#print(service.set_operation_status(True))
#service.set_curve_config({"CVTSSE": True,"RSTE":True})
print(service.get_curve_config())
#print (service.get_charge_restart_vbat())
print(service.get_operation_status())
print (service.get_system_config())

service.set_system_config({"EEP_OFF":True})

print (service.get_system_config())



print(service.get_fault_status())
print(service.get_charge_status())





print (service.get_voltage_current())
print(service.get_constant_current())


print(service.get_constant_voltage_curve())
print(service.get_constant_current_curve())
print(service.get_float_voltage_curve())

