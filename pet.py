from tools import *

class Pet(object):
  _cooldown = 3
  _counter = 0

  def ap(self,hunter):
    return hunter.ap()*.6

  def focus_gen(self,hunter):
    return hunter.focus_gen()

  def critmod(self,hunter):
    crit_chance = min(hunter.crit.total()/100.0 + .1,1)
    crit_mod = 2.00
    return (crit_mod * crit_chance + (1-crit_chance))

  def combat_experience(self,hunter):
    return hunter.meta.talent7 == 2 and 1.70 or 1.5

  def mastery(self,hunter):
    bm_mas =  (1++hunter.mastery.total()/100.0)
    return hunter.meta.spec == 0 and bm_mas or 1

  def versatility(self,hunter):
    return (1+hunter.versatility.total()/100.0)

  def multistrike(self,hunter):
    mchance = hunter.multistrike.total()/100.0
    return 1+.6*mchance

  def base(self,hunter,states={}):
    ap = self.ap(hunter)
    if states and states['Focus Fire'].active():
      ap *= 1.1
    dmg = ap/3.5*2 # 100% weapon damage
    return dmg

  def basic(self,hunter,states={}):
    ap = self.ap(hunter)
    if states and states['Focus Fire'].active():
      ap *= 1.1

    dmg = ap
    dmg *= armormod()
    dmg *= self.critmod(hunter)
    dmg *= self.multistrike(hunter)
    dmg *= self.versatility(hunter)
    dmg *= self.combat_experience(hunter)
    dmg *= self.mastery(hunter)
    dmg *= 1.1 # spiked collar

    if hunter.meta.spec == 0:
      dmg *= 1.2 # empowered pets

    if hunter.meta.talent5 == 1:
      dmg *= 1.5

    if states and states['Bestial Wrath'].active():
      dmg *= 1.2

    return dmg

  def do_basic(self,hunter,focus,time,states):
    dmg = 0
    emp = False
    if hunter.meta.spec in (MM,SV,) and hunter.meta.talent7 == 2:
      return dmg,focus
    if states['Enhanced Basic Attacks'].active():
      self._counter = 0
      emp = True
    if self._counter > 0:
      self._counter -= time
    else:
      if focus >= 50:
        self._counter = self._cooldown
        dmg = self.basic(hunter, states) * 2
        if not emp:
          focus -= 50
      elif focus >= 25:
        self._counter = self._cooldown
        dmg = self.basic(hunter, states)
        if not emp:
          focus -= 25
    if dmg and states['Cobra Strikes'].active():
      states['Cobra Strikes'].use_stack()
      dmg = dmg / self.critmod(hunter) * 2 # guaranteed crit
    focus += time * self.focus_gen(hunter)
    return dmg,focus

  def auto(self,hunter,states={}):
    dmg = self.base(hunter,states)
    dmg *= armormod()
    dmg *= self.critmod(hunter)
    dmg *= self.multistrike(hunter)
    dmg *= self.versatility(hunter)
    dmg *= self.combat_experience(hunter)
    if hunter.meta.spec == 0:
      dmg *= self.mastery(hunter)*1.2 # empowered pets
    return dmg

  def do_spells(self,hunter):
    melee = {'name':'Pet (melee)',
             'id':'pet-melee',
             'attributes':[
              {'id':'weapon',
               'title':'Weapon co.',
               'value':'100%',},
              {'id':'base',
               'title':'Base damage',
               'value':'%.02f' % self.base(hunter),},
              {'id':'armor',
               'title':'Armor',
               'value':tooltip('spell',armormod())},
              {'id':'crit',
               'title':'Crit',
               'value':tooltip('spell',self.critmod(hunter)),},
              {'id':'mastery',
               'title':'Mastery',
               'value':tooltip('spell',self.mastery(hunter)),},
              {'id':'multistrike',
               'title':'Multistrike',
               'value':tooltip('spell',self.multistrike(hunter)),},
              {'id':'versatility',
               'title':'Versatility',
               'value':tooltip('spell',self.versatility(hunter)),},
              {'id':'combat',
               'title':'Combat Experience',
               'value':tooltip('spell',self.combat_experience(hunter)),},
              {'id':'emp',
               'title':'Empowered Pets',
               'value':hunter.meta.spec == BM and '120.00%' or '100.00%',},
              {'id':'damage',
               'title':'Damage',
               'value':'%.02f' % self.auto(hunter)},
              {'id':'speed',
               'title':'Time per attack',
               'value':'%ss' % tooltip('time',2/1.1/hunter.haste.total())},
             ]}
    basic = {'name':'Pet (basic)',
             'id':'pet-melee',
             'attributes':[
              {'id':'weapon',
               'title':'Weapon co.',
               'value':'100%',},
              {'id':'base',
               'title':'Base damage',
               'value':'%.02f' % self.base(hunter),},
              {'id':'armor',
               'title':'Armor',
               'value':tooltip('spell',armormod())},
              {'id':'crit',
               'title':'Crit',
               'value':tooltip('spell',self.critmod(hunter))},
              {'id':'mastery',
               'title':'Mastery',
               'value':tooltip('spell',self.mastery(hunter))},
              {'id':'combat',
               'title':'Combat Experience',
               'value':tooltip('spell',self.combat_experience(hunter))},
              {'id':'multistrike',
               'title':'Multistrike',
               'value':tooltip('spell',self.multistrike(hunter))},
              {'id':'versatility',
               'title':'Versatility',
               'value':tooltip('spell',self.versatility(hunter))},
              {'id':'emp',
               'title':'Empowered Pets',
               'value':hunter.meta.spec == BM and '120.00%' or '100.00%',},
              {'id':'collar',
               'title':'Spiked Collar',
               'value':'110.00%',},
              {'id':'blink',
               'title':'Blink Strikes',
               'value':hunter.meta.talent5 == 1 and '150.00%' or '100.00%',},
              {'id':'damage',
               'title':'Damage',
               'value':'%.02f' % self.basic(hunter),},
             ]}
    return (melee,basic,)