from states import *
from cds import *
from conditions import *
from priorities import *

from calcs.spells import *
from calcs.tools import *
from calcs.pet import Pet

def runner(hunter,options,aoe=False,lastcalc=0):
  states = states_computable(hunter)
  cds = cds_computable(hunter)
  conditions = conditions_computable(hunter,options,aoe)
  pet = Pet()

  def update_states(time,action,pet_basic,boss_health,focus_costs):
    for k,state in states.items():
      state.update_state(time,action,states,pet_basic,boss_health,focus_costs)
      states[k] = state
    for k,cd in cds.items():
      cd.update_state(time,action,states)
      cds[k] = cd

  table = []
  time_sum = 0
  dmg_sum = 0
  pet_basic_sum = 0
  auto_sum = 0
  poison_sum = 0
  incend_sum = 0
  pet_auto_sum = 0
  beast_cleave_sum = 0
  serpent_sum = 0
  pb_counter = 0
  i = 0 # step counter
  shot_counts = {}
  max_focus = hunter.max_focus()
  ending_focus = max_focus
  pet_max_focus = max_focus
  pet_ending_focus = pet_max_focus
  iterations = 200
  total_time = 400
  spell_id = ''

  _priority = aoe and [bm_aoe_priority,mm_aoe_priority,sv_aoe_priority] or [bm_priority,mm_priority,sv_priority]
  while time_sum < total_time:
    starting_focus = ending_focus
    pet_starting_focus = pet_ending_focus
    boss_health = 1-time_sum/float(total_time)
    for priority in _priority[hunter.meta.spec]:
      if False not in [c(hunter,options,aoe).validate(cds,states,starting_focus,boss_health) for c in priority['conditions']]:
        spell_id = priority['id']
        spell_class = spell_id.lower().replace(' ','_')+'_rotation'
        spell = priority['spell'](hunter)

        modifiers = product([s.damage_modifier() for s in states.values()])
        t_modifiers = product([s.time_modifier() for s in states.values()])
        f_modifiers = product([s.focus_modifier() for s in states.values()])
        time = spell.casttime() / t_modifiers
        if spell.casttime():
          time = max(GCD,time)
        f_gains = [s.focus_gains(states,time) for s in states.values()]
        f_gains = [fg for fg in f_gains if fg]
        f_gains = f_gains and sum(f_gains) or 0
        dmg = spell.damage(states) * modifiers
        if aoe:
          dmg += dmg * spell.aoe() * (options['aoe1']-1)
          if spell_id == 'Chimera Shot':
            dmg *= 2
        auto_dmg = AutoShot(hunter).dps(states) * time * t_modifiers * modifiers
        auto_sum += auto_dmg
        poison_dmg = PoisonedAmmo(hunter).dps(states) * time * t_modifiers * modifiers
        poison_sum += poison_dmg
        incend_dmg = IncendiaryAmmo(hunter).dps(states) * options['aoe1'] * time * t_modifiers * modifiers
        incend_sum += incend_dmg
        if spell_id in ('Arcane Shot','Multi-Shot',):
          serpent_sum += spells.SerpentSting(hunter).instant() * modifiers

        # pet stuff
        p_modifiers = product([s.pet_damage_modifier() for s in states.values()])
        pt_modifiers = product([s.pet_time_modifier() for s in states.values()])
        pf_gains = [s.pet_focus_gains(states,time) for s in states.values()]
        pf_gains = [pfg for pfg in pf_gains if pfg]
        pf_gains = pf_gains and sum(pf_gains) or 0
        pet_basic,pet_ending_focus = pet.do_basic(hunter, pet_starting_focus, time, states)
        pet_ending_focus += pf_gains
        pet_ending_focus += spell.pet_focus_gain() # Fervor/Focus Fire
        pet_basic_sum += pet_basic
        if pet_basic:
          pb_counter += 1
        pet_ending_focus = min(pet_max_focus,pet_ending_focus)
        pet_auto = pet.auto(hunter,states) * time * pt_modifiers * p_modifiers
        pet_auto_sum += pet_auto
        if states['Beast Cleave'].active():
          beast_cleave_sum += (pet_auto + pet_basic) * max(0,(options['aoe1'] - 1)) # perk makes it 100%?

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
          if states['Thrill of the Hunt'].active() and spell_id in ('Aimed Shot','Arcane Shot','Multi-Shot'):
            focus_costs -= 20
            focus_costs = max(0,focus_costs)
          if states['Bombardment'].active() and spell_id == 'Multi-Shot':
            focus_costs -= 25
            focus_costs = max(0,focus_costs)
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
                                't_modifiers':'%.02f%%' % (t_modifiers*100),
                                'auto':'%.02f' % auto_dmg,
                                'incend':'%.02f' % incend_dmg,
                                'poison':'%.02f' % poison_dmg,
                                'pet_auto':'%.02f' % pet_auto},
                      'pet':{'focus':int(pet_starting_focus),'damage':pet_basic},
                      'states':[s.info(states,time) for s in states.values()],
                      'cds':[c.info() for c in cds.values()],
                      'conditions':[c.validate(cds,states,starting_focus,1-i/float(iterations)) for c in conditions],})
        update_states(time,spell_id,pet_basic,boss_health,focus_costs)
        time_sum += time
        dmg_sum += dmg
        break

  dmg_sum += auto_sum
  shot_counts['Auto Shot'] = {'counter':'--',
                              'total':auto_sum,}
  totg = states['Touch of the Grave'].total()
  if totg:
    dmg_sum += totg
    shot_counts['Touch of the Grave'] = {'counter':states['Touch of the Grave'].counter(),
                                         'total':totg,}
  if hunter.meta.talent7 == TIER7.index(EXOTICMUNITIONS):
    if aoe:
      dmg_sum += incend_sum
      shot_counts['Incendiary Ammo'] = {'counter':'--',
                                        'total':incend_sum}
    else:
      dmg_sum += poison_sum
      shot_counts['Poison Ammo'] = {'counter':'--',
                                    'total':poison_sum}
  if hunter.meta.talent7 != TIER7.index(VERSATILITY) or hunter.meta.spec == BM:
    shot_counts['Pet (auto)'] = {'counter':'--',
                                 'total':pet_auto_sum}
    dmg_sum += pet_auto_sum
  if hunter.meta.talent7 != TIER7.index(VERSATILITY) or hunter.meta.spec == BM:
    shot_counts['Pet (basic)'] = {'counter':pb_counter,
                                 'total':pet_basic_sum}
    dmg_sum += pet_basic_sum
  if hunter.meta.spec == SV:
    uptime = states['Serpent Sting'].uptime()
    serpent_sum += spells.SerpentSting(hunter).dps()/15 * uptime # this method is really DPCT
    if aoe:
      serpent_sum *= options['aoe1']
    dmg_sum += serpent_sum
    shot_counts['Serpent Sting'] = {'counter':'--',
                                    'total':serpent_sum}
  if hunter.meta.spec == BM and aoe:
    dmg_sum += beast_cleave_sum
    shot_counts['Beast Cleave'] = {'counter':'--',
                                   'total':beast_cleave_sum}
  if hunter.meta.talent5 == TIER5.index(STAMPEDE):
    auto = pet_auto_sum
    dmg = auto + pet_basic_sum
    dps = dmg / time_sum
    shot_counts['Stampede']['total'] = shot_counts['Stampede']['counter'] * 20 * 4 * dps

  meta = {'states':states,'cds':cds,'conditions':conditions}
  shots=[]
  for k,sc in shot_counts.items():
    shot_counts[k]['percent'] = sc['total']/dmg_sum*100.0
    shot_counts[k]['name'] = k
    shots.append(shot_counts[k])
  shots = sorted(shots, key=lambda term: term['name'])
  diff = (dmg_sum/time_sum-lastcalc)
  diff_success = diff >= 0 and 'success' or 'failure'
  totals = {'damage':'%.02f' % dmg_sum,
            'time':time_sum,
            'shots':shots,
            'dps':'%.02f' % (dmg_sum/time_sum),
            'diff':'%.02f' % abs(diff),
            'diff_success':diff_success}
  return (table,meta,totals)