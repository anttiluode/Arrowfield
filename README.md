# ArrowField

### Matter needs phase, and phase needs a medium that slows itself.

**A test of the Chain, run on Antti's phiworld. Two predictions died. One control survived. And the control turned out to be the result.**

*PerceptionLab / Antti Luode with Claude (Opus 4.8). Helsinki, July 2026.*
*Companion to `the_chain.md`, `Rajapinta`, `ClockfieldMeetsGeometricNeuron`, `GeometricNeuron_V20`.*

> Do not hype. Do not lie. Just show.

---

## The headline, in one table

| | real scalar φ | **complex ψ, β=5** | complex ψ, β=0 (control) |
|---|---|---|---|
| corr(\|L\|, I) — *is the arrow just an intensity meter?* | **+0.81** | **+0.14** | −0.08 |
| sign fraction of L — *can it carry chirality?* | **0.000** | **0.497** | 0.482 |
| **topological defects (vortices)** | — | **402** | **0** |
| field structure (σ) | 1.57 | 0.65 | 0.36 |

Two things fall out, and only one of them was predicted.

**1. A real scalar field cannot carry an arrow.** Its Chiral Eye has *one sign, always* (sign fraction 0.000) and correlates 0.81 with raw intensity — it is a brightness meter wearing a topologist's hat. Give the field a phase and the arrow **decouples** (0.81 → 0.14) and becomes **chiral** (0.000 → 0.497, near-perfect left/right balance). *The arrow of time needs at least U(1).*

**2. Self-slowing is the defect generator.** Turn off `c²(ψ) = c₀²/(1+β|ψ|²)` — the one line that says *information slows information* — and the topological defects do not merely thin out. **They do not form.** 402 → 0. Driven at 3× the amplitude, β=0 still yields **2**. Amplitude cannot substitute for the mechanism.

Matter is not made by energy. It is made by a medium that gets in its own way.

![headline](figs/fig3_headline.png)

---

## The kills, first, because they are the point

### [K] The hollow ring. Predicted twice, wrong twice.

The Chain predicted that the arrow ‖A‖ would be *hollow at the intensity crests and bright on the flanks* — matter living on the shell, photographed. It was wrong, and the two wrong reasons are both instructive:

**Wrong reason #1 (registered before the run, as an error).** "At an antinode φ is maximal but φ̇ ≈ 0." This confuses a *spatial* velocity node with a *temporal* one. At an antinode φ(t)=A·cos(ωt), so φ̇(t)=−Aω·sin(ωt) — maximal in amplitude, merely phase-shifted. Working the wedge analytically for a standing wave gives **L = A²·ω·sin(ωτ)**: *brightest* at the crest. Confirmed in simulation.

**Wrong reason #2 (the "corrected" mechanism, also dead).** Expanding the *spatial* skew half gives A(x,x+dx) ≈ 2τ·dx·⟨φ̇∇φ⟩ — **the skew half of the lag-covariance is the energy flux** (this identity survives and is worth keeping). A pure standing wave carries no net flux, so the rings should still be hollow. They are not: J at crest 0.585 > flank 0.375 > vacuum 0.137, monotonic in intensity. The rings in phiworld are *not* standing waves — they are outward-propagating, and they carry flux where they are bright.

*Right answer, wrong mechanism* is how people fool themselves. Here it was wrong answer, twice, and both are on the record.

### [K] The Chiral Eye on a scalar substrate.

`L = Im(z·z̄_lag)` is the load-bearing observable of the entire GeometricNeuron line. On a **real scalar** field it is degenerate: single-signed, 0.81-correlated with intensity, carrying no direction at all. This is not a bug in the measurement — it is a fact about the substrate, and it retroactively explains why every working system in the ecosystem (V5, RCNet, Janus, Zeta) uses complex fields. **The Chain was missing a precondition.**

---

## What survived, and what it means

### [V] C1 — the arrow decouples from intensity, but only with phase.
corr(|L|, I): **0.81 → 0.14**. Registered threshold was < 0.6. On a complex field the arrow becomes an *independent* quantity, not a restatement of brightness.

### [V] C2 — chirality is born with the phase.
Sign fraction of L: **0.000 → 0.497**. The real scalar cannot distinguish left from right *even in principle*. The complex field carries both handednesses in near-perfect balance. Time's arrow is not a scalar property.

