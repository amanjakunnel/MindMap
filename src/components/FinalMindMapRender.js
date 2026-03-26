import React, { useRef, useEffect } from 'react';
import renderMindMap from './RenderMindMap';

export default function FinalMindMapRender({ mapData }) {
  const divRef = useRef(null);

  useEffect(() => {
    const cleanup = renderMindMap(divRef.current, mapData);
    return cleanup;
  }, []);

  return <div ref={divRef} />;
}
