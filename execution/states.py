from calcs import spells
from calcs.tools import *

class State(object):
  state_id = 'Spell'
  _damage_modifier = 1
  _pet_damage_modifier = 1
  _focus_modifier = 1
  _time_modifier = 1
  _pet_time_modifier = 1
  _focus_gains = 0 # per sec
  _pet_focus_gains = 0
  _duration = 0
  _stacks = 0
  _active = False
  _uptime = 0
  
  def __init__(self,hunter):
    self.hunter = hunter
  
  def damage_modifier(self):
    return self._damage_modifier
  def pet_damage_modifier(self):
    return self._pet_damage_modifier
  def time_modifier(self):
    return self._time_modifier
  def pet_time_modifier(self):
    return self._pet_time_modifier
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
  def pet_focus_gains(self,states,time=None):
    return self._pet_focus_gains
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
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    pass

class BestialWrathState(State):
  computable = True
  state_id = 'Bestial Wrath'
  _damage_modifier = 1.1
  _pet_damage_modifier = 1.2
  _focus_modifier = 0.5
  _duration = 0
  
  def damage_modifier(self):
    return self.active() and self._damage_modifier or 1
  
  def petdamage_modifier(self):
    return self.active() and self._pet_damage_modifier or 1
  
  def focus_modifier(self):
    return self.active() and self._focus_modifier or 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.BestialWrath(self.hunter).duration() # the behavior of this spell class is outside the scope of this
    else:
      self._duration -= time
    if self.active():
      self._uptime += time
  
  def active(self):
    return self.duration() > 0

class GoForTheThroat(State):
  computable = True
  state_id = 'Invigoration (Go for the Throat)'
  _timer = 0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    t_modifier = product([s.time_modifier() for s in states.values()])
    if self.active(): # reset
      self._timer = self._timer - self.time_to_proc()
    self._timer += time * t_modifier
 
  def active(self):
    if self.hunter.meta.spec == BM:
      return self._timer >= self.time_to_proc()
 
  def time_to_proc(self):
    # multiply time by by t_modifier? Then
    speed = self.hunter.weaponspeed/self.hunter.haste.total()
    crit = self.hunter.crit.total()/100.0
    return speed/crit
  
  def pet_focus_gains(self,states,time):
    return self.active() and 15 or 0

class Invigoration(State):
  computable = True
  state_id = 'Invigoration'
  _timer = 0
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self.active(): # reset
      self._timer = self._timer - self.time_to_proc()
   
    if pet_basic:
      self._timer += 1
 
  def time_to_proc(self):
    return 1/.15
 
  def active(self):
    return self._timer >= self.time_to_proc()
   
  def focus_gains(self,states,time):
    if self.active():
      return 20
    else:
      return 0

class LockAndLoadProc(State):
  computable = True
  state_id = 'Lock and Load (proc)'
  _timer = 0
  
  def time_to_proc(self):
    ms = 2.0 * self.hunter.multistrike.total() / 100.0 / 3.0 # 2 chances every 3 seconds
    return 1/ms
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self._timer >= self.time_to_proc(): # reset
      self._timer -= self.time_to_proc()
    if states['Black Arrow'].active():
      self._timer += time
  
  def active(self):
    return self._timer >= self.time_to_proc()

class LockAndLoadState(State):
  computable = True
  state_id = 'Lock and Load'
  _active = False
  _duration = 0
  _stacks = 0
 
  # going to need a class of procs to pass here
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    lnl = states['Lock and Load (proc)']
    if lnl.active():
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
 
  def time_modifier(self):
    return self.active() and self._time_modifier or 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.RapidFire(self.hunter).duration()
    else:
      self._duration -= time
   
  def active(self):
    return self.duration() > 0

class FocusFireState(State):
  computable = True
  state_id = 'Focus Fire'
  _time_modifier = 1.2
  _active = False
  _duration = 20
 
  def time_modifier(self):
    return self.active() and self._time_modifier or 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.FocusFire(self.hunter).duration()
    else:
      self._duration -= time
  
  def active(self):
    return self.duration() > 0

class Berserking(State):
  computable = True
  state_id = 'Berserking'
  _time_modifier = 1.15
  _duration = -1
 
  def time_modifier(self):
    return self.active() and self._time_modifier or 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.Berserking(self.hunter).duration()
    else:
      self._duration -= time
      
  def active(self):
    return self.duration() > 0

class BlackArrowState(State):
  computable = True
  state_id = 'Black Arrow'
  _duration = 0
  _stacks = 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.BlackArrow(self.hunter).duration()
    else:
      self._duration -= time
  
  def active(self):
    return self.duration() > 0

class ExplosiveTrapState(State):
  computable = True
  state_id = 'Explosive Trap'
  _duration = 0
  _stacks = 1
 
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.ExplosiveTrap(self.hunter).duration()
    else:
      self._duration -= time
  
  def active(self):
    return self.duration() > 0

