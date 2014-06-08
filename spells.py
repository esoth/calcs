import inspect
import sys

from tools import *
from stats import Calc

GCD = 1
BM_MASTERY_BASE = .16
MM_MASTERY_BASE = .168
SV_MASTERY_BASE = .08
BM_MASTERY_SCALAR = 2
MM_MASTERY_SCALAR = 2
SV_MASTERY_SCALAR = 1

class Documentable(Calc):
  """ Contains a value and a formula. The formula is a textual output to be displayed
        on a page """
  value = 0.0
  formula = 'a generic formula'
  descriptions = {}

class Spell(Calc):
  _weapon = 0.0 # a coefficient
  _ap = 0.0 # a coefficient
  _critchance = 0 # in addition to base crit, such as from a spell
  _critmod = 0 # in addition to the base 200%
  _armor = 0 # mitigating modifier
  _buff = 0 # probably either physical or magical
  _casttime = 2
  _spec = 0 # any special modifier
  _focus = 0 # focus cost
  _cd = 0
  _duration = 0
  
  def weapon(self):
    return self._weapon
  def ap(self):
    return self._ap
  def critchance(self):
    return self._critchance
  def critmod(self):
    return self._critmod
  def armor(self):
    return self._armor
  def buff(self):
    return self._buff
  def casttime(self):
    return self._casttime
  def spec(self):
    return self._spec
  def focus(self):
    return self._focus
  def cd(self):
    return self._cd
  def duration(self):
    return self._duration
  
  def attributes(self):
    _attributes = []
    _attributeslist = (('weapon','Weapon co.'),
                       ('ap','AP co.'),
                       ('base','Base damage'),
                       ('totalcritmod','Crit modifier'),
                       ('armor','Armor mit.'),
                       ('mastery','Mastery buff'),
                       ('buff','Buff'),
                       ('spec','Spec. based mod.'),
                       ('speed','Cast time'),
                       ('focus','Focus cost'),
                       ('cd','Cooldown'),
                       ('damage','Damage'),
                       ('dps','DPS'),)
    
    for attrid,attrtitle in _attributeslist:
      to_pretty = ('weapon','ap','totalcritmod','mastery','armor','buff','spec',)
      to_double = ('speed','base','damage','dps',)
      func = getattr(self,attrid)
      value = getattr(self,attrid)()
      if attrid in to_pretty:
        value = pretty(value)
      elif attrid in to_double:
        value = '%.02f' % value
      attr = {'id':attrid,
              'title':attrtitle,
              'value':value,}
      attr['klass'] = u'%s_%s' % (attrid,self.__class__.__name__)
      if func.func_doc and func.func_doc.strip():
        attr['description'] = func.func_doc.strip()
      _attributes.append(attr)
    return _attributes
  
  def __init__(self, hunter):
    """ Must be initiated with a hunter object """
    self.hunter = hunter
  
  def base(self):
    """ Base damage from AP and/or Weapon """
    return self.hunter.weapondmg() * self.weapon() + self.hunter.ap() * self.ap()
    
  def totalcritmod(self):
    """ Takes into account increased crit chance and/or modifier unique to this spell"""
    crit_chance = min(self.critchance() + self.hunter.crit.total_static()/float(self.hunter.crit.rating())/100.0,1)
    crit_mod = self.critmod() + 2.00
    return (crit_mod * crit_chance + (1-crit_chance))
    
  def damage(self):
    dmg = self.base() * self.totalcritmod()
    _mastery = self.mastery()
    if self.armor():
      dmg = dmg * self.armor()
    if self.buff():
      dmg = dmg * self.buff()
    if self.mastery():
      dmg = dmg * self.mastery()
    if self.spec():
      dmg = dmg * self.spec()
    if self.modifiers():
      dmg = dmg * self.modifiers()
    
    # multistrike
    return dmg
  
  def modifiers(self):
    """ additional modifiers """
    return 0
  
  def mastery(self):
    return 0
  
  def speed(self):
    hasted = self.casttime()/(1+self.hunter.haste.total_static()/float(self.hunter.haste.rating())/100.0)
    return max(1.0,hasted)
  
  def dps(self):
    dmg = self.damage()
    speed = self.speed()
    return dmg/speed
  
  def special(self):
    """ We might need to have a special consideration, like a guaranteed crit """
    return self.damage()