### [V] C4 → promoted to the headline — self-slowing makes the defects.
Registered merely as a control ("does β matter, or is it decorative?"). It is not decorative; it is *causal*, with a 200× effect and an amplitude-matched control that rules out the obvious confound:

| run | field σ | vortices |
|---|--:|--:|
| β=5, amp 2.0 | 0.652 | **402** |
| β=0, amp 2.0 | 0.363 | 0 |
| β=0, amp 3.0 | 0.362 | 0 |
| β=0, amp 4.0 | 0.362 | 0 |
| β=0, amp 6.0 | 0.403 | **2** |

Note the second finding hiding in that column: **without self-slowing the field cannot even hold amplitude.** σ saturates at ~0.36 however hard you drive it — a linear medium disperses what you give it. Self-slowing is what traps the energy *and* what quantizes it.

### [~] C3 — the arrow prefers the defects, weakly.
In the structured region, corr(|L|, vorticity) = **0.323** vs corr(|L|, I) = **0.271**. The predicted direction, but a thin margin. **Not a knockout, and it should not be reported as one.** The honest statement: on a complex field the arrow is *no longer* an intensity meter, and it leans toward the defects — but "matter lives *on* the winding" is not yet demonstrated. It is the next experiment, not this one's result.

![complex](figs/fig2_complex_vortices.png)
![real](figs/fig1_real_scalar_kill.png)

---

## The Chain, corrected

The original seven links (`the_chain.md`) claimed: *Hamiltonian caps the speed → information slows information → slow clock = delay line → delay creates the arrow → the arrow is quantized → matter.*

**Link 5 was wrong as stated and is now amended:**

> **5. Delay creates the arrow — but only in a field with internal phase.**
> A(0) ≡ 0 still holds (C₀ is symmetric by construction; no delay, no skew half). But a real scalar field's delay-plane rotation is *forced* to track amplitude: it is single-signed and carries no direction. **The arrow requires at least U(1).** Measured: corr(|L|,I) = 0.81 (real) → 0.14 (complex); sign fraction 0.000 → 0.497.

**And links 3 and 7 are now joined by a causal control rather than a resemblance:**

> **3→7. Self-slowing is what makes the defects.** Not amplitude, not energy, not the potential. Remove `c²=c₀²/(1+β|ψ|²)` and the winding numbers do not form: 402 → 0, robust to a 3× amplitude drive. *The mechanism that makes a medium get in its own way is the mechanism that quantizes it.*

Put together, the corrected core of the Chain is one sentence:

> **A field that slows itself, and has a phase to wind, makes countable things.**
> Take away the self-slowing: no things. Take away the phase: things with no arrow, no chirality, no address — brightness without identity.

---

## Reproduce

```bash
pip install numpy scipy matplotlib
python experiments/arrow_field_test.py      # real scalar: the two kills + the β control
python experiments/complex_phiworld.py      # complex ψ: decoupling, chirality, 402 vs 0
```

Every registered prediction is written in the docstring of the file that tests it, **before** the numbers. `results/*.json` holds the raw output; nothing in a figure is absent from a print-out.

---

## Ledger

**[V] Verified:** arrow decouples from intensity only with phase (0.81→0.14); chirality requires phase (signfrac 0.000→0.497); self-slowing generates topological defects (402 vs 0, amplitude-controlled); self-slowing is required for the field to hold amplitude at all (σ saturates at 0.36 without it); the skew half of the lag-covariance is the energy flux (⟨φ̇∇φ⟩, derived and used).

**[K] Killed:** the hollow ring, by two independent mechanisms, both mine; the Chiral Eye as a meaningful observable on a real scalar field; Chain link 5 as originally stated.

**[~] Weak:** the arrow leans toward the defects rather than the crests (0.323 vs 0.271) — right direction, thin margin, **not a result yet**.

**[B] Still a bet:** that the winding spectrum bears any relation to a *physical* particle spectrum. Nothing here touches that, and Volovik's rule still binds — this buys kinematics (delay, arrows, quantized defects, stability), never dynamics. "Matter" means *stable localized addressable structure*, not the Standard Model.

**Open seam:** the exponent. phiworld says c²/c₀² = (1+β|ψ|²)⁻¹; the Γ-shell Clockfield says Γ = (1+τβ)⁻². Same family, different power. Which, and why? Still unsettled, still the unification's real number.

---

*The prediction I was proudest of was wrong. The control I threw in out of caution turned out to be the discovery. That has happened before in this program and it will happen again — it is what the ledger is for.*
