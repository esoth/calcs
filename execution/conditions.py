from calcs.spells import *
from calcs.tools import *

class Condition:
  """ True or False conditions """
  # we probably want to make a choices based on a set of all conceivable conditions, instead
  # of looking at states and CDs directly. A Condition will check the relevant states and
  # CD(s) and return True or False if it's available
  # A priority rotation list will then order conditions in a certain way and select the first
  # spell that returns a condition of True
 
  def __init__(self,hunter,options,aoe):
    self.hunter = hunter
    self.options = options
    self.aoe = aoe
   
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
    buffer = 0
    spell = ArcaneShot(self.hunter)
    # spell.focus() this is a minimum if we allow focus pooling to be customized
    checks = [focus >= 30+buffer or (states['Bestial Wrath'].active() and focus >= 15) or (states['Thrill of the Hunt'].active() and focus >= 10+buffer)]
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

class GlaiveTossCondition(Condition):
  title = "Glaive Toss - talented and off CD"
  id = 'GT'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = GlaiveToss(self.hunter)
    checks = [cds['Glaive Toss'].cdtime <= 0 or False,
              focus >= spell.focus(),
              self.hunter.meta.talent6 == 0]
    return False not in checks

class PowershotCondition(Condition):
  title = "Powershot - talented and off CD"
  id = 'PS'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = Powershot(self.hunter)
    checks = [cds['Powershot'].cdtime <= 0 or False,
              focus >= spell.focus(),
              self.hunter.meta.talent6 == 1]
    return False not in checks

class BarrageCondition(Condition):
  title = "Barrage - talented and off CD"
  id = 'Ba'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = Barrage(self.hunter)
    checks = [cds['Barrage'].cdtime <= 0 or False,
              focus >= spell.focus(),
              self.hunter.meta.talent6 == 2]
    return False not in checks

class AMurderOfCrowsCondition(Condition):
  title = "A Murder of Crows - talented and off CD"
  id = 'MoC'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = MurderOfCrows(self.hunter)
    checks = [cds['A Murder of Crows'].cdtime <= 0 or False,
              focus >= spell.focus(),
              self.hunter.meta.talent5 == 0]
    return False not in checks

class StampedeCondition(Condition):
  title = "Stampede - talented and off CD"
  id = 'St'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [cds['Stampede'].cdtime <= 0 or False,
              self.hunter.meta.talent5 == 2]
    return False not in checks

class RapidFireCondition(Condition):
  title = "Rapid Fire - MM only and off CD"
  id = 'RF'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [cds['Rapid Fire'].cdtime <= 0 or False,
              self.hunter.meta.spec == 1]
    return False not in checks

class ChimeraShotCondition(Condition):
  title = "Chimera Shot - off CD"
  id = 'Ch'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = ChimeraShot(self.hunter)
    checks = [cds['Chimera Shot'].cdtime <= 0 or False,
              focus >= spell.focus()]
    return False not in checks

class AimedShotCondition(Condition):
  title = "Aimed Shot - focus check"
  id = 'Ai'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = AimedShot(self.hunter)
    return focus >= spell.focus() or (states['Thrill of the Hunt'].active() and focus >= spell.focus()-20)

class BlackArrowCondition(Condition):
  title = "Black Arrow - focus and CD check"
  id = 'BA'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = BlackArrow(self.hunter)
    checks = [cds['Black Arrow'].cdtime <= 0 or False,
              focus >= spell.focus()]
    return False not in checks

class ExplosiveShotCondition(Condition):
  title = "Explosive Shot - off CD"
  id = 'ES'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = ExplosiveShot(self.hunter)
    checks = [cds['Explosive Shot'].cdtime <= 0 or False,
              focus >= spell.focus()]
    return False not in checks

class FocusingShotCondition(Condition):
  title = "Focusing Shot - talented"
  id = 'FS'
  computable = True

  def validate(self, cds, states, focus, time):
    return self.hunter.meta.talent7 == 1

class ArcaneTorrentCondition(Condition):
  title = "Arcane Torrent - Blood Elf, not max focus"
  id = 'AT'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [cds['Arcane Torrent'].cdtime <= 0 or False,
              self.hunter.meta.race == BLOODELF,
              focus <= self.hunter.max_focus()-20]
    return False not in checks

class BerserkingCondition(Condition):
  title = "Berserking - Troll"
  id = 'BZ'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [cds['Berserking'].cdtime <= 0 or False,
              self.hunter.meta.race == TROLL]
    return False not in checks

class KillShotCondition(Condition):
  title = "Kill Shot - off CD and <= 35% boss health"
  id = 'KS'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = KillShot(self.hunter)
    checks = [cds['Kill Shot'].cdtime <= 0 or False,
              states['Kill Shot'].active()]
    return False not in checks

class ExplosiveTrapCondition(Condition):
  title = "Explosive Trap - off cd, not active"
  id = 'ET'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = ExplosiveTrap(self.hunter)
    checks = [cds['Explosive Trap'].cdtime <= 0 or False,
              not states['Explosive Trap'].active()]
    return False not in checks

