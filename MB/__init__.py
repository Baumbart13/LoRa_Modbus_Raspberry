from .Meter import Meter
from . import DZG


def create_connections(class_type:type, addresses:list[tuple], host:str, port:str) -> list:
	conns:list[class_type] = []
	for name, strAddr in addresses.items():
		if name == "_comment":
			continue
		mb_addr = int(strAddr, 16)
		conns.append(class_type(name=name, unit_id=mb_addr, auto_close=True, auto_open=True, host=host, port=port))
	return conns
