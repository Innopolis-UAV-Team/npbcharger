from time import sleep
from services import NPB1700Service
from driver import NPB1700
from commands import NPB1700Commands

npb = NPB1700("/dev/ttyACM0")
service = NPB1700Service(npb)
print(service.read_parameter(NPB1700Commands.FAULT_STATUS))
print(service.read_parameter(NPB1700Commands.CHG_STATUS))

print(service.read_parameter(NPB1700Commands.CURVE_CC))
print(service.read_parameter(NPB1700Commands.CURVE_CV))
print(service.read_parameter(NPB1700Commands.CURVE_FV))


#print (service.write_parameter(NPB1700Commands.CURVE_CC, 12))
#print (service.write_parameter(NPB1700Commands.CURVE_CV, 32))
#print (service.write_parameter(NPB1700Commands.CURVE_FV, 29.8))


#print(service.read_parameter(NPB1700Commands.CURVE_CC))
#print(service.read_parameter(NPB1700Commands.CURVE_CV))
#print(service.read_parameter(NPB1700Commands.CURVE_FV))
