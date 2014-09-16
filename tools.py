API_KEY = 'n3kp7varcf4wrtkmu3qcgqzszgtyznmb'

def armormod():
  """ 1-1938/(1938+5234); 1938 is boss armor, 134*103-11864; K=3610 """
  base = 1938.0
  return 1.0-base/(base+3610)
  
# races
HUMAN = 1
ORC = 2
DWARF = 3
NIGHTELF = 4
UNDEAD = 5
TAUREN = 6
GNOME = 7
TROLL = 8
GOBLIN = 9
BLOODELF = 10
DRAENEI = 11
WORGEN = 22
PANDAREN = 24

RACES = ((HUMAN,'Human'),
         (DWARF,'Dwarf'),
         (NIGHTELF,'Night Elf'),
         (GNOME,'Gnome'),
         (DRAENEI,'Draenei'),
         (WORGEN,'Worgen'),
         (ORC,'Orc'),
         (UNDEAD,'Undead'),
         (TAUREN,'Tauren'),
         (TROLL,'Troll'),
         (GOBLIN,'Goblin'),
         (BLOODELF,'Blood Elf'),
         (PANDAREN,'Pandaren'),)
PANDARENS = (24,25,26,) # neutral, alliance, horde are codes as separate races!

# specs
BM = 0
MM = 1
SV = 2
SPECS = ((BM,'Beast Mastery'),
         (MM,'Marksmanship'),
         (SV,'Survival'),)

# talents
POSTHASTE = 'Posthaste'
NARROWESCAPE = 'Narrow Escape'
CROUCHINGTIGER = 'Crouching Tiger, Hidden Dragon'
TIER1 = [POSTHASTE,NARROWESCAPE,CROUCHINGTIGER]
BINDINGSHOT = 'Binding Shot'
WYVERNSTING = 'Wyvern Sting'
INTIMIDATION = 'Intimidation'
TIER2 = [BINDINGSHOT,WYVERNSTING,INTIMIDATION]
EXHILARATION = 'Exhilaration'
IRONHAWK = 'Iron Hawk'
SPIRITBOND = 'Spirit Bond'
TIER3 = [EXHILARATION,IRONHAWK,SPIRITBOND]
FERVOR = 'Fervor'
STEADYFOCUS = 'Steady Focus'
DIREBEAST = 'Dire Beast'
THRILLOFTHEHUNT = 'Thrill of the Hunt'
TIER4 = [STEADYFOCUS,DIREBEAST,THRILLOFTHEHUNT]
AMURDEROFCROWS = 'A Murder of Crows'
BLINKSTRIKES = 'Blink Strikes'
STAMPEDE = 'Stampede'
TIER5 = [AMURDEROFCROWS,BLINKSTRIKES,STAMPEDE]
GLAIVETOSS = 'Glaive Toss'
POWERSHOT = 'Powershot'
BARRAGE = 'Barrage'
TIER6 = [GLAIVETOSS,POWERSHOT,BARRAGE]
EXOTICMUNITIONS = 'Exotic Munitions'
FOCUSINGSHOT = 'Focusing Shot'
VERSATILITY = 'Versatility'
TIER7 = [EXOTICMUNITIONS,FOCUSINGSHOT,VERSATILITY]
TALENTS = [TIER1,TIER2,TIER3,TIER4,TIER5,TIER6,TIER7]

def product(value):
  if value:
    _next = value.pop()
    return _next * product(value)
  else:
    return 1

import json
from urllib import urlopen
REGIONS = (('eu','EU'),('us','US'))

# SERVERS - Get all US servers than all EU servers """
_servers = []
try:
  _servers = [(r['slug'],r['name']) for r in json.load(urlopen('https://us.api.battle.net/wow/realm/status?apikey=%s' % API_KEY))['realms']]
except:
  pass # kinda crashes the whole site otherwise!
try:
  eu_realms = json.load(urlopen('https://eu.api.battle.net/wow/realm/status?apikey=%s' % API_KEY))['realms']
  for r in eu_realms:
    if (r['slug'],r['name']) not in _servers:
      _servers.append((r['slug'],r['name']))
except:
  pass
SERVERS = _servers

SERVER_NAMES = {}
for slug,name in SERVERS:
  SERVER_NAMES[slug] = name
    
def tooltip(compid,value):
  if compid in ('buff','armor',):
    return '%.02f%%' % value
  elif compid == 'spec':
    return '%.02f' % (value*100.0)
  elif compid == 'attunement':
    return value == 1 and '--' or '%.02f%%' % (value*100.0)
  elif compid == 'spell':
    return '%.02f%%' % (value*100.0)
  elif compid == 'racial' and value <= 100: # humans actually get a rating
    return '%.02f%%' % value
  elif isinstance(value,float):
    return '%.02f' % value
  else:
    return value

def orc_ap():
  ap = 345
  dur = 15
  cd = 120
  return ap * dur / cd