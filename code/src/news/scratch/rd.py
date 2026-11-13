import json
for x in json.load(open('bridge.json')):
    if x['id'] in (19609,19612,19611,19606):
        print(x['id'], x['from_node'],'->',x['to_node']); print(str(x['body'])[:1800]); print('----')
for x in json.load(open('unread.json'))[:1]:
    print('LETTER', x['id'], x['created_at']); print(x['dream'][:2000])
