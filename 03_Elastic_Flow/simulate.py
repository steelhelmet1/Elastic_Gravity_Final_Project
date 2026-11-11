import numpy as np
import matplotlib.pyplot as plt
N=100; L=20.0; dx=L/N; x=np.linspace(-L/2,L/2,N); X,Y=np.meshgrid(x,x); r=np.sqrt(X**2+Y**2)+1e-6
S = 1.0*np.exp(-r**2/(2*1.5**2))
kx = 2*np.pi*np.fft.fftfreq(N, d=dx); KX, KY = np.meshgrid(kx, kx); K2 = KX**2 + KY**2; K2[0,0]=1e-10
S_k = np.fft.fft2(S); S_k[0,0] = 0 
Phi = np.real(np.fft.ifft2(-S_k/K2))
vy, vx = np.gradient(Phi, dx, dx)
fig, ax = plt.subplots(figsize=(10,8))
im = ax.imshow(Phi, extent=[-L/2,L/2,-L/2,L/2], origin='lower', cmap='viridis')
ax.streamplot(x, x, -vx, -vy, color='white', density=1.5)
ax.set_title('Flow Field in Elastic Medium\n(v = -∇Φ)'); plt.colorbar(im, ax=ax)
plt.tight_layout(); plt.savefig('elastic_flow_link.png', dpi=150)
