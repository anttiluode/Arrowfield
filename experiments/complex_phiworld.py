"""
COMPLEX PHIWORLD -- the experiment the failure demanded
=======================================================
The real-scalar test returned corr(|L|, I) = 0.81: on a real scalar field
the Chiral Eye is an INTENSITY METER, not an arrow. It cannot distinguish
"this lump is bright" from "this lump has a direction."

Hypothesis (the chain's missing precondition):
    THE ARROW NEEDS INTERNAL PHASE. A real scalar field has no U(1); its
    delay-plane rotation is forced to track amplitude. Give the field a
    phase -- psi in C -- and the arrow should DECOUPLE from intensity and
    become an independent, sign-carrying, topological quantity.

Substrate: phiworld, complexified (Ginzburg-Landau / NLS form).
    c^2(|psi|) = c0^2 / (1 + beta*|psi|^2)     <-- same self-slowing
    V'(psi)    = -psi + lambda*|psi|^2*psi     <-- same cap, U(1)-symmetric
    psi_tt     = c^2 lap(psi) - V'(psi) - g*biharm(psi)

Chiral Eye, now in its native form (V5, verbatim):
    L(x) = < Im( psi(t) * conj(psi(t-lag)) ) >

=== REGISTERED PREDICTIONS (before the run) ===

C1  DECOUPLING. corr(|L|, I) should DROP substantially below the real-scalar
    value of 0.81. Predict < 0.6. If it stays ~0.8, phase buys nothing and
    the chain's link 5 is in serious trouble on ANY substrate.

C2  SIGN STRUCTURE. On the real field, L had essentially one sign (it tracked
    intensity). On the complex field, L should carry BOTH SIGNS -- chirality --
    with a meaningful negative fraction. Predict min-sign fraction > 0.15.
    (Real-scalar baseline is measured in the same run for comparison.)

C3  TOPOLOGY. With a phase, the field can carry winding. Predict detectable
    integer phase defects (vortices, where the phase winds by +/-2pi around a
    plaquette), and predict L is CONCENTRATED ON THEM rather than on the
    intensity crests -- i.e. corr(|L|, |vorticity|) should exceed
    corr(|L|, I) in the structured region.
    THIS IS THE RISKY ONE. If the arrow lives on the defects and not on the
    crests, "matter is quantized winding, and it lives where the intensity
    is NOT" is a photograph. If L still just tracks I, the chain is wrong
    about where addresses come from and we say so.

C4  SELF-SLOWING STILL LOAD-BEARING. beta=0 control should again show weaker
    structure and (now) fewer pinned defects.

Do not hype. Do not lie. Just show.
"""
import numpy as np, json, os
from scipy.signal import convolve2d

LAP = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float64)
def lap(f):
    return (convolve2d(f.real, LAP, mode='same', boundary='wrap')
            + 1j*convolve2d(f.imag, LAP, mode='same', boundary='wrap'))
def biharm(f): return lap(lap(f))

