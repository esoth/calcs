import inspect
import sys

from tools import *
from stats import Calc

GCD = 1

class Spell(Calc):
  _weapon = 0.0 # a coefficient
  _ap = 0.0 # a coefficient
  _critchance = 0 # in addition to base crit, such as from a spell
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
                       ('multistrike','Multistrike'),
                       ('speed','Cast time'),
                       ('focus','Focus cost'),
                       ('cd','Cooldown'),
                       ('damage','Damage'),
                       ('dps','DPS'),
                       ('regular_hit','Regular hit'))
    
    for attrid,attrtitle in _attributeslist:
      to_pretty = ('weapon','ap','totalcritmod','mastery','armor','buff','spec','perk','versatility','multistrike')
      to_double = ('speed','base','damage','dps','regular_hit',)
      func = getattr(self,attrid)
      value = getattr(self,attrid)()
      if attrid == 'armor':
        value *= 100
      if attrid in to_pretty:
        value = tooltip('spell',value)
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
  
  def multistrike(self):
    """ Two independent chances to do 30% damage = dmg * (1 +.6 * multi) """
    # v + 2*v*m*.3
    # v + .6*vm
    # v(1+.6m)
    mchance = self.hunter.multistrike.total()/100.0
    return 1+.6*mchance

  def critmod(self):
    if self.hunter.meta.spec == 1:
      return self.hunter.mastery.total()/100.0
    return 0
    
  def totalcritmod(self):
    """ Takes into account increased crit chance and/or modifier unique to this spell"""
    crit_chance = min(self.critchance() + self.hunter.crit.total()/100.0,1)
    crit_mod = self.critmod() + 2.00
    return (crit_mod * crit_chance + (1-crit_chance))
  
  def lone(self):
    """ Lone Wolf (Versatility) talent """
    return self.hunter.meta.talent7 == 2 and self.hunter.meta.spec != 0 and 1.3
    
  def damage(self, states={}):
    dmg = self.base() * self.totalcritmod()
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
    if self.multistrike():
      dmg = dmg * self.multistrike()
      
    return dmg
  
  def regular_hit(self, states={}):
    """ No crit or multistrike """
    dmg = self.base()
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
      
    return dmg
  
  def modifiers(self):
    """ additional modifiers """
    return 0
  
  def mastery(self):
    """ Sniper training for MM """
    if self.hunter.meta.spec == 1:
      return 1+self.hunter.mastery.total()/100.0
    return 0
  
  def speed(self):
    hasted = self.casttime()/self.hunter.haste.total()
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
    return 1+self.hunter.versatility.total()/100.0

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
    """ Sniper training for MM, Magic damage for SV """
    if self.hunter.meta.spec == 2: # SV
      return 1+self.hunter.mastery.total()/100.0
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
  _focus = -50

class FocusFire(Spell):
  computable = True
  name = "Focus Fire"
  _duration = 20

class DireBeast(PhysicalSpell):
  computable = True
  name = "Dire Beast"
  _duration = 15
  _ap = .5714 # http://www.esoth.com/blog/warlords-of-draenor-hunter-theorycrafting
  _cd = 30
  
  def damage(self,states={}):
    t_modifiers = product([s.time_modifier() for s in states.values()])
    attacks = int(15/(2/self.hunter.haste.total()/t_modifiers))+1
    dmg = self.ap()*self.hunter.ap()*attacks
    dmg *= self.totalcritmod()
    dmg *= self.multistrike()
    dmg *= self.armor()
    if self.hunter.meta.spec==0:
      dmg *= (1+self.hunter.mastery.total()/100.0+.2)
    return dmg
  
  def regular_hit(self):
    dmg = self.ap()*self.hunter.ap()
    dmg *= self.armor()
    if self.hunter.meta.spec==0:
      dmg *= (1+self.hunter.mastery.total()/100.0+.2)
    return dmg

class AutoShot(PhysicalSpell):
  computable = True
  name = "Auto Shot"
  _weapon = 1.0
  _ap = 0
  
  def base(self):
    """ Base damage from AP and/or Weapon """
    return self.hunter.weapondmg(normalize=False) * self.weapon() + self.hunter.ap() * self.ap()
  
  def speed(self):
    hasted = self.hunter.weaponspeed/self.hunter.haste.total()
    return hasted

class PoisonedAmmo(MagicSpell):
  computable = True
  name = "Poisoned Ammo (Exotic Ammunitions)"
  _weapon = .4
  
  def speed(self):
    hasted = self.hunter.weaponspeed/self.hunter.haste.total()
    return hasted

class ArcaneShot(MagicSpell):
  computable = True
  name = "Arcane Shot"
  _weapon = .95
  _casttime = GCD
  _focus = 30
  _perk = 1.2

class BlackArrow(MagicSpell):
  computable = True
  name = "Black Arrow"
  _weapon = 0
  _ap = 1.416
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
 
  def damage(self, states={}):
    base = super(ChimeraShot,self).damage(states)
    if states and (states['Careful Aim'].active() or states['Rapid Fire'].active()):
      # we can assume this is a MM hunter
      base = base/self.totalcritmod()
      crit_chance = min(self.critchance() + .6 + self.hunter.crit.total()/100.0,1)
      crit_mod = 2+self.hunter.mastery.total()/100.0
      crit = (crit_mod * crit_chance + (1-crit_chance))
      return base * crit
    return base

class AimedShot(PhysicalSpell):
  computable = True
  name = "Aimed Shot"
  _weapon = 2.55
  _casttime = 2.5
  _focus = 50
  _perk = 1.2
 
  def damage(self, states={}):
    base = super(AimedShot,self).damage(states)
    if states and (states['Careful Aim'].active() or states['Rapid Fire'].active()):
      # we can assume this is a MM hunter
      base = base/self.totalcritmod()
      crit_chance = min(self.critchance() + self.hunter.crit.total()/100.0,1)
      crit_mod = 2+self.hunter.mastery.total()/100.0
      crit = (crit_mod * crit_chance + (1-crit_chance))
      return base * crit
    return base
  
class CobraShot(MagicSpell):
  computable = True
  name = "Cobra Shot"
  _weapon = 0.35
  _casttime = 2
  _focus = -14
  _perk = 1.2
  
  def casttime(self):
    haste = self.hunter.haste.total()
    return self._casttime/haste
  
class ExplosiveShot(MagicSpell):
  computable = True
  name = "Explosive Shot"
  _ap = .4 * 4
  _casttime = GCD
  _focus = 15
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
      return (1+self.hunter.mastery.total()/100.0)
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
 
  def damage(self, states={}):
    base = super(SteadyShot,self).damage(states)
    if states and (states['Careful Aim'].active() or states['Rapid Fire'].active()):
      # we can assume this is a MM hunter
      base = base/self.totalcritmod()
      crit_chance = min(self.critchance() + self.hunter.crit.total()/100.0,1)
      crit_mod = 2+self.hunter.mastery.total()/100.0
      crit = (crit_mod * crit_chance + (1-crit_chance))
      return base * crit
    return base
  
class ExplosiveTrap(MagicSpell):
  computable = True
  name = "Explosive Trap"
  _cd = 30
  _ap = .0427 * 11
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
    """ 36.1% * 2 (two glaives) * 4 (primary target). """
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
  _ap = .65 * 30 # http://www.esoth.com/blog/warlords-of-draenor-hunter-theorycrafting
  _cd = 120
  _focus = 60

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