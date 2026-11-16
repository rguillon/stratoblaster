# Copyright (c) 2026 Renaud Guillon
"""The JavaScript run in the page by `analyse_perf.py`.

Each constant is one function, evaluated in the game's page. They read Babylon's own objects
(`BABYLON.EngineStore`), so they work on the production build, which has no test API.
"""

# Shared by the probes below: the level's scene (the one with the most meshes) and the component
# a mesh belongs to, from its name and its ancestors (`playfield`, `ground-root`).
HELPERS = """
  const B = window.BABYLON;
  const engine = B.EngineStore.Instances[0];
  const levelScene = () => engine.scenes.reduce(
    (best, s) => (!best || s.meshes.length > best.meshes.length ? s : best), null);
  const TRAFFIC = /^(imposter-|prop-(car-|van|bus|truck|tanker)[^/]*$)/;
  const SKY = /^(cloud|aurora|sky|rain|snow|weather|lightning|plume|star|sun|moon|ash|ember|fog)/;
  const componentOf = (mesh) => {
    const chain = [];
    for (let n = mesh; n; n = n.parent) chain.push(n.name);
    const top = chain[chain.length - 1];
    const second = chain.length > 1 ? chain[chain.length - 2] : mesh.name;
    const name = mesh.name;
    if (top === 'playfield') {
      if (/^playfield-ship/.test(second) || /^ship-/.test(name)) return 'player ship';
      if (/^enemy-(bullet|missile|laser|shot|beam)/.test(second)) return 'enemy shots';
      if (/^enemy-/.test(second)) return 'enemies & bosses';
      if (/^(bullet|laser|missile)/.test(name)) return 'player shots';
      if (/^(blast|bomb|bonus|spark|impact|flash|debris)/.test(name)) return 'effects & bonuses';
      return 'playfield other';
    }
    if (top === 'ground-root') {
      if (/^terrain-chunk/.test(name)) return 'terrain';
      if (/^(street|road)/.test(name)) return 'roads';
      if (TRAFFIC.test(name)) return 'traffic';
      return 'buildings & props';
    }
    if (SKY.test(name)) return 'sky & weather';
    return 'other';
  };
  const mean = (a) => a.reduce((x, y) => x + y, 0) / Math.max(1, a.length);
"""

# Before the page's scripts: every worker's questions and answers with their times, the cookie that
# holds the graphics quality at High (so the automatic quality changes nothing while measuring),
# and a profile of the page's start when asked for (`__bootProfile`).
INIT = """() => {
  document.cookie = 'stratoblaster_graphics_quality=1; SameSite=Lax';
  const log = (window.__workerLog = []);
  const Native = window.Worker;
  let count = 0;
  window.Worker = function (url, options) {
    const worker = new Native(url, options);
    const index = count++;
    const post = worker.postMessage.bind(worker);
    worker.postMessage = (message, transfer) => {
      const m = message || {};
      const what = m.job ? JSON.stringify(m.job).slice(0, 60) : (m.level && m.level.id) || '';
      log.push({worker: index, way: 'ask', kind: m.kind, id: m.id, what: String(what),
        at: performance.now()});
      return post(message, transfer);
    };
    worker.addEventListener('message', (event) => {
      const d = event.data || {};
      log.push({worker: index, way: 'answer', kind: d.kind, id: d.id, at: performance.now()});
    });
    return worker;
  };
  window.Worker.prototype = Native.prototype;
  if (sessionStorage.getItem('__bootProfile')) console.profile('boot');
}"""

