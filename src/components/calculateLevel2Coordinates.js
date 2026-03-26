export default function calculateLevel2Coordinates({
    numberOfNodes,
    parent,
    index
  }) {
    const spread = (60 * Math.PI) / 180;
    const radius = 5.0;
    const slice = numberOfNodes > 1 ? spread / (numberOfNodes - 1) : 0;
    const angle = slice * index + parent.angle - spread / 2;
    const x = parent.x + radius * Math.cos(angle);
    const y = parent.y + radius * Math.sin(angle);
    return { x, y, angle };
  }
