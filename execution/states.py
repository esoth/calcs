from calcs import spells
from calcs.tools import product

class State(object):
  state_id = 'Spell'
  _damage_modifier = 1
  _focus_modifier = 1
  _time_modifier = 1
  _focus_gains = 0 # per sec
  _duration = 0
  _stacks = 0
  _active = False
  _uptime = 0
  
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
  def stacks(self):
    return self._stacks
  def active(self):
    return self._active
  def focus_gains(self,states,time=None):
    return self._focus_gains
  def uptime(self):
    return self._uptime
 
  def info(self, states, time):
    return {'state_id':self.state_id,
            'active':self.active(),
            'tooltip':self.tooltip(states,time)}
  
  def tooltip(self, states, time=None):
    tt = "State = %s" % self.state_id
    if self.duration():
      tt += ", duration: %.02f" % self.duration()
    if self.stacks():
      tt += ", stacks: %d" % self.stacks()
    if self.damage_modifier() != 1:
      tt += ", dmg mod: %.02f%%" % self.damage_modifier()
    if self.time_modifier() != 1:
      tt += ", haste: %.02f%%" % self.time_modifier()
    if self.focus_modifier() != 1:
      tt += ", focus mod: %.02f%%" % self.focus_modifier()
    if self.focus_gains(states,time):
      tt += ", +focus: %.02f" % self.focus_gains(states,time)
    return tt
 
  def update_state(self,time,actionid,procs,boss_health):
    pass

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
 
  def update_state(self,time,actionid,procs,boss_health):
    if actionid == self.state_id:
      self._duration = spells.BestialWrath(self.hunter).duration() # the behavior of this spell class is outside the scope of this
      self._active = True
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False
    else:
      self._uptime += time

class LockAndLoadState(State):
  computable = True
  state_id = 'Lock and Load'
  _active = False
  _duration = 0
  _stacks = 0
 
  # going to need a class of procs to pass here
  def update_state(self,time,actionid,procs,boss_health):
    lnl = procs['Lock and Load']
    if lnl.activate():
      self._stacks += 1
      self._duration = 15
     
    if actionid == 'Explosive Shot' and self.stacks() and self.duration():
      self._stacks -= 1
 
  def active(self):
    return self.stacks() and self.duration()

class RapidFire(State):
  computable = True
  state_id = 'Rapid Fire'
  _time_modifier = 1.4
  _active = False
  _duration = 15
  _stacks = 1
 
  def time_modifier(self):
    return self.active() and self._time_modifier or 1
 
  def update_state(self,time,actionid,procs,boss_health):
    if actionid == self.state_id:
      self._duration = spells.RapidFire(self.hunter).duration()
      self._active = True
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False

class BlackArrowState(State):
  computable = True
  state_id = 'Black Arrow'
  _duration = 0
  _stacks = 1
 
  def update_state(self,time,actionid,procs,boss_health):
    if actionid == self.state_id:
      self._duration = spells.BlackArrow(self.hunter).duration()
      self._active = True
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False
  
  def active(self):
    return self.duration() > 0

class SerpentStingState(State):
  computable = True
  state_id = 'Serpent Sting'
  _total = 0
  _duration = 0

  def update_state(self,time,actionid,procs,boss_health):
    if actionid == 'Arcane Shot':
      self._duration = spells.SerpentSting(self.hunter).duration()
      self._active = True
      self._total += spells.SerpentSting(self.hunter).damage()
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False
  
  def total(self):
    return self._total

class CarefulAimState(State):
  computable = True
  state_id = 'Careful Aim'
  _active = False

  def update_state(self,time,actionid,procs,boss_health):
    self._active = boss_health >= .8

class KillShotState(State):
  computable = True
  state_id = 'Kill Shot'
  _active = False

  def update_state(self,time,actionid,procs,boss_health):
    self._active = boss_health <= .35

class KillShotDouble(State):
  computable = True
  state_id = 'Kill Shot Double'
  _active = True

  def update_state(self,time,actionid,procs,boss_health):
    if actionid == 'Kill Shot':
      self._active = not self._active

class DireBeast(State):
  computable = True
  state_id = 'Dire Beast'
  _stacks = 0
  _timer = 2.5 # attacks about every 2.5 seconds
  # no haste scaling? http://wod.wowhead.com/spell=120679#comments:id=1648296
  # this looks wrong. Looks like it's 2/haste ~ 9 attacks!
  
  def speed(self):
    return 2/self.hunter.haste.total()
  
  def stack_amount(self):
    return int(15/self.speed())+1

  def update_state(self,time,actionid,procs,boss_health):
    if actionid == self.state_id:
      self._stacks = self.stack_amount()
      self._timer = self.speed()
      #self._duration = spells.DireBeast(self.hunter).duration()
      #self._active = True
    elif self._stacks:
      self._timer -= time
  
  def active(self):
    return bool(self._stacks)
 
  def focus_gains(self,states,time):
    if self._timer <= 0:
      self._stacks -= 1
      self._timer = self.speed() # reset
      return 5
    else:
      return 0

class Fervor(State):
  computable = True
  state_id = 'Fervor'
  _active = False

  def update_state(self,time,actionid,procs,boss_health):
    if actionid == self.state_id:
      self._duration = spells.Fervor(self.hunter).duration()
      self._active = True
    else:
      self._duration -= time
    if self.duration() < 0:
      self._active = False
 
  def focus_gains(self,states,time):
    if self.active():
      return 5.0*time
    else:
      return 0

class ViperVenomState(State):
  computable = True
  state_id = 'Viper Venom'
  _active = False
  _starting_counter = 3
  _counter = _starting_counter
 
  def update_state(self,time,actionid,procs,boss_health):
    ss = procs['Viper Venom']
    if ss.activate():
      self._active = True
    else:
      self._active = False
 
  def focus_gains(self,states,time):
    if self.active():
      return 6

class FrenzyState(State):
  computable = True
  state_id = 'Frenzy'
  _counter = 0
 
  def update_state(self,time,actionid,procs,boss_health):
    if actionid == 'Focus Fire':
      self._counter = 0
    else:
      self._counter += time
      self._counter_to_proc = self._counter
   
    self._counter_to_proc += time
 
  def stacks(self):
    return 2/.4*self._counter
          
      
      
      
import inspect, sys
def states_computable(hunter):
  _states = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _states = [k for name,k in _states if issubclass(k,State)]
  states = {}
  for k in _states:
    o = k(hunter)
    states[o.state_id] = o
  return states