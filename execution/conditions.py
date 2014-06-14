from calcs.spells import *

class Condition:
  """ True or False conditions """
  # we probably want to make a choices based on a set of all conceivable conditions, instead
  #   of looking at states and CDs directly. A Condition will check the relevant states and
  #   CD(s) and return True or False if it's available
  # A priority rotation list will then order conditions in a certain way and select the first
  #   spell that returns a condition of True
  
  def __init__(self,hunter):
    self.hunter = hunter

  def validate(self):
    return True

class NoActionCondition(Condition):
  title = "Default if no other option - pass"
  id = '--'
  computable = True
  
  def validate(self, cds, states, focus, time):
    return True

class BestialWrathCondition(Condition):
  title = "Bestial Wrath condition: off CD"
  id = 'BW'
  computable = True
  
  def validate(self, cds, states, focus, time):
    cd = BestialWrath(self.hunter).cd
    return cds['Bestial Wrath'].cdtime <= 0 or False

class KillCommandCondition(Condition):
  title = "Kill Command condition: off CD, 40+ focus (20+ if during Bestial Wrath)"
  id = 'KC'
  computable = True
  
  def validate(self, cds, states, focus, time):
    spell = KillCommand(self.hunter)
    
    checks = [cds['Kill Command'].cdtime <= 0 or False,
              focus >= 40 or (states['Bestial Wrath'].active() and focus >= 20)]
    return False not in checks

class ArcaneShotCondition(Condition):
  title= "Arcane shot condition: 70+ focus, (20+, if during Bestial Wrath)"
  id = 'AS'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = ArcaneShot(self.hunter)
    # spell.focus() this is a minimum if we allow focus pooling to be customized
    checks = [focus >= 70 or (states['Bestial Wrath'].active() and focus >= 20)]
    return False not in checks

class CobraShotCondition(Condition):
  title = "Cobra Shot condition - true if appropriate spec"
  id = 'CS'
  computable = True
  
  def validate(self, cds, states, focus, time):
    return self.hunter.meta.spec != 1

class SteadyShotCondition(Condition):
  title = "Steady Shot condition - true if appropriate spec"
  id = 'SS'
  computable = True
  
  def validate(self, cds, states, focus, time):
    return self.hunter.meta.spec == 1



import inspect, sys
def conditions_computable(hunter):
  _conditions = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  conditions = [k(hunter) for name,k in _conditions if issubclass(k,Condition)]
  return conditions