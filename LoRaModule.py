from rak811.rak811_v3 import Rak811
from typing import List


class LoRaModule(Rak811):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def reboot(self) -> List[str]:
		# We use the "_list" variant to drain the buffer
		return super()._send_command_list(f'set_config=device_restart')
