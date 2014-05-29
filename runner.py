from hunter import Hunter
from huntermeta import HunterMeta
from spells import *
from stats import AgilityStat, Proc
from tools import armormod

capacitive = Proc(rppm=23.247, magnitude=73365.34, static_haste=1.1752)
print 'Capacitive average check: %f' % (capacitive.average()/5)

esothmeta = HunterMeta()
esothmeta.race = 'Pandaren'
esothmeta.spec = 2 # SV
esothmeta.weaponmin = 19049
esothmeta.weaponmax = 35379
esothmeta.weaponspeed = 3
esothmeta.talentstr = '0000000'

esoth = Hunter()
esoth.meta = esothmeta

agility = AgilityStat(esoth.meta)
agility.gear(450)
print 'Agility pre-gear check: %f' % agility.total_static()
agility.gear(20000)
print 'Agility with 20k gear: %f' % agility.total_static()

esoth.setgear(agility=30899,
              crit=17616,
              haste=10504,
              mastery=5410,
              readiness=0,
              multistrike=0)
#fake = Spell(weapon=.5,armor=armormod(),buff=1.05) # a generic physical damage spell that uses 50% weapon damage
#print 'Fake damage: %.02f' % fake.damage(esoth).value
#print 'Fake formula: ' + fake.damage(esoth).formula

def doshot(klass):
  shot = klass()
  print '%s dmg: %.02f' % (shot.name, shot.damage(esoth).value)
  print '%s speed: %.02f (%.02f haste)' % (shot.name, shot.speed(esoth), esoth.haste.total_static())
  print '%s dps: %.02f' % (shot.name, shot.dps(esoth))
  print '%s formula: %s' % (shot.name, shot.damage(esoth).formula)
  print '---'
  

doshot(AutoShot)
doshot(ArcaneShot)
doshot(BlackArrow)
doshot(ChimeraShot)
doshot(AimedShot)
doshot(CobraShot)
doshot(ExplosiveShot)
doshot(KillShot)
doshot(FocusingShot)