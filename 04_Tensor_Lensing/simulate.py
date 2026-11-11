import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.interpolate import interp1d
import warnings; warnings.filterwarnings("ignore")

N=128; L=100.0; dx=L/N; x=np.linspace(-L/2,L/2,N,endpoint=False)
X,Y,Z = np.meshgrid(x,x,x,indexing='ij'); r = np.sqrt(X**2+Y**2+Z**2)+1e-6
lam=2.0; mu=1.0; rho0=1.0; sigma=1.5
rho_strain = 2.5*np.exp(-r**2/(2*sigma**2))

kx = 2*np.pi*np.fft.fftfreq(N,d=dx); KX,KY,KZ = np.meshgrid(kx,kx,kx,indexing='ij')
K2 = KX**2+KY**2+KZ**2; K2[0,0,0]=1e-10
rho_k = np.fft.fftn(rho_strain); rho_k[0,0,0] = 0 
Phi = np.real(np.fft.ifftn(-rho_k/((lam+2*mu)*K2)))
cs2 = (lam + 2 * mu) / rho0
g00 = -(1.0 + 2.0 * Phi / cs2) 
grr = 1.0 / (1.0 + 2.0 * Phi / cs2 + 1e-6)

r_bins = np.linspace(sigma*1.0, L/4.0, 100); g00_r, grr_r = [], []
for i in range(len(r_bins)-1):
    mask = (r>=r_bins[i]) & (r<r_bins[i+1])
    if np.any(mask): g00_r.append(np.mean(g00[mask])); grr_r.append(np.mean(grr[mask]))
r_c = (r_bins[:-1]+r_bins[1:])/2
g00_i = interp1d(r_c, g00_r, kind='cubic', fill_value="extrapolate")
grr_i = interp1d(r_c, grr_r, kind='cubic', fill_value="extrapolate")

R_cut = 8.0
idx_cut = np.argmin(np.abs(r_c - R_cut))
r_cut_val = r_c[idx_cut]
A_cut = -g00_i(r_cut_val)
M_eff = r_cut_val * (1.0 - A_cut) / 2.0

def A_r(r_val):
    if r_val >= R_cut: return 1.0 - 2.0 * M_eff / r_val
    return -g00_i(r_val)

def B_r(r_val):
    if r_val >= R_cut: return 1.0 / (1.0 - 2.0 * M_eff / r_val)
    return grr_i(r_val)

def defl(b):
    def f(r_val): return A_r(r_val) / r_val**2 - 1 / b**2
    r_scan = np.linspace(0.5, max(5*b, 20.0), 1000)
    f_scan = np.array([f(r_val) for r_val in r_scan])
    sign_changes = np.where(np.diff(np.sign(f_scan)) != 0)[0]
    if len(sign_changes) == 0: return np.nan
    idx = sign_changes[-1]
    try: r0 = brentq(f, r_scan[idx], r_scan[idx+1], xtol=1e-12)
    except ValueError: return np.nan
    A0 = A_r(r0)
    def integrand_u(u):
        r_val = 1.0 / u
        A = A_r(r_val); B = B_r(r_val)
        val = 1 - A * (b * u)**2
        if val <= 1e-12: return 0.0
        return b * np.sqrt(A * B) / np.sqrt(val)
    u0 = 1.0 / r0
    integral, _ = quad(integrand_u, 1e-10, u0 - 1e-10, limit=200)
    return 2 * integral - np.pi

b_vals = np.linspace(2.0, 25.0, 25); alphas = np.array([defl(b) for b in b_vals])

fig, ax = plt.subplots(1,2, figsize=(15,6))
ax[0].plot(r_c, -np.array(g00_r), 'bo-'); ax[0].plot(r_c, grr_r, 'ro--'); ax[0].axhline(1.0, color='k', ls=':')
ax[0].axvline(R_cut, color='green', linestyle='--', label='R_cut')
ax[0].set_title('(a) Effective Acoustic Metric Profiles'); ax[0].legend(['-g_00', 'g_rr', 'Flat Limit', 'R_cut']); ax[0].grid(True)
mask = ~np.isnan(alphas)
ax[1].loglog(b_vals[mask], np.abs(alphas[mask]), 'go-'); ax[1].loglog(b_vals, 4*M_eff/b_vals, 'k--')
ax[1].set_title('(b) Light Deflection Angle'); ax[1].legend(['Simulation', 'GR (4M_eff/b)']); ax[1].grid(True, which='both')
plt.tight_layout(); plt.savefig('tensor_lensing_final_curves.png', dpi=150)
