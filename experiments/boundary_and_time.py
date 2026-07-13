"""
BOUNDARY AND TIME -- Antti's catch
==================================
The 402-vs-0 vortex result was measured at burn=1400 steps (t=112). The wave
needs only ~64 cells (~800 steps) to reach the wall. With periodic wrap, the
field had ALREADY collided with its own wake and gone turbulent. The clean
rings -- the "atoms" -- exist only BEFORE that.

So: are the vortices real physics (modulational instability of a focusing
medium), or a BOX ARTIFACT (self-interference of the wrapped field)?

Two controls:
  (a) TIME. Count vortices vs t, including t well before any wrap-around.
  (b) BOUNDARY. Add an absorbing sponge at the edges so the field radiates
      away instead of reflecting. Rerun beta=5 vs beta=0.

=== REGISTERED PREDICTIONS ===
E1  Vortices appear EARLY, before the wrap could matter (t < 800 steps).
    Rationale: a focusing nonlinearity is MODULATIONALLY UNSTABLE -- a broad
    envelope breaks into filaments and nucleates vortices on its own. That is
    intrinsic, not a boundary effect. Predict >0 vortices well before crossing.
E2  With an ABSORBING boundary, beta=5 still yields many more vortices than
    beta=0. If absorption kills the gap, the headline was a box artifact and
    the README gets a correction in bold.
E3  The FRACTAL/turbulent late state IS at least partly a box artifact: with
    energy free to leave, the late field should be cleaner and decaying, not
    a scale-filling cascade.

Do not hype. Do not lie. Just show.
"""
import numpy as np, json, os
from scipy.signal import convolve2d
LAP = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float64)
def lap(f):
    return (convolve2d(f.real, LAP, mode='same', boundary='wrap')
            + 1j*convolve2d(f.imag, LAP, mode='same', boundary='wrap'))
def biharm(f): return lap(lap(f))

def sponge(N, width=22, strength=0.12):
    """absorbing collar: damping ramps up near the walls, 0 in the interior."""
    x = np.arange(N); X, Y = np.meshgrid(x, x, indexing='ij')
    d = np.minimum(np.minimum(X, N-1-X), np.minimum(Y, N-1-Y)).astype(float)
    s = np.clip((width - d)/width, 0, 1)
    return strength * s**2

def winding(th):
    def w(a,b):
        d=b-a; return (d+np.pi)%(2*np.pi)-np.pi
    d1=w(th,np.roll(th,-1,0)); d2=w(np.roll(th,-1,0),np.roll(np.roll(th,-1,0),-1,1))
    d3=w(np.roll(np.roll(th,-1,0),-1,1),np.roll(th,-1,1)); d4=w(np.roll(th,-1,1),th)
    return np.round((d1+d2+d3+d4)/(2*np.pi)).astype(int)

def run(beta, absorbing, N=128, dt=0.06, damping=0.001, pcub=0.2, g=0.02,
        steps=1500, probe_every=100, seed=1, core=slice(30,98)):
    rng = np.random.default_rng(seed)
    x=np.arange(N); X,Y=np.meshgrid(x,x,indexing='ij'); c=N//2; r=N/15.0
    env = 2.0*np.exp(-((X-c)**2+(Y-c)**2)/(2*r**2))
    ph = convolve2d(0.9*rng.standard_normal((N,N)), np.ones((5,5))/25., mode='same', boundary='wrap')
    psi = env*np.exp(1j*2.5*ph); old = psi.copy()
    absorb = sponge(N) if absorbing else np.zeros((N,N))
    trace=[]
    for t in range(steps):
        I=np.abs(psi)**2
        c2=1.0/(1.0+beta*I+1e-9)
        a=c2*lap(psi) - (-psi+pcub*I*psi) - g*biharm(psi)
        v=psi-old
        new=psi+(1.0-damping*dt)*v+(dt**2)*a
        new*= np.exp(-absorb)                       # the sponge
        old,psi=psi,new
        if t % probe_every == 0 and t>0:
            w = winding(np.angle(psi))[core, core]  # count in the INTERIOR only
            trace.append((t, int((w!=0).sum()), float(np.abs(psi[core,core]).std())))
    return trace

if __name__=="__main__":
    os.makedirs("results",exist_ok=True); out={}
    CROSS = 800   # steps for the wave to reach the wall
    for absorbing in [False, True]:
        for beta in [5.0, 0.0]:
            tag=f"{'absorb' if absorbing else 'wrap'}_beta{beta:g}"
            tr = run(beta, absorbing)
            early = [n for (t,n,s) in tr if t < CROSS]
            late  = [n for (t,n,s) in tr if t >= CROSS]
            out[tag]={"trace":tr,"early_mean":float(np.mean(early)),
                      "late_mean":float(np.mean(late)),
                      "early_max":int(max(early)), "late_max":int(max(late))}
            print(f"{tag:18s} | pre-crossing <v>={np.mean(early):7.1f} (max {max(early):4d}) "
                  f"| post-crossing <v>={np.mean(late):7.1f} (max {max(late):4d})")
    json.dump(out, open("results/boundary_and_time.json","w"), indent=1)
    print("\n(interior-only counts; sponge absorbs at the walls; CROSS=800 steps)")
