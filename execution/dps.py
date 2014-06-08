from states import *
from cds import *
from conditions import *


from calcs.spells import *

def product(value):
  if value:
    _next = value.pop()
    return _next * product(value)
  else:
    return 1
    
    
bm_priority = [{'id':'Bestial Wrath',
                'conditions':[BestialWrathCondition,],
                'spell':BestialWrath},
               {'id':'Kill Command',
                'conditions':[KillCommandCondition,],
                'spell':KillCommand},
               {'id':'Arcane Shot',
                'conditions':[ArcaneShotCondition,],
                'spell':ArcaneShot},
               {'id':'Pass',
                'conditions':[NoActionCondition,],
                'spell':NoneSpell},
              ]
    
def runsingle(hunter):
  states = states_computable(hunter)
  cds = cds_computable(hunter)
  conditions = conditions_computable(hunter)
 
  def update_states(time,action):
    for k,state in states.items():
      state.update_state(time,action)
      states[k] = state
    for k,cd in cds.items():
      cd.update_state(time,action)
      cds[k] = cd
 
  table = []
  time_sum = 0
  dmg_sum = 0
  shot_counts = {}
  ending_focus = 100
  iterations = 200
  for i in range(0,iterations):
    starting_focus = ending_focus
    for priority in bm_priority:
      if False not in [c(hunter).validate(cds,states,starting_focus,1-i/float(iterations)) for c in priority['conditions']]:
        spell_id = priority['id']
        spell_class = spell_id.lower().replace(' ','_')+'_rotation'
        if spell_id in shot_counts:
          shot_counts[spell_id] = shot_counts[spell_id] + 1
        else:
          shot_counts[spell_id] = 1
        
        spell = priority['spell'](hunter)
        modifiers = product([s.damage_modifier() for s in states.values()])
        t_modifiers = product([s.time_modifier() for s in states.values()])
        f_modifiers = product([s.focus_modifier() for s in states.values()])
        time = spell.casttime() * t_modifiers
        if time != 0:
          time = max(1,time)
        dmg = spell.damage() * modifiers
       
        focus_passive = time * hunter.focus_gen() * t_modifiers
        focus_costs = spell.focus() * f_modifiers
        #if not gcd, calculate passive first and cap at max focus
        if time > 1:
          ending_focus = min(100,starting_focus + focus_passive) - focus_costs
        else:
          ending_focus = min(100,starting_focus + focus_passive - focus_costs)

        table.append({'action':{'iteration':i,
                                'actionid':spell_id,
                                'starting_focus':int(starting_focus),
                                'focus_passive':'%.02f' % focus_passive,
                                'focus_active':focus_costs,
                                'dmg':'%.02f' % dmg,
                                'time':'%.02f' % time,
                                'totaltime':'%.02f' % time_sum,
                                'modifiers':'%.02f%%' % (modifiers*100),},
                      'states':[s.info() for s in states.values()],
                      'cds':[c.info() for c in cds.values()],
                      'conditions':[c.validate(cds,states,starting_focus,1-i/float(iterations)) for c in conditions],})
        update_states(time,spell_id)
        time_sum += time
        dmg_sum += dmg
        break
  meta = {'states':states,'cds':cds,'conditions':conditions}
  totals = {'damage':'%.02f' % dmg_sum,'time':time_sum,'shot_counts':shot_counts,'dps':'%.02f' % (dmg_sum/time_sum)}
  return (table,meta,totals)