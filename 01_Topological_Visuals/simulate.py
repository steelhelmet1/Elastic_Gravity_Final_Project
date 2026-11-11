import numpy as np
import matplotlib.pyplot as plt
N = 300; L = 6.0
x = np.linspace(-L, L, N); y = np.linspace(-L, L, N)
X, Y = np.meshgrid(x, y); r = np.sqrt(X**2 + Y**2) + 1e-6; theta = np.arctan2(Y, X)
def shape_sphere(): return np.exp(-r**2), np.zeros_like(X), np.zeros_like(Y)
def shape_ring(): return np.exp(-(r - 2.0)**2), np.zeros_like(X), np.zeros_like(Y)
def shape_cylinder(): return np.ones_like(X), -1.0/np.sqrt(r)*np.sin(theta), 1.0/np.sqrt(r)*np.cos(theta)
def shape_sink(): return np.ones_like(X), -1.0/np.sqrt(r)*np.cos(theta), -1.0/np.sqrt(r)*np.sin(theta)
def shape_dipole(): return np.ones_like(X), (X**2 - Y**2)/(r**4), (2*X*Y)/(r**4)
def shape_knot():
    rho = np.exp(-(r - 2.0)**2) * (1 + 0.5 * np.sin(3 * theta))
    return rho, -1.0/np.sqrt(r+1)*np.sin(theta), 1.0/np.sqrt(r+1)*np.cos(theta)
shapes = {'1. Sphere': shape_sphere, '2. Ring': shape_ring, '3. Cylinder': shape_cylinder, '4. Open Sink': shape_sink, '5. Dipole': shape_dipole, '6. Knot': shape_knot}
fig, axes = plt.subplots(2, 3, figsize=(20, 12)); axes = axes.flatten()
for i, (name, func) in enumerate(shapes.items()):
    ax = axes[i]; rho, vx, vy = func()
    if i in [0, 1, 5]: im = ax.imshow(rho, extent=[-L, L, -L, L], origin='lower', cmap='inferno'); c = 'red'
    else: im = ax.imshow(np.clip(-1.0/r, 0, 5), extent=[-L, L, -L, L], origin='lower', cmap='viridis'); c = 'cyan'
    if np.max(np.abs(vx)) > 1e-5: ax.streamplot(x, y, vx, vy, color='white', density=1.5, arrowsize=1.5)
    ax.set_title(name, color=c, fontsize=16, fontweight='bold'); ax.set_xticks([]); ax.set_yticks([])
plt.tight_layout(); plt.savefig('all_shapes_final_dashboard.png', dpi=150)
