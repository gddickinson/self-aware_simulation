// node web/static/sim_engine.test.mjs: the JS engine against Python reference values (tests/fixtures/sim_runs.json,
// written by scripts/make_sim_fixture.py from the real game code via web/headless.py).
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { PyRandom, pyHashTuple, pymod, pyFixed } from './py_random.js';
import { checkRun, diff } from './sim_compare.js';
import { Game } from './sim_engine.js';

const F = JSON.parse(readFileSync(new URL('../../tests/fixtures/sim_runs.json', import.meta.url)));
let n = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); n++; };

for (const s of F.rng) {
  const r = new PyRandom(s.seed);
  ok(!diff(s.random, Array.from({ length: 5 }, () => r.random())).length, `random() seed ${s.seed}`);
  ok(!diff(s.randint, Array.from({ length: 10 }, () => r.randint(25000, 45000))).length, `randint seed ${s.seed}`);
  ok(!diff(s.uniform, Array.from({ length: 5 }, () => r.uniform(-1, 1))).length, `uniform seed ${s.seed}`);
  ok(!diff(s.choices, Array.from({ length: 20 }, () => r.choices([0, 1, 2, 3, 4], [30, 30, 20, 15, 5]))).length, `choices seed ${s.seed}`);
  ok(!diff(s.sample, Array.from({ length: 5 }, () => r.sample([0, 1, 2, 3, 4, 5, 6, 7], 3))).length, `sample seed ${s.seed}`);
  ok(!diff(s.randrange, Array.from({ length: 10 }, () => r.randrange(37))).length, `randrange seed ${s.seed}`);
}
for (const [t, h, m] of F.hashes) {
  ok(pyHashTuple(t) === BigInt(h), `hash(${t}) = ${h}, got ${pyHashTuple(t)}`);
  ok(Number(pymod(Number(pyHashTuple(t) % 100n), 100)) === m, `hash(${t}) % 100`);
}
for (const [x, f2, f1] of F.formats) { ok(pyFixed(x, 2) === f2, `${x}:.2f`); ok(pyFixed(x, 1) === f1, `${x}:.1f`); }

for (const ref of F.runs) {
  const t0 = Date.now(), r = checkRun(ref, F.every);
  assert.ok(r.ok, `seed ${ref.seed}: ${r.problems.join('; ')}`);
  n++;
  console.log(`seed ${ref.seed}: ${ref.steps} frames, ${r.matched}/${r.total} snapshots and ${r.events} events identical (${Date.now() - t0} ms)`);
}

// Same seed, same run; share-link actions replay; different seeds differ.
const a = new Game(99), b = new Game(99), c = new Game(100);
for (let i = 0; i < 500; i++) { a.update(); b.update(); c.update(); }
ok(!diff(a.snapshot(true), b.snapshot(true)).length, 'deterministic');
ok(diff(a.snapshot(true), c.snapshot(true)).length > 0, 'seeds differ');
console.log(`ok: ${n} checks`);
