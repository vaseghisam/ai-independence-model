# Model specification

This technical note specifies the calculations in this repository. It is not a copy of the accompanying article.

## Variables and units

| Symbol | Meaning | Code |
| --- | --- | --- |
| $R$ | Recoverable opportunity in accessible human intellectual material | state 0 |
| $C$ | Capability index for the specified domain and task | state 1 |
| $J_H,J_A$ | Useful intellectual input rates from human material and AI investigation | `J_H`, `J_A` |
| $E_H,E_M$ | Effective observation rates delivered through humans and machines | `E_H`, `E_M` |
| $p_H$ | Replenishment rate of recoverable human-source opportunity | `p_H` |
| $B$ | Budget remaining after observation costs | `B` |
| $s$ | Fraction of that budget assigned to AI investigation | `s` |

Time and learning quantities use normalised, task-specific model units. $R$ has learning units; $J$, $E$ and $p_H$ have learning units per model time; $B$ has resource units per model time. The gain coefficients convert learning inputs to capability change. The capability index is not a percentage or a general intelligence scale.

## Equations

$$
\dot R=p_H-J_H,\qquad y_H=a_H\frac{R}{R+K}.
$$

$$
E=E_H+E_M,\qquad G(E)=1-\lambda+\lambda\frac{E}{E+E_0}.
$$

$$
y_A=q a_A\frac{C^n}{C^n+C_0^n}G(E).
$$

$$
B=B_{\mathrm{tot}}-c_HE_H-c_ME_M\geq0,
\qquad s=\frac{1}{1+\exp[-\beta(y_A-y_H)]}.
$$

$$
J_H=B(1-s)y_H,\qquad J_A=Bsy_A.
$$

$$
\dot C=\gamma_HJ_H+\gamma_AJ_A+\gamma_E(E_H+E_M)-\delta C.
$$

The code raises an error if specified observation costs exceed the budget. Extra ODE states integrate $J_H,J_A,E_H,E_M,p_H$ for numerical accounting; they do not change the dynamics of $R,C$.

The parameter $q$ combines correctness, novelty to the system and usefulness. It does not measure novelty to human knowledge. Observations, objectives and infrastructure are prescribed; the model does not simulate independent sensor construction or the formation of goals.

## Shared parameters

Initial conditions are $R(0)=6$ and $C(0)=0.15$. The horizon is 100 model-time units.

| Symbols | Values | Code fields |
| --- | --- | --- |
| $B_{\mathrm{tot}},a_H,K$ | 1, 1, 1 | `budget`, `a_h`, `K` |
| $C_0,n,\beta$ | 0.8, 2, 8 | `c_mid`, `n`, `beta` |
| $\gamma_H,\gamma_A,\gamma_E$ | 0.09, 0.09, 0.03 | `gamma_h`, `gamma_a`, `gamma_e` |
| $\delta,E_0$ | 0.015, 0.2 | `delta`, `e_mid` |
| $c_H,c_M$ | 0.6, 0.2 | `cost_h`, `cost_m` |

## Six scenarios

In the code, `empirical` denotes $\lambda$ and `p_h` denotes the initial replenishment rate.

| Case | $a_A$ | $q$ | $\lambda$ | $p_H$ | $E_H$ | $E_M$ |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1 | 0.9 | 0 | 0.015 | 0 | 0 |
| B | 1.8 | 0.9 | 1 | 0.015 | 0.35 | 0.03 |
| C | 1.8 | 0.9 | 1 | 0.015 | Prescribed decrease from 0.35 | Prescribed increase from 0.03 towards 0.60 |
| D | 1 | 0.08 | 0 | 0.15 | 0.05 | 0 |
| E | 1 | 0.9 | 0 | 0.015 before time 35; 0.75 thereafter | 0 | 0 |
| F | 1.8 | 0.9 | 1 | 0.015 | 0.35 before time 40; 0 thereafter | 0.03 before time 40; 0 thereafter |

For C, define

$$
L(t)=\frac{1}{1+\exp[-(t-35)/5]},\qquad
u(t)=\frac{L(t)-L(0)}{1-L(0)}.
$$

Then $E_H(t)=0.35[1-u(t)]$ and $E_M(t)=0.03+0.57u(t)$. The implementation clips $u$ to $[0,1]$, which does not alter it over the simulated interval $0\leq t\leq100$.

## Reported shares

$$
\phi_I=\frac{J_H}{J_H+J_A},\qquad
\phi_H=\frac{J_H+E_H}{J_H+J_A+E_H+E_M}.
$$

The CSV fields are `human_intellectual_share` and `human_direct_share`. Where a denominator is zero, the stored share is zero by computational convention; there is then no corresponding input flow from which to infer independence. These fractions do not measure historical human contribution or the value of human activity.

## Removal experiments

Every intervention begins at time 60; inherited capability is retained.

- **B and C:** set $E_H=0$, $s=1$ and $p_H=0$. Thus $J_H=0$ and all remaining budget goes to AI investigation. $E_M$ continues according to its original scenario. Existing human-source stock is no longer consulted.
- **A:** set $\gamma_A=0$. AI results can still be produced, but they no longer increase capability. The original allocation rule is retained.

The code fields are `human_stop` and `gamma_a_stop`. The final-capability ratio is intervention $C(100)$ divided by baseline $C(100)$. Alternative reallocation rules can change that ratio.

## Sensitivity calculation

All settings match A except $q$ and $p_H$. The grid contains 61 values of $q$ from 0 to 1 and 61 values of $p_H$ from 0 to 0.5. A vectorised RK4 integration uses a step of 0.025 up to time 100. The figure plots $100\phi_I(100)$ and contours at 5% and 50%; these are rate shares, not scenario probabilities.

## Numerical implementation

The adaptive solver integrates separate segments at each imposed discontinuity. Its derivative uses the interior one-sided value at segment endpoints. The standard calculation uses relative tolerance $10^{-8}$, absolute tolerance $10^{-10}$ and maximum step 0.25. The refined calculation uses $10^{-10}$, $10^{-12}$ and maximum step 0.10.

Baseline CSVs sample every 0.1 model-time unit; standalone figure CSVs sample every 0.05. The standalone F plot includes both one-sided flow values at time 40 to draw its discontinuity vertically. Both rows have the same continuous state $R,C$.

For fixed human yield and observations, write $Y_A=q a_AG(E)$. When $Y_A>y_H>0$, equality of the two yields occurs at

$$
C_* = C_0\left(\frac{y_H}{Y_A-y_H}\right)^{1/n}.
$$

The solver checks this identity at selected positive stocks. It also checks resource balance and $R(t)=R(0)+\int p_H\,dt-\int J_H\,dt$, along with the boundary cases described in the README. Full numerical records are in `data/verification.json`.
