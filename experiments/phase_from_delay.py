"""
PHASE FROM DELAY
================
Question: is phase PRIMITIVE (must be put into the field by hand), or is it
MANUFACTURED BY DELAY (already latent in any real field with memory)?

Construction (pure Takens -- no Hilbert transform, no complex field):
    at each pixel, form the delay pair   u(x,t) = ( phi(x,t), phi(x,t-tau) )
    define the DELAY PHASE               theta(x,t) = atan2( phi(x,t-tau), phi(x,t) )
    compute the winding number of theta around each spatial plaquette.

If a REAL SCALAR field -- the one that scored signfrac 0.000 and had NO
chirality whatsoever as measured -- turns out to carry integer phase windings
once viewed through a delay, then PHASE WAS ALREADY THERE. It is not an extra
ingredient. It is what memory looks like from the inside.

=== REGISTERED PREDICTIONS ===
D1  The real scalar phiworld (beta=5), viewed in delay coordinates, HAS
    nonzero winding numbers.  Predict > 20 defects.
D2  THE DISCRIMINATOR. Winding requires PROPAGATION. A pure standing pattern
    has a spatially-uniform temporal phase and cannot wind. So the beta=0
    control -- which disperses and does not self-trap -- should show FEWER
    delay-phase defects than beta=5, mirroring the complex-field result.
    If beta=0 shows MORE, D2 dies and delay-phase is measuring dispersion,
    not structure.
D3  NULL CONTROL. Spatially-shuffled field (destroys spatial coherence,
    preserves per-pixel statistics) should give a LARGE, meaningless defect
    count -- confirming that the measure is not trivially counting noise.
    Real runs must sit far BELOW the shuffled null.

Do not hype. Do not lie. Just show.
"""
import numpy as np, json, os
from scipy.signal import convolve2d
LAP = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float64)
def lap(f): return convolve2d(f, LAP, mode='same', boundary='wrap')
def biharm(f): return lap(lap(f))

def run_real(beta, N=128, dt=0.08, damping=0.001, pcub=0.2, g=0.02,
             burn=1400, window=400):
    x = np.arange(N); X, Y = np.meshgrid(x, x, indexing='ij')
    c = N//2; r = N/15.0
    phi = 2.0*np.exp(-((X-c)**2 + (Y-c)**2)/(2*r**2)); old = phi.copy()
    buf = np.zeros((window, N, N))
    for t in range(burn+window):
        c2 = 1.0/(1.0 + beta*phi**2 + 1e-9)
        a = c2*lap(phi) - (-phi + pcub*phi**3) - g*biharm(phi)
        v = phi - old
        new = phi + (1.0-damping*dt)*v + (dt**2)*a
        old, phi = phi, new
        if t >= burn: buf[t-burn] = phi
    return buf

def winding_count(theta):
    def w(a,b):
        d = b-a; return (d+np.pi)%(2*np.pi)-np.pi
    d1 = w(theta, np.roll(theta,-1,0))
    d2 = w(np.roll(theta,-1,0), np.roll(np.roll(theta,-1,0),-1,1))
    d3 = w(np.roll(np.roll(theta,-1,0),-1,1), np.roll(theta,-1,1))
    d4 = w(np.roll(theta,-1,1), theta)
    wind = np.round((d1+d2+d3+d4)/(2*np.pi)).astype(int)
    return wind

def delay_phase_defects(buf, lag=6, t_at=-1):
    """theta = atan2( phi(t-lag), phi(t) ) -- the Takens delay phase."""
    a = buf[t_at]; b = buf[t_at-lag]
    theta = np.arctan2(b, a)
    wind = winding_count(theta)
    return int((wind!=0).sum()), wind, theta

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True); out = {}
    rng = np.random.default_rng(0)
    for beta in [5.0, 0.0]:
        buf = run_real(beta)
        n, wind, theta = delay_phase_defects(buf)
        # averaged over several readout times, to show it is not a fluke frame
        ns = [delay_phase_defects(buf, t_at=-1-k*20)[0] for k in range(5)]
        # D3 null: shuffle space, keep per-pixel time series intact
        sh = buf.reshape(buf.shape[0], -1)
        idx = rng.permutation(sh.shape[1])
        shuf = sh[:, idx].reshape(buf.shape)
        n_null = delay_phase_defects(shuf)[0]
        out[f"beta_{beta:g}"] = {"defects": n, "defects_over_frames": ns,
                                 "mean_defects": float(np.mean(ns)),
                                 "shuffled_null": n_null,
                                 "field_std": float(buf.std())}
        print(f"beta={beta:g}:  delay-phase defects = {n}  (5 frames: {ns})"
              f"   shuffled null = {n_null}   sigma={buf.std():.3f}")
        np.savez_compressed(f"results/delayphase_beta_{beta:g}.npz",
                            wind=wind, theta=theta, phi=buf[-1])
    json.dump(out, open("results/phase_from_delay.json","w"), indent=1)
