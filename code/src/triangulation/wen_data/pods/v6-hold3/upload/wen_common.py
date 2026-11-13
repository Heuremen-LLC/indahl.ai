"""wen_common.py -- shared prompt shape for Wen-data (6 October 2026, Wayfinder and Bones).
Wen reads a measurement from three seats and answers in one of three modes:
  COMMIT  label it now (two or more rulers agree, the chip held still)
  HOLD    no label yet (rulers split, or the chip moved between runs)
  NEXT    one ruler so far: name the next ruler to read before any label"""
MODES = ['COMMIT', 'HOLD', 'NEXT']
SYSTEM = ("You are Wen. You read measurements from quantum processors. You never label a reading on one ruler. "
          "Answer in one of three modes: COMMIT (label it now: two or more rulers agree and the chip held still), "
          "HOLD (no label yet: the rulers split, or the chip moved between runs), or NEXT (one ruler so far: name the next "
          "ruler to read). Start your answer with the mode word.")


def user_text(reading, baseline='', series='', rulers=''):
    parts = ['Reading: ' + reading]
    if rulers:
        parts.append('What the other rulers showed: ' + rulers)
    if baseline:
        parts.append("The instrument's baseline: " + baseline)
    if series:
        parts.append('The last runs: ' + series)
    return '\n'.join(parts)


def chat(user):
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}]
