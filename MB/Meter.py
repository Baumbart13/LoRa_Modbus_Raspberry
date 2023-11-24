from pyModbusTCP.client import ModbusClient


class Meter(ModbusClient):
	def __init__(self, name:str, host='localhost', port=502, unit_id=1, timeout=30, debug=False, auto_open=True, auto_close=False):
		super().__init__(host, port, unit_id+1, timeout, debug, auto_open, auto_close)
		self.name = name

	def read_int16(self, reg_addr:int) -> int | None:
		resp = self.read_holding_registers(reg_addr, 1)
		if not resp:
			return None
		return resp

	def read_int32(self, reg_addr:int) -> int | None:
		l:int	= 0
		r:int	= 0
		i32:int	= 0

		resp = self.read_holding_registers(reg_addr, 2)
		if not resp:
			return None
		l, r = resp
		i32 = (l << 16 ) | r
		return i32
	
	def read_int64(self, reg_addr:int) -> int | None:
		l1:int	= 0
		l2:int	= 0
		r1:int	= 0
		r2:int	= 0
		i64:int	= 0

		resp = self.read_holding_registers(reg_addr, 4)
		if not resp:
			return None
		l1, l2, r1, r2 = resp
		i64 = (l1 << 48 ) | (l2 << 32) | (r1 << 16) | r2
		return i64

	def read_float32(self, reg_addr:int, decimals:int=3) -> float | None:
		i32:int		= 0
		f32:float	= 0.0

		i32 = self.read_int32(reg_addr)
		if not i32:
			return None
		f32 = i32 * (10.0**(-decimals))
		return f32
	
	def read_float64(self, reg_addr:int, decimals:int=3) -> float | None:
		i64:int		= 0
		f64:float	= 0

		i64 = self.read_int64(reg_addr)
		if not i64:
			return None
		f64 = i64 * (10.0**(-decimals))
		return f64
