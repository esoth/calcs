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

class Spell(Calc):
  _weapon = 0.0 # a coefficient
  _ap = 0.0 # a coefficient
  _critchance = 0 # in addition to base crit, such as from a spell
  _critmod = 0 # in addition to the base 200%
  _armor = 0 # mitigating modifier
  _buff = 0 # probably either physical or magical
  _casttime = GCD
  _spec = 0 # any special modifier
  _focus = 0 # focus cost
  _cd = 0
  _duration = 0
  _perk = 0
  _versatility = 0
  
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
                       ('perk','Draenor perk'),
                       ('spec','Spec. based mod.'),
                       ('versatility','Versatility'),
                       ('speed','Cast time'),
                       ('focus','Focus cost'),
                       ('cd','Cooldown'),
                       ('damage','Damage'),
                       ('dps','DPS'),)
    
    for attrid,attrtitle in _attributeslist:
      to_pretty = ('weapon','ap','totalcritmod','mastery','armor','buff','spec','perk','versatility')
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
    
    if self.lone():
      attr = {'id':'lone',
              'title':'Lone Wolf',
              'description': self.lone.func_doc.strip(),
              'value': '%.02f%%' % (self.lone()*100)}
      _attributes.insert(-3,attr)
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
  
  def lone(self):
    """ Lone Wolf (Versatility) talent """
    return self.hunter.meta.talent7 == 2 and self.hunter.meta.spec != 0 and 1.3
    
  def damage(self, states={}):
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
    if self.perk():
      dmg = dmg * self.perk()
    if self.modifiers():
      dmg = dmg * self.modifiers()
    if self.lone():
      dmg = dmg * self.lone()
    if self.versatility():
      dmg = dmg * self.versatility()
    
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
  
  def perk(self):
    """ Draenor perk """
    return self._perk

  def versatility(self):
    """ Versatility """
    return (1+self.hunter.versatility.total_static()/float(self.hunter.versatility.rating())/100.0)

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

class BestialWrath(Spell):
  name = "Bestial Wrath"
  _duration = 10
  _casttime = 0
  _cd = 100

class RapidFire(Spell):
  computable = True
  name = "Rapid Fire"
  _duration = 15
  _casttime = 0
  _cd = 180

class Stampede(Spell):
  computable = True
  name = "Stampede"
  _duration = 20
  _cd = 300

class Fervor(Spell):
  computable = True
  name = "Fervor"
  _duration = 10
  _cd = 30

class FocusFire(Spell):
  computable = True
  name = "Focus Fire"
  _duration = 20

class DireBeast(Spell):
  computable = True
  name = "Dire Beast"
  _duration = 15
  _cd = 30

class AutoShot(PhysicalSpell):
  computable = True
  name = "Auto Shot"
  _weapon = 1.0
  _ap = 0
  
  def speed(self):
    hasted = self.hunter.weaponspeed/(1+self.hunter.haste.total_static()/self.hunter.haste.rating()/100)
    return hasted

class PoisonedAmmo(MagicSpell):
  computable = True
  name = "Poisoned Ammo (Exotic Ammunitions)"
  _weapon = 2.0
  
  def speed(self):
    hasted = self.hunter.weaponspeed/(1+self.hunter.haste.total_static()/self.hunter.haste.rating()/100)
    return hasted

class ArcaneShot(MagicSpell):
  computable = True
  name = "Arcane Shot"
  _weapon = 1.4
  _casttime = GCD
  _focus = 30
  _perk = 1.2

class BlackArrow(MagicSpell):
  computable = True
  name = "Black Arrow"
  _weapon = 0
  _ap = 1.41858
  _casttime = GCD
  _focus = 35
  _cd = 30
  _perk = 1.2
  _spec = 1.3
  _duration = 20

  def spec(self):
    """ Trap Mastery """
    return super(BlackArrow,self).spec()

class ChimeraShot(MagicSpell):
  computable = True
  name = "Chimera Shot"
  _weapon = 1.9
  _casttime = GCD
  _focus = 35
  _cd = 9

class AimedShot(PhysicalSpell):
  computable = True
  name = "Aimed Shot"
  _weapon = 2.55
  _casttime = 2.5
  _focus = 50
  _perk = 1.2
  
class CobraShot(MagicSpell):
  computable = True
  name = "Cobra Shot"
  _weapon = 0.35
  _casttime = 2
  _focus = -14
  _perk = 1.2
  
  def casttime(self):
    haste = 1+self.hunter.haste.total_static()/self.hunter.haste.rating()/100
    return self._casttime/haste
  
class ExplosiveShot(MagicSpell):
  computable = True
  name = "Explosive Shot"
  _ap = .8 * 4
  _casttime = GCD
  _focus = 25
  _cd = 6

class KillShot(PhysicalSpell):
  computable = True
  name = "Kill Shot"
  _weapon = 5.5
  _casttime = GCD
  _cd = 10

class KillCommand(PhysicalSpell):
  computable = True
  name = "Kill Command"
  _focus = 40
  _casttime = GCD
  _cd = 6
  _ap = 1.575
  _perk = 1.2
  
  def spec(self):
    """ Combat Experience (1.5 base, 1.7 if Versatility) """
    return self.hunter.meta.talent7 == 2 and 1.7 or 1.5
    
  def mastery(self):
    """ +dmg modifier if Survival """
    if self.hunter.meta.spec == 0: # BM
      base = BM_MASTERY_BASE
      return 1+base+self.hunter.mastery.total_static()/float(self.hunter.mastery.rating())/100.0*BM_MASTERY_SCALAR
    return 0

class MultiShot(PhysicalSpell):
  computable = True
  name = "Multi-Shot"
  _focus = 40
  _weapon = .3


class SerpentSting(MagicSpell):
  computable = True
  name = "Serpent Sting"
  _ap = 1.256
  _duration = 15

class SteadyShot(PhysicalSpell):
  computable = True
  name = "SteadyShot"
  _focus = -14
  _casttime = 2
  _weapon = .35
  _perk = 1.2
  
class ExplosiveTrap(MagicSpell):
  computable = True
  name = "Explosive Trap"
  _cd = 30
  _ap = .0426906 * 11
  _duration = 20
  _spec = 1.3

  def cd(self):
    if self.hunter.meta.spec == 2:
      return self._cd/2
    else:
      return self._cd

class GlaiveToss(PhysicalSpell):
  computable = True
  name = "Glaive Toss"
  _focus = 15
  _ap = .361 * 4 * 2
  _cd = 15
  
  def ap(self):
    """ 36.1% * 2 (two glaives) * 4 (primary target). Should it be four hits? """
    return super(GlaiveToss,self).ap()

class Barrage(PhysicalSpell):
  computable = True
  name = "Barrage"
  _cd = 40
  _focus = 30
  _casttime = 3
  _weapon = 4.8

class Powershot(PhysicalSpell):
  computable = True
  name = "Powershot"
  _weapon = 4.5
  _casttime = 2.25
  _focus = 15
  _cd = 45

class MurderOfCrows(PhysicalSpell):
  computable = True
  name = "A Murder of Crows"
  _ap = .206 * 30
  _cd = 120
  _focus = 60
  
  def ap(self):
    """ I don't actually know the AP on this - placeholder """
    return super(MurderOfCrows,self).ap()

class FocusingShot(PhysicalSpell):
  computable = True
  name = "Focusing Shot"
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