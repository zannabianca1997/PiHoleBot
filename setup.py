import json

with open("setup.json") as setup_file:
    setup = json.load(setup_file)

locals().update(setup)
