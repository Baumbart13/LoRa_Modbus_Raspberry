#!/usr/bin/env python3
# V3.0.x firmware
from rak811.rak811_v3 import Rak811, Rak811Error
import ttn_secrets as ttn
import LoRa
import time

configure_for_ttn = False
join = True

def main():
	print("Create LoRa")
	lora = Rak811()
	print("Configure LoRa")
	lora.set_config(f'lora:work_mode:{LoRa.WORK_MODE_LoraWAN}')
	lora.set_config(f'lora:join_mode:{LoRa.JOIN_MODE_OTAA}')
	lora.set_config('lora:region:EU868')
	lora.set_config(f'lora:app_eui:{ttn.APP_EUI}')
	lora.set_config(f'lora:app_key:{ttn.APP_KEY}')
	lora.set_config(f'lora:confirm:{LoRa.CONFIRM_Confirm}')
	if configure_for_ttn:
		print("Configure for TTN")
		lora.set_config('lora:ch_mask:0,FF00')
		lora.set_config('lora:ch_mask:1,0000')
		lora.set_config('lora:ch_mask:2,0000')
		lora.set_config('lora:ch_mask:3,0000')
		lora.set_config('lora:ch_mask:4,0000')
	print("Joining LoRa")
	join_error:bool = True
	while join_error:
		join_error = False
		try:
			lora.join()
		except Rak811Error as e:
			print(e, ", retrying in a few seconds")
			join_error = True
			time.sleep(20)
			print("Retrying to join")
	print('Send "Hello World" to LoRa')
	lora.send(bytes([0xFF]))
	print("Close LoRa")
	lora.close()

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print(e)