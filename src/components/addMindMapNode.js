import { CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer';

const levelClass = {
  0: 'root-rect magenta',
  1: 'level1-pill violet',
  2: 'pill blue',
};

const maxLen = {
  0: 18,
  1: 14,
  2: 16,
};

export default function addMindMapNode(scene, { level, label, x, y }) {
  const truncated = label.length > maxLen[level]
    ? label.slice(0, maxLen[level] - 1) + '…'
    : label;

  const el = document.createElement('div');
  el.className = `mind-map-node ${levelClass[level] ?? 'pill blue'}`;
  el.textContent = truncated;
  el.dataset.fullLabel = label;

  const obj = new CSS2DObject(el);
  obj.position.set(x, y, 0);
  scene.add(obj);

  return el;
}
