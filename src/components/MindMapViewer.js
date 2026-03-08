import React, { createRef, useEffect } from 'react';
import * as THREE from 'three';
import renderMindMap from './RenderMindMap';



export default function MindMapViewer() {
  const divRef = createRef();
  useEffect(() => renderMindMap(divRef.current), [divRef]);
  return (
      <div ref={divRef} />
  );
}

  // 
  // console.log("In Mind Map viewer");
  
  // const divRef = createRef();
  // console.log(divRef.current);
  // Test

 
  //

  // useEffect(() => renderMindMap(divRef.current), [divRef]);

  // console.log("useEffect created");
  // console.log(divRef);
  
  // return (
  //   <div>
  //     MindMapviewer
  //     <div  className="MindMapViewer" ref={divRef} />
  //   </div>
      
  

  // );


// export default function MindMapViwer() {

    
//   const divRef = createRef();
//   useEffect(() => {
//     const scene = new THREE.Scene();
//     const camera = new THREE.PerspectiveCamera(
//       75,
//       window.innerWidth / window.innerHeight,
//       0.1,
//       1000
//     );
//     const renderer = new THREE.WebGLRenderer();
//     renderer.setSize(window.innerWidth, window.innerHeight);
//     divRef.current.appendChild(renderer.domElement);
//     const geometry = new THREE.BoxGeometry();
//     const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
//     const cube = new THREE.Mesh(geometry, material);
//     scene.add(cube);
//     camera.position.z = 5;
//     function animate() {
//       requestAnimationFrame(animate);
//       cube.rotation.x += 0.01;
//       cube.rotation.y += 0.01;
//       renderer.render(scene, camera);
//     }
//     animate();
//   }, [divRef]);
//   return <div className="MindMapViewer" ref={divRef} />;
// }