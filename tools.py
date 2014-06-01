def armormod():
  """ 1-24836/(24836+46203.33) """
  base = 24835
  return 1-base/(base+46203.33)
  
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
DIREBEAST = 'Dire Beast'
THRILLOFTHEHUNT = 'Thrill of the Hunt'
TIER4 = [FERVOR,DIREBEAST,THRILLOFTHEHUNT]
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

def istalent(talentstr,talent): # talentstr is 6 digits of numbers 0-2
  _talents = []
  for i in range(0,len(talentstr)):
    _talents.append(TALENTS[i][int(talentstr[i])])
  return talent in _talents

import json
from urllib import urlopen
REGIONS = (('eu','EU'),('us','US'))
SERVERS = [(r['slug'],r['name']) for r in json.load(urlopen('http://us.battle.net/api/wow/realm/status'))['realms']]
for r in json.load(urlopen('http://eu.battle.net/api/wow/realm/status'))['realms']:
  if (r['slug'],r['name']) not in SERVERS:
    SERVERS.append((r['slug'],r['name']))
  
def pretty(value,percent=True):
  if not value:
    return '--'
  elif percent:
    value *= 100
    
  if isinstance(value,float):
    if value < 0.01: # float rounding errors, blech
      return '--'
    return '%.02f%s' % (value,percent and '%' or '')
  else:
    return value