class DireBeastCondition(Condition):
  title = "Dire Beast - talented and off CD"
  id = 'DB'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = DireBeast(self.hunter)
    checks = [cds['Dire Beast'].cdtime <= 0 or False,
              self.hunter.meta.talent4 == 1]
    return False not in checks

class FervorCondition(Condition):
  title = "Fervor - talented and off CD"
  id = 'Fe'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = Fervor(self.hunter)
    checks = [cds['Fervor'].cdtime <= 0 or False,
              focus <= 50,
              self.hunter.meta.talent4 == 0]
    return False not in checks

class FocusFireCondition(Condition):
  title = "Focus Fire - 5 stacks of Frenzy"
  id = "FF"
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [states['Frenzy'].stacks() == 5]
    return False not in checks

class MultiShotCondition(Condition):
  title = "MultiShot condition: 40 focus or 20 focus and BW/Bombardment"
  id = 'MS'
  computable = True

  def validate(self, cds, states, focus, time):
    spell = MultiShot(self.hunter)

    checks = [focus >= spell.focus() or (states['Bestial Wrath'].active() and focus >= spell.focus()/2) or (states['Bombardment'].active() and focus >= spell.focus()/2)]
    return False not in checks

class BombardmentCondition(Condition):
  title = "Bombardment: if this is falling off, prioritize Multi-Shot"
  id = 'Bb'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [states['Bombardment'].duration() <= 2]
    return False not in checks

class BeastCleaveCondition(Condition):
  title = "Beast Cleave: if this is falling off, prioritize Multi-Shot"
  id = 'Beast Cleave'
  computable = True

  def validate(self, cds, states, focus, time):
    checks = [states['Beast Cleave'].duration() <= 2]
    return False not in checks



 
def fpassive(states, hunter, time):
  t_modifiers = product([s.time_modifier() for s in states.values()])
  return time * hunter.focus_gen() * t_modifiers
 
def spell_check(hunter,spell,spell_name,focus,arc_cost,cds,states):
  """ 1. If less than cobra/focusing shot cast time, check if we have focus to do arc + spell
      2. If less than cobra/focusing shot cast time + 1, check if we have focus to do arc + cobra + spell
  """
  cob = CobraShot(hunter)
  foc = FocusingShot(hunter)
  cobra_speed = cob.casttime() / product([s.time_modifier() for s in states.values()])
  focusing_speed = foc.casttime() / product([s.time_modifier() for s in states.values()])
 
  cost = spell.focus()
 
  if hunter.meta.talent7 == 1:
    cast_speed = focusing_speed
    f_cast = abs(foc.focus())
  else:
    cast_speed = cobra_speed
    f_cast = abs(cob.focus())
   
  arc_cost1 = arc_cost2 = cost
  if states['Bestial Wrath'].duration() >= cast_speed:
    cost /= 2
    arc_cost1 /= 2
  if states['Bestial Wrath'].duration() >= cast_speed + 1:
    arc_cost2 /= 2
   
  check = False
  if cds[spell_name].cdtime <= cast_speed:
    check = focus + fpassive(states,hunter,1) > cost + arc_cost1
  elif cds[spell_name].cdtime <= cast_speed + 1:
    check = focus + fpassive(states,hunter,1+cast_speed) + f_cast > cost + arc_cost2
  else:
    check = True # don't bother with anything longer

  return check

class BMArcaneSpecialCondition(Condition):
  title = "BM Arcane Shot - special focus check"
  id = 'BMA'
  computable = True

  def validate(self, cds, states, focus, time):
    br = Barrage(self.hunter)
    kc = KillCommand(self.hunter)
    arc = ArcaneShot(self.hunter)
    moc = MurderOfCrows(self.hunter)
   
    arc_cost = arc.focus()
   
    if states['Thrill of the Hunt'].active():
      arc_cost -= 20
    
    steady_focus = self.hunter.meta.talent4 == TIER4.index(STEADYFOCUS) and states['Steady Focus']._timer < 3
    steady_focus = steady_focus and self.hunter.meta.talent7 != TIER7.index(FOCUSINGSHOT) and focus < 70
   
    # if fervor is up in one GCD, assume we exhaust current focus
    fervor = False #cds['Fervor'].cdtime <= 1 and self.hunter.meta.talent4 == 0
   
    checks = [not steady_focus,
              spell_check(self.hunter,br,'Barrage',focus,arc_cost,cds,states) or fervor,
              spell_check(self.hunter,kc,'Kill Command',focus,arc_cost,cds,states) or fervor,
              spell_check(self.hunter,moc,'A Murder of Crows',focus,arc_cost,cds,states) or fervor]
    return False not in checks

