import json,sys
P='/home/user/folk-instruments/research/rounds/r3-adversarial.json'
d=json.load(open(P)); add=json.load(open(sys.argv[1]))
for k in ('reviewed','missing_claims','reference_candidates','sources_checked'):
    if k in add:
        if k=='reviewed':
            ids={r['id'] for r in add[k]}; d[k]=[r for r in d[k] if r['id'] not in ids]
        d[k]+=add[k]
if 'summary' in add: d['summary']=add['summary']
json.dump(d,open(P,'w'),indent=1,ensure_ascii=False); json.load(open(P)); print('ok',len(d['reviewed']),len(d['sources_checked']))
