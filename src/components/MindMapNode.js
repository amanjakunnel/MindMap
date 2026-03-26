import React from 'react';
import cx from 'classnames';

export default function MindMapNode({ level, label }) {
  const maxLen = level === 0 ? 18 : level === 1 ? 14 : 16;
  const displayLabel = label.length > maxLen ? label.slice(0, maxLen - 1) + '…' : label;
  return (
    <div
      xmlns="http://www.w3.org/1999/xhtml"
      className={cx(
        'mind-map-node',
        level === 0 && 'magenta root-rect',
        level === 1 && 'violet level1-pill',
        level === 2 && 'blue pill',
        level >= 3 && 'turquoise pill'
      )}
    >
      <div>{displayLabel}</div>
    </div>
  );
}
