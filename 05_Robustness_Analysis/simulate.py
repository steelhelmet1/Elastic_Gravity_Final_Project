import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.interpolate import interp1d
import warnings; warnings.filterwarnings("ignore")

resolutions = [128, 256]
convergence_results = {}

for N in resolutions:
    L = 100.0; dx = L / N; x = np.linspace(-L/2, L/2, N, endpoint=False)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij'); r = np.sqrt(X**2 + Y**2 + Z**2) + 1e-6
    lam = 2.0; mu = 1.0; rho0 = 1.0; sigma = 1.5
    rho_strain = 2.5 * np.exp(-r**2 / (2 * sigma**2))
    kx = 2 * np.pi * np.fft.fftfreq(N, d=dx); KX, KY, KZ = np.meshgrid(kx, kx, kx, indexing='ij')
    K2 = KX**2 + KY**2 + KZ**2; K2[0, 0, 0] = 1e-10
    rho_k = np.fft.fftn(rho_strain); rho_k[0,0,0] = 0 
    Phi = np.real(np.fft.ifftn(-rho_k / ((lam + 2 * mu) * K2)))
    cs2 = (lam + 2 * mu) / rho0
    g00 = -(1.0 + 2.0 * Phi / cs2)
    grr = 1.0 / (1.0 + 2.0 * Phi / cs2 + 1e-6)
    
    r_bins = np.linspace(sigma * 1.0, L / 4.0, 100)
    r_c_list, g00_r, grr_r = [], [], []
    for i in range(len(r_bins)-1):
        mask = (r >= r_bins[i]) & (r < r_bins[i+1])
        if np.any(mask): 
            r_c_list.append((r_bins[i] + r_bins[i+1]) / 2)
            g00_r.append(np.mean(g00[mask]))
            grr_r.append(np.mean(grr[mask]))
    r_c = np.array(r_c_list)
    convergence_results[N] = (r_c, np.array(g00_r))

lame_ratios = [0.5, 1.0, 2.0, 5.0]
sensitivity_alphas = {}

N_std = 128; L_std = 100.0; dx_std = L_std / N_std
x_std = np.linspace(-L_std/2, L_std/2, N_std, endpoint=False)
X_s, Y_s, Z_s = np.meshgrid(x_std, x_std, x_std, indexing='ij'); r_s = np.sqrt(X_s**2 + Y_s**2 + Z_s**2) + 1e-6
rho_s = 2.5 * np.exp(-r_s**2 / (2 * sigma**2))
kx_s = 2 * np.pi * np.fft.fftfreq(N_std, d=dx_std); KX_s, KY_s, KZ_s = np.meshgrid(kx_s, kx_s, kx_s, indexing='ij')
K2_s = KX_s**2 + KY_s**2 + KZ_s**2; K2_s[0, 0, 0] = 1e-10

b_vals = np.linspace(8.0, 20.0, 20)