class SerpentStingState(State):
  computable = True
  state_id = 'Serpent Sting'
  _total = 0
  _duration = 0
  _uptime = 0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid in ('Arcane Shot','Multi-Shot',):
      self._duration = spells.SerpentSting(self.hunter).duration()
    self._duration -= time
    if self.active():
      self._uptime += time
  
  def uptime(self):
    return self._uptime
  
  def active(self):
    return self.duration() > 0
  
  def total(self):
    return self._total

class EmpoweredBasicAttackState(State):
  computable = True
  state_id = 'Empowered Basic Attack'
  _counter = 0.0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self.active(): # reset
      self._counter = 0.0
    if pet_basic:
      self._counter += .2
 
  def active(self):
    return self._counter >= 1

class BombardmentState(State):
  computable = True
  state_id = 'Bombardment'
  _active = False
  _duration = 0

  def time_modifier(self):
    return self.active() and self._time_modifier or 1

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == 'Multi-Shot':
      self._duration = 5
    else:
      self._duration -= time

  def active(self):
    return self.hunter.meta.spec == MM and self.duration() > 0

class BeastCleaveState(State):
  computable = True
  state_id = 'Beast Cleave'
  _active = False
  _duration = 0

  def time_modifier(self):
    return self.active() and self._time_modifier or 1

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == 'Multi-Shot':
      self._duration = 4
    else:
      self._duration -= time

  def active(self):
    return self.hunter.meta.spec == BM and self.duration() > 0

class ThrillOfTheHuntState(State):
  computable = True
  state_id = 'Thrill of the Hunt'
  _counter = float(0)
  _stacks = 0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self.hunter.meta.talent4 == TIER4.index(THRILLOFTHEHUNT):
      if self.active() and actionid in ('Arcane Shot','Aimed Shot','Multi-Shot'):
        self._stacks -= 1
      if actionid in ('Arcane Shot','Aimed Shot','Kill Command','A Murder of Crows','Explosive Shot','Black Arrow',
                      'Chimera Shot','Glaive Toss','Barrage','Powershot','Multi-Shot') and not self.active():
        self._counter += .3
      if self._counter > 1: # reset and add stacks
        self._counter -= 1
        self._stacks = 3
  
  def active(self):
    return bool(self.stacks())

class CarefulAimState(State):
  computable = True
  state_id = 'Careful Aim'
  _active = False

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    self._active = boss_health >= .8

class KillShotState(State):
  computable = True
  state_id = 'Kill Shot'
  _active = False

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    self._active = boss_health <= .35

class KillShotDouble(State):
  computable = True
  state_id = 'Kill Shot Double'
  _active = True

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
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

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._stacks = self.stack_amount()
      self._timer = self.speed()
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

class TouchOfTheGraveProc(State):
  computable = True
  state_id = 'Touch of the Grave'
  _counter = 0
  _total = 0
  _proc = 0
    
  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self._proc >= 30 and self.hunter.meta.race == UNDEAD:
      self._proc -= 30   
      spell = spells.TouchOfTheGrave(self.hunter).damage(states)
      self._counter += 1
      self._total += spell
    self._proc += time
  
  def counter(self):
    return self._counter
  def total(self):
    return self._total

class ImprovedAimedShotState(State):
  computable = True
  state_id = 'Improved Aimed Shot'
  _counter = 0.0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if self._counter > 1:
      self._counter -= 1
    if actionid == 'AimedShot' and (states['Careful Aim'].active() or states['Rapid Fire'].active()):
      # we can assume this is a MM hunter
      base = base/self.totalcritmod()
      crit_chance = min(self.critchance() + .6 + self.hunter.crit.total()/100.0,1)
      self._counter += crit_chance
  
  def active(self):
    return self._counter >= 1
 
  def focus_gains(self,states,time):
    return self.active() and 20 or 0

class FrenzyState(State):
  computable = True
  state_id = 'Frenzy'
  _stacks = 0
  _counter = 0.0

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == 'Focus Fire':
      self._counter = 0
    if pet_basic:
      self._counter += .4
  
  def stacks(self):
    return min(int(self._counter),5)
  
  def active(self):
    return self.stacks()>=1
 
  def pet_time_modifier(self):
    return self.stacks()*.04+1

class Fervor(State):
  computable = True
  state_id = 'Fervor'
  _active = False
  _duration = 0
  _max = 50

  def update_state(self,time,actionid,states,pet_basic,boss_health,aoe=0):
    if actionid == self.state_id:
      self._duration = spells.Fervor(self.hunter).duration()
    if self.active():
      self._max -= 5.0*time
    else:
      self._max = 50
    self._duration -= time
 
  def focus_gains(self,states,time):
    if self.active():
      return min(self._max,5.0*time)
  
  def pet_focus_gains(self,states,time):
    if self.active():
      return min(self._max,5.0*time)
      
  def active(self):
    return self._duration > 0
          
      
      
      
import inspect, sys
def states_computable(hunter):
  _states = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _states = [k for name,k in _states if issubclass(k,State)]
  states = {}
  for k in _states:
    o = k(hunter)
    states[o.state_id] = o
  return states