class PhysicalSpell(Spell):
  _armor = armormod()
  _buff = 1.05
  
  def buff(self):
    """ Physical vulnerability debuff """
    return super(PhysicalSpell,self).buff()
    
class MagicSpell(Spell):
  """ Magic Damage for Survival mastery """
  _buff = 1.05

  def buff(self):
    """ Magic vulnerability debuff """
    return super(MagicSpell,self).buff()
    
  def mastery(self):
    """ +dmg modifier if Survival """
    if self.hunter.meta.spec == 2: # SV
      base = SV_MASTERY_BASE
      return 1+base+self.hunter.mastery.total_static()/float(self.hunter.mastery.rating())/100.0*SV_MASTERY_SCALAR
    return 0

class NoneSpell(Spell):
  name = "Pass"
  _casttime = GCD

class AutoShot(PhysicalSpell):
  computable = True
  name = "Auto Shot"
  _weapon = 1.0
  _ap = 0
  
  def speed(self):
    hasted = self.hunter.weaponspeed/(1+self.hunter.haste.total_static()/self.hunter.haste.rating())
    return hasted

class ArcaneShot(MagicSpell):
  computable = True
  name = "Arcane Shot"
  _weapon = 1.4
  _casttime = GCD
  _focus = 30

class BestialWrath(Spell):
  name = "Bestial Wrath"
  _duration = 10
  _casttime = 0
  _cd = 100

class BlackArrow(MagicSpell):
  computable = True
  name = "Black Arrow"
  _weapon = 0
  _ap = 1.41858
  _casttime = GCD
  _focus = 35
  _cd = 30
  _spec = 1.3 # trap mastery
  
  def spec(self):
    """ Trap mastery """
    return self._spec

class ChimeraShot(MagicSpell):
  computable = True
  name = "Chimera Shot"
  _weapon = 1.9
  _casttime = GCD
  _focus = 45
  _cd = 9

class AimedShot(PhysicalSpell):
  computable = True
  name = "Aimed Shot"
  _weapon = 2.55
  _casttime = 2.5
  _focus = 50
  
class CobraShot(MagicSpell):
  computable = True
  name = "Cobra Shot"
  _weapon = 0.35
  _casttime = 2
  _focus = -14
  
class ExplosiveShot(MagicSpell):
  computable = True
  name = "Explosive Shot"
  _ap = .8 * 3
  _casttime = GCD
  _focus = 25
  _cd = 6

class KillShot(PhysicalSpell):
  computable = True
  name = "Kill Shot"
  _weapon = 4.75
  _casttime = GCD
  _cd = 10

class KillCommand(PhysicalSpell):
  computable = True
  name = "Kill Command"
  _focus = 40
  _casttime = GCD
  _cd = 6
  _ap = 1.575
  
  def spec(self):
    """ Combat Experience """
    return 1.5
    
  def mastery(self):
    """ +dmg modifier if Survival """
    if self.hunter.meta.spec == 0: # BM
      base = BM_MASTERY_BASE
      return 1+base+self.hunter.mastery.total_static()/float(self.hunter.mastery.rating())/100.0*BM_MASTERY_SCALAR
    return 0

class MultiShot(PhysicalSpell):
  computable = True
  name = "Multi-Shot"

class SerpentSting(MagicSpell):
  computable = True
  name = "Serpent Sting"

class SteadyShot(PhysicalSpell):
  computable = True
  name = "SteadyShot"
  
class ExplosiveTrap(MagicSpell):
  computable = True
  name = "Explosive Trap"

class Barrage(PhysicalSpell):
  computable = True
  name = "Barrage"

class Powershot(PhysicalSpell):
  computable = True
  name = "Powershot"

class MurderOfCrows(PhysicalSpell):
  computable = True
  name = "A Murder of Crows"

class BearTrap(PhysicalSpell):
  computable = True
  name = "Bear Trap"

class FocusingShot(PhysicalSpell):
  computable = True
  name = "FocusingShot"
  _weapon = 1.00
  _casttime = 3
  _focus = -50



def do_spells(meta, hunter):
  spelltable = []
  _spells = inspect.getmembers(sys.modules[__name__], lambda term: getattr(term,'computable',False))
  sorted(_spells, key=lambda term: term[0])
    
  for name,klass in _spells:
    spell = klass(hunter)
    spelltable.append({'name':spell.name,
                       'attributes':spell.attributes()})
  return spelltable