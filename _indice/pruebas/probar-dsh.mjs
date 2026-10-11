// Prueba opcional: node probar-dsh.mjs <checkout-dsh-compilado> <paquete-skill>
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [checkout, paquete] = process.argv.slice(2);
assert(checkout && paquete, 'Indica checkout DSH compilado y carpeta del paquete.');
const fuente = await fs.realpath(paquete);
const modulo = path.resolve(checkout, 'packages/skill/skill-filesystem/lib/index.js');
const { FileSystemSkillProvider } = await import(pathToFileURL(modulo));
const base = await fs.mkdtemp(path.join(os.tmpdir(), 'gm-dsh-loader-'));
await fs.chmod(base, 0o700);
const controller = new AbortController();
const avisos = [];
const ctx = { get: () => undefined, logger: { warn: x => avisos.push(x) } };
const provider = new FileSystemSkillProvider(ctx,
  { invalidate: () => {}, signal: controller.signal },
  { includeDefaultRoots: false, customSkillDirs: [base], watch: false });

async function archivos(raiz, prefijo = '') {
  const resultado = [];
  for (const entrada of await fs.readdir(path.join(raiz, prefijo), { withFileTypes: true })) {
    const relativo = path.join(prefijo, entrada.name);
    if (entrada.isDirectory()) resultado.push(...await archivos(raiz, relativo));
    else if (entrada.isFile()) resultado.push(relativo);
  }
  return resultado.sort();
}

try {
  const copia = path.join(base, 'gamemaker-biblioteca');
  await fs.cp(fuente, copia, { recursive: true, dereference: true });
  const opciones = { cwd: base, signal: controller.signal };
  const observed = await provider.list(opciones);
  const candidates = Array.isArray(observed) ? observed : observed.candidates;
  assert.equal(candidates.length, 1);
  assert.equal(candidates[0].name, 'gamemaker-biblioteca');
  const loaded = await provider.get(candidates[0], opciones);
  const raw = await fs.readFile(path.join(fuente, 'SKILL.md'), 'utf8');
  const cuerpo = raw.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/)?.[1].trim();
  assert(cuerpo, 'Falta cuerpo de skill con frontmatter.');
  assert.equal(loaded.content, cuerpo);
  assert.equal(loaded.resourceBase.path, copia);
  const manifest = await archivos(fuente);
  assert.deepEqual(await archivos(copia), manifest);
  for (const relativo of manifest) {
    assert.deepEqual(await fs.readFile(path.join(copia, relativo)),
      await fs.readFile(path.join(fuente, relativo)));
  }
  assert.equal(avisos.length, 0);
  const identidad = JSON.parse(await fs.readFile(path.resolve(checkout,
    'packages/skill/skill-filesystem/package.json'), 'utf8'));
  console.log(JSON.stringify({ loader: identidad.name, version: identidad.version,
    plataforma: process.platform, node: process.version, archivos: manifest.length,
    cuerpoExacto: true, referenciasAccesibles: true, avisos: 0,
    peticionesLLM: 0, raicesGlobalesConsultadas: false }));
} finally {
  controller.abort();
  await provider.dispose();
  await fs.rm(base, { recursive: true, force: true });
}
