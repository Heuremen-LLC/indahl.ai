"""Load the guards into any chat model. This builds the messages list that every chat API takes. Pass --base-url and --model to send it to an OpenAI-compatible endpoint you run yourself
(for example a local server). Without them it prints the messages and sends nothing."""
import sys, json, argparse, urllib.request
import faultsguards as fg
ap = argparse.ArgumentParser(); ap.add_argument('--base-url'); ap.add_argument('--model'); ap.add_argument('--task', default='A vendor says its device error rate is 0.1 percent. We measured 0.4 percent on 200 shots. Is the vendor wrong?'); a = ap.parse_args()
messages = [dict(role='system', content=fg.system_prompt()), dict(role='user', content=a.task)]
if not (a.base_url and a.model): print(json.dumps(messages, indent=1)[:1500] + '\n... (not sent; add --base-url and --model to send)'); sys.exit(0)
req = urllib.request.Request(a.base_url.rstrip('/') + '/chat/completions', data=json.dumps(dict(model=a.model, messages=messages)).encode(), headers={'Content-Type': 'application/json'})
print(json.load(urllib.request.urlopen(req, timeout=300))['choices'][0]['message']['content'])