class SVArcaneSpecialCondition(Condition):
  title = "SV Arcane Shot - special focus check"
  id = 'SVA'
  computable = True

  def validate(self, cds, states, focus, time):
    ba = BlackArrow(self.hunter)
    es = ExplosiveShot(self.hunter)
    arc = ArcaneShot(self.hunter)
    moc = MurderOfCrows(self.hunter)
    br = Barrage(self.hunter)
   
    arc_cost = arc.focus()
   
    if states['Thrill of the Hunt'].active():
      arc_cost -= 20
    
    steady_focus = self.hunter.meta.talent4 == TIER4.index(STEADYFOCUS) and states['Steady Focus']._timer < 3
    steady_focus = steady_focus and self.hunter.meta.talent7 != TIER7.index(FOCUSINGSHOT) and focus < 70
   
    # if fervor is up in one GCD, assume we exhaust current focus
    fervor = False #cds['Fervor'].cdtime <= 1 and self.hunter.meta.talent4 == 0
   
    checks = [not steady_focus,
              spell_check(self.hunter,br,'Barrage',focus,arc_cost,cds,states) or fervor,
              spell_check(self.hunter,ba,'Black Arrow',focus,arc_cost,cds,states) or fervor,
              spell_check(self.hunter,es,'Explosive Shot',focus,arc_cost,cds,states) or fervor,
              spell_check(self.hunter,moc,'A Murder of Crows',focus,arc_cost,cds,states) or fervor]
    return False not in checks

class MMAimedSpecialCondition(Condition):
  title = "MM Aimed Shot - special focus check"
  id = 'MMA'
  computable = True

  def validate(self, cds, states, focus, time):
    ba = BlackArrow(self.hunter)
    es = ExplosiveShot(self.hunter)
    aim = AimedShot(self.hunter)
    moc = MurderOfCrows(self.hunter)
    br = Barrage(self.hunter)
   
    aim_cost = aim.focus()
   
    if states['Thrill of the Hunt'].active():
      aim_cost -= 20
    
    steady_focus = self.hunter.meta.talent4 == TIER4.index(STEADYFOCUS) and states['Steady Focus']._timer < 3
    steady_focus = steady_focus and self.hunter.meta.talent7 != TIER7.index(FOCUSINGSHOT) and focus < 70
   
    # if fervor is up in one GCD, assume we exhaust current focus
    fervor = False #cds['Fervor'].cdtime <= 1 and self.hunter.meta.talent4 == 0
   
    checks = [not steady_focus,
              spell_check(self.hunter,br,'Barrage',focus,aim_cost,cds,states) or fervor,
              spell_check(self.hunter,moc,'A Murder of Crows',focus,aim_cost,cds,states) or fervor]
    return False not in checks

class BWHoldCondition(Condition):
  """ The purpose here is to guarantee we get two KCs during BW """
  title = "Hold Bestial Wrath for Kill Command"
  id = 'BH'
  computable = True
 
  def validate(self, cds, states, focus, time):
    spell = KillCommand(self.hunter)
    if self.options['bm3']:
      return cds['Kill Command'].cdtime <= 2
    return True

class NoDBBWCondition(Condition):
  title = "No Dire Beast during BW"
  id = 'NDB'
  computable = True
 
  def validate(self, cds, states, focus, time):
    if self.options['bm4']:
      return not states['Bestial Wrath'].active()
    return True

class NoFFBWCondition(Condition):
  title = "No Focus Fire during BW"
  id = 'NFF'
  computable = True
 
  def validate(self, cds, states, focus, time):
    if self.options['bm5']:
      return not states['Bestial Wrath'].active()
    return True

class FocusFireSpecialCondition(Condition):
  title = "Use Focus Fire just before BW"
  id = 'FFB'
  computable = True
 
  def validate(self, cds, states, focus, time):
    return self.options['bm6'] and not states['Focus Fire'].active() and states['Frenzy'].stacks() and cds['Bestial Wrath'].cdtime <= 2


class AimedShotOnlyCACondition(Condition):
  title = "Don't use anything but Aimed Shot during Careful Aim"
  id = 'CAA'
  computable = True
 
  def validate(self, cds, states, focus, time):
    if self.options['mm1']==0:
      return not states['Careful Aim'].active() and not states['Rapid Fire'].active()
    return True

class NoChimeraCACondition(Condition):
  title = "Don't use anything but Aimed Shot during Careful Aim"
  id = 'CAA'
  computable = True
 
  def validate(self, cds, states, focus, time):
    if self.options['mm1']==1:
      return not states['Careful Aim'].active() and not states['Rapid Fire'].active()
    return True

class InstantShotsCondition(Condition):
  title = "Only cast instant shots if after Focusing Shot"
  id = 'AFS'
  computable = True
   
  def validate(self, cds, states, focus, time):
    if self.options['mm2'] and not states['Focusing Shot'].active():
      return False
    return True

class AoEMainNukesCondition(Condition):
  title = "Only cast instant shots if after Focusing Shot"
  id = 'AFS'
  computable = True
   
  def validate(self, cds, states, focus, time):
    return self.options['aoe2']

class AoEMainNukesFocusCondition(Condition):
  title = "Only cast instant shots if after Focusing Shot"
  id = 'AFS'
  computable = True
   
  def validate(self, cds, states, focus, time):
    if self.options['aoe2'] and self.options['aoe3']:
      return focus > self.options['aoe3']
    return True
  



import inspect, sys
def conditions_computable(hunter,options,aoe):
  _conditions = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  conditions = [k(hunter,options,aoe) for name,k in _conditions if issubclass(k,Condition)]
  return conditions