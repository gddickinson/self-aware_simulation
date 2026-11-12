// Python's `random` module in JavaScript, exactly: CPython's MT19937 seeded from an integer (init_by_array over the
// 32-bit words of abs(seed)) plus random(), uniform(), randrange(), randint(), choice(), choices(weights) and sample()
// with CPython 3.12's algorithms, so the browser draws the same numbers in the same order as the game's Python code.
// Also pyHashTuple(): Python's hash() of a tuple of numbers (the dream simulation uses it). Checked by
// sim_engine.test.mjs against tests/fixtures/sim_runs.json.
const N = 624, M = 397;

export class PyRandom {
  constructor(seed = 0) { this.mt = new Uint32Array(N); this.mti = N + 1; this.seed(seed); }

  initGenrand(s) {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < N; i++) mt[i] = (Math.imul(1812433253, mt[i - 1] ^ (mt[i - 1] >>> 30)) + i) >>> 0;
    this.mti = N;
  }

  seed(seed) {
    let n = BigInt(seed);
    if (n < 0n) n = -n;
    const key = [];
    while (n > 0n) { key.push(Number(n & 0xffffffffn)); n >>= 32n; }
    if (!key.length) key.push(0);
    this.initGenrand(19650218);
    const mt = this.mt;
    let i = 1, j = 0;
    for (let k = Math.max(N, key.length); k; k--) {
      mt[i] = ((mt[i] ^ Math.imul(mt[i - 1] ^ (mt[i - 1] >>> 30), 1664525)) + key[j] + j) >>> 0;
      i++; j++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      if (j >= key.length) j = 0;
    }
    for (let k = N - 1; k; k--) {
      mt[i] = ((mt[i] ^ Math.imul(mt[i - 1] ^ (mt[i - 1] >>> 30), 1566083941)) - i) >>> 0;
      i++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
    }
    mt[0] = 0x80000000;
  }

  uint32() {
    const mt = this.mt;
    if (this.mti >= N) {
      let kk = 0, y;
      for (; kk < N - M; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + M] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      for (; kk < N - 1; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + (M - N)] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      y = (mt[N - 1] & 0x80000000) | (mt[0] & 0x7fffffff);
      mt[N - 1] = mt[M - 1] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      this.mti = 0;
    }
    let y = mt[this.mti++];
    y ^= y >>> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >>> 18;
    return y >>> 0;
  }

  random() { const a = this.uint32() >>> 5, b = this.uint32() >>> 6; return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0); }
  getrandbits(k) { return k <= 0 ? 0 : this.uint32() >>> (32 - k); }      // 1 <= k <= 32 is all the game needs
  randbelow(n) {                                                            // CPython _randbelow_with_getrandbits
    if (!(n > 0 && n <= 0xffffffff && Number.isInteger(n))) throw new RangeError(`randbelow(${n})`);
    const k = 32 - Math.clz32(n);
    let r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  }
  uniform(a, b) { return a + (b - a) * this.random(); }
  randrange(start, stop) {
    if (stop === undefined) return this.randbelow(start);
    if (!Number.isInteger(start) || !Number.isInteger(stop)) throw new TypeError('randrange() needs integers');
    if (stop - start <= 0) throw new RangeError(`empty range in randrange(${start}, ${stop})`);
    return start + this.randbelow(stop - start);
  }
  randint(a, b) { return this.randrange(a, b + 1); }
  choice(seq) {
    if (!seq.length) throw new RangeError('Cannot choose from an empty sequence');
    return seq[this.randbelow(seq.length)];
  }
  choices(population, weights) {                                            // k = 1, as the game always asks
    const cum = []; let acc = 0;
    for (const w of weights) { acc += w; cum.push(acc); }
    const x = this.random() * (cum[cum.length - 1] + 0.0);
    let lo = 0, hi = population.length - 1;                                // bisect_right(cum, x, 0, n - 1)
    while (lo < hi) { const mid = (lo + hi) >> 1; if (x < cum[mid]) hi = mid; else lo = mid + 1; }
    return population[lo];
  }
  sample(population, k) {                                                   // pool branch (n <= setsize)
    const n = population.length;
    let setsize = 21;
    if (k > 5) setsize += 4 ** Math.ceil(Math.log(k * 3) / Math.log(4));
    if (n > setsize) throw new RangeError('sample(): set-based branch not ported');
    const pool = population.slice(), out = [];
    for (let i = 0; i < k; i++) { const j = this.randbelow(n - i); out.push(pool[j]); pool[j] = pool[n - i - 1]; }
    return out;
  }
  // random.getstate()[1]: index into the state and the sum of the 624 words mod 2**32 (a cheap sync check).
  stateCheck() { let s = 0; for (let i = 0; i < N; i++) s = (s + this.mt[i]) % 4294967296; return { mti: this.mti, sum: s }; }
}

