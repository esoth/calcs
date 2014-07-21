from calcs.spells import *
from calcs.tools import *

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
    checks = [focus >= 40 or (states['Bestial Wrath'].active() and focus >= 20) or (states['Thrill of the Hunt'].active() and focus >= 20)]
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



import inspect, sys
def conditions_computable(hunter):
  _conditions = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  conditions = [k(hunter) for name,k in _conditions if issubclass(k,Condition)]
  return conditions