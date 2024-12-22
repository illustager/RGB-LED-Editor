import serial
import serial.tools.list_ports as list_ports

# ports = list_ports.comports()
# for port in ports:
# 	print(port.device, port.description)

# port = input("Enter port: ")

port = 'COM16'

ser = serial.Serial(port, 115200, timeout=1)

f = open('file', 'wb', buffering=1024)

while True:
	try:
		data = ser.read(1024)
		if data is not None:
			f.write(data)
	except KeyboardInterrupt:
		break

f.close()
ser.close()

print("Done")