from typing import Final
from ttn_secrets import APP_EUI, APP_KEY
from rak811.rak811_v3 import Rak811, Rak811Error
import time
import logging


JOIN_MODE_OTAA:Final = 0
JOIN_MODE_ABP:Final = 1

WORK_MODE_LoraWAN:Final = 0
WORK_MODE_LoraP2P:Final = 1

CLASS_A:Final = 0
CLASS_B:Final = 1
CLASS_C:Final = 2

CONFIRM_Unconfirm:Final = 0
CONFIRM_Confirm:Final = 1
CONFIRM_Multicast:Final = 2
CONFIRM_Proprietary:Final = 3

DATA_RATE_EU868_default:Final = 0


def configure_lora(lora:Rak811, data_rate:int=0) -> None:
	lora.set_config(f'lora:work_mode:{WORK_MODE_LoraWAN}')
	lora.set_config(f'lora:join_mode:{JOIN_MODE_OTAA}')
	lora.set_config('lora:region:EU868')
	lora.set_config(f'lora:app_eui:{APP_EUI}')
	lora.set_config(f'lora:app_key:{APP_KEY}')
	lora.set_config(f'lora:confirm:{CONFIRM_Confirm}')
	lora.set_config(f'lora:dr:{data_rate}')

def join_lora(lora:Rak811, retries:int=9999, timeout:float=10) -> None:
	join_error:bool = True
	for i in range(0, retries):
		join_error = False
		try:
			lora.join()
		except Rak811Error as e:
			logging.error(f"{str(e)}, retrying in a few seconds")
			join_error = True
			time.sleep(timeout)
			logging.error("Retrying to join")
		if not join_error:
			break

def pack_for_lora(values:dict) -> bytes:
	n = len(values)
	msg:bytearray = bytearray()
	msg.append(n)
	for key, value in values.items():
		msg.extend(key.encode('ascii'))
		val_prep = int(value*1000).to_bytes(4)
		msg.extend(val_prep)
	print(msg)
	return bytes(msg)

def fit_for_packaging(values:dict) -> list[dict]:
	"""Splits the packet into 3 chunks of data, to not overshoot the
	size-limit of a single packet.
	"""
	items = list(values.items())
	chunk_size = len(items) // 3
	chunks = [dict(items[i:i+chunk_size]) for i in range(0, len(items), chunk_size)]
	return chunks

def fit_for_packaging2(dictionary:dict) -> list[dict]:
    """Splits the packet into exactly 3 chunks of data, to not overshoot the
    size-limit of a single packet.
    """
    items = list(dictionary.items())
    chunk_size = len(items) // 3
    chunks = [dict(items[i:i+chunk_size]) for i in range(0, len(items), chunk_size)]
    
	# Should the amount not exactly dividable by 3, could the last chunk end
	# bigger. Thus the last elements are moved to the previous chunk
    if len(chunks) > 3:
        chunks[-2].update(chunks[-1])
        chunks.pop()
    return chunks
