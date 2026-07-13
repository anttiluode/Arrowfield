# POST-HOC robustness run at 192^2, chunked per beta arm (sandbox time limits).
import numpy as np, json, sys, time, os
exec(open('kz_quench.py').read().split('results = {}')[0].replace('Ngrid   = 128','Ngrid   = 192'))
beta = float(sys.argv[1])
store = json.load(open('kz_posthoc_raw.json')) if os.path.exists('kz_posthoc_raw.json') else {}
t0=time.time()
for tq in tauQs:
    key=f"beta{beta:g}_tau{tq}"
    if key in store: continue
    store[key]=run_batch(tq, beta, seed0=555+int(1000*beta)+tq)
    print(key, store[key], f"({time.time()-t0:.0f}s)", flush=True)
    json.dump(store, open('kz_posthoc_raw.json','w'))
