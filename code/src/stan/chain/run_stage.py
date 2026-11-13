"""run_stage.py RCFILE -- CMD...  runs CMD and writes its exit code to RCFILE (the event the chain waits on)."""
import subprocess, sys, os
rcf = sys.argv[1]; cmd = sys.argv[sys.argv.index('--') + 1:]
try: rc = subprocess.run(cmd).returncode
except Exception as e: print('run_stage:', e); rc = 99
open(rcf + '.tmp', 'w').write(str(rc)); os.replace(rcf + '.tmp', rcf)
sys.exit(rc)
