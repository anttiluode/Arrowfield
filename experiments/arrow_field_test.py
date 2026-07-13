"""
THE ARROW-FIELD TEST
====================
Does the skew half of the lag-covariance -- the arrow, A -- live on the
SHELL of a phiworld structure, or in its CORE?

The chain (the_chain.md) claims:
    A(tau) ~= -(tau/2) <psi ^ psi_dot>,   tau = int Gamma dt,   A(0) == 0
    frozen core: Gamma=0 -> tau=0 -> A=0.  free flow: no rotation -> A=0.
    the shell: both -> A != 0 -> arrow -> sequence -> address -> matter.

Substrate: Antti's phiworld, verbatim equations.
    c^2(phi) = c0^2 / (1 + beta*phi^2)      <-- "information slows information"
    V'(phi)  = -phi + lambda*phi^3          <-- the Hamiltonian's speed cap
    phi_tt   = c^2 lap(phi) - V'(phi) - g*biharm(phi),  Verlet + damping

FOUR MAPS, measured per pixel over a steady-state time window:
    I(x)     = <phi^2>                        intensity (the control)
    Gamma(x) = c(x)/c0 = 1/sqrt(1+beta*I)     local clock rate
    L(x)     = <phi(t) d/dt phi(t-tau) - d/dt phi(t) phi(t-tau)>
                                              delay-plane angular momentum
                                              (V5's Chiral Eye, scalar version)
    J(x)     = <phi_dot * grad phi>           information current
                                              (= the SPATIAL skew half of C_tau,
                                               derived: A(x,x+dx) ~ 2 tau dx <phi_dot grad phi>)

=== REGISTERED PREDICTIONS (written before the run) ===

P1  L is DEGENERATE on a scalar field. Analytically, for a standing wave
    phi = A(x)cos(wt):  L = A(x)^2 * w * sin(w*tau).  So L should just track
    intensity.  Predict corr(L, I) > 0.8.  If so, the Chiral Eye needs a
    multi-component field to say anything -- on a scalar it is an
    intensity/frequency meter, nothing more.

P2  MY PRIOR PREDICTION WAS WRONG, and is registered here as expected-to-fail:
    I claimed A would be "hollow at the crests because phi_dot ~ 0 at an
    antinode."  That confuses a spatial velocity node with a temporal one.
    Predict L is BRIGHT at crests.  Registering my own error so it cannot be
    quietly retconned.

P3  J IS THE REAL SHELL OBSERVABLE. A pure standing wave carries no net flux:
    <phi_dot grad phi> time-averages to zero in a fully-formed standing ring.
    Predict: |J| is near-zero in the vacuum, SUPPRESSED at the ring crests,
    and PEAKED in the gradient zones between them.
    Quantitatively: corr(|J|, I) should be LOW (< 0.5), while
    corr(|J|, |grad I|) should be HIGHER.  The "hollow ring" survives, but
    via flux cancellation, not via the mechanism I originally gave.

P4  THE KILLER CONTROL. Set beta = 0 (no self-slowing; c is constant, the
    medium no longer responds to its own intensity).  If the ring structure
    and the A-field look the SAME as beta=5, then "information slows
    information" is DECORATIVE and link 3 of the chain is dead.
    Predict: beta=0 gives qualitatively different (weaker/dispersing)
    localization.  This is the experiment that can kill the whole picture.

Do not hype. Do not lie. Just show.
"""
import numpy as np, json, os
from scipy.signal import convolve2d

LAP = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float64)

def lap(f):  return convolve2d(f, LAP, mode='same', boundary='wrap')
def biharm(f): return lap(lap(f))

class PhiWorld:
    """Antti's phiworld, headless. Equations verbatim from phiworld.py."""
    def __init__(self, N=128, dt=0.08, damping=0.001, base_c_sq=1.0,
                 beta=5.0, pot_lin=1.0, pot_cub=0.2, biharm_g=0.02, seed=0):
        self.N, self.dt, self.damping = N, dt, damping
        self.c0_sq, self.beta = base_c_sq, beta
        self.plin, self.pcub, self.g = pot_lin, pot_cub, biharm_g
        # gaussian pulse init -- the one that makes the rings in the screenshot
        x = np.arange(N); X, Y = np.meshgrid(x, x, indexing='ij')
        c = N // 2; r = N / 15.0
        self.phi = 2.0 * np.exp(-((X-c)**2 + (Y-c)**2) / (2*r**2))
        self.phi_old = self.phi.copy()

    def c_sq(self, phi):
        return self.c0_sq / (1.0 + self.beta * (phi**2) + 1e-9)

    def step(self):
        a = (self.c_sq(self.phi) * lap(self.phi)
             - (-self.plin*self.phi + self.pcub*self.phi**3)
             - self.g * biharm(self.phi))
        v = self.phi - self.phi_old
        new = self.phi + (1.0 - self.damping*self.dt)*v + (self.dt**2)*a
        self.phi_old, self.phi = self.phi, new

