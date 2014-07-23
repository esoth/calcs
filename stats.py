from huntermeta import HunterMeta
from tools import *

class Calc(object):
  def __init__(self, **kw):
    self.update(**kw)

  def update(self, **kw):
    for k,v in kw.items():
      if hasattr(self, k):
        setattr(self, k, v)

class Stat(object):
  """ A stat - calculates totals """
  hunter = None
  procs = []
  
  # defaults - always call the method, but default the methods just return these
  _gear = float(0)
  _food = float(0)
  _flask = float(0)
  _spec = float(1)
  _buff = float(0)
  _base = float(0)
  _rating = 1 # rating/1% ratio
  
  def __init__(self,hunter):
    if isinstance(hunter,HunterMeta):
      self.hunter = hunter
    else:
      raise Exception('Stat object must be initiated with a HunterMeta object')
  
  # these methods are setters if a value is passed, otherwise getters
  def gear(self,value=''):
    if value:
      self._gear = value
    else:
      return self._gear
  
  def food(self,value=''):
    if value:
      self._food = value
    else:
      return self._food
  def flask(self,value=''):
    if value:
      self._flask = value
    else:
      return self._flask
  def buff(self,value=''):
    if value:
      self._buff = value
    else:
      return self._buff
  def base(self,value=''):
    if value:
      self._base = value
    else:
      return self._base
  def spec(self,value=''):
    if value:
      self._spec = value
    else:
      return self._spec
  def rating(self,value=''):
    if value:
      self._rating = value
    else:
      return self._rating
  def racial(self):
    return 0
  
  def attunement(self):
    return 1
  
  def ratings(self):
    return self.attunement()*sum([self.gear(), self.food(), self.flask()])
  
  def total_static(self):
    """ The total at all times, before procs """
    stats = self.ratings()/float(self.rating())
    return stats + self.buff() + self.base() + self.racial()
    
  def total(self):
    """ The total with proc averages """
    return self.total_static()
  
  def total_display(self):
    return '%.02f%%' % self.total()
  
  def sum_procs(self, procs=[]):
    return sum([p.average() for p in self.procs])
    
class AgilityStat(Stat):
  """ Behaves a bit differently than ratings based stats """
  _base = 1288
  _spec = 1.05
  _buff = 5
  
  def rating(self):
    return '--'
  
  def base(self):
    """ To do: get a proper list of starting stats per race """
    from tools import HUMAN,ORC,DWARF,NIGHTELF,UNDEAD,TAUREN,GNOME,TROLL,GOBLIN,BLOODELF,DRAENEI,WORGEN,PANDAREN
    racemap = {HUMAN:1284,
               ORC:1281,
               DWARF:1280,
               NIGHTELF:1288,
               UNDEAD:1282,
               TAUREN:1280,
               GNOME:1280, # not actually playable
               TROLL:1286,
               GOBLIN:1286,
               BLOODELF:1286,
               DRAENEI:1349,
               WORGEN:1286,
               PANDAREN:1282}
    return racemap[self.hunter.race]
  
  def buff(self):
    """ Kings """
    return super(AgilityStat,self).buff()
  
  def spec(self):
    """ Mail armor: 5% agi """
    return super(AgilityStat,self).spec()
  
  def total_static(self):
    """ The total at all times, before procs """
    return (self.ratings() + self.base()) * self.spec() * (1+self.buff()/100.0)
  
  def total_display(self):
    return '%.02f' % self.total()

class CritStat(Stat):
  """ Buffs, agi class bonus, boss crit depression """
  _rating = 110
  _buff = 5
  _base = 15-3 # 10=crit for agi users, 3=boss crit suppression

  def attunement(self):
    """ 5% more crit from rating sources for MM """
    return self.hunter.spec == 1 and 1.05 or 1
  
  def racial(self):
    if self.hunter.race in (BLOODELF,WORGEN):
      return 1
    return 0
  
  def buff(self):
    """ 5% crit buff """
    return super(CritStat,self).buff()
  
  def base(self):
    """ Crit depression for +3 boss levels (-3%) + 10% crit for agi users"""
    return super(CritStat,self).base()
  
  def food(self):
    """ Pandarens receive double value """
    _food = self.hunter.spec == 1 and 150 or 0
    if self.hunter.race in PANDARENS:
      _food *= 2
    return _food
  
  def flask(self):
    return self.hunter.spec == 1 and 500 or 0
  
  def total_display(self):
    """ In game tooltip will appear 3% higher, plus 1% for some racials """
    return super(CritStat,self).total_display()

