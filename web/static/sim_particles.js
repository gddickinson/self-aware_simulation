// Particle effects of world events: port of modules/particle_effects.py (ParticleEffect) with the same draws.
const TAU = 2 * Math.PI;

export class ParticleEffect {
  constructor(R, position, type, color = [255, 255, 255], duration = 2000, count = 30) {
    Object.assign(this, { position: [position[0], position[1]], type, color, duration, elapsed: 0, particles: [] });
    const P = this.particles, [px, py] = this.position;
    if (type === 'burst' || !['implosion', 'spiral', 'rain', 'code'].includes(type)) {
      const [s0, s1, z0, z1, l0] = type === 'burst' ? [50, 200, 2, 6, 0.5] : [20, 100, 2, 5, 0.6];
      for (let i = 0; i < count; i++) {
        const a = R.uniform(0, TAU), sp = R.uniform(s0, s1);
        const size = R.uniform(z0, z1);
        P.push({ position: [px, py], velocity: [Math.cos(a) * sp, Math.sin(a) * sp], size, life: R.uniform(l0, 1.0) });
      }
    } else if (type === 'implosion') {
      for (let i = 0; i < count; i++) {
        const a = R.uniform(0, TAU), d = R.uniform(100, 300), sp = R.uniform(50, 150);
        const sx = px + Math.cos(a) * d, sy = py + Math.sin(a) * d;
        const vx = (px - sx) / (duration / 1000) * sp / 100, vy = (py - sy) / (duration / 1000) * sp / 100;
        const size = R.uniform(2, 6);
        P.push({ position: [sx, sy], velocity: [vx, vy], size, life: R.uniform(0.5, 1.0) });
      }
    } else if (type === 'spiral') {
      for (let i = 0; i < count; i++) {
        const a = (i / count) * Math.PI * 2, d = R.uniform(10, 50);
        const av = R.uniform(1, 3) * R.choice([-1, 1]), size = R.uniform(2, 5);
        P.push({ position: [px + Math.cos(a) * d, py + Math.sin(a) * d], angle: a, distance: d, angular_velocity: av, size, life: R.uniform(0.7, 1.0) });
      }
    } else if (type === 'rain') {
      for (let i = 0; i < count; i++) {
        const sx = px + R.uniform(-100, 100), sy = py - R.uniform(50, 150);
        const vx = R.uniform(-5, 5), vy = R.uniform(50, 150), size = R.uniform(1, 4);
        P.push({ position: [sx, sy], velocity: [vx, vy], size, life: R.uniform(0.6, 1.0) });
      }
    } else {
      for (let i = 0; i < count; i++) {
        const ch = R.choice('01010101'), sx = px + R.uniform(-100, 100), sy = py - R.uniform(0, 200);
        const vy = R.uniform(30, 80), size = R.uniform(12, 24);
        P.push({ position: [sx, sy], velocity: [0, vy], character: ch, size, life: R.uniform(0.7, 1.0) });
      }
    }
  }

  update(dt) {
    this.elapsed += dt;
    if (this.elapsed >= this.duration) return false;
    const lifePct = 1.0 - (this.elapsed / this.duration), t = this.type;
    for (const p of this.particles) {
      if (t === 'spiral') {
        p.angle += p.angular_velocity * dt / 1000;
        if (lifePct > 0.5) p.distance += 20 * dt / 1000; else p.distance -= 40 * dt / 1000;
        p.position[0] = this.position[0] + Math.cos(p.angle) * p.distance;
        p.position[1] = this.position[1] + Math.sin(p.angle) * p.distance;
      } else if (t === 'code') {
        p.position[1] += p.velocity[1] * dt / 1000;
      } else if (t === 'burst' || t === 'default' || t === 'rain') {
        p.position[0] += p.velocity[0] * dt / 1000; p.position[1] += p.velocity[1] * dt / 1000;
        if (t === 'rain') p.velocity[1] += 50 * dt / 1000;
        p.velocity[0] *= 0.98; p.velocity[1] *= 0.98;
      } else continue;
      p.life = Math.max(0, p.life - dt / this.duration);
    }
    return true;
  }
}
