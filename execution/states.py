from calcs.spells import *

class State(object):
  state_id = 'Spell'
  _damage_modifier = 1
  _focus_modifier = 1
  _time_modifier = 1
  _duration = 1
  _stacks = 1
  _active = False
  
  def __init__(self,hunter):
    self.hunter = hunter
  
  def damage_modifier(self):
    return self._damage_modifier
  def time_modifier(self):
    return self._time_modifier
  def focus_modifier(self):
    return self._focus_modifier
  def duration(self):
    return self._duration
  def stacks_modifier(self):
    return self._stacks
  def active(self):
    return self._active
 
  def info(self):
    return {'state_id':self.state_id,
            'damage_modifier':self.damage_modifier(),
            'duration':self.duration(),
            'active':self.active(),
            'stacks':self.stacks()}
 
  def update_state(self,time,actionid):
    pass

# example
class BestialWrathState(State):
  computable = True
  state_id = 'Bestial Wrath'
  _damage_modifier = 1.1
  _focus_modifier = 0.5
  _active = False
  _time_modifier = 1
  _duration = 10
  _stacks = 1
  
  def stacks(self):
    return self.active() and 1 or 0
  
  def damage_modifier(self):
    return self.active() and self._damage_modifier or 1
  
  def focus_modifier(self):
    return self.active() and self._focus_modifier or 1
 
  def update_state(self,time,actionid):
    if actionid == self.state_id:
      self._duration = BestialWrath(self.hunter).duration() # the behavior of this spell class is outside the scope of this
      self._active = True
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False
      
      
      
      
import inspect, sys
def states_computable(hunter):
  _states = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _states = [k for name,k in _states if issubclass(k,State)]
  states = {}
  for k in _states:
    o = k(hunter)
    states[o.state_id] = o
  return states