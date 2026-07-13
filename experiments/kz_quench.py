"""
KIBBLE-ZUREK QUENCH OF COMPLEX PHIWORLD
========================================
PerceptionLab / Antti Luode + Claude. Helsinki, July 2026.
Do not hype. Do not lie. Just show.

REGISTERED PREDICTIONS (written before any run):

  Setup: 2D complex field psi, second-order dynamics with damping and
  the phiworld self-slowing term:

      psi_tt = c0^2/(1 + beta*|psi|^2) * lap(psi)
               - eps(t)*psi - g*|psi|^2*psi - gamma*psi_t + noise

  eps(t) = -eps0 * t/tauQ  (ramped linearly through the U(1)-breaking
  transition at t=0; clipped at +-eps0). Vortices are counted at the
  moment <|psi|^2> first reaches half its equilibrium value eps0/g.

  P1 (KZ scaling): vortex number N follows a power law N ~ tauQ^(-sigma).
      Mean-field KZ predictions for a 2D complex field:
        overdamped  (z=2, nu=1/2):  sigma = 2*nu/(1+nu*z) = 1/2
        underdamped (z=1, nu=1/2):  sigma = 2*nu/(1+nu*z) = 2/3
      With gamma=0.3 the dynamics are mixed; REGISTERED CLAIM is only
      that a clean power law appears with sigma in [0.4, 0.8]. If the
      log-log plot is not a line, P1 dies and phiworld is NOT in the
      known class.

  P2 (the phiworld question): the self-slowing term (beta=5) changes
      the PREFACTOR of N(tauQ) but NOT the exponent sigma, i.e.
      |sigma(beta=5) - sigma(beta=0)| < 0.1.
      If beta changes the exponent, phiworld is in a different
      universality class from GP/Ginzburg-Landau and every "GP-class"
      claim in Arrowfield must be re-audited.

  Nulls / controls:
      - beta=0 arm IS the control for P2.
      - counting at a fixed threshold (not fixed time) controls for the
        trivial fact that slow quenches condense later.
      - 4 seeds per point; error bars are seed std of log10(N).

  Kill conditions, stated now:
      - r^2 of the log-log fit < 0.9  -> P1 dead.
      - |sigma_b5 - sigma_b0| >= 0.1  -> P2 dead.
      - N < 10 at some tauQ -> that point is excluded from the fit
        (Poisson floor), and the exclusion is reported.
"""
import numpy as np, json, time

rng_master = np.random.default_rng(7)

# ---------------- parameters ----------------
Ngrid   = 128
dx      = 1.0
dt      = 0.08
c0sq    = 1.0
eps0    = 1.0
g       = 1.0
gamma   = 0.3
eta     = 1e-3          # thermal noise amplitude
tauQs   = [12, 25, 50, 100, 200, 400]
nseeds  = 4
thresh  = 0.5 * eps0/g  # count vortices when <|psi|^2> crosses this

def lap(f):
    return (np.roll(f,1,-1)+np.roll(f,-1,-1)+np.roll(f,1,-2)+np.roll(f,-1,-2)-4*f)/dx**2

def wrap(a):
    return (a+np.pi) % (2*np.pi) - np.pi

def count_vortices(psi):
    th = np.angle(psi)
    dxth = wrap(np.roll(th,-1,axis=-1)-th)
    dyth = wrap(np.roll(th,-1,axis=-2)-th)
    circ = dxth + np.roll(dyth,-1,axis=-1) - np.roll(dxth,-1,axis=-2) - dyth
    return int(np.sum(np.abs(circ) > np.pi))

def run_batch(tauQ, beta, seed0):
    """4 seeds batched as leading axis. Returns list of vortex counts,
    each measured at that seed's own threshold crossing."""
    rng = np.random.default_rng(seed0)
    shape = (nseeds, Ngrid, Ngrid)
    psi = 1e-3*(rng.standard_normal(shape)+1j*rng.standard_normal(shape))
    vel = np.zeros(shape, complex)
    t = -tauQ
    tmax = 3.0*tauQ
    counts = [None]*nseeds
    while t < tmax and any(c is None for c in counts):
        eps = np.clip(-eps0*t/tauQ, -eps0, eps0)
        csq = c0sq/(1.0 + beta*np.abs(psi)**2)
        acc = csq*lap(psi) - eps*psi - g*np.abs(psi)**2*psi - gamma*vel
        vel += dt*acc + eta*np.sqrt(dt)*(rng.standard_normal(shape)+1j*rng.standard_normal(shape))
        psi += dt*vel
        t += dt
        m = np.mean(np.abs(psi)**2, axis=(-2,-1))
        for s in range(nseeds):
            if counts[s] is None and m[s] >= thresh:
                counts[s] = count_vortices(psi[s])
    return [c if c is not None else -1 for c in counts]

results = {}
t0 = time.time()
for beta in [5.0, 0.0]:
    for tq in tauQs:
        c = run_batch(tq, beta, seed0=int(1000*beta)+tq)
        results[f"beta{beta:g}_tau{tq}"] = c
        print(f"beta={beta:g} tauQ={tq:4d}  vortices={c}  ({time.time()-t0:.0f}s)", flush=True)

# ---------------- fits ----------------
def fit(beta):
    xs, ys, es, excluded = [], [], [], []
    for tq in tauQs:
        c = np.array(results[f"beta{beta:g}_tau{tq}"], float)
        c = c[c >= 0]
        if len(c) == 0 or np.mean(c) < 10:
            excluded.append(tq); continue
        xs.append(np.log10(tq)); ys.append(np.mean(np.log10(np.maximum(c,1))))
        es.append(np.std(np.log10(np.maximum(c,1))))
    xs, ys = np.array(xs), np.array(ys)
    p, cov = np.polyfit(xs, ys, 1, cov=True)
    yhat = np.polyval(p, xs)
    ss = 1 - np.sum((ys-yhat)**2)/np.sum((ys-np.mean(ys))**2)
    return dict(slope=p[0], slope_err=float(np.sqrt(cov[0,0])), intercept=p[1],
                r2=float(ss), excluded=excluded, xs=xs.tolist(), ys=ys.tolist(), es=es)

f5, f0 = fit(5.0), fit(0.0)
print("\nbeta=5 :", f5)
print("beta=0 :", f0)
json.dump(dict(results=results, fit_beta5=f5, fit_beta0=f0,
               params=dict(N=Ngrid,dt=dt,eps0=eps0,g=g,gamma=gamma,eta=eta,thresh=thresh)),
          open("/home/claude/kz/kz_results.json","w"), indent=1)
