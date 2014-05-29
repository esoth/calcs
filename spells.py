import inspect
import sys

from tools import *
from stats import Calc

GCD = 1

class Documentable(Calc):
  """ Contains a value and a formula. The formula is a textual output to be displayed
        on a page """
  value = 0.0
  formula = 'a generic formula'

class Spell(Calc):
  weapon = 0.0 # a coefficient
  ap = 0.0 # a coefficient
  critchance = 0 # in addition to base crit, such as from a spell
  critmod = 0 # in addition to the base 200%
  armor = 0 # mitigating modifier
  buff = 0 # probably either physical or magical
  casttime = 2
  spec = 0 # any special modifier
  focus = 0 # focus cost
  cd = 0
  
  def __init__(self, hunter):
    """ Must be initiated with a hunter object """
    self.hunter = hunter
  
  def damage(self):
    """ Needs a HunterCalc class to get stats """
    base = self.hunter.weapondmg() * self.weapon + self.hunter.ap() * self.ap
    
    crit_chance = min(self.critchance + critify(self.hunter.crit.total_static()),1)
    crit_mod = self.critmod + 2.00
    crit = (crit_mod * crit_chance + (1-crit_chance))
    dmg = base * crit
    _mastery = self.mastery()
    if self.armor:
      dmg = dmg * self.armor
    if self.buff:
      dmg = dmg * self.buff
    if _mastery:
      dmg = dmg * _mastery
    if self.spec:
      dmg = dmg * self.spec
    _modifiers = self.modifiers()
    if _modifiers['value']:
      dmg = dmg * _modifiers['value']
    
    # multistrike
    
    formula = "(WeaponDamage * %.02f + AP * %.02f) *  %.02fcrit *  %.02farmor * %.02fmastery * %.02fbuff%s" % (self.weapon,
                self.ap,crit,self.armor or 1.0,_mastery or 1.0, self.buff or 1.0,_modifiers['formula'])
    return Documentable(value=dmg,formula=formula)
  
  def modifiers(self):
    """ additional modifiers """
    return {'value':0,'formula':''}
  
  def mastery(self):
    return 0
  
  def speed(self):
    """ Needs a HunterCalc class to get stats """
    hasted = self.casttime/(1+hastify(self.hunter.haste.total_static()))
    return max(1.0,hasted)
  
  def dps(self):
    """ Needs a HunterCalc class to get stats """
    dmg = self.damage().value
    speed = self.speed()
    return dmg/speed
  
  def special(self):
    """ We might need to have a special consideration, like a guaranteed crit """
    return self.damage()

class AutoShot(Spell):
  computable = True
  name = "Auto Shot"
  weapon = 1.0
  ap = 0
  buff = 1.05
  armor = armormod()
  
  def modifiers(self):
    """ additional modifiers """
    if istalent(self.hunter.meta.talentstr,EXOTICMUNITIONS):
      return {'value':2.0,'formula':' * 2.0(Poison Ammo)'}
    else:
      return super(AutoShot,self).modifiers()
  
  def speed(self):
    """ Needs a HunterCalc class to get stats """
    hasted = self.hunter.weaponspeed/(1+hastify(self.hunter.haste.total_static()))
    return hasted

class SVMastery(Spell):
  """ Magic Damage for Survival mastery """
    
  def mastery(self):
    if self.hunter.meta.spec == 2: # SV
      base = .08
      return 1+base+mastify(self.hunter.mastery.total_static())
    return 0

class ArcaneShot(SVMastery):
  computable = True
  name = "Arcane Shot"
  weapon = 1.4
  buff = 1.05
  casttime = GCD
  focus = 30

class BlackArrow(SVMastery):
  computable = True
  name = "Black Arrow"
  weapon = 0
  buff = 1.05
  ap = 1.41858
  casttime = GCD
  focus = 35
  cd = 30
  spec = 1.3 # trap mastery

class ChimeraShot(Spell):
  computable = True
  name = "Chimera Shot"
  weapon = 1.9
  buff = 1.05
  casttime = GCD
  focus = 45
  cd = 9

class AimedShot(Spell):
  computable = True
  name = "Aimed Shot"
  weapon = 2.55
  buff = 1.05
  armor = armormod()
  casttime = 2.5
  focus = 50
  
class CobraShot(SVMastery):
  computable = True
  name = "Cobra Shot"
  weapon = 0.35
  buff = 1.05
  casttime = 2
  focus = -14
  
class ExplosiveShot(SVMastery):
  computable = True
  name = "Explosive Shot"
  ap = .8 * 3
  buff = 1.05
  casttime = GCD
  focus = 25
  cd = 6

class KillShot(Spell):
  computable = True
  name = "Kill Shot"
  weapon = 4.75
  buff = 1.05
  casttime = GCD
  cd = 10

class KillCommand(Spell):
  computable = True
  name = "Kill Command"

class MultiShot(Spell):
  computable = True
  name = "Multi-Shot"

class SerpentSting(Spell):
  computable = True
  name = "Serpent Sting"

class SteadyShot(Spell):
  computable = True
  name = "SteadyShot"
  
class ExplosiveTrap(Spell):
  computable = True
  name = "Explosive Trap"

class Barrage(Spell):
  computable = True
  name = "Barrage"

class Powershot(Spell):
  computable = True
  name = "Powershot"

class MurderOfCrows(Spell):
  computable = True
  name = "A Murder of Crows"

class BearTrap(Spell):
  computable = True
  name = "Bear Trap"

class FocusingShot(Spell):
  computable = True
  name = "FocusingShot"
  weapon = 1.00
  buff = 1.05
  casttime = 3
  focus = -50
  
def pretty(value):
  if not value:
    return ''
  if isinstance(value,float):
    return '%.02f%%' % value
  else:
    return value
  
def build_spell(spell):
  spell = {'name':       spell.name,
           'damage':     '%.02f' % spell.damage().value,
           'speed':      '%.02f' % spell.speed(),
           'dps':        '%.02f' % spell.dps(),
           'weapon':     pretty(spell.weapon),
           'ap':         pretty(spell.ap),
           'critchance': pretty(spell.critchance),
           'critmod':    pretty(spell.critmod),
           'armor':      pretty(spell.armor),
           'buff':       pretty(spell.buff),
           'casttime':   spell.casttime,
           'spec':       pretty(spell.spec),
           'focus':      spell.focus,
           'cd':         spell.cd,
           'formula':    spell.damage().formula,
          }
  # make pretty
  for k,v in spell.items():
    spell[k] = pretty(v)
  return spell

def do_spells(meta, hunter):
  spelltable = []
  _spells = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  sorted(_spells, key=lambda term: term[0])
    
  for name,klass in _spells:
    spell = klass(hunter)
    spelltable.append(build_spell(spell))
  return spelltable