# Once a level plays (or a menu shows): times every frame. `work` is the main thread's time from
# the engine's begin to its end of frame (the simulation, the view's update and the drawing),
# `render` the part inside `scene.render()` of any scene, `gpu` the GPU's time (a timer query).
PLAY_PROBE = (
    """() => {
"""
    + HELPERS
    + """
  const probe = {frames: [], last: 0, begin: 0, render: 0};
  const insts = [];
  for (const scene of engine.scenes) {
    const inst = new B.SceneInstrumentation(scene);
    inst.captureActiveMeshesEvaluationTime = true;
    inst.captureRenderTargetsRenderTime = true;
    insts.push([scene, inst]);
    const draw = scene.render.bind(scene);
    scene.render = function (a, b) {
      const t = performance.now();
      draw(a, b);
      probe.render += performance.now() - t;
    };
  }
  let gpu = null;
  try {
    gpu = new B.EngineInstrumentation(engine);
    gpu.captureGPUFrameTime = true;
  } catch (e) { gpu = null; }
  engine.onBeginFrameObservable.add(() => {
    const now = performance.now();
    probe.interval = probe.last ? now - probe.last : 0;
    probe.last = now;
    probe.begin = now;
    probe.render = 0;
  });
  engine.onEndFrameObservable.add(() => {
    let draws = 0, active = 0, evaluate = 0, targets = 0;
    for (const [scene, inst] of insts) {
      const drawn = inst.drawCallsCounter.current;
      if (!drawn) continue;
      draws += drawn;
      active += scene.getActiveMeshes().length;
      evaluate += inst.activeMeshesEvaluationTimeCounter.current;
      targets += inst.renderTargetsRenderTimeCounter.current;
    }
    const g = gpu ? gpu.gpuFrameTimeCounter.current / 1e6 : 0;
    probe.frames.push([probe.begin, probe.interval, performance.now() - probe.begin,
      probe.render, g, draws, active, evaluate, targets,
      performance.memory ? performance.memory.usedJSHeapSize : 0]);
  });
  window.__perfProbe = probe;
}"""
)

# Returns the frames timed since the last call, and forgets them.
TAKE_FRAMES = """() => {
  const frames = window.__perfProbe.frames;
  window.__perfProbe.frames = [];
  return frames;
}"""

