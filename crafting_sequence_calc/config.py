import json

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        
        self.tier = 14 
        self.data = { 
            "quality_scores": {
                "普通": 1,
                "优质": 5,
                "精良": 30,
                "史诗": 200,
                "传说": 1500
            },
            "active_tier": 14,
            14: self.generate_default()}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                # 将键从字符串转换为整数
                self.data = {
                    int(key) if key.isdigit() else key: value
                    for key, value in raw_data.items()
                }
                self.tier = self.data['active_tier']

                # 验证配置完整性
                if self.tier not in self.data:
                    self.data[self.tier] = self.generate_default()
        except json.JSONDecodeError:
            print("配置文件格式错误，重置为默认配置")
            self.data = {
                "active_tier": 14,
                14: self.generate_default()
            }
        except FileNotFoundError:
            self.save_config()  # 如果文件不存在，创建一个默认配置文件

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def update_tier(self, tier):
        self.tier = tier 
        self.data["active_tier"] = tier
        if tier not in self.data:
            self.data[tier] = self.generate_default()
        self.save_config()

    def update_craft_active(self, craft_active):
        self.data[self.tier]['craft_active'] = craft_active
        self.save_config()

    def update_quality_scores(self, scores):
        self.data["quality_scores"] = scores
        self.save_config()

    def update_sequences(self, sequences):
        self.data[self.tier]["sequences"] = sequences
        self.save_config()

    def update_best_sequence(self, best_sequence):
        self.data[self.tier]["best_sequence"] = best_sequence
        self.save_config()

    def generate_default(self):
        return {
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