for ratio in lame_ratios:
    lam_val = ratio * 1.0; mu_val = 1.0
    rho_k_s = np.fft.fftn(rho_s); rho_k_s[0,0,0] = 0 
    Phi_ratio = np.real(np.fft.ifftn(-rho_k_s / ((lam_val + 2 * mu_val) * K2_s)))
    cs2_v = (lam_val + 2 * mu_val) / rho0
    g00_v = -(1.0 + 2.0 * Phi_ratio / cs2_v)
    grr_v = 1.0 / (1.0 + 2.0 * Phi_ratio / cs2_v + 1e-6)
    
    r_b = np.linspace(sigma * 1.0, L_std / 4.0, 100) 
    r_rc_list, g0_l, gr_l = [], [], []
    for i in range(len(r_b)-1):
        msk = (r_s >= r_b[i]) & (r_s < r_b[i+1])
        if np.any(msk): 
            r_rc_list.append((r_b[i] + r_b[i+1]) / 2)
            g0_l.append(np.mean(g00_v[msk]))
            gr_l.append(np.mean(grr_v[msk]))
    r_rc = np.array(r_rc_list)
    
    g0_i = interp1d(r_rc, g0_l, kind='cubic', fill_value="extrapolate")
    gr_i = interp1d(r_rc, gr_l, kind='cubic', fill_value="extrapolate")
    
    R_cut = 8.0
    idx_cut = np.argmin(np.abs(r_rc - R_cut))
    r_cut_val = r_rc[idx_cut]
    A_cut = -g0_i(r_cut_val)
    M_eff_ratio = r_cut_val * (1.0 - A_cut) / 2.0
    
    def defl_test(b):
        def A_r(r):
            if r >= R_cut: return 1.0 - 2.0*M_eff_ratio/r
            if r < r_rc[0]: return -g0_i(r_rc[0]) 
            return -g0_i(r)
            
        def B_r(r):
            if r >= R_cut: return 1.0 / (1.0 - 2.0*M_eff_ratio/r)
            if r < r_rc[0]: return gr_i(r_rc[0])
            return gr_i(r)
        
        def f(r): return A_r(r)/r**2 - 1/b**2
        
        r_scan = np.linspace(3.0, max(5*b, 20.0), 2000)
        f_scan = np.array([f(r) for r in r_scan])
        
        if np.max(f_scan) < 0: return np.nan 
            
        sign_changes = np.where(np.diff(np.sign(f_scan)) != 0)[0]
        if len(sign_changes) == 0: return np.nan
        
        idx = sign_changes[-1]
        try: 
            r0 = brentq(f, r_scan[idx], r_scan[idx+1], xtol=1e-10)
        except ValueError: 
            return np.nan
        
        A0 = A_r(r0)
        
        def integrand_theta(theta):
            sin_t = np.sin(theta); cos_t = np.cos(theta)
            if sin_t <= 1e-10: return 0.0
            r = r0 / sin_t
            A = A_r(r); B = B_r(r)
            val = cos_t**2 + (1 - A / A0) * sin_t**2
            if val <= 1e-14: return 0.0
            return (1.0 / np.sqrt(A0)) * np.sqrt(A * B) * cos_t / np.sqrt(val)
            
        integral, _ = quad(integrand_theta, 0, np.pi/2, limit=500)
        return 2 * integral - np.pi
        
    alphas_ratio = [defl_test(b) for b in b_vals]
    sensitivity_alphas[ratio] = np.array(alphas_ratio)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
rc_128, g00_128 = convergence_results[128]; rc_256, g00_256 = convergence_results[256]
axes[0].plot(rc_128, -g00_128, 'bo-', label='N = 128 Grid')
axes[0].plot(rc_256, -g00_256, 'r--x', label='N = 256 Grid (High-Res)')
axes[0].set_title(r'(a) Grid Convergence Analysis'); axes[0].set_xlabel(r'Radial Distance \(r\)'); axes[0].set_ylabel(r'\(-g_{00}\) Profile')
axes[0].legend(); axes[0].grid(True, alpha=0.3)

for i, ratio in enumerate(lame_ratios):
    alfs = sensitivity_alphas[ratio]; msk = ~np.isnan(alfs)
    b_plot = b_vals[msk]
    a_plot = np.abs(alfs[msk])
    
    if len(b_plot) > 0:
        axes[1].loglog(b_plot, a_plot, 'o-', label=r'Lamé Ratio \(\lambda/\mu = ' + str(ratio) + r'\)')
        mid_idx = len(b_plot) // 2
        b_fit = b_plot[mid_idx]
        a_fit = a_plot[mid_idx] * b_fit
        axes[1].loglog(b_plot, a_fit / b_plot, 'k:', linewidth=1.5, alpha=0.5) 

axes[1].set_title(r'(b) Parameter Sensitivity (\(\lambda/\mu\) variation)')
axes[1].set_xlabel(r'Impact Parameter \(b\)')
axes[1].set_ylabel(r'Deflection Angle \(\alpha(b)\)')
axes[1].legend(); axes[1].grid(True, which='both', alpha=0.3)
plt.tight_layout(); plt.savefig('robustness_analysis_results.png', dpi=200)
