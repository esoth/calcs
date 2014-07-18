from states import *
from cds import *
from conditions import *
from procs import *
from priorities import *

from calcs.spells import *
from calcs.tools import product
from calcs.pet import Pet, pet_states_computable
        
def runsingle(hunter):
  states = states_computable(hunter)
  procs = procs_computable(hunter)
  cds = cds_computable(hunter)
  conditions = conditions_computable(hunter)
  pet = Pet()
  pet_states = pet_states_computable(pet,hunter)
 
  def update_states(time,action,boss_health):
    for k,proc in procs.items():
      proc.update_state(time,action,states)
      procs[k] = proc
    for k,cd in cds.items():
      cd.update_state(time,action,states)
      cds[k] = cd
    for k,state in states.items():
      state.update_state(time,action,procs,boss_health)
      states[k] = state
 
  table = []
  time_sum = 0
  dmg_sum = 0
  pet_basic_sum = 0
  pb_counter = 0
  shot_counts = {}
  _priority = [bm_priority,mm_priority,sv_priority]
  max_focus = hunter.max_focus()
  ending_focus = max_focus
  pet_max_focus = 100
  pet_ending_focus = pet_max_focus
  iterations = 200
  i = 0
  haste_counter = 0 # applied to auto dps instead of time_sum
                    # auto should scale equally with any haste procs
                    # so a 1s ability under Rapid Fire is the same as
                    # unhasted auto dps * 1.4
  total_time = 360
  while time_sum < total_time:
    starting_focus = ending_focus
    pet_starting_focus = pet_ending_focus
    boss_health = 1-time_sum/float(total_time)
    for priority in _priority[hunter.meta.spec]:
      if False not in [c(hunter).validate(cds,states,starting_focus,boss_health) for c in priority['conditions']]:
        spell_id = priority['id']
        spell_class = spell_id.lower().replace(' ','_')+'_rotation'
        spell = priority['spell'](hunter)

        modifiers = product([s.damage_modifier() for s in states.values()])
        t_modifiers = product([s.time_modifier() for s in states.values()])
        f_modifiers = product([s.focus_modifier() for s in states.values()])
        time = spell.casttime() / t_modifiers
        if time != 0:
          time = max(1,time)
        f_gains = [s.focus_gains(states,time) for s in states.values()]
        f_gains = [fg for fg in f_gains if fg]
        f_gains = f_gains and sum(f_gains) or 0
        dmg = spell.damage(states) * modifiers
        haste_counter += spell.casttime()
          
        # pet stuff
        pet_basic,pet_ending_focus = pet.do_basic(hunter, pet_starting_focus, time, states, pet_states)
        if spell_id == 'Fervor':
          pet_ending_focus = min(pet_max_focus,pet_ending_focus+50)
        pet_basic_sum += pet_basic
        if pet_basic:
          pb_counter += 1
        pet_ending_focus = min(pet_max_focus,pet_ending_focus)

        if spell_id in shot_counts:
          shot_counts[spell_id]['counter'] += 1
          shot_counts[spell_id]['total'] += dmg
        else:
          shot_counts[spell_id] = {'counter': 1,'total': dmg}
       
        focus_passive = time * hunter.focus_gen() * t_modifiers
        focus_total_gains = focus_passive + f_gains
        focus_costs = spell.focus()
        if focus_costs > 0: # don't make cobra cost during BW!
          focus_costs *= f_modifiers
        #if not gcd, calculate passive first and cap at max focus
        if time > 1:
          ending_focus = min(max_focus,min(max_focus,starting_focus + focus_total_gains) - focus_costs)
        else:
          ending_focus = min(max_focus,starting_focus + focus_total_gains - focus_costs)

        table.append({'action':{'actionid':spell_id,
                                'starting_focus':int(starting_focus),
                                'focus_passive':'%.02f' % focus_passive,
                                'focus_gains':'%.02f' % f_gains,
                                'focus_active':focus_costs >= 0 and '%.02f' % focus_costs or '+%.02f' % float(abs(focus_costs)),
                                'dmg':'%.02f' % dmg,
                                'time':'%.02f' % time,
                                'totaltime':'%.02f' % time_sum,
                                'boss_health':'%.02f%%' % (boss_health*100),
                                'modifiers':'%.02f%%' % (modifiers*100),
                                't_modifiers':'%.02f%%' % (t_modifiers*100)},
                      'pet':{'focus':int(pet_starting_focus),'damage':pet_basic},
                      'states':[s.info(states,time) for s in states.values()],
                      'cds':[c.info() for c in cds.values()],
                      'conditions':[c.validate(cds,states,starting_focus,1-i/float(iterations)) for c in conditions],})
        update_states(time,spell_id,boss_health)
        time_sum += time
        dmg_sum += dmg
        break

  # add Bestial Wrath uptime as a modifier
  bw = 1+states['Bestial Wrath'].uptime()/time_sum
  auto_dmg = AutoShot(hunter).dps()*haste_counter*bw
  dmg_sum += auto_dmg
  shot_counts['Auto Shot'] = {'counter':'--',
                              'total':auto_dmg,}
  if hunter.meta.talent7 == 0:
    poison_dmg = PoisonedAmmo(hunter).dps()*haste_counter*bw
    shot_counts['Poison Ammo'] = {'counter':'--',
                                  'total':poison_dmg}
    dmg_sum += poison_dmg
  if hunter.meta.talent7 != 2 or hunter.meta.spec == 0:
    pet_auto = pet.auto(hunter)*haste_counter*bw
    shot_counts['Pet (auto)'] = {'counter':'--',
                                 'total':pet_auto}
    dmg_sum += pet_auto
  if hunter.meta.talent7 != 2 or hunter.meta.spec == 0:
    shot_counts['Pet (basic)'] = {'counter':pb_counter,
                                 'total':pet_basic_sum}
    dmg_sum += pet_basic_sum
  if hunter.meta.spec == 2:
    serpent = states['Serpent Sting'].total()
    shot_counts['Serpent Sting'] = {'counter':'--',
                                    'total':serpent}
    dmg_sum += serpent

  meta = {'states':states,'cds':cds,'conditions':conditions}
  shots=[]
  for k,sc in shot_counts.items():
    shot_counts[k]['percent'] = sc['total']/dmg_sum*100.0
    shot_counts[k]['name'] = k
    shots.append(shot_counts[k])
  shots = sorted(shots, key=lambda term: term['name'])
  totals = {'damage':'%.02f' % dmg_sum,
            'time':time_sum,
            'shots':shots,
            'dps':'%.02f' % (dmg_sum/time_sum),}
  return (table,meta,totals)