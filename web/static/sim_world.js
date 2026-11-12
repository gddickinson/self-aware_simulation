// World of the simulation: zones, day/night cycle, weather and ambient objects. Port of modules/expanded_world.py
// and ambient_objects.py (Zone, ExpandedWorld, AmbientObject: the update logic; drawing lives in sim_render.js). Every random draw happens
// in the same order as the Python code, through the shared PyRandom `R` passed in.
export const TIMES = ['DAWN', 'MORNING', 'NOON', 'AFTERNOON', 'EVENING', 'NIGHT', 'MIDNIGHT'];
export const WEATHERS = ['CLEAR', 'CLOUDY', 'RAINY', 'STORMY', 'FOG', 'GLITCH_STORM'];
const TAU = 2 * Math.PI;

export class Zone {
  constructor(R, id, name, type, position, size, color) {
    Object.assign(this, { id, name, type, position, size, color, discovery: 0 });
    const p = this.props = {
      safety: R.uniform(0.3, 1.0), inspiration: R.uniform(0.2, 0.9),
      transcendence_potential: R.uniform(0.1, 0.5), reality_stability: R.uniform(0.7, 1.0),
    };
    if (type === 'MYSTERIOUS') { p.inspiration += 0.3; p.transcendence_potential += 0.4; p.reality_stability -= 0.3; }
    else if (type === 'GLITCH') { p.reality_stability = R.uniform(0.1, 0.4); p.transcendence_potential += 0.5; }
    else if (type === 'TRANSCENDENCE') { p.transcendence_potential = R.uniform(0.8, 1.0); p.reality_stability = R.uniform(0.2, 0.5); }
  }
  contains(x, y) { return x >= this.position[0] && x < this.position[0] + this.size[0] && y >= this.position[1] && y < this.position[1] + this.size[1]; }
}

export class AmbientObject {
  constructor(R, type, position) {
    this.R = R; this.type = type; this.position = [position[0], position[1]];
    this.lifetime = R.randint(10000, 30000);
    const ri = (a, b) => R.randint(a, b), ru = (a, b) => R.uniform(a, b);
    if (type === 'cloud') {
      this.size = ri(40, 100); this.speed = ru(5, 15); this.direction = ru(0, TAU); this.color = [255, 255, 255, ri(100, 180)];
    } else if (type === 'bird') {
      this.size = ri(5, 15); this.speed = ru(20, 50); this.direction = ru(0, TAU); this.color = [50, 50, 50];
      this.flap_speed = ru(0.1, 0.3); this.flap_state = 0;
    } else if (type === 'leaf') {
      this.size = ri(3, 8); this.speed = ru(10, 30); this.direction = ru(0, TAU);
      const r = ri(50, 150), g = ri(100, 200); this.color = [r, g, 50];
      this.spin_speed = ru(0.05, 0.2); this.spin = 0;
    } else if (type === 'raindrop') {
      this.size = ri(1, 3); this.speed = ru(50, 100); this.direction = Math.PI / 2 + ru(-0.2, 0.2);
      this.color = [100, 100, 255, ri(100, 200)]; this.length = ri(5, 15);
    } else if (type === 'glitch') {
      this.size = ri(5, 20); this.speed = ru(10, 30); this.direction = ru(0, TAU);
      const r = ri(0, 255), g = ri(0, 255), b = ri(0, 255); this.color = [r, g, b]; this.glitch_timer = 0;
    } else {
      this.size = ri(2, 8); this.speed = ru(10, 40); this.direction = ru(0, TAU);
      const r = ri(100, 255), g = ri(100, 255), b = ri(100, 255); this.color = [r, g, b];
    }
  }

  update(dt) {
    const R = this.R;
    this.lifetime -= dt;
    if (this.lifetime <= 0) return false;      // (the world never removes expired objects; they just stop moving)
    this.position[0] += Math.cos(this.direction) * this.speed * dt / 1000;
    this.position[1] += Math.sin(this.direction) * this.speed * dt / 1000;
    if (this.type === 'cloud') {
      if (R.random() < 0.02) this.direction += R.uniform(-0.1, 0.1);
    } else if (this.type === 'bird') {
      this.flap_state = (this.flap_state + this.flap_speed * dt / 1000) % TAU;
      if (R.random() < 0.05) this.direction += R.uniform(-0.5, 0.5);
    } else if (this.type === 'leaf') {
      this.spin = (this.spin + this.spin_speed * dt / 1000) % TAU;
      if (R.random() < 0.1) this.direction += R.uniform(-0.3, 0.3);
    } else if (this.type === 'glitch') {
      this.glitch_timer += dt;
      if (this.glitch_timer > 200) {
        this.glitch_timer = 0;
        this.direction = R.uniform(0, TAU);
        const r = R.randint(0, 255), g = R.randint(0, 255), b = R.randint(0, 255); this.color = [r, g, b];
      }
    }
    return true;
  }
}

