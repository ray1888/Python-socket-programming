import os
import json

Basedir = os.path.dirname(os.getcwd())
Confdir = Basedir+"/conf/"

with open(Confdir+"config.json", "r") as f:
	config = f.read()
	config = json.loads(config)
	Host = config["Host"]
	Port = config["Port"]
	Mode = config["Mode"]

	print("Host is {}".format(Host))
	print("Port is {}".format(Port))
	print("Mode is {}".format(Mode))