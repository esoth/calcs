from huntermeta import HunterMeta
from stats import *
  
class Hunter(object):  
  weaponmin = 0
  weaponmax = 0
  weaponspeed = 3
  procm = ProcManager()
  
  def __init__(self):
    self.meta = HunterMeta()
    self.agility = AgilityStat(self.meta)
    self.crit = CritStat(self.meta)
    self.haste = HasteStat(self.meta)
    self.mastery = MasteryStat(self.meta)
    self.readiness = ReadinessStat(self.meta)
    self.multistrike = MultistrikeStat(self.meta)
  
  def setgear(self,**kw):
    """ Update gear values for all stats """
    for k,v in kw.items():
      if isinstance(getattr(self,k),Stat):
        getattr(self,k).gear(v)

  def weapondmg(self):
    """ Weapon damage is average of weapon's min and max, plus AP/3.5 * Weapon Speed """
    wpn = (self.weaponmin + self.weaponmax) / 2
    ap = self.ap() / 3.5 * self.weaponspeed # "Attack Power now increases Weapon Damage at a rate of 1 DPS per 3.5 Attack Power"
    return wpn + ap
  
  def ap(self):
    """ Currently using a 5% AP boost - is this right? """
    return self.agility.total_static()*1.05