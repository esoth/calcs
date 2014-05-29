from hunter import HunterMeta
from tools import critify, hastify, mastify, PANDARENS

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
  _gear = 0.0
  _food = 0.0
  _flask = 0.0
  _buffa = 0.0
  _basea = 0.0
  _buffm = 0.0
  _spec = 0.0
  
  def __init__(self,hunter):
    if isinstance(hunter,HunterMeta):
      self.hunter = hunter
    else:
      raise Exception('Stat object must be initiated with a HunterCalc object')
  
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
  def buffa(self,value=''):
    if value:
      self._buffa = value
    else:
      return self._buffa
  def basea(self,value=''):
    if value:
      self._basea = value
    else:
      return self._basea
  def buffm(self,value=''):
    if value:
      self._buffm = value
    else:
      return self._buffm
  def spec(self,value=''):
    if value:
      self._spec = value
    else:
      return self._spec
  
  def additives(self):
    return max(self.gear(), self.food(), self.flask(), self.buffa(), self.basea(),0) # could theoretically be negative otherwise
  
  def multiplicatives(self):
    return (1+self.buffm())*(1+self.spec())
  
  def total_static(self):
    """ The total at all times, before procs """
    a = self.additives()
    m = self.multiplicatives()
    return a*m
    
  def total_averaged(self, procs=[]):
    """ The total with proc averages """
    return self.total_static() + self.sum_procs(procs)
  
  def sum_procs(self, procs=[]):
    return sum([p.average() for p in self.procs])
    
class AgilityStat(Stat):
  """ The mail specialization only works on gear """
  _flask = 1000
  _basea = 218
  _buffm = 0.05
  _spec = 0.05
  
  def food(self):
    return self.hunter.race in PANDARENS and 600 or 300 # Pandaren
  
  def additives(self):
    return max(self.gear()*(1+self.spec()) + self.food() + self.flask() + self.buffa() + self.basea(),0)
  
  def multiplicatives(self):
    return (1+self.buffa())

class CritStat(Stat):
  """ Buffs, agi class bonus, boss crit depression """
  _buffa = critify(100/5.0)**-1
  _basea = critify(100/5.2)**-1 # -4.8% boss depression, 10% base crit
  _spec = .1 # base 10% crit for hunters

class HasteStat(Stat):
  """ 5% haste buff """
  _buffa = hastify(100/5.0)

class MasteryStat(Stat):
  """ 5% mastery buff """
  _buffa = mastify(100/5.0)

class ReadinessStat(Stat):
  """ Assuming this defaults to zero for now """

class MultistrikeStat(Stat):
  """ Assuming this defaults to zero for now """

class Proc(Calc):
  rppm = 1.0
  magnitude = 0.0
  duration = 0.0
  static_haste = 1.0
  
  def average(self):
    return self.magnitude*self.rppm/(6.0/self.static_haste)
  
  def uptime(self):
    return 0.0

class ProcManager(object):
  agility = []
  haste = []
  crit = []
  mastery = []
  multistrike = []
  readiness = []
  
  def proc_table(self):
    pass