from huntermeta import HunterMeta
from tools import PANDARENS

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
  _buffa = float(0)
  _basea = float(0)
  _buffm = float(0)
  _spec = float(0)
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
  def rating(self,value=''):
    """ Level 90 values """
    if value:
      self._rating = value
    else:
      return self._rating
  
  def attunement(self):
    return 1.0
  
  def additives(self):
    return max(self.attunement()*sum([self.gear(), self.food(), self.flask()]) + self.buffa() + self.basea(),0) # could theoretically be negative otherwise
  
  def multiplicatives(self):
    return (1+self.buffm())*(1+self.spec())
  
  def total_static(self):
    """ The total at all times, before procs """
    a = self.additives()
    m = self.multiplicatives()
    return a*m
  
  def total_percent(self):
    """ The percent that shows up in the character """
    try:
      return self.total_static()/float(self.rating())
    except ValueError:
      return None
    
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
  
  def rating(self):
    return '--'
  
  def basea(self):
    """ To do: get a proper list of starting stats per race """
    return super(AgilityStat,self).basea()
  
  def flask(self):
    """ Flask of Spring Blossoms """
    return super(AgilityStat,self).flask()
  
  def food(self):
    """ Pandarens receive double """
    return self.hunter.race in PANDARENS and 600 or 300 # Pandaren
  
  def additives(self):
    return max(self.gear()*(1+self.spec()) + self.food() + self.flask() + self.buffa() + self.basea(),0)
  
  def multiplicatives(self):
    return (1+self.buffa())

class CritStat(Stat):
  """ Buffs, agi class bonus, boss crit depression """
  _rating = 16
  _buffa = _rating * 5
  _basea = _rating * (10 - 3) # 10=crit for agi users, 3=boss crit suppression

  def attunement(self):
    """ 5% more crit from rating sources for MM """
    if self.hunter.spec != 1:
      return 1.0
    return 1.05
  
  def buffa(self):
    """ 5% crit buff """
    return super(CritStat,self).buffa()
  
  def basea(self):
    """ Crit depression for +3 boss levels (-3%) + 10% crit for agi users"""
    return super(CritStat,self).basea()

class HasteStat(Stat):
  """ 5% haste buff """
  _rating = 23
  _buffa = _rating * 5
  
  def buffa(self):
    """ 5% haste buff """
    return super(HasteStat,self).buffa()

class MasteryStat(Stat):
  """ 5% mastery buff """
  _rating = 23
  _buffa = _rating * 5
  
  def buffa(self):
    """ 5% mastery buff """
    return super(MasteryStat,self).buffa()
  
  def additives(self):
    """ For mastery, the mastery buff counts since it is technically a rating """
    return max(self.attunement()*sum([self.gear(), self.food(), self.flask(), self.buffa()]) + self.basea(),0) # could theoretically be negative otherwise

class VersatilityStat(Stat):
  """ 3% versatility buff """
  _rating = 23
  _buffa = _rating * 3

class MultistrikeStat(Stat):
  """ 5% multistrike buff """
  _rating = 23
  _buffa = _rating * 5

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