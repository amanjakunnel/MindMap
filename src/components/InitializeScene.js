import * as THREE from 'three';

export default function initializeScene(div) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  const renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, window.innerHeight);
  div.appendChild(renderer.domElement);
  camera.position.z = 5;
  return { scene, renderer, camera };
}
