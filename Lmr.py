#!/usr/bin/env python

from rak811.rak811_v3 import Rak811Error
from LoRaModule import LoRaModule as Rak811
import MB
from MB import DZG
import LoRa
import config
import logging
import time
import sys


configuration = config.configuration
mb_conf = configuration["modbus"]
lora_conf = configuration["lora"]


def boot(lora:Rak811, mb_conf:dict, lora_conf:dict, activate_lora:bool=True, activate_modbus:bool=True) -> list[DZG.WH4013]:
	"""
	Configure the Rak811-LoRa Module as well as create
	a list of all Modbus-Meters and return those meters.
	"""
	if activate_lora:
		logging.debug("Configuring LoRa module")
		LoRa.configure_lora(lora, data_rate=lora_conf["data-rate"])
		logging.debug("Joining LoRa cloud")
		LoRa.join_lora(lora, timeout=lora_conf["retry_timeout"])

	meters:list[DZG.WH4013] = []
	if activate_modbus:
		logging.debug("Creating modbus-connections")
		mb_host, mb_port = mb_conf["location"].split(':')
		mb_port = int(mb_port)
		mb_addresses = mb_conf["meters"]
		meters:list[DZG.WH4013] = MB.create_connections(DZG.WH4013, mb_addresses, mb_host, mb_port)

	return meters

def shutdown(lora:Rak811, meters:list[MB.Meter]) -> None:
	lora.close()
	for meter in meters:
		meter.close()

def test_run(runs:int, meters:list[DZG.WH4013], lora:Rak811) -> None:
	for i in range(runs):
		values:dict[str, float] = {}
		for meter in meters:
			logging.debug("Reading from %s, 0x%X", meter.name, meter.unit_id)
			value = meter.read_current_power()
			values[meter.name] = value

			# There needs to be a timeout between each call for a new
			# modbus-device. Minimum looks like 500ms, but 750ms is much
			# safer to use. Original SPS-Version has a timeout of 1000ms.
			time.sleep(0.750)
		if logging.getLevelName == logging.DEBUG:
			for key, value in values.items():
				logging.info('"%s": "%s"', key, value)
		
		# Need to split the package, as 40 bytes are too large to send
		# in one single send
		# Applies to data rates below 3
		if lora_conf["data-rate"] < 3:
			fitted_packets = LoRa.fit_for_packaging2(values)
			for fit in fitted_packets:
				pack = LoRa.pack_for_lora(fit)
				lora.send(pack)
				#time.sleep(0.050)
		else:
			lora.send(values)

		logging.info("Next run starting in 5 seconds...")
		time.sleep(5)
	logging.info("End of test")

def run(meters:list[DZG.WH4013], lora:Rak811, mb_timeout:float) -> None:
	values:dict[str, float] = {}
	for meter in meters:
		logging.debug("Reading from %s, 0x%X", meter.name, meter.unit_id)
		value = meter.read_current_power()
		if value is not None:
			values[meter.name] = value

		# There needs to be a timeout between each call for a new
		# modbus-device. Minimum looks like 500ms, but 750ms is much
		# safer to use. Original SPS-Version has a timeout of 1000ms.
		time.sleep(mb_timeout)
	for key, value in values.items():
		logging.debug('"%s": "%s"', key, value)
	
	# Need to split the package, as 40 bytes are too large to send
	# in one single packet
	# Applies to data rates below 3
	if lora_conf["data-rate"] < 3:
		fitted_packets = LoRa.fit_for_packaging2(values)
		for fit in fitted_packets:
			pack = LoRa.pack_for_lora(fit)
		try:
			lora.send(pack)
		except Rak811Error as e:
			if "Errno 80" in str(e):
				lora.reboot()
			#time.sleep(0.050)
	else:
		try:
			pack = LoRa.pack_for_lora(values)
			lora.send(pack)
		except Rak811Error as e:
			logging.error(e)

def exit(lora:Rak811, meters:list[MB.Meter]) -> None:
	logging.info("Closing connection to LoRa-module")
	lora.close()
	logging.info("Closing connection to electrical meters")
	for meter in meters:
		meter.close()
	logging.info("Exiting program...")

def main() -> None:
	lora = Rak811()
	meters:list[DZG.WH4013] = boot(lora, mb_conf, lora_conf)

#	if logging.root.level == logging.DEBUG:
#		test_run(5, meters, lora)
#		return
	try:
		while True:
			run(meters, lora, mb_conf["timeout"])
			for i in range(lora_conf["poll_time"]//60,0,-1):
				seconds = i * 60
				logging.debug("Waiting for next poll... %s seconds remaining", seconds)
				time.sleep(60)
	except KeyboardInterrupt:
		pass
	finally:
		exit(lora, meters)

def main_once():
	lora = Rak811()
	meters:list[DZG.WH4013] = boot(lora, mb_conf, lora_conf)
	try:
		run(meters, lora, mb_conf["timeout"])
	except KeyboardInterrupt:
		pass
	finally:
		exit(lora, meters)

if __name__ == "__main__":
	logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", datefmt='%m/%d/%YT%I:%M:%S', force=True)
	logging.root.addHandler(logging.StreamHandler(sys.stdout))
	logging.root.addHandler(logging.FileHandler(configuration["log_file"]))
	for i in range(1, len(logging.root.handlers)):
		logging.root.handlers[i].setFormatter(logging.root.handlers[0].formatter)
	logging.root.setLevel(logging.DEBUG)
	logging.root.name = "ESPO LMR"
	main_once()