class HasteStat(Stat):
  """ 5% haste buff """
  _rating = 100
  _buff = 5
  
  def racial(self):
    """ Night Elf 1% (assume night), Goblin """
    return self.hunter.race in (NIGHTELF,GOBLIN,) and .01 or 0
  
  def buff(self):
    """ 5% haste buff """
    return super(HasteStat,self).buff()
  
  def total_static(self):
    """ Haste works a bit different in that it's all multiplicative """
    stats = 1 + self.ratings()/float(self.rating())/100
    stats *= (1+self.buff()/100.0)
    stats *= (1 + self.racial())
    return stats

  def total_display(self):
    return '%.02f%%' % ((self.total_static()-1)*100.0)

class MasteryStat(Stat):
  """ 5% mastery buff """
  _rating = 55
  _buff = 550 # this one is actually rating!
  
  def food(self):
    """ Pandarens receive double value """
    _food = self.hunter.spec == 0 and 150 or 0
    if self.hunter.race in PANDARENS:
      _food *= 2
    return _food
  
  def flask(self):
    return self.hunter.spec == 0 and 500 or 0
  
  def rating(self):
    if self.hunter.spec == 0:
      return 55.0
    elif self.hunter.spec == 1:
      return 110.0
    else:
      return 110.0
  
  def base(self):
    if self.hunter.spec == 0:
      return 16
    elif self.hunter.spec == 1:
      return 8
    else:
      return 8
  
  def buff(self):
    """ 5% mastery buff - but technically a rating """
    return super(MasteryStat,self).buff()

  def attunement(self):
    """ 5% more mastery from rating sources for BM """
    return self.hunter.spec == 0 and 1.05 or 1
  
  def ratings(self):
    """ For mastery, the mastery buff counts since it is technically a rating """
    return self.attunement()*sum([self.gear(), self.food(), self.flask(), self.buff()])
  
  def total_static(self):
    """ The total at all times, before procs """
    stats = self.ratings()/self.rating()
    return stats + self.base()

class VersatilityStat(Stat):
  """ 3% versatility buff """
  _rating = 130
  _buff = 3
  
  def racial(self):
    return self.hunter.race == HUMAN and 100 or 0
  
  def ratings(self):
    return sum([self.gear(), self.food(), self.flask(), self.racial()])
  
  def total_static(self):
    """ The total at all times, before procs """
    stats = self.ratings()/float(self.rating())
    return stats + self.buff() + self.base()

class MultistrikeStat(Stat):
  """ 5% multistrike buff """
  _rating = 66
  _buff = 5
  
  def base(self):
    """ SV starts at 10 """
    return self.hunter.spec == SV and 10 or 0
  
  def food(self):
    """ Pandarens receive double value """
    _food = self.hunter.spec == SV and 150 or 0
    if self.hunter.race in PANDARENS:
      _food *= 2
    return _food
  
  def flask(self):
    return self.hunter.spec == SV and 500 or 0

  def attunement(self):
    """ 5% more multistrike from rating sources for SV """
    return self.hunter.spec == SV and 1.05 or 1

class Proc(Calc):
  rppm = 1.0
  magnitude = float(0)
  duration = float(0)
  static_haste = 1.0
  
  def average(self):
    return self.magnitude*self.rppm/(6.0/self.static_haste)
  
  def uptime(self):
    return float(0)

class ProcManager(object):
  agility = []
  haste = []
  crit = []
  mastery = []
  multistrike = []
  versatility = []
  
  def proc_table(self):
    pass