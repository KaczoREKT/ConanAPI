import yaml
from app.other.utils import read_file

class Config:
    def __init__(self, path="config.yaml"):
        self.config = yaml.safe_load(read_file(path))

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def save(self, path="config.yaml"):
        with open(path, "w") as file:
            yaml.safe_dump(self.config, file, default_flow_style=False)

main_config = Config()