# What the level's scene holds, mesh by mesh: its component, whether it is shown, its triangles and
# instances, the bytes of its vertex, index and instance buffers (a geometry shared by several
# meshes is counted once), its material; then the textures, with the components that use them.
INVENTORY = (
    """() => {
"""
    + HELPERS
    + """
  const scene = levelScene();
  const gl = engine._gl;
  const out = {meshes: [], textures: [], kinds: {}, parts: {}, enemies: {}, canvas: {
    width: engine.getRenderWidth(), height: engine.getRenderHeight(),
    samples: gl.getParameter(gl.SAMPLES), css: [innerWidth, innerHeight],
    scaling: engine.getHardwareScalingLevel()},
    lights: scene.lights.map((l) => l.name), materials: scene.materials.length,
    effects: Object.keys(engine._compiledEffects || {}).length,
    particleSystems: scene.particleSystems.length,
    layers: (scene.effectLayers || []).map((l) => l.name),
    nodes: scene.transformNodes.length, total: scene.meshes.length,
    heap: performance.memory ? performance.memory.usedJSHeapSize : 0,
    viewport: scene.activeCamera ? scene.activeCamera.viewport : null};
  const geometries = new Set();
  const users = new Map();
  const materials = {};
  for (const mesh of scene.meshes) {
    const component = componentOf(mesh);
    const shown = mesh.isEnabled() && mesh.isVisible;
    const indices = mesh.getTotalIndices ? mesh.getTotalIndices() : 0;
    const vertices = mesh.getTotalVertices ? mesh.getTotalVertices() : 0;
    let bytes = 0;
    const geometry = mesh.geometry;
    if (geometry && !geometries.has(geometry.uniqueId)) {
      geometries.add(geometry.uniqueId);
      for (const kind of geometry.getVerticesDataKinds()) {
        const buffer = geometry.getVertexBuffer(kind);
        if (buffer && !buffer.getIsInstanced()) bytes += vertices * buffer.getSize() * 4;
      }
      bytes += indices * (vertices > 65535 ? 4 : 2);
    }
    let instanceBytes = 0;
    const thin = mesh._thinInstanceDataStorage;
    if (thin && thin.matrixData) instanceBytes += thin.matrixData.byteLength;
    const custom = mesh._userThinInstanceBuffersStorage;
    if (custom && custom.data) {
      for (const key of Object.keys(custom.data)) {
        if (custom.data[key]) instanceBytes += custom.data[key].byteLength || 0;
      }
    }
    const material = mesh.material;
    if (material) {
      (materials[component] = materials[component] || new Set()).add(material.uniqueId);
      for (const texture of material.getActiveTextures()) {
        if (!users.has(texture.uniqueId)) users.set(texture.uniqueId, new Set());
        users.get(texture.uniqueId).add(component);
      }
    }
    let kind = '';
    if (component === 'enemies & bosses') {
      let node = mesh;
      while (node.parent && node.parent.name !== 'playfield') node = node.parent;
      kind = node.name.replace(/^enemy-/, '').replace(/-\\d+$/, '');
      const entry = (out.enemies[kind] = out.enemies[kind] || {models: {}, shown: {}, meshes: 0,
        shownMeshes: 0, triangles: 0});
      entry.models[node.name] = 1;
      entry.meshes += 1;
      if (shown) {
        entry.shown[node.name] = 1;
        entry.shownMeshes += 1;
        entry.triangles += indices / 3;
      }
    }
    if (shown && mesh.parent) {
      // The shown meshes of the playfield and the ground by name (numbers dropped): what a model
      // is made of.
      const part = component + ' | ' + mesh.name.replace(/\\d+/g, '#');
      const entry = (out.parts[part] = out.parts[part] || [0, 0]);
      entry[0] += 1;
      entry[1] += (indices / 3) * Math.max(1, mesh.thinInstanceCount || 0);
    }
    out.meshes.push([component, shown ? 1 : 0, indices / 3, mesh.thinInstanceCount || 0,
      bytes, instanceBytes, kind, mesh.receiveShadows ? 1 : 0]);
  }
  for (const component of Object.keys(materials)) out.kinds[component] = materials[component].size;
  for (const kind of Object.keys(out.enemies)) {
    out.enemies[kind].models = Object.keys(out.enemies[kind].models).length;
    out.enemies[kind].shown = Object.keys(out.enemies[kind].shown).length;
  }
  for (const texture of scene.textures) {
    const size = texture.getSize();
    const internal = texture.getInternalTexture();
    const used = users.get(texture.uniqueId);
    out.textures.push({name: String(texture.name || '').slice(0, 40),
      type: texture.getClassName(), width: size.width, height: size.height,
      cube: !!texture.isCube, target: !!texture.isRenderTarget,
      mipmaps: internal ? !!internal.generateMipMaps : false,
      samples: internal ? internal.samples : 1, kind: internal ? internal.type : 0,
      users: used ? Array.from(used) : []});
  }
  return out;
}"""
)