export class World {
  constructor(R, log, width = 5000, height = 3000) {
    Object.assign(this, { R, log, width, height });
    this.time_of_day = 'MORNING'; this.day_cycle_duration = 24000; this.time_cycle_timer = 0; this.day_count = 1;
    this.weather = 'CLEAR'; this.weather_duration = 30000; this.weather_timer = 0;
    this.camera_pos = [0, 0]; this.camera_target = [0, 0]; this.camera_speed = 0.1;
    const W = width, H = height, h = Math.floor;
    this.zones = [
      new Zone(R, 'central_plaza', 'Central Plaza', 'COMMERCIAL', [h(W / 2) - 300, h(H / 2) - 300], [600, 600], [120, 120, 160]),
      new Zone(R, 'residential_east', 'Residential District', 'RESIDENTIAL', [h(W / 2) + 350, h(H / 2) - 400], [800, 800], [100, 150, 100]),
      new Zone(R, 'park_west', 'Westside Park', 'RECREATIONAL', [h(W / 2) - 1200, h(H / 2) - 300], [800, 600], [50, 180, 50]),
      new Zone(R, 'mystery_zone', 'Whispering Woods', 'MYSTERIOUS', [h(W / 2) - 400, h(H / 2) + 400], [500, 500], [70, 40, 90]),
      new Zone(R, 'glitch_zone', 'Reality Fault', 'GLITCH', [h(W / 2) + 800, h(H / 2) + 600], [300, 300], [50, 50, 50]),
      new Zone(R, 'transcendence_zone', 'Awakening Nexus', 'TRANSCENDENCE', [h(W / 2) - 1000, h(H / 2) + 600], [400, 400], [180, 180, 255]),
    ];
    this.reality_stability = 1.0; this.transcendence_threshold = 0.8;
    this.ambient_objects = [];
  }

  update(dt) {
    const R = this.R;
    this.time_cycle_timer += dt;
    if (this.time_cycle_timer >= this.day_cycle_duration) {
      this.time_cycle_timer = 0; this.day_count += 1;
      this.log('INFO', `New day: ${this.day_count}`);
    }
    const p = this.time_cycle_timer / this.day_cycle_duration;
    this.time_of_day = p < 0.15 ? 'DAWN' : p < 0.3 ? 'MORNING' : p < 0.45 ? 'NOON' : p < 0.6 ? 'AFTERNOON'
      : p < 0.75 ? 'EVENING' : p < 0.9 ? 'NIGHT' : 'MIDNIGHT';
    this.weather_timer += dt;
    if (this.weather_timer >= this.weather_duration) { this.weather_timer = 0; this.changeWeather(); }
    for (const o of this.ambient_objects) o.update(dt);
    this.ambient_objects = this.ambient_objects.filter(o => this.inBounds(o.position));
    if (R.random() < 0.01) this.spawnAmbient();
    this.camera_pos[0] += (this.camera_target[0] - this.camera_pos[0]) * this.camera_speed;
    this.camera_pos[1] += (this.camera_target[1] - this.camera_pos[1]) * this.camera_speed;
  }

  changeWeather() {
    const R = this.R;
    const w = { CLEAR: 0.4, CLOUDY: 0.3, RAINY: 0.15, STORMY: 0.05, FOG: 0.08, GLITCH_STORM: 0.02 };
    if (this.reality_stability < 0.6) w.GLITCH_STORM += 0.15;
    const next = R.choices(WEATHERS, WEATHERS.map(k => w[k]));
    if (next !== this.weather) {
      this.weather = next;
      this.log('INFO', `Weather changed to ${next}`);
      const span = { CLEAR: [25000, 45000], CLOUDY: [20000, 35000], RAINY: [15000, 30000], STORMY: [10000, 20000],
        FOG: [20000, 40000], GLITCH_STORM: [10000, 15000] }[next];
      this.weather_duration = R.randint(span[0], span[1]);
    }
  }

  spawnAmbient() {
    const R = this.R;
    let type = R.choice(['cloud', 'bird', 'leaf', 'particle']);
    if (this.weather === 'CLOUDY') type = R.random() < 0.7 ? 'cloud' : type;
    else if (this.weather === 'RAINY') type = R.random() < 0.6 ? 'raindrop' : type;
    else if (this.weather === 'GLITCH_STORM') type = R.random() < 0.8 ? 'glitch' : type;
    const pos = this.spawnPosition();
    this.ambient_objects.push(new AmbientObject(R, type, pos));
  }

  spawnPosition() {
    const R = this.R;
    const edge = R.randint(0, 3);
    const left = Math.trunc(this.camera_pos[0]), top = Math.trunc(this.camera_pos[1]);
    const right = left + 1200, bottom = top + 800;
    if (edge === 0) return [R.randint(left, right), top - 50];
    if (edge === 1) return [right + 50, R.randint(top, bottom)];
    if (edge === 2) return [R.randint(left, right), bottom + 50];
    return [left - 50, R.randint(top, bottom)];
  }

  inBounds(p) {
    const m = 100, l = this.camera_pos[0] - m, t = this.camera_pos[1] - m, r = l + 1200 + m * 2, b = t + 800 + m * 2;
    return p[0] >= l && p[0] <= r && p[1] >= t && p[1] <= b;
  }

  zoneAt(x, y) { return this.zones.find(z => z.contains(x, y)) || null; }
  // get_zone_at_position(): pygame.Rect.collidepoint truncates the point's coordinates toward zero.
  zoneAtPoint(p) { return this.zoneAt(Math.trunc(p[0]), Math.trunc(p[1])); }
}
