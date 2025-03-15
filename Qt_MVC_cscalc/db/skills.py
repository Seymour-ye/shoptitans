import db.heroes as HEROES



SKILLS = {

    'assassinate': {
        'zh': "暗中行动",
        'en': "Assassinate",
        'type': 'p',
        'heroes': HEROES.all_rogue_heroes() | set("Spellblade, Spellknight".lower().split(', '))
    },

    'batteringblows': {
        'zh': "擂鼓呐喊",
        'en': "Battering Blows",
        'type': 'p',
        'heroes': HEROES.all_fighter_heroes() | set("Spellblade, Spellknight, Velite, Praetorian".lower().split(', '))
    },

    'bladedance': {
        'zh': "刃之舞",
        'en': "Dance of Blades",
        'type': 'p',
        'heroes': HEROES.all_rogue_heroes() | HEROES.all_spellcaster_heroes()
    },

    'cloakndagger': {
        'zh': "斗篷匕首",
        'en': "Cloak & Dagger",
        'type': 'p',
        'heroes': HEROES.all_rogue_heroes() | set("Spellblade, Spellknight".lower().split(', '))
    },

    'doublecast': {
        'zh': "双重施法",
        'en': 'Double Cast',
        'type': 'p',
        'heroes': HEROES.all_spellcaster_heroes()
    },

    'extraplating': {
        'zh': "额外镀层",
        'en': "Extra Plating",
        'type': 'p',
        'heroes': HEROES.all_fighter_heroes() | set("Spellblade, Spellknight".lower().split(', '))
    },

    'finesse': {
        'zh': "灵巧",
        'en':"Finesse",
        'type': 'p',
        'heroes': HEROES.all_rogue_heroes() | set("Spellblade, Spellknight".lower().split(', '))
    },

    'glancingblows': {
        'zh': "偏斜攻击",
        'en': "Glancing Blows",
        'type': 'p',
        'heroes': HEROES.all_rogue_heroes() | set("Spellblade, Spellknight".lower().split(', '))
    },

    'megapunch': {
        'zh': "破败打击",
        'en': "Destructive Strikes",
        'type': 'p',
        'heroes': set("Grandmaster".lower().split(', '))
    },

    'perfectform': {
        'zh': "完美形态",
        'en': 'Perfect Form',
        'type': 'p',
        'heroes': HEROES.all_fighter_heroes() | HEROES.all_spellcaster_heroes()
    },

    'petrify': {
        'zh': "石化",
        'en': 'Petrify',
        'type': 'p',
        'heroes': set("Sorcerer, Warlock".lower().split(', '))
    },

    'poisoncloud': {
        'zh': "魔气云雾",
        'en': 'Poison Cloud',
        'type': 'p',
        'heroes': set("Sorcerer, Warlock".lower().split(', '))
    },

    'whirlwind': {
        'zh': "旋风攻击",
        'en': 'Whirlwind Attack',
        'type': 'p',
        'heroes': HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes() | set("Spellblade, Spellknight, Velite, Praetorian".lower().split(', '))
    },

    'arcanemaster': {
        'zh': "大法师",
        'en': "Adept",
        'type': 's',
        'heroes': HEROES.all_spellcaster_heroes() | set(" Berserker, Jarl, Acrobat, Trickster".lower().split(', '))
    },

    'critcritmult': {
        'zh': "奋起反击",
        'en': 'Telling Blows',
        'type': 's',
        'heroes': HEROES.all_spellcaster_heroes() | HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes()
    },

    'megacrit': {
        'zh': "天赋异禀",
        'en': 'All Natural',
        'type': 's',
        'heroes': HEROES.all_spellcaster_heroes() | HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes()
    },

    'megacritmult': {
        'zh': "慈悲商人",
        'en': 'Death Dealer',
        'type': 's',
        'heroes':  HEROES.all_spellcaster_heroes() | HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes()
    },

    'megaevasion': {
        'zh': "模糊动作",
        'en': 'Blurred Movement',
        'type': 's',
        'heroes':  HEROES.all_spellcaster_heroes() | HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes()
    },

    'megahp': {
        'zh': "无动于衷",
        'en': 'Impervious',
        'type': 's',
        'heroes':  HEROES.all_spellcaster_heroes() | HEROES.all_fighter_heroes() | HEROES.all_rogue_heroes()
    },

    'snipermaster': {
        'zh': "狙击手",
        'en': 'Marksman',
        'type': 's',
        'heroes': set("Thief, Trickster, Musketeer, Conquistador, Wanderer, Pathfinder, Ranger, Warden, Spellblade, Spellknight, Dancer, Acrobat, Mage, Archmage, Druid, Arch Druid, Dark Knight, Death Knight".lower().split(', '))
    },

    'warmaster': {
        'zh': "战争大师",
        'en': 'Warlord',
        'type': 's',        
        'heroes': set("Soldier, Mercenary, Barbarian, Chieftain, Knight, Lord, Thief, Trickster, Musketeer, Conquistador, Wanderer, Pathfinder, Spellblade, Spellknight, Ninja, Sensei, Samurai, Daimyo, Berserker, Jarl, Cleric, Bishop, Geomancer, Astramancer, Dark Knight, Death Knight, Chronomancer, Fateweaver".lower().split(', '))

    },
}