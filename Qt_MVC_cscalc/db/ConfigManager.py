import json

class ConfigManager:
    def __init__(self):
        self.config_file = 'local.json'
        self.data = self.generate_config_default()
        self.load_config()

    def generate_tier_default(self):
        return {
            'best_sequence': [],
            'sequences': [[],[],[],[],[]],
            'craft_active': 0,
            'scores': [1,5,30,200,1500]
        }
    
    def generate_enchantment_default(self):
        return {
            'superior':[],
            'flawless':[],
            'epic':[],
            'legendary':[],
            'result':[]
        }
    
    def generate_config_default(self):
        return {
            'active_tier': 14, 
            14: self.generate_tier_default(),
            'enchantment': self.generate_enchantment_default(),
            'logs':[] #'YYYY-MM-DD HH:MM action description',...
        }

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
            self.data = self.generate_config_default()
        except FileNotFoundError:
            self.save_config()  # 如果文件不存在，创建一个默认配置文件

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

