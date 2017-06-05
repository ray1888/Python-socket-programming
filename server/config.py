import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(BASE_DIR+'/config.json',"rb") as f:
	f.readline()
	 