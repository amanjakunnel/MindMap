import { renderToStaticMarkup } from 'react-dom/server';

const DPR = 2;

function loadImage(url) {
  const image = new window.Image();
  return new Promise((resolve) => {
    image.onload = () => resolve(image);
    image.src = url;
  });
}

export default async function renderToCanvas(content, { width, height }) {
  const canvas = document.createElement('canvas');
  canvas.width = width * DPR;
  canvas.height = height * DPR;
  const ctx = canvas.getContext('2d');
  const url = `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="${width * DPR}" height="${height * DPR}">
      <style type="text/css">
        <![CDATA[
          ${document.getElementById('styles')?.innerHTML ?? ''}
        ]]>
      </style>
      <g transform="scale(${DPR})">
      <foreignObject width="${width}" height="${height}">
      ${renderToStaticMarkup(content)}
      </foreignObject>
      </g>
      </svg>`;
  const image = await loadImage(url);
  ctx.drawImage(image, 0, 0);
  return canvas;
}
