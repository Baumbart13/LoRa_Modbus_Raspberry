from .Meter import Meter
import logging

class WH4013(Meter):
	def __init__(self, name: str, host='localhost', port=502, unit_id=1, timeout=30, debug=False, auto_open=True, auto_close=False):
		super().__init__(name, host, port, unit_id, timeout, debug, auto_open, auto_close)
	
	def read_current_power(meter:Meter) -> float:
		REG_ADDR = 0x4000
		value = meter.read_float32(REG_ADDR)
		if value is None:
			logging.error("Could not read power from meter: %s, mb_addr=%x, reg_addr=%x", meter.name, meter.unit_id, REG_ADDR)
			return None
		return abs(value)
