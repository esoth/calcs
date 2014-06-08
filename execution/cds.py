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
      
      
      
      
import inspect, sys
def cds_computable(hunter):
  _cds = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _cds = [k for name,k in _cds if issubclass(k,Cooldown)]
  cds = {}
  for k in _cds:
    o = k(hunter)
    cds[o.actionid] = o
  return cds