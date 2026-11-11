import numpy as np
import matplotlib.pyplot as plt
N=1024; L=60.0; dx=L/N; x=np.linspace(-L/2,L/2,N,endpoint=False)
psi0 = (1.0/np.cosh(x/np.sqrt(2))).astype(np.complex128)
k = 2*np.pi*np.fft.fftfreq(N,d=dx); K2 = k**2
def step(psi, dt, nl):
    psi = np.fft.ifft(np.fft.fft(psi)*np.exp(-1j*K2*dt/2))
    psi *= np.exp(1j*nl*np.abs(psi)**2*dt)
    return np.fft.ifft(np.fft.fft(psi)*np.exp(-1j*K2*dt/2))
psi_l, psi_n = psi0.copy(), psi0.copy(); pl, pn = [], []
for i in range(2000):
    psi_l = step(psi_l, 0.01, 0.0); psi_n = step(psi_n, 0.01, 1.0)
    if i%10==0: pl.append(np.max(np.abs(psi_l)**2)); pn.append(np.max(np.abs(psi_n)**2))
t = np.arange(0,2000,10)*0.01
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(t, pl, 'r--', lw=2, label='Linear (Dispersion)'); ax.plot(t, pn, 'b-', lw=2.5, label='Nonlinear (Stable)')
ax.set_title('Dynamical Stability: Linear vs Nonlinear'); ax.legend(); ax.grid(True); ax.set_ylim(0,1.1)
plt.tight_layout(); plt.savefig('true_stable_soliton_fixed.png', dpi=150)
