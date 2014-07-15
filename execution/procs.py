from calcs.spells import *
from states import State

class Proc(object):
  proc_id = 'Spell'
  _stacks = 1
  _duration = 1
  _counter_to_proc = 1
  _start_counter = 5
  _damage_modifier = 1
  _focus_modifier = 1
  _time_modifier = 1
  _duration = 1
  _stacks = 1
  
  def __init__(self,hunter):
    self.hunter = hunter
  
  def counter_to_proc(self):
    return self._counter_to_proc
  def duration(self):
    return self._duration
  def stacks(self):
    return self._stacks
  def activate(self):
    return False
 
  def info(self):
    return {'state_id':self.state_id,
            'damage_modifier':self.damage_modifier(),
            'duration':self.duration(),
            'active':self.active(),
            'stacks':self.stacks()}
 
  def update_state(self,time,actionid,states):
    pass

class LockAndLoadProc(Proc):
  computable = True
  proc_id = 'Lock and Load'
  _counter_to_proc = None
  
  def time_to_proc(self):
    ms = 2.0 * self.hunter.multistrike.total() / 100.0 / 3.0
    return 1/ms
 
  def update_state(self,time,actionid,states):
    if self._counter_to_proc <= 0:
      self._counter_to_proc = self.time_to_proc()
    if states['Black Arrow'].active():
      self._counter_to_proc -= time
  
  def activate(self):
    return self._counter_to_proc <= 0

class ViperVenomProc(Proc):
  computable = True
  proc_id = 'Viper Venom'
  _start_counter = 3
  _counter_to_proc = 3
 
  def update_state(self,time,actionid,states):
    if self._counter_to_proc < 0: # reset if just proc'd
      self._counter_to_proc = self._start_counter

    if states['Serpent Sting'].active():
      self._counter_to_proc -= time
 
  def activate(self):
    return self._counter_to_proc <= 0

class DireBeastProc(Proc):
  computable = True
  proc_id = 'Dire Beast'
  _start_counter = 2
  _counter_to_proc = 2 # first one goes out right away
 
  def update_state(self,time,actionid,states):
    if self._counter_to_proc < 0: # reset if just proc'd
      self._counter_to_proc = self._start_counter

    if states['Dire Beast'].active():
      self._counter_to_proc -= time
 
  def activate(self):
    return self._counter_to_proc <= 0
      
      
import inspect, sys
def procs_computable(hunter):
  _procs = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  _procs = [k for name,k in _procs if issubclass(k,Proc)]
  procs = {}
  for k in _procs:
    o = k(hunter)
    procs[o.proc_id] = o
  return procs