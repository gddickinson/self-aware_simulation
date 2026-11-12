// Static-site data layer: answers api() calls from the JSON files exported by scripts/build_static.py (/info and the
// sample Python runs /run/<seed>). The simulation itself runs in the browser, so nothing else is needed.
const files = new Map();
export async function staticApi(path) {
  const rel = path.replace(/^\/+/, '').split('?')[0];
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}
