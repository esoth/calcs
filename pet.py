#Bite: .168 AP
from tools import armormod

class Pet(object):
  _cooldown = 3
  _counter = 0
  
  def ap(self,hunter):
    return hunter.ap()/3.0
  
  def focus_gen(self,hunter):
    return hunter.focus_gen()
    
  def combat_experience(self,hunter):
    return hunter.meta.talent7 == 2 and 1.7 or 1.5
  
  def mastery(self,hunter):
    bm_mas =  (1++hunter.mastery.total()/100.0)
    return hunter.meta.spec == 0 and bm_mas or 1
  
  def versatility(self,hunter):
    return (1+hunter.versatility.total()/100.0)

  def basic(self,hunter,states,pet_states):
    ap = self.ap(hunter)
    
    dmg = ap
    dmg *= armormod()
    dmg *= self.versatility(hunter)
    dmg *= self.combat_experience(hunter)
    dmg *= self.mastery(hunter)
    dmg *= 1.1 # spiked collar
    
    if hunter.meta.spec == 0:
      dmg *= 1.2 # empowered pets
    
    if hunter.meta.talent5 == 1:
      dmg *= 1.5
    
    if states['Bestial Wrath'].active():
      dmg *= 1.2

    return dmg
  
  def do_basic(self,hunter,focus,time,states,pet_states):
    dmg = 0
    if hunter.meta.spec in (1,2,) and hunter.meta.talent7 == 2:
      return dmg,focus
    if self._counter > 0:
      self._counter -= time
    else:
      self._counter = self._cooldown
      if focus >= 50:
        dmg = self.basic(hunter, states, pet_states) * 2
        focus -= 50
      elif focus >= 25:
        dmg = self.basic(hunter, states, pet_states)
        focus -= 25
    focus += time * self.focus_gen(hunter)
    return dmg,focus
  
  def auto(self,hunter):
    dmg = self.ap(hunter)/3.5*2 # 100% weapon damage
    dmg *= armormod()
    dmg *= self.versatility(hunter)
    dmg *= self.combat_experience(hunter)
    if hunter.meta.spec == 0:
      dmg *= self.mastery(hunter)*1.2 # empowered pets
    return dmg


import inspect, sys
def pet_states_computable(pet,hunter):
  return []