def grad(f):
    gx = (np.roll(f,-1,0) - np.roll(f,1,0)) * 0.5
    gy = (np.roll(f,-1,1) - np.roll(f,1,1)) * 0.5
    return gx, gy

def run_and_measure(beta, N=128, burn=1400, window=600, lag=6, seed=0):
    """Burn in to steady state, then record a window and build the four maps."""
    w = PhiWorld(N=N, beta=beta, seed=seed)
    for _ in range(burn): w.step()

    buf = np.zeros((window, N, N))
    for t in range(window):
        w.step()
        buf[t] = w.phi

    dt = w.dt
    phid = np.gradient(buf, dt, axis=0)          # phi_dot(t, x, y)

    # I: intensity (mean square, mean removed)
    mu = buf.mean(axis=0)
    I = ((buf - mu)**2).mean(axis=0)

    # Gamma: local clock rate = c/c0 = 1/sqrt(1 + beta*<phi^2>)
    Gam = 1.0 / np.sqrt(1.0 + beta * (buf**2).mean(axis=0) + 1e-12)

    # L: delay-plane angular momentum (the Chiral Eye, scalar version)
    #    L = < phi(t) phidot(t-lag) - phidot(t) phi(t-lag) >
    a, b = buf[lag:], buf[:-lag]
    ad, bd = phid[lag:], phid[:-lag]
    L = (a*bd - ad*b).mean(axis=0)

    # J: information current = < phi_dot * grad phi >   (the spatial skew half)
    Jx = np.zeros((N,N)); Jy = np.zeros((N,N))
    for t in range(window):
        gx, gy = grad(buf[t])
        Jx += phid[t]*gx; Jy += phid[t]*gy
    Jx /= window; Jy /= window
    Jmag = np.hypot(Jx, Jy)

    gIx, gIy = grad(I)
    gI = np.hypot(gIx, gIy)
    return dict(I=I, Gamma=Gam, L=L, J=Jmag, gradI=gI, phi_final=w.phi, buf_std=buf.std())

def corr(a, b, mask=None):
    a, b = a.ravel(), b.ravel()
    if mask is not None:
        m = mask.ravel(); a, b = a[m], b[m]
    if a.std() < 1e-12 or b.std() < 1e-12: return float('nan')
    return float(np.corrcoef(a, b)[0,1])

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    out = {}
    for beta in [5.0, 0.0]:
        tag = f"beta_{beta:g}"
        print(f"\n=== {tag} " + "="*40)
        m = run_and_measure(beta)
        # analyse only where the structure is (top 40% of intensity) + report global
        live = m['I'] > np.percentile(m['I'], 60)
        r = {
            "corr_L_I":        corr(np.abs(m['L']), m['I']),
            "corr_J_I":        corr(m['J'], m['I']),
            "corr_J_gradI":    corr(m['J'], m['gradI']),
            "corr_J_I_live":   corr(m['J'], m['I'], live),
            "corr_J_gradI_live": corr(m['J'], m['gradI'], live),
            "Gamma_min":       float(m['Gamma'].min()),
            "Gamma_mean":      float(m['Gamma'].mean()),
            "I_max":           float(m['I'].max()),
            "field_std":       float(m['buf_std']),
            "J_at_crest":      float(m['J'][m['I'] > np.percentile(m['I'],95)].mean()),
            "J_at_flank":      float(m['J'][(m['I'] > np.percentile(m['I'],55)) &
                                            (m['I'] < np.percentile(m['I'],80))].mean()),
            "J_at_vacuum":     float(m['J'][m['I'] < np.percentile(m['I'],20)].mean()),
        }
        for k,v in r.items(): print(f"  {k:22s} {v:+.4f}")
        out[tag] = r
        np.savez_compressed(f"results/maps_{tag}.npz",
                            I=m['I'], Gamma=m['Gamma'], L=m['L'], J=m['J'],
                            gradI=m['gradI'], phi=m['phi_final'])
    json.dump(out, open("results/arrow_field.json","w"), indent=1)