def run(beta, N=128, dt=0.06, damping=0.001, pcub=0.2, g=0.02,
        burn=1600, window=700, lagsteps=6, seed=1):
    rng = np.random.default_rng(seed)
    x = np.arange(N); X, Y = np.meshgrid(x, x, indexing='ij')
    c = N//2; r = N/15.0
    env = 2.0*np.exp(-((X-c)**2 + (Y-c)**2)/(2*r**2))
    # same gaussian pulse, but with a random phase texture: the field is now
    # allowed to have internal structure it did not have before.
    ph = 0.9*rng.standard_normal((N,N))
    ph = convolve2d(ph, np.ones((5,5))/25., mode='same', boundary='wrap')
    psi = env*np.exp(1j*2.5*ph)
    psi_old = psi.copy()

    for t in range(burn + window):
        I_loc = np.abs(psi)**2
        c2 = 1.0/(1.0 + beta*I_loc + 1e-9)
        Vp = -psi + pcub*I_loc*psi                 # U(1)-symmetric cap
        a = c2*lap(psi) - Vp - g*biharm(psi)
        v = psi - psi_old
        new = psi + (1.0 - damping*dt)*v + (dt**2)*a
        psi_old, psi = psi, new
        if t == burn:
            buf = np.zeros((window, N, N), dtype=complex)
        if t >= burn:
            buf[t-burn] = psi

    # --- maps ---
    I = (np.abs(buf)**2).mean(axis=0)

    # Chiral Eye, native complex form: L = < Im( psi(t) conj(psi(t-lag)) ) >
    a_, b_ = buf[lagsteps:], buf[:-lagsteps]
    L = np.imag(a_*np.conj(b_)).mean(axis=0)

    # real-scalar control on the SAME run: use Re(psi) only, scalar Chiral Eye
    R = buf.real
    Rd = np.gradient(R, dt, axis=0)
    ar, br = R[lagsteps:], R[:-lagsteps]
    ard, brd = Rd[lagsteps:], Rd[:-lagsteps]
    L_real = (ar*brd - ard*br).mean(axis=0)

    # vorticity: phase winding around each plaquette (integer, in units of 2pi)
    th = np.angle(buf.mean(axis=0))
    def w(a, b):
        d = b - a
        return (d + np.pi) % (2*np.pi) - np.pi
    d1 = w(th, np.roll(th,-1,0))
    d2 = w(np.roll(th,-1,0), np.roll(np.roll(th,-1,0),-1,1))
    d3 = w(np.roll(np.roll(th,-1,0),-1,1), np.roll(th,-1,1))
    d4 = w(np.roll(th,-1,1), th)
    wind = np.round((d1+d2+d3+d4)/(2*np.pi)).astype(int)
    nvort = int((wind != 0).sum())
    # smear the defect map so correlations are not measuring single pixels
    vmag = convolve2d(np.abs(wind).astype(float), np.ones((5,5)), mode='same', boundary='wrap')
    return dict(I=I, L=L, L_real=L_real, wind=wind, vmag=vmag,
                nvort=nvort, psi=buf[-1], field_std=float(np.abs(buf).std()))

def corr(a,b,mask=None):
    a,b = a.ravel().astype(float), b.ravel().astype(float)
    if mask is not None:
        m = mask.ravel(); a,b = a[m], b[m]
    if a.std()<1e-12 or b.std()<1e-12: return float('nan')
    return float(np.corrcoef(a,b)[0,1])

def signfrac(L):
    p = (L > 0).sum(); n = (L < 0).sum()
    return float(min(p,n)/max(p+n,1))

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    out = {}
    for beta in [5.0, 0.0]:
        tag = f"cplx_beta_{beta:g}"
        print(f"\n=== {tag} " + "="*38)
        m = run(beta)
        live = m['I'] > np.percentile(m['I'], 60)
        r = {
            "corr_absL_I":        corr(np.abs(m['L']), m['I']),
            "corr_absL_I_live":   corr(np.abs(m['L']), m['I'], live),
            "corr_absL_vort":     corr(np.abs(m['L']), m['vmag']),
            "corr_absL_vort_live":corr(np.abs(m['L']), m['vmag'], live),
            "corr_absLreal_I":    corr(np.abs(m['L_real']), m['I']),   # scalar control
            "signfrac_L":         signfrac(m['L']),
            "signfrac_L_real":    signfrac(m['L_real']),
            "n_vortices":         m['nvort'],
            "field_std":          m['field_std'],
        }
        for k,v in r.items(): print(f"  {k:22s} {v:+.4f}" if isinstance(v,float) else f"  {k:22s} {v}")
        out[tag] = r
        np.savez_compressed(f"results/maps_{tag}.npz",
                            I=m['I'], L=m['L'], wind=m['wind'], vmag=m['vmag'])
    json.dump(out, open("results/complex_phiworld.json","w"), indent=1)
