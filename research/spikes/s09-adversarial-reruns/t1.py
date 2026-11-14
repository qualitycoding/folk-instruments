import sys,json,time; sys.path.insert(0,'.')
import reed2 as M
t=time.time(); print('check orig fs, 2.0', M.an(M.run(2.0)), time.time()-t, flush=True)
for fs in (44100,88200,176400,705600):
    for v0 in (1.0,1.5,2.5,3.5):
        print(fs,v0,json.dumps(M.an(M.run(v0,fs=fs))),flush=True)
