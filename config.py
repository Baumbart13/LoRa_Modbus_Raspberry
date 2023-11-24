import json
import os
import logging

def load_config(path:str="./config.json") -> dict:
	logging.debug("Fetching config")
	conf:dict = None
	with open(path, 'r', encoding="utf-8") as inFile:
		conf = json.load(inFile)
	return conf

configuration:dict = load_config()