// Python's floored modulo for numbers.
export const pymod = (a, b) => ((a % b) + b) % b;

const MOD61 = (1n << 61n) - 1n, U64 = (1n << 64n) - 1n;
const XX1 = 11400714785074694791n, XX2 = 14029467366897019727n, XX5 = 2870177450012600261n;

// hash() of an int or float (CPython _Py_HashDouble; equal ints and floats hash the same).
export function pyHashNumber(v) {
  if (v === 0) return 0n;
  if (!Number.isFinite(v)) throw new RangeError('hash of inf/nan not needed');
  let sign = 1n, m = v;
  if (m < 0) { sign = -1n; m = -m; }
  let e = Math.floor(Math.log2(m)) + 1;
  m = m / 2 ** e;
  if (m >= 1) { m /= 2; e++; } else if (m < 0.5) { m *= 2; e--; }
  let x = 0n;
  while (m) {
    x = ((x << 28n) & MOD61) | (x >> 33n);
    m *= 268435456.0;
    e -= 28;
    const y = Math.floor(m);
    m -= y;
    x += BigInt(y);
    if (x >= MOD61) x -= MOD61;
  }
  e = e >= 0 ? e % 61 : 61 - 1 - ((-1 - e) % 61);
  x = ((x << BigInt(e)) & MOD61) | (x >> BigInt(61 - e));
  let h = sign * x;
  if (h === -1n) h = -2n;
  return h;
}

// hash(tuple(values)) for a tuple of numbers (CPython's xxHash-based tuplehash), as a BigInt.
export function pyHashTuple(values) {
  let acc = XX5;
  for (const v of values) {
    const lane = BigInt.asUintN(64, pyHashNumber(v));
    acc = (acc + lane * XX2) & U64;
    acc = ((acc << 31n) | (acc >> 33n)) & U64;
    acc = (acc * XX1) & U64;
  }
  acc = (acc + (BigInt(values.length) ^ (XX5 ^ 3527539n))) & U64;
  if (acc === U64) return 1546275796n;
  return BigInt.asIntN(64, acc);
}

// hash(tuple(values)) % m with Python's floored modulo, as a Number.
export const pyHashMod = (values, m) => Number(((pyHashTuple(values) % BigInt(m)) + BigInt(m)) % BigInt(m));

// Python's f"{x:.{d}f}": the exact binary value rounded half-to-even (JS toFixed rounds exact ties away from zero).
export function pyFixed(x, d) {
  const neg = x < 0 || Object.is(x, -0), s = Math.abs(x).toFixed(100), [ip, fp] = s.split('.');
  let n = BigInt(ip + fp.slice(0, d));
  const rest = fp.slice(d), first = rest[0], tail = /[1-9]/.test(rest.slice(1));
  if (first > '5' || (first === '5' && (tail || n % 2n === 1n))) n += 1n;
  let digits = n.toString().padStart(d + 1, '0');
  if (d) digits = digits.slice(0, -d) + '.' + digits.slice(-d);
  return (neg ? '-' : '') + digits;
}
