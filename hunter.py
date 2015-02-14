from huntermeta import HunterMeta
from stats import *
from tools import tooltip, orc_ap

class Hunter(object):
  weaponmin = 0
  weaponmax = 0
  weaponspeed = 3

  def __init__(self, meta, equipped):
    if isinstance(meta,HunterMeta):
      self.meta = meta
    else:
      raise Exception('Hunter object must be instantiated with a HunterMeta object')
    self.agility = AgilityStat(meta)
    self.crit = CritStat(meta)
    self.haste = HasteStat(meta)
    self.mastery = MasteryStat(meta)
    self.versatility = VersatilityStat(meta)
    self.multistrike = MultistrikeStat(meta)
    self.equipped = equipped

  def do_stats(self):
    complist = [('gear','Gear'),
                ('proc','From procs (avg)'),
                ('flask','Flask'),
                ('food','Food'),
                ('enchants','Enchants'),
                ('racial','Racial'),
                ('attunement','Attunement'),
                ('spec','Special'),
                ('buff','Buff'),
                ('base','Base stats'),
                ('rating','Rating per 1%')]
    statlist = [('agility','Agility'),
                ('crit','Critical Strike'),
                ('haste','Haste'),
                ('mastery','Mastery'),
                ('versatility','Versatility'),
                ('multistrike','Multistrike'),]

    _stats = []
    for statid,stattitle in statlist:
      _components = []
      for compid,comptitle in complist:
        func = getattr(getattr(self,statid),compid)
        component = {'title':comptitle,
                     'id':compid,
                     'description':'',
                     'value': tooltip(compid,func())}
        if func.func_doc and func.func_doc.strip():
          component['description'] = func.func_doc.strip()
        _components.append(component)
      display_func = getattr(self,statid).total_display
      stat_dict = {'id':statid,
                     'title':stattitle,
                     'components':_components,
                     'total':display_func(),}
      if display_func.func_doc:
        stat_dict['description'] = display_func.func_doc.strip()
      _stats.append(stat_dict)

    _stats.append({'id': 'weapondmg',
                   'title': 'Weapon dmg.',
                   'components': [{'title':'Weapon min.',
                                   'id':'weaponmin',
                                   'value': '%d.00' % self.weaponmin},
                                  {'title':'Weapon max.',
                                   'id':'weaponmax',
                                   'value': '%d.00' % self.weaponmax},
                                  {'title':'Weapon avg.',
                                   'id':'weaponavg',
                                   'value': '%.02f' % ((self.weaponmin+self.weaponmax)/2.0)},
                                  {'title':'Weapon speed.',
                                   'id':'weaponspeed',
                                   'value': '%d.00' % self.weaponspeed},
                                  {'title':'AP',
                                   'id':'ap',
                                   'value': '%.02f' % self.ap()},],
                   'total': '%.02f' % self.weapondmg(),
                   'description': self.weapondmg.func_doc.strip()})
    _stats.append({'id': 'ap',
                   'title': 'AP',
                   'components': [{'title':'From agility',
                                   'id':'agility',
                                   'value': self.agility.total()},
                                  {'title':'Orc racial',
                                   'id':'racial',
                                   'value': orc_ap()},
                                  {'title':'10% Buff',
                                   'id':'buff',
                                   'value': '110.00%',
                                   'description': u'True Shot Aura'},],
                   'total': '%.02f' % self.ap(),
                   'description': self.ap.func_doc.strip()})
    _stats.append({'id': 'focusregen',
                   'title': 'Focus Regen',
                   'total': '%.02f' % self.focus_gen()})

    return _stats

  def do_procs(self,proc_info):
    """ to do """
    self.agility.proc(proc_info['agility']['total'])
    self.crit.proc(proc_info['crit']['total'])
    self.haste.proc(proc_info['haste']['total'])
    self.mastery.proc(proc_info['mastery']['total'])
    self.multistrike.proc(proc_info['multistrike']['total'])
    self.versatility.proc(proc_info['versatility']['total'])

  def rylakstalker2(self):
    setids = (115545,115549,115546,115547,115548)
    return len([e['id'] for e in self.equipped if e['id'] in setids]) >= 2

  def rylakstalker4(self):
    setids = (115545,115549,115546,115547,115548)
    return len([e['id'] for e in self.equipped if e['id'] in setids]) >= 4

  def setgear(self,**kw):
    """ Update gear values for all stats """
    for k,v in kw.items():
      if isinstance(getattr(self,k),Stat):
        getattr(self,k).gear(v)

  def weapondmg(self,normalize=True,ap=1,archmage=1):
    """ Weapon damage is average of weapon's min and max, plus AP/3.5 * Weapon Speed """
    wpn = (self.weaponmin + self.weaponmax) / 2.0
    # ap parameter is bonus ap, probably from Improved Focus Fire
    ap = self.ap(archmage) * ap / 3.5 * (normalize and 2.8 or self.weaponspeed) # "Attack Power now increases Weapon Damage at a rate of 1 DPS per 3.5 Attack Power"
    return wpn + ap

  def ap(self,archmage=1):
    """ 10% AP buff """
    orc = self.meta.race == ORC and orc_ap()
    return ((self.agility.total()+orc)*archmage)*1.10

  def focus_gen(self):
    """ Base focus generation - 4 * haste """
    return self.haste.total()*4.0

  def max_focus(self):
    return self.meta.spec in (0,1,) and 120 or 100