# The cost of drawing each component, on one frozen frame: the game's loop is stopped, and the
# level's scene is drawn again and again, as it is and then with one thing taken away at a time (a
# component's meshes hidden, the glow layers or the shadows off, fewer pixels). Each variant gives
# the main thread's time to draw the frame, the GPU's, and the draw calls; the difference with the
# whole frame is what the thing costs. `frames`: the frames drawn per variant.
ABLATION = (
    """async (frames) => {
"""
    + HELPERS
    + """
  const scene = levelScene();
  const loops = engine._activeRenderLoops.slice();
  engine.stopRenderLoop();
  const inst = new B.SceneInstrumentation(scene);
  const timer = new B.EngineInstrumentation(engine);
  timer.captureGPUFrameTime = true;
  const next = () => new Promise((resolve) => requestAnimationFrame(resolve));
  const sorted = (a) => a.slice().sort((x, y) => x - y);
  const median = (a) => sorted(a)[a.length >> 1] || 0;
  // The mean without the slowest tenth of the frames (a garbage collection, another process).
  const trimmed = (a) => mean(sorted(a).slice(0, Math.ceil(a.length * 0.9)));
  const draw = async () => {
    const cpu = [], gpu = [], draws = [];
    for (let i = 0; i < frames + 10; i++) {
      await next();
      const start = performance.now();
      engine.beginFrame();
      scene.render();
      engine.endFrame();
      if (i < 10) continue;
      cpu.push(performance.now() - start);
      draws.push(inst.drawCallsCounter.current);
      const g = timer.gpuFrameTimeCounter.current;
      if (g > 0) gpu.push(g / 1e6);
    }
    return {cpu: trimmed(cpu), gpu: median(gpu), draws: mean(draws)};
  };
  const shown = scene.meshes.filter((m) => m.isEnabled());
  const groups = {};
  for (const mesh of shown) {
    const component = componentOf(mesh);
    (groups[component] = groups[component] || []).push(mesh);
  }
  const layers = scene.effectLayers || [];
  const glow = (on) => { for (const layer of layers) layer.isEnabled = on; };
  const out = {variants: {}, mainPass: {}, counts: {}, enemyKinds: {}};
  const kinds = {};
  for (const mesh of groups['enemies & bosses'] || []) {
    let node = mesh;
    while (node.parent && node.parent.name !== 'playfield') node = node.parent;
    const kind = node.name.replace(/^enemy-/, '').replace(/-\\d+$/, '');
    (kinds[kind] = kinds[kind] || []).push(mesh);
  }
  const without = async (meshes) => {
    for (const mesh of meshes) mesh.setEnabled(false);
    const result = await draw();
    for (const mesh of meshes) mesh.setEnabled(true);
    return result;
  };
  out.variants['whole frame'] = await draw();
  for (const component of Object.keys(groups)) {
    out.counts[component] = groups[component].length;
    out.variants[component] = await without(groups[component]);
  }
  out.variants['whole frame (again)'] = await draw();
  for (const kind of Object.keys(kinds)) {
    out.enemyKinds[kind] = await without(kinds[kind]);
    out.enemyKinds[kind].meshes = kinds[kind].length;
  }
  out.variants['whole frame (after kinds)'] = await draw();
  for (const layer of layers) {
    layer.isEnabled = false;
    out.variants['no glow layer: ' + layer.name] = await draw();
    layer.isEnabled = true;
  }
  glow(false);
  out.variants['no glow layers'] = await draw();
  glow(true);
  scene.shadowsEnabled = false;
  out.variants['no shadows'] = await draw();
  glow(false);
  // The main pass alone (no glow layers, no shadow map), whole then without each component.
  out.mainPass['whole frame'] = await draw();
  for (const component of Object.keys(groups)) {
    out.mainPass[component] = await without(groups[component]);
  }
  scene.shadowsEnabled = true;
  glow(true);
  // The hidden meshes (pooled models, masters of instances) taken out of the scene's list.
  const all = scene.meshes.slice();
  const hidden = all.filter((m) => !m.isEnabled());
  scene.meshes.length = 0;
  for (const mesh of all) if (mesh.isEnabled()) scene.meshes.push(mesh);
  out.variants['no hidden meshes in the scene'] = await draw();
  scene.meshes.length = 0;
  for (const mesh of all) scene.meshes.push(mesh);
  out.counts['hidden meshes'] = hidden.length;
  const scaling = engine.getHardwareScalingLevel();
  engine.setHardwareScalingLevel(scaling * 2);
  out.variants['half the pixels across'] = await draw();
  engine.setHardwareScalingLevel(scaling / 2);
  out.variants['twice the pixels across'] = await draw();
  engine.setHardwareScalingLevel(scaling);
  out.variants['nothing drawn'] = await without(shown);
  out.variants['whole frame (end)'] = await draw();
  for (const loop of loops) engine.runRenderLoop(loop);
  return out;
}"""
)

# The page's own timings of its start: the files loaded and when the title screen showed.
BOOT_TIMINGS = """() => ({
  now: performance.now(),
  files: performance.getEntriesByType('resource').map((r) => ({
    name: r.name.split('/').pop().split('?')[0], start: r.startTime, time: r.duration,
    bytes: r.transferSize, size: r.decodedBodySize})),
  heap: performance.memory ? performance.memory.usedJSHeapSize : 0,
})"""
