import json, hashlib, time
plan = {
 'written': time.strftime('%Y-%m-%dT%H:%M:%S'), 'by': 'Bones, on Wayfinder\'s "Coin."',
 'question': 'do 12 FLOATING xmrig threads (rx/wow profile [-1]x12) hash more per second than 12 PINNED (auto: 0,2,4,6,8,10,12,14,9,11,13,15) on Armature, without lengthening her deeps',
 'why': '480 s window 15:51-15:59: xmrig 10.57 of 12 cores while ~2.06 cores idle; pinned CPUs 100% busy, free hyperthreads 1,3,5,7 at 6.7%',
 'arms': ['P', 'F', 'P', 'F', 'P'], 'switch': 'config hot reload (~32 ms), NO restart; affinity READ BACK from /2/backends before an arm counts',
 'window': 'opens at her next deep start after the switch, closes 2 deep starts later (hpcs_sampler v3); unkeyed after 600 s is labelled',
 'quantity': 'hs_mean_integrated (H/s, what the coin sees); beside it H/CPU-s, xmrig cores, others cores, clock %, her deep durations, pauses',
 'none': 'the P arms, interleaved on both sides of every F arm',
 'rulers': ['SPLIT-sum: OLS y = a + b.t + P.x', 'SPLIT-product: OLS ln y = a + b.t + p.x', 'bracket: each F minus the mean of its two P neighbours'],
 'bar': 'two-sided, family of 3 rulers: t.ppf(1-(1-0.95**(1/3))/2, dof)',
 'states': ['moved_up', 'moved_down', 'inside_the_bar', 'cannot_tell_no_width', 'the_rulers_disagree'],
 'apparatus': ['affinity_read_back_wrong', 'thread_count_not_12', 'switch_not_seen_in_30s', 'unkeyed', 'sampler_unread', 'restarted_in_window'],
 'decision': 'KEEP FLOATING only if H/s reads moved_up on EVERY ruler that ran AND her mean deep duration does not read moved_up (longer) on ANY ruler that ran. Otherwise PINNED, the status quo. Any apparatus fault or error -> PINNED.',
 'power': '5 arms, 2 dof: an effect smaller than the arm-to-arm spread will read inside_the_bar, and that is a reading',
 'prediction': 'none registered (NO PREREG GUESSES)'}
s = json.dumps(plan, indent=1, sort_keys=True)
open('affinity_arms_plan.json', 'w').write(s + '\n')
print('PLAN sha256', hashlib.sha256(s.encode()).hexdigest()[:16], 'written', plan['written'])
