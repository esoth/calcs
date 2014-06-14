class Cooldown:
  actionid = 'Cooldown'
  cdtime = 0
  
  def __init__(self,hunter):
    self.hunter = hunter
 
  def info(self):
    return {'actionid':self.actionid,
            'cdtime':self.cdtime}
 
  def update_state(self,time,actionid):
    self.cdtime = 0

class BestialWrathCD(Cooldown):
  actionid = 'Bestial Wrath'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import BestialWrath
    if actionid == self.actionid:
      self.cdtime = BestialWrath(self.hunter).cd()
    else:
      self.cdtime -= time

class KillCommandCD(Cooldown):
  actionid = 'Kill Command'
  computable = True
  
  def update_state(self,time,actionid):
    from calcs.spells import KillCommand
    if actionid == self.actionid:
      self.cdtime = KillCommand(self.hunter).cd()
    else:
      self.cdtime -= time

class ChimeraShotCD(Cooldown):
  actionid = 'Chimera Shot'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import ChimeraShot
    if actionid == self.actionid:
      self.cdtime = ChimeraShot(self.hunter).cd()
    else:
      self.cdtime -= time
     
class BlackArrowCD(Cooldown):
  actionid = 'Black Arrow'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import BlackArrow
    if actionid == self.actionid:
      self.cdtime = BlackArrow(self.hunter).cd()
    else:
      self.cdtime -= time
     
class ExplosiveShotCD(Cooldown):
  actionid = 'Explosive Shot'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import ExplosiveShot
    if actionid == self.actionid:
      self.cdtime = ExplosiveShot(self.hunter).cd()
    else:
      self.cdtime -= time
     
class RapidFireCD(Cooldown):
  actionid = 'Rapid Fire'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import RapidFire
    if actionid == self.actionid:
      self.cdtime = RapidFire(self.hunter).cd()
    else:
      self.cdtime -= time
     
class MurderOfCrowsCD(Cooldown):
  actionid = 'A Murder Of Crows'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import MurderOfCrows
    if actionid == self.actionid:
      self.cdtime = MurderOfCrows(self.hunter).cd()
    else:
      self.cdtime -= time
     
class FervorCD(Cooldown):
  actionid = 'Fervor'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import Fervor
    if actionid == self.actionid:
      self.cdtime = Fervor(self.hunter).cd()
    else:
      self.cdtime -= time
     
class DireBeastCD(Cooldown):
  actionid = 'Dire Beast'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import DireBeast
    if actionid == self.actionid:
      self.cdtime = DireBeast(self.hunter).cd()
    else:
      self.cdtime -= time
     
class ExplosiveTrapCD(Cooldown):
  actionid = 'Explosive Trap'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import ExplosiveTrap
    if actionid == self.actionid:
      self.cdtime = ExplosiveTrap(self.hunter).cd()
    else:
      self.cdtime -= time
     
class FocusFireCD(Cooldown):
  actionid = 'Focus Fire'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import FocusFire
    if actionid == self.actionid:
      self.cdtime = FocusFire(self.hunter).cd()
    else:
      self.cdtime -= time
     
class KillShotCD(Cooldown):
  actionid = 'Kill Shot'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import KillShot
    if actionid == self.actionid:
      self.cdtime = KillShot(self.hunter).cd()
    else:
      self.cdtime -= time
     
class PowershotCD(Cooldown):
  actionid = 'Powershot'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import Powershot
    if actionid == self.actionid:
      self.cdtime = Powershot(self.hunter).cd()
    else:
      self.cdtime -= time
     
class GlaiveTossCD(Cooldown):
  actionid = 'Glaive Toss'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import GlaiveToss
    if actionid == self.actionid:
      self.cdtime = GlaiveToss(self.hunter).cd()
    else:
      self.cdtime -= time
     
class BarrageCD(Cooldown):
  actionid = 'Barrage'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import Barrage
    if actionid == self.actionid:
      self.cdtime = Barrage(self.hunter).cd()
    else:
      self.cdtime -= time
     
class StampedeCD(Cooldown):
  actionid = 'Stampede'
  computable = True
 
  def update_state(self,time,actionid):
    from calcs.spells import Stampede
    if actionid == self.actionid:
      self.cdtime = Stampede(self.hunter).cd()
    else:
      self.cdtime -= time
      
      
      
import inspect, sys
def cds_computable(hunter):
  _cds = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _cds = [k for name,k in _cds if issubclass(k,Cooldown)]
  cds = {}
  for k in _cds:
    o = k(hunter)
    cds[o.actionid] = o
  return cds