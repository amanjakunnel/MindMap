import React, { createRef, useEffect } from 'react';
import renderMindMap from './RenderMindMap';

export default function FinalMindMapRender() {
  const divRef = createRef();
  useEffect(() => renderMindMap(divRef.current), [divRef]);
  return (
      <div ref={divRef} />
  );
}
