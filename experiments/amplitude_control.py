"""
THE CONFOUND KILLER
===================
complex_phiworld gave beta=5 -> 402 vortices, beta=0 -> 0.
But the beta=0 field was also weaker (sigma 0.36 vs 0.65). Obvious confound:
maybe defects need AMPLITUDE, not self-slowing.

Test: drive the beta=0 initial amplitude up and count vortices again.

REGISTERED: if amplitude-matched beta=0 still gives ~0 vortices, SELF-SLOWING
is the defect generator. If it gives hundreds, the headline dies.

RESULT (see README): beta=0 at 3x drive gives 2 vortices vs 402. Confound dead.
Second finding: without self-slowing the field CANNOT HOLD AMPLITUDE --
sigma saturates at ~0.36 however hard it is driven. A linear medium disperses.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import complex_phiworld as C
from scipy.signal import convolve2d
import inspect

src = inspect.getsource(C.run)
src = src.replace("def run(beta, N=128", "def run2(beta, amp=2.0, N=128")
src = src.replace("env = 2.0*np.exp", "env = amp*np.exp")
ns = {'np': np, 'convolve2d': convolve2d, 'lap': C.lap, 'biharm': C.biharm}
exec(src, ns)
run2 = ns['run2']

if __name__ == "__main__":
    print(f"{'run':>26} | {'field_std':>9} | {'vortices':>8}")
    ref = run2(5.0, amp=2.0)
    print(f"{'beta=5, amp=2.0 (ref)':>26} | {ref['field_std']:9.3f} | {ref['nvort']:8d}")
    for amp in [2.0, 3.0, 4.0, 6.0]:
        m = run2(0.0, amp=amp)
        print(f"{'beta=0, amp='+str(amp):>26} | {m['field_std']:9.3f} | {m['nvort']:8d}")
