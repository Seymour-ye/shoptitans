import json

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = {
            "quality_scores": {
                "普通": 1,
                "优质": 5,
                "精良": 30,
                "史诗": 200,
                "传说": 1500
            },
            "sequences": {
                "石头x0": [],
                "石头x1": [],
                "石头x2": [],
                "石头x3": [],
                "石头x4": []
            },
            "best_sequence": [],
            'craft_active': 0
        }
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.save_config()  # 如果文件不存在，创建一个默认配置文件

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def update_craft_active(self, craft_active):
        self.data['craft_active'] = craft_active
        self.save_config()

    def update_quality_scores(self, scores):
        self.data["quality_scores"] = scores
        self.save_config()

    def update_sequences(self, sequences):
        self.data["sequences"] = sequences
        self.save_config()

    def update_best_sequence(self, best_sequence):
        self.data["best_sequence"] = best_sequence
        self.save_config()

