from MB.DZG import Meter
import config
import time

config_mb = config.configuration["modbus"]

def create_connections(conf:dict) -> list[Meter]:
	conns:list[Meter] = []
	host, port = conf["location"].split(':')
	port = int(port)
	for name, strAddr in conf["meters"].items():
		if name == "_comment":
			continue
		mb_addr = int(strAddr, 16)
		conns.append(Meter(name=name, unit_id=mb_addr, auto_close=True, auto_open=True, host=host, port=port))
	return conns

def main():
	meters = create_connections(config_mb)
	
	for i in range(2):
		values:dict = {}
		for meter in meters:
			print(f"Reading from {meter.name}")
			value = meter.read_float32(0x4000)
			if value:
				print("Got value!")
				values[meter.name] = value
			else:
				print("No return")
			time.sleep(0.750)
		print("#######\tPrinting results")
		for key, value in values.items():
			print(f'"{key}": "{value}"')
		print(f"#######\tNext run will start in {config_mb['poll_time']}")
		time.sleep(config_mb["poll_time"])
	
	print("End tests")

if __name__=="__main__":
	main()