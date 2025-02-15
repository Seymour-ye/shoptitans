import json
import db.constants as CONSTANTS

class ConfigManager:
    def __init__(self):
        self.config_file = 'local.json'
        self.data = self.generate_config_default()
        self.load_config()

    def generate_tier_default(self, tier):
        return {
            'best_sequence': [],
            'craft_active': 0,
            'scores': [1,5,30,200,1500],
            'back_switch': False,
            'back_switch_rate': 0,
            'sequences': self.generate_tier_default_sequence(tier, False),
            'marked':[False, False, False, False, False]
        }
    
    def generate_tier_default_sequence(self, tier, backswitch):
        ret = []
        unv = CONSTANTS.unvisibles(tier, backswitch)
        for i in range(5):
            seq = []
            for j in range(unv[i]):
                seq.append((0,0))
            ret.append(seq)
        return ret

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
            14: self.generate_tier_default(14),
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
                    self.data[self.tier] = self.generate_tier_default(self.tier)
        except json.JSONDecodeError:
            print("配置文件格式错误，重置为默认配置")
            self.data = self.generate_config_default()
        except FileNotFoundError:
            self.save_config()  # 如果文件不存在，创建一个默认配置文件

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def get_quality_score(self, tier, quality_index):
        return self.data[tier]['scores'][quality_index]
    
    def update_quality_score(self, tier, quality_index, score):
        self.data[tier]['scores'][quality_index] = score 
        self.save_config()

    def update_active_tier(self, tier):
        self.data['active_tier'] = tier 
        if tier not in self.data:
            self.data[tier] = self.generate_tier_default(tier)
        self.save_config()

    def get_back_switch(self, tier):
        return self.data[tier]['back_switch']

    def get_back_switch_rate(self, tier):
        return self.data[tier]['back_switch_rate']
    
    def update_back_switch(self, tier, checked):
        self.data[tier]['back_switch'] = checked 
        self.save_config()

    def update_back_switch_rate(self, tier, value):
        self.data[tier]['back_switch_rate'] = value 
        self.save_config()

    def update_craft_active(self, tier, value):
        self.data[tier]['craft_active'] = value 
        self.save_config()

    def get_craft_active(self, tier):
        return self.data[tier]['craft_active']
    
    def get_craft_sequence(self, tier, sequence_index):
        return self.data[tier]['sequences'][sequence_index]
        
    def get_craft_sequences(self, tier):
        return self.data[tier]['sequences']
    
    def add_sequence_log(self, tier, sequence_index, quality, amount):
        self.data[tier]['sequences'][sequence_index].append((quality, amount))
        self.save_config()
    
    def sequence_log_backspace(self, tier, sequence_index):
        if len(self.data[tier]['sequences'][sequence_index]) > CONSTANTS.unvisibles(tier, self.get_back_switch(tier))[sequence_index]:
            self.data[tier]['sequences'][sequence_index].pop()
        self.save_config()

    def reset_sequences(self, tier):
        self.data[tier]['sequences'] = self.generate_tier_default_sequence(tier, self.get_back_switch(tier))
        self.data[tier]['craft_active'] = 0
        self.save_config()

    def craft_item(self, tier):
        for i in range(5):
            if self.data[tier]['sequences'][i]:
                self.data[tier]['sequences'][i].pop(0)
        self.save_config()

    def craft_back_switch(self, tier):
        curr_craft_active = (self.get_craft_active(tier) - 1) % 5
        self.update_craft_active(tier, curr_craft_active)  #更新craft active
        if self.data[tier]['sequences'][curr_craft_active]:
            self.data[tier]['sequences'][curr_craft_active].pop(0) # 多消耗一个
        self.craft_item(tier)   #做一个

    def craft_stone(self, tier):
        for i in range(5):
            if i != self.get_craft_active(tier):
                if self.data[tier]['sequences'][i]:
                    self.data[tier]['sequences'][i].pop(0)
        self.update_craft_active(tier, (self.get_craft_active(tier) + 1) % 5)
        self.save_config()

    def get_best_sequence(self, tier):
        return self.data[tier]['best_sequence']
    
    def update_best_sequence(self, tier, sequence):
        self.data[tier]['best_sequence'] = sequence 
        self.save_config()

    def get_sequence_mark(self, tier, i):
        return self.data[tier]['marked'][i]
    
    def update_sequence_mark(self, tier, i, checked):
        self.data[tier]['marked'][i] = checked
        self.save_config()