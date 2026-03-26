import addConnection from './addConnection';
import addMindMapNode from './addMindMapNode';
import colors from './colors';
import initializeScene from './InitializeScene';
import calculateLevel1Coordinates from './calculateLevel1Coordinates';
import calculateLevel2Coordinates from './calculateLevel2Coordinates';

export default function renderMindMap(div, data) {
  const { scene, renderer, labelRenderer, camera } = initializeScene(div);

  // Build flat node list
  const res = [];
  for (let i = 1; i <= Object.keys(data).length; i++) {
    const node = data[String(i)];
    res.push(node.id === 1
      ? { id: node.id, label: node.label }
      : { id: node.id, label: node.label, parent: node.parent }
    );
  }

  const root = res.find(n => n.parent === undefined);
  const level1 = res.filter(n => n.parent === root.id);
  root.x = 0; root.y = 0; root.level = 0;

  const nodeElements = [];
  nodeElements.push(addMindMapNode(scene, root));

  const radius1 = 4.0;

  for (let i = 0; i < level1.length; i++) {
    const { x, y, angle } = calculateLevel1Coordinates({
      numberOfNodes: level1.length,
      parent: root,
      radius: radius1,
      index: i,
    });
    const l1node = { ...level1[i], x, y, level: 1, angle };
    nodeElements.push(addMindMapNode(scene, l1node));
    addConnection(scene, { color: colors.magenta, parentNode: root, childNode: l1node });

    const level2 = res.filter(n => n.parent === l1node.id).slice(0, 3);
    for (let j = 0; j < level2.length; j++) {
      const { x: x2, y: y2 } = calculateLevel2Coordinates({
        numberOfNodes: level2.length,
        parent: l1node,
        index: j,
      });
      const l2node = { ...level2[j], x: x2, y: y2, level: 2 };
      nodeElements.push(addMindMapNode(scene, l2node));
      addConnection(scene, { color: colors.violet, parentNode: l1node, childNode: l2node });
    }
  }

  camera.position.z = 13;

  // Pan state
  let isPanning = false;
  let lastX = 0, lastY = 0;

  function panStart(e) {
    if (e.button !== 0) return;
    isPanning = true;
    lastX = e.clientX;
    lastY = e.clientY;
  }

  function panMove(e) {
    if (!isPanning) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const worldHeight = 2 * Math.tan(Math.PI * 75 / 360) * camera.position.z;
    const scale = worldHeight / rect.height;
    // At default zoom the map fits the screen so little panning needed.
    // When zoomed in the limit expands so every node stays reachable.
    const panLimit = Math.max(1, 9.5 - worldHeight / 2);
    camera.position.x = Math.max(-panLimit, Math.min(panLimit,
      camera.position.x - (e.clientX - lastX) * scale));
    camera.position.y = Math.max(-panLimit, Math.min(panLimit,
      camera.position.y + (e.clientY - lastY) * scale));
    lastX = e.clientX;
    lastY = e.clientY;
  }

  function panEnd() {
    isPanning = false;
  }

  // Zoom + prevent browser ctrl+scroll zoom
  function onWheel(e) {
    e.preventDefault();
    if (e.ctrlKey) return;
    const factor = e.deltaY > 0 ? 1.08 : 0.92;
    camera.position.z = Math.max(2, Math.min(13, camera.position.z * factor));
  }

  renderer.domElement.addEventListener('mousedown', panStart);
  window.addEventListener('mousemove', panMove);
  window.addEventListener('mouseup', panEnd);
  div.addEventListener('wheel', onWheel, { passive: false });

  // Tooltip
  const tooltip = document.createElement('div');
  tooltip.style.cssText = [
    'position:absolute',
    'background:rgba(20,20,20,0.82)',
    'color:#fff',
    'padding:6px 10px',
    'border-radius:8px',
    'font-size:12px',
    'font-family:sans-serif',
    'pointer-events:none',
    'display:none',
    'max-width:240px',
    'word-break:break-word',
    'z-index:20',
    'line-height:1.4',
  ].join(';');
  div.style.position = 'relative';
  div.appendChild(tooltip);

  function onMouseMove(e) {
    if (tooltip.style.display === 'block') {
      const rect = div.getBoundingClientRect();
      tooltip.style.left = `${e.clientX - rect.left + 14}px`;
      tooltip.style.top = `${e.clientY - rect.top - 14}px`;
    }
  }
  div.addEventListener('mousemove', onMouseMove);

  nodeElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
      tooltip.textContent = el.dataset.fullLabel;
      tooltip.style.display = 'block';
    });
    el.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });
    el.addEventListener('mousedown', panStart);
  });

  // Animation loop
  let animationId;
  let cancelled = false;

  function animate() {
    if (cancelled) return;
    animationId = requestAnimationFrame(animate);
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }
  animate();

  return () => {
    cancelled = true;
    cancelAnimationFrame(animationId);
    renderer.dispose();
    renderer.domElement.removeEventListener('mousedown', panStart);
    window.removeEventListener('mousemove', panMove);
    window.removeEventListener('mouseup', panEnd);
    div.removeEventListener('wheel', onWheel);
    div.removeEventListener('mousemove', onMouseMove);
    while (div.firstChild) div.removeChild(div.firstChild);
  };
}
