import requests

GITHUB_UPDATE_URL = ''

qualities = {
            "普通": "#ffffff",  # 白色
            "优质": "#00ff00",  # 绿色
            "精良": "#4da6ff",  # 蓝色
            "史诗": "#a64ca6",  # 紫色
            "传说": "#ffd700",  # 金色
        }

default_scores = [1, 5, 30, 200, 1500]

switchables = {
    #Tier: Stone, Sigil
    1: (False, False),
    2: (False, False),
    3: (False, False),
    4: (True, False),
    5: (False, False),
    6: (False, False),
    7: (True, False),
    8: (False, False),
    9: (True, False),
    10: (True, False),
    11: (False, True),
    12: (True, True),
    13: (False, True),
    14: (True, True)
}