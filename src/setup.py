import json

with open("/etc/opt/PiHoleBot/setup.json") as setup_file:
    setup = json.load(setup_file)

locals().update(setup)
