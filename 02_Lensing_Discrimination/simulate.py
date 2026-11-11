import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")

M=0.5; rho0=1.0; cs0=1.0
profiles = {
    'Sphere': lambda r: (rho0 + M * np.exp(-r**2), 0.0),
    'Ring': lambda r: (rho0 + M * np.exp(-(r - 2.0)**2), 0.0),
    'Cylinder': lambda r: (rho0, np.sqrt(M / max(r, 1e-6))),
    'Open Sink': lambda r: (rho0, -np.sqrt(2 * M / max(r, 1e-6))),
    'Dipole': lambda r: (rho0, M / max(r**2, 1e-6)),
    'Knot': lambda r: (rho0 + M * np.exp(-(r - 3.0)**2) * (1 + 0.5*np.cos(3*r)), 0.0) 
}

def get_AB(r, func):
    rho, v = func(r); cs = np.sqrt(rho); denom = cs**2 - v**2
    A = (denom * (rho / cs)) / (rho0 / cs0)
    B = ((rho / cs) / denom) / (rho0 / cs0)
    return A, B

def angle(b, func):
    def f(r):
        A, _ = get_AB(r, func)
        return A / r**2 - 1 / b**2
        
    r_scan = np.logspace(-4, np.log10(max(50*b, 100)), 2000)
    f_scan = np.array([f(r) for r in r_scan])
    sign_changes = np.where(np.diff(np.sign(f_scan)) != 0)[0]
    
    if len(sign_changes) == 0: return np.nan
    idx = sign_changes[-1]
    try: r0 = brentq(f, r_scan[idx], r_scan[idx + 1], xtol=1e-14)
    except ValueError: return np.nan
        
    A0, _ = get_AB(r0, func)
    
    def integrand_theta(theta):
        sin_t = np.sin(theta); cos_t = np.cos(theta)
        if sin_t <= 1e-10: return 0.0
        r = r0 / sin_t
        A, B = get_AB(r, func)
        val = cos_t**2 + (1 - A / A0) * sin_t**2
        if val <= 1e-14: return 0.0
        return (1.0 / np.sqrt(A0)) * np.sqrt(A * B) * cos_t / np.sqrt(val)
        
    integral, _ = quad(integrand_theta, 0, np.pi/2, limit=500)
    return 2 * integral - np.pi

b_vals = np.logspace(0.5, 2, 30)
colors = ['blue', 'green', 'purple', 'red', 'orange', 'brown']
markers = ['o', 's', '^', 'D', 'v', '*']

fig, ax = plt.subplots(1, 2, figsize=(16, 6))
for i, (name, func) in enumerate(profiles.items()):
    alphas = np.array([angle(b, func) for b in b_vals])
    mask = ~np.isnan(alphas)
    if np.any(mask):
        ax[0].loglog(b_vals[mask], np.abs(alphas[mask]), marker=markers[i], color=colors[i], label=name)
        ax[1].semilogx(b_vals[mask], alphas[mask] * b_vals[mask] / M, marker=markers[i], color=colors[i], label=name)

ax[0].loglog(b_vals, 4*M/b_vals, 'k--', linewidth=2, label='GR (4M/b)')
ax[1].axhline(4, color='k', linestyle='--', linewidth=2, label='GR coeff = 4')
ax[1].axhline(0, color='gray', linestyle=':', linewidth=1)
ax[0].set_ylim(1e-10, 10)

ax[0].set_xlabel('Impact parameter b'); ax[0].set_ylabel(r'|Deflection Angle \(\alpha\)|')
ax[0].set_title('(a) Deflection Angle'); ax[0].legend(); ax[0].grid(True, which='both', alpha=0.3)
ax[1].set_xlabel('b'); ax[1].set_ylabel(r'\(\alpha \cdot b / M\)')
ax[1].set_title('(b) Lensing Coefficient'); ax[1].legend(); ax[1].grid(True, which='both', alpha=0.3)

plt.tight_layout(); plt.savefig('exact_math_results_final.png', dpi=150)
