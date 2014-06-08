from huntermeta import HunterMeta
from stats import *
from tools import pretty
  
class Hunter(object):  
  weaponmin = 0
  weaponmax = 0
  weaponspeed = 3
  
  def __init__(self):
    self.meta = HunterMeta()
    self.agility = AgilityStat(self.meta)
    self.crit = CritStat(self.meta)
    self.haste = HasteStat(self.meta)
    self.mastery = MasteryStat(self.meta)
    self.versatility = VersatilityStat(self.meta)
    self.multistrike = MultistrikeStat(self.meta)
  
  def do_stats(self):
    complist = [('gear','Gear'),
                ('flask','Flask'),
                ('food','Food'),
                ('buffa','Buff (additive)'),
                ('buffm','Buff (multiplicative)'),
                ('basea','Base stats'),
                ('spec','Spec/class bonus'),
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
                     'value': compid in ('buffm','spec') and pretty(func()) or pretty(func(),percent=False)}
        if func.func_doc and func.func_doc.strip():
          component['description'] = func.func_doc.strip()
        _components.append(component)
      _stats.append({'id':statid,
                     'title':stattitle,
                     'components':_components,
                     'total':getattr(self,statid).total_static()})

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
                                   'value': self.agility.total_static()},
                                  {'title':'5% Buff',
                                   'id':'buff',
                                   'value': '105.00%',
                                   'description': u'Not sure if this is right'},],
                   'total': '%.02f' % self.ap(),
                   'description': self.ap.func_doc.strip()})
    return _stats
  
  def setgear(self,**kw):
    """ Update gear values for all stats """
    for k,v in kw.items():
      if isinstance(getattr(self,k),Stat):
        getattr(self,k).gear(v)

  def weapondmg(self):
    """ Weapon damage is average of weapon's min and max, plus AP/3.5 * Weapon Speed """
    wpn = (self.weaponmin + self.weaponmax) / 2
    ap = self.ap() / 3.5 * self.weaponspeed # "Attack Power now increases Weapon Damage at a rate of 1 DPS per 3.5 Attack Power"
    return wpn + ap
  
  def ap(self):
    """ Currently using a 5% AP boost - is this right? """
    return self.agility.total_static()*1.05
  
  def focus_gen(self):
    """ Base focus generation - 4 * haste """
    return (1 + self.haste.total_static()/self.haste.rating()/100)*4.0