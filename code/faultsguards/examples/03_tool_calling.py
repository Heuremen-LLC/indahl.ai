"""Function calling: hand a model the schemas, run whatever call it makes, return the result. The model's call is faked here so the example runs with nothing installed."""
import json
import faultsguards as fg
schemas = fg.tool_schemas(); print('tools offered:', [t['function']['name'] for t in schemas])
fake_call = dict(name='search', arguments=json.dumps({'query': 'two option'}))     # what a model would return in a tool_calls entry
result = fg.call_tool(fake_call['name'], json.loads(fake_call['arguments'])); print('result to send back as the tool message:'); print(json.dumps(result, indent=1)[:600])
