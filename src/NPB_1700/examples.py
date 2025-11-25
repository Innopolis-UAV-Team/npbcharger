from driver import NPB1700
from services import NPB1700Service
from commands import NPB1700Commands

npb = NPB1700("/dev/ttyACM0")
service = NPB1700Service(npb)

print(service.get_fault_status())
print(service.get_charge_status())
print (service.get_curve_config())
print (service.get_system_config())
print (service.get_system_status())

print (service.get_voltage_current())


print(service.get_constant_voltage_curve())
print(service.get_constant_current_curve())
print(service.get_float_voltage_curve())

#print(service.get_constant_voltage())
#print(service.get_constant_current())

