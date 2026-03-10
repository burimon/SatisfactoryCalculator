export function connectionAnchorPoint(fromRect, toRect) {
  const fromCenterX = fromRect.x + fromRect.width / 2;
  const fromCenterY = fromRect.y + fromRect.height / 2;
  const toCenterX = toRect.x + toRect.width / 2;
  const toCenterY = toRect.y + toRect.height / 2;
  const dx = toCenterX - fromCenterX;
  const dy = toCenterY - fromCenterY;
  const halfWidth = fromRect.width / 2;
  const halfHeight = fromRect.height / 2;

  if (Math.abs(dx) < 0.0001 && Math.abs(dy) < 0.0001) {
    return { x: fromCenterX + halfWidth, y: fromCenterY };
  }

  const scaleX = halfWidth / Math.max(Math.abs(dx), 0.0001);
  const scaleY = halfHeight / Math.max(Math.abs(dy), 0.0001);
  const scale = Math.min(scaleX, scaleY);

  return {
    x: fromCenterX + dx * scale,
    y: fromCenterY + dy * scale,
  };
}

export function elementOffsetWithinAncestor(element, ancestor) {
  let x = 0;
  let y = 0;
  let current = element;

  while (current && current !== ancestor) {
    x += current.offsetLeft;
    y += current.offsetTop;
    current = current.offsetParent;
  }

  return { x, y };
}

export function portAnchorInWorld(node, nodeEl, portEl, side) {
  const offset = elementOffsetWithinAncestor(portEl, nodeEl);
  return {
    x: node.x + (side === "left" ? offset.x : offset.x + portEl.offsetWidth),
    y: node.y + offset.y + portEl.offsetHeight / 2,
  };
}

export function nodeRect(node, nodeEl) {
  return {
    x: node.x,
    y: node.y,
    width: nodeEl.offsetWidth,
    height: nodeEl.offsetHeight,
  };
}

export function edgeControlPoints(start, end) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const curve = Math.max(80, Math.min(220, Math.abs(dx) * 0.45 + Math.abs(dy) * 0.15));
  return {
    control1: { x: start.x + Math.sign(dx || 1) * curve, y: start.y },
    control2: { x: end.x - Math.sign(dx || 1) * curve, y: end.y },
  };
}

export function bezierMidpoint(start, control1, control2, end) {
  return {
    x: 0.125 * start.x + 0.375 * control1.x + 0.375 * control2.x + 0.125 * end.x,
    y: 0.125 * start.y + 0.375 * control1.y + 0.375 * control2.y + 0.125 * end.y,
  };
}

export function includePoint(bounds, point, padding = 0) {
  if (!bounds) {
    return {
      minX: point.x - padding,
      minY: point.y - padding,
      maxX: point.x + padding,
      maxY: point.y + padding,
    };
  }
  return {
    minX: Math.min(bounds.minX, point.x - padding),
    minY: Math.min(bounds.minY, point.y - padding),
    maxX: Math.max(bounds.maxX, point.x + padding),
    maxY: Math.max(bounds.maxY, point.y + padding),
  };
}

export function includeRect(bounds, rect, padding = 0) {
  let nextBounds = includePoint(bounds, { x: rect.x, y: rect.y }, padding);
  nextBounds = includePoint(nextBounds, { x: rect.x + rect.width, y: rect.y + rect.height }, padding);
  return nextBounds;
}
