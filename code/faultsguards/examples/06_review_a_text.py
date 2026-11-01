"""Build a review prompt for a text you wrote, against the faults most likely to apply. Two planted examples show the difference: a text with a baseline built after the result, and one that states the baseline first.
Send the prompt to a model you choose. Nothing is sent here."""
import faultsguards as fg
bad = 'Our method beats the baseline by 12 percent. The baseline was tuned afterwards on the same data to make the comparison fair.'
good = 'The baseline and the method each got the same 500 samples, the same window and the same number of tuning trials, written down before either ran. The method is 12 percent better, interval 4 to 19.'
for name, t in (('after the fact', bad), ('written first', good)):
    p = fg.review_prompt(t, numbers=[1, 3, 4, 6, 9]); print('=== text %s: prompt is %d characters, covers faults %s' % (name, len(p), [1, 3, 4, 6, 9])); print(p[:300] + ' ...\n')
