import requests
import markdown

GITHUB_UPDATES_FILE_URL = 'https://raw.githubusercontent.com/Seymour-ye/shoptitans/refs/heads/main/Qt_MVC_cscalc/UPDATES.md'
GITHUB_README_FILE_URL = 'https://raw.githubusercontent.com/Seymour-ye/shoptitans/refs/heads/main/Qt_MVC_cscalc/README.md'

def fetch_readme():
    response = requests.get(GITHUB_README_FILE_URL)
    if response.status_code == 200:
        content = response.text
        return markdown.markdown(content)
    else:
        return "聪明的人才看得见我，看不见说明你傻。"

def fetch_updates():
    response = requests.get(GITHUB_UPDATES_FILE_URL)
    if response.status_code == 200:
        content = response.text
        return markdown.markdown(content)
    else:
        return "不联网还想看更新，我快递过去给你啊？"
    
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