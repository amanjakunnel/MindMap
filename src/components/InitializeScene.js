import * as THREE from 'three';
import { CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer';

export default function initializeScene(div) {
  const navHeight = 80;
  const width = window.innerWidth;
  const height = window.innerHeight - navHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);

  // WebGL renderer — handles connection lines
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0xf8f9fa);
  div.appendChild(renderer.domElement);

  // CSS2D renderer — handles node labels as real DOM elements
  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(width, height);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0';
  labelRenderer.domElement.style.left = '0';
  labelRenderer.domElement.style.pointerEvents = 'none';
  div.appendChild(labelRenderer.domElement);

  camera.position.z = 9;

  return { scene, renderer, labelRenderer, camera };
}
