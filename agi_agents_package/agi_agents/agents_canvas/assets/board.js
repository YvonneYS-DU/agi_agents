(function () {
  const container = document.getElementById('__BOARD_CONTAINER_ID__');
  const svg = document.getElementById('__CONNECTION_LAYER_ID__');
  const nodesLayer = document.getElementById('__NODES_LAYER_ID__');
  if (!container || !svg || !nodesLayer) return;
  if (container.dataset.initialized === '1') return;
  container.dataset.initialized = '1';

  const SVG_NS = 'http://www.w3.org/2000/svg';
  const tempMarkerId = `${svg.id}-arrow-temp`;
  const DEFAULT_WIDTH = 6;
  const WIDTH_PRESETS = [
    { value: 6, label: 'Thin' },
    { value: 10, label: 'Medium' },
    { value: 14, label: 'Thick' },
  ];
  const MIN_WIDTH = 2;
  const MAX_WIDTH = 40;
  const HIT_STROKE_PADDING = 50;

  let nodeCounter = 0;
  let connections = [];
  let tempLine = null;
  let connectionStartNode = null;
  let connectionStartHandle = null;
  let pointerMoveHandler = null;
  let pointerUpHandler = null;
  let connectionIdCounter = 0;
  let activeConnectionMenu = null;
  let activeConnectionForMenu = null;
  let outsideMenuHandler = null;
  let selectedNode = null;
  let tempMarker = null;
  let tooltipEl = null;
  let tooltipConnection = null;

  function normalizeWidth(value) {
    const numeric = Number.isFinite(value) ? Number(value) : DEFAULT_WIDTH;
    return Math.min(Math.max(numeric, MIN_WIDTH), MAX_WIDTH);
  }

  function getDefs() {
    let defs = svg.querySelector('defs');
    if (!defs) {
      defs = document.createElementNS(SVG_NS, 'defs');
      svg.insertBefore(defs, svg.firstChild);
    }
    return defs;
  }

  function createArrowMarker(id) {
    const marker = document.createElementNS(SVG_NS, 'marker');
    marker.setAttribute('id', id);
    marker.setAttribute('viewBox', '0 0 16 16');
    marker.setAttribute('refX', '14');
    marker.setAttribute('refY', '8');
    marker.setAttribute('markerWidth', '9');
    marker.setAttribute('markerHeight', '9');
    marker.setAttribute('orient', 'auto');
    marker.setAttribute('markerUnits', 'strokeWidth');

    const path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', 'M 2 2 L 14 8 L 2 14 z');
    path.setAttribute('class', 'canvas-arrowhead');
    marker.appendChild(path);
    getDefs().appendChild(marker);
    return marker;
  }

  function ensureTempMarker() {
    if (tempMarker && tempMarker.parentNode) {
      return tempMarker;
    }
    const existing = svg.querySelector(`#${tempMarkerId}`);
    if (existing) {
      tempMarker = existing;
      return tempMarker;
    }
    tempMarker = createArrowMarker(tempMarkerId);
    return tempMarker;
  }

  function ensureTooltip() {
    if (tooltipEl && tooltipEl.parentNode) {
      return tooltipEl;
    }
    const tooltip = document.createElement('div');
    tooltip.className = 'canvas-tooltip';
    container.appendChild(tooltip);
    tooltipEl = tooltip;
    return tooltipEl;
  }

  function formatConnectionType(type) {
    switch (type) {
      case 'rule':
        return 'Rule';
      case 'custom':
        return 'Custom';
      case 'direct':
      default:
        return 'Direct';
    }
  }

  function positionTooltip(evt) {
    if (!tooltipEl || !tooltipEl.parentNode) {
      return;
    }
    const rect = container.getBoundingClientRect();
    const offsetX = evt.clientX - rect.left + 12;
    const offsetY = evt.clientY - rect.top + 12;
    const maxLeft = rect.width - tooltipEl.offsetWidth - 12;
    const maxTop = rect.height - tooltipEl.offsetHeight - 12;
    const clampedLeft = Math.max(12, Math.min(offsetX, maxLeft));
    const clampedTop = Math.max(12, Math.min(offsetY, maxTop));
    tooltipEl.style.left = `${clampedLeft}px`;
    tooltipEl.style.top = `${clampedTop}px`;
  }

  function showConnectionTooltip(evt, connection) {
    tooltipConnection = connection;
    const tooltip = ensureTooltip();
    const typeLabel = formatConnectionType(connection.metadata?.type);
    tooltip.textContent = `${typeLabel} · Click to edit`;
    tooltip.classList.add('visible');
    positionTooltip(evt);
  }

  function updateConnectionTooltip(evt, connection) {
    if (tooltipConnection !== connection) {
      return;
    }
    positionTooltip(evt);
  }

  function hideConnectionTooltip() {
    tooltipConnection = null;
    if (tooltipEl) {
      tooltipEl.classList.remove('visible');
    }
  }

  function syncMarkerWithLine(line, marker) {
    if (!marker) {
      return;
    }
    const path = marker.querySelector('path');
    if (!path) {
      return;
    }
    const computed = window.getComputedStyle(line);
    let strokeColor = computed?.stroke;
    if (!strokeColor || strokeColor === 'none') {
      strokeColor = line.getAttribute('stroke') || '#2563eb';
    }
    path.setAttribute('fill', strokeColor);
    path.setAttribute('stroke', strokeColor);
    line.setAttribute('marker-end', `url(#${marker.id})`);
  }

  function cancelTempConnection() {
    if (tempLine && tempLine.parentNode) {
      tempLine.parentNode.removeChild(tempLine);
    }
    tempLine = null;
    if (connectionStartNode) {
      connectionStartNode.classList.remove('node-connecting');
    }
    connectionStartNode = null;
    connectionStartHandle = null;
    if (pointerMoveHandler) {
      window.removeEventListener('pointermove', pointerMoveHandler, true);
      pointerMoveHandler = null;
    }
    if (pointerUpHandler) {
      window.removeEventListener('pointerup', pointerUpHandler, true);
      pointerUpHandler = null;
    }
  }

  function closeConnectionMenu() {
    if (activeConnectionMenu && activeConnectionMenu.parentNode) {
      activeConnectionMenu.parentNode.removeChild(activeConnectionMenu);
    }
    activeConnectionMenu = null;
    activeConnectionForMenu = null;
    if (outsideMenuHandler) {
      window.removeEventListener('pointerdown', outsideMenuHandler, true);
      outsideMenuHandler = null;
    }
  }

  function clearSelectedNode() {
    if (selectedNode && selectedNode.parentNode) {
      selectedNode.classList.remove('selected');
    }
    selectedNode = null;
  }

  function selectNode(node) {
    if (!node) {
      clearSelectedNode();
      return;
    }
    if (selectedNode === node) {
      return;
    }
    if (selectedNode && selectedNode.parentNode) {
      selectedNode.classList.remove('selected');
    }
    selectedNode = node;
    selectedNode.classList.add('selected');
  }

  function removeNode(node) {
    if (!node) {
      return;
    }
    const nodeId = node.dataset.id;
    closeConnectionMenu();
    connections = connections.filter((connection) => {
      if (connection.from === nodeId || connection.to === nodeId) {
        if (tooltipConnection === connection) {
          hideConnectionTooltip();
        }
        if (connection.line && connection.line.parentNode) {
          connection.line.parentNode.removeChild(connection.line);
        }
        if (connection.label && connection.label.parentNode) {
          connection.label.parentNode.removeChild(connection.label);
        }
        if (connection.marker && connection.marker.parentNode) {
          connection.marker.parentNode.removeChild(connection.marker);
        }
        if (connection.hitLine && connection.hitLine.parentNode) {
          connection.hitLine.parentNode.removeChild(connection.hitLine);
        }
        return false;
      }
      return true;
    });
    node.classList.remove('selected');
    if (node.parentNode) {
      node.parentNode.removeChild(node);
    }
    clearSelectedNode();
  }

  container.addEventListener('pointerdown', (evt) => {
    if (evt.target.closest('.canvas-node') || evt.target.closest('.connection-menu')) {
      return;
    }
    clearSelectedNode();
    closeConnectionMenu();
    hideConnectionTooltip();
  });

  function applyConnectionStyle(connection) {
    const type = connection.metadata?.type || 'direct';
    connection.line.classList.remove('direct', 'rule', 'custom');
    connection.line.classList.add(type);

    const width = normalizeWidth(connection.metadata?.width);
    connection.metadata = { ...connection.metadata, width };
    connection.line.setAttribute('stroke-width', String(width));
    if (connection.hitLine) {
      connection.hitLine.setAttribute('stroke-width', String(width + HIT_STROKE_PADDING));
    }

    const labelText = connection.metadata?.label || '';
    if (labelText) {
      if (!connection.label) {
        connection.label = createConnectionLabel(labelText);
      }
      if (connection.label) {
        connection.label.textContent = labelText;
      }
    } else if (connection.label) {
      connection.label.remove();
      connection.label = null;
    }

    syncMarkerWithLine(connection.line, connection.marker);
  }

  function setConnectionMode(connection, mode, labelText = '') {
    if (!connection) {
      return;
    }
    const width = normalizeWidth(connection.metadata?.width);
    switch (mode) {
      case 'direct':
        connection.metadata = { type: 'direct', width };
        break;
      case 'rule':
        connection.metadata = { type: 'rule', label: labelText || '规则', width };
        break;
      case 'custom':
        connection.metadata = { type: 'custom', label: labelText || '自定义', width };
        break;
      default:
        connection.metadata = { type: 'direct', width };
        break;
    }
    applyConnectionStyle(connection);
    updateLine(connection);
  }

  function setConnectionWidth(connection, width) {
    if (!connection) {
      return;
    }
    const normalized = normalizeWidth(width) * 2;
    connection.metadata = {
      ...connection.metadata,
      width: normalized,
    };
    connection.line.setAttribute('stroke-width', String(normalized));
    if (connection.hitLine) {
      connection.hitLine.setAttribute('stroke-width', String(normalized + HIT_STROKE_PADDING));
    }
    syncMarkerWithLine(connection.line, connection.marker);
  }

  function openConnectionMenu(connection, evt) {
    if (!connection) {
      return;
    }
    closeConnectionMenu();
    activeConnectionForMenu = connection;
  hideConnectionTooltip();

    const menu = document.createElement('div');
    menu.className = 'connection-menu';
    menu.innerHTML = `
      <h4>连接模式</h4>
      <div class="menu-options">
        <button data-mode="direct">Direct</button>
        <button data-mode="rule">Rule</button>
        <button data-mode="custom">自定义</button>
      </div>
      <div class="menu-info hidden">直接把上一个 Agent 输出的结果输送到下一个节点</div>
      <div class="menu-input hidden">
        <input type="text" placeholder="" />
        <button data-action="confirm">确定</button>
      </div>
    `;

    menu.addEventListener('pointerdown', (event) => event.stopPropagation());
    menu.addEventListener('pointerup', (event) => event.stopPropagation());

    const containerRect = container.getBoundingClientRect();
    container.appendChild(menu);

    const repositionMenu = () => {
      const menuRect = menu.getBoundingClientRect();
      let left = evt.clientX - containerRect.left + 12;
      let top = evt.clientY - containerRect.top - menuRect.height / 2;
      const maxLeft = containerRect.width - menuRect.width - 12;
      const maxTop = containerRect.height - menuRect.height - 12;
      left = Math.max(12, Math.min(left, maxLeft));
      top = Math.max(12, Math.min(top, maxTop));
      menu.style.left = `${left}px`;
      menu.style.top = `${top}px`;
    };
    repositionMenu();

    const buttons = menu.querySelectorAll('[data-mode]');
    const inputWrapper = menu.querySelector('.menu-input');
    const infoLine = menu.querySelector('.menu-info');
    const inputField = inputWrapper.querySelector('input');
    const confirmButton = inputWrapper.querySelector('[data-action="confirm"]');

  const currentType = connection.metadata?.type || 'direct';
    buttons.forEach((button) => {
      const mode = button.dataset.mode;
      if (mode === currentType) {
        button.classList.add('active');
      }
      button.addEventListener('click', () => {
        buttons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');

        if (mode === 'direct') {
          infoLine.classList.remove('hidden');
          inputWrapper.classList.add('hidden');
          delete inputWrapper.dataset.mode;
          inputField.value = '';
          setConnectionMode(connection, 'direct');
          return;
        }

        infoLine.classList.add('hidden');
        inputWrapper.classList.remove('hidden');
        inputWrapper.dataset.mode = mode;
        inputField.placeholder = mode === 'rule' ? '输入规则或条件说明' : '输入自定义标签';
        inputField.value = connection.metadata?.label || '';
        requestAnimationFrame(() => inputField.focus());
      });
    });

    if (currentType !== 'direct') {
      infoLine.classList.add('hidden');
      inputWrapper.classList.remove('hidden');
      inputWrapper.dataset.mode = currentType;
      inputField.placeholder = currentType === 'rule' ? '输入规则或条件说明' : '输入自定义标签';
      inputField.value = connection.metadata?.label || '';
    } else {
      infoLine.classList.remove('hidden');
      inputWrapper.classList.add('hidden');
      delete inputWrapper.dataset.mode;
    }

    const commitSelection = () => {
      const pendingMode = inputWrapper.dataset.mode;
      if (!pendingMode) {
        return;
      }
      const value = inputField.value.trim();
      const label = value || (pendingMode === 'rule' ? '规则' : '自定义');
      setConnectionMode(connection, pendingMode, label);
      closeConnectionMenu();
    };

    confirmButton.addEventListener('click', commitSelection);
    inputField.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        commitSelection();
      } else if (event.key === 'Escape') {
        event.preventDefault();
        closeConnectionMenu();
      }
    });

    const thicknessButtons = menu.querySelectorAll('.thickness-options [data-width]');
    const currentWidth = normalizeWidth(connection.metadata?.width);
    thicknessButtons.forEach((button) => {
      const widthValue = normalizeWidth(Number.parseFloat(button.dataset.width || ''));
      if (Math.abs(widthValue - currentWidth) < 0.05) {
        button.classList.add('active');
      }
      button.addEventListener('click', () => {
        thicknessButtons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');
        setConnectionWidth(connection, widthValue);
      });
    });

    outsideMenuHandler = (event) => {
      if (menu.contains(event.target)) {
        return;
      }
      closeConnectionMenu();
    };
    window.addEventListener('pointerdown', outsideMenuHandler, true);

    activeConnectionMenu = menu;
  }

  function getAnchorPoint(node, direction) {
    const containerRect = container.getBoundingClientRect();
    if (direction) {
      const handle = node.querySelector(`.node-handle.handle-${direction}`);
      if (handle) {
        const handleRect = handle.getBoundingClientRect();
        return {
          x: handleRect.left + handleRect.width / 2 - containerRect.left,
          y: handleRect.top + handleRect.height / 2 - containerRect.top,
        };
      }
    }

    const rect = node.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2 - containerRect.left;
    const centerY = rect.top + rect.height / 2 - containerRect.top;

    switch (direction) {
      case 'top':
        return { x: centerX, y: rect.top - containerRect.top };
      case 'bottom':
        return { x: centerX, y: rect.bottom - containerRect.top };
      case 'left':
        return { x: rect.left - containerRect.left, y: centerY };
      case 'right':
        return { x: rect.right - containerRect.left, y: centerY };
      default:
        return { x: centerX, y: centerY };
    }
  }

  function createConnectionLabel(textContent) {
    if (!textContent) return null;
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.classList.add('canvas-label');
    label.textContent = textContent;
    svg.appendChild(label);
    return label;
  }

  function updateLine(connection) {
    const nodeA = nodesLayer.querySelector(`[data-id="${connection.from}"]`);
    const nodeB = nodesLayer.querySelector(`[data-id="${connection.to}"]`);
    if (!nodeA || !nodeB) return;

    const pointA = getAnchorPoint(nodeA, connection.fromDirection || 'top');
    const pointB = getAnchorPoint(nodeB, connection.toDirection || 'top');

    connection.line.setAttribute('x1', pointA.x);
    connection.line.setAttribute('y1', pointA.y);
    connection.line.setAttribute('x2', pointB.x);
    connection.line.setAttribute('y2', pointB.y);

    if (connection.hitLine) {
      connection.hitLine.setAttribute('x1', pointA.x);
      connection.hitLine.setAttribute('y1', pointA.y);
      connection.hitLine.setAttribute('x2', pointB.x);
      connection.hitLine.setAttribute('y2', pointB.y);
    }

    if (connection.label) {
      const midX = (pointA.x + pointB.x) / 2;
      const midY = (pointA.y + pointB.y) / 2 - 6;
      connection.label.setAttribute('x', midX);
      connection.label.setAttribute('y', midY);
    }

    syncMarkerWithLine(connection.line, connection.marker);
  }

  function updateConnectionsFor(nodeId) {
    connections
      .filter((connection) => connection.from === nodeId || connection.to === nodeId)
      .forEach(updateLine);
  }

  function connectNodes(nodeA, handleA, nodeB, handleB) {
    if (!nodeA || !nodeB || nodeA === nodeB) return;

    const fromDirection = handleA?.dataset?.direction || 'top';
    const toDirection = handleB?.dataset?.direction || 'top';

    const existing = connections.find(
      (connection) =>
        (connection.from === nodeA.dataset.id && connection.to === nodeB.dataset.id) ||
        (connection.from === nodeB.dataset.id && connection.to === nodeA.dataset.id),
    );
    if (existing) {
      return;
    }

    const width = normalizeWidth(DEFAULT_WIDTH);
    const metadata = { type: 'direct', width };
    const connectionId = ++connectionIdCounter;

    const hitLine = document.createElementNS(SVG_NS, 'line');
    hitLine.classList.add('canvas-connection', 'canvas-connection-hit');
    hitLine.setAttribute('stroke', 'transparent');
    hitLine.setAttribute('stroke-width', String(metadata.width + HIT_STROKE_PADDING));
    hitLine.setAttribute('pointer-events', 'stroke');
    svg.appendChild(hitLine);

    const line = document.createElementNS(SVG_NS, 'line');
    line.classList.add('canvas-connection', metadata.type || 'direct');
    line.setAttribute('stroke-width', String(metadata.width));
    svg.appendChild(line);

    const markerId = `${svg.id}-arrow-${connectionId}`;
    const marker = createArrowMarker(markerId);
    line.setAttribute('marker-end', `url(#${markerId})`);

    const connection = {
      id: connectionId,
      from: nodeA.dataset.id,
      to: nodeB.dataset.id,
      fromDirection,
      toDirection,
      line,
      metadata,
      marker,
      hitLine,
    };

    line.addEventListener('click', (evt) => {
      evt.stopPropagation();
      openConnectionMenu(connection, evt);
    });

    line.addEventListener('pointerenter', (evt) => {
      showConnectionTooltip(evt, connection);
    });
    line.addEventListener('pointermove', (evt) => {
      updateConnectionTooltip(evt, connection);
    });
    line.addEventListener('pointerleave', () => {
      hideConnectionTooltip();
    });

    hitLine.addEventListener('click', (evt) => {
      evt.stopPropagation();
      openConnectionMenu(connection, evt);
    });

    hitLine.addEventListener('pointerenter', (evt) => {
      showConnectionTooltip(evt, connection);
    });
    hitLine.addEventListener('pointermove', (evt) => {
      updateConnectionTooltip(evt, connection);
    });
    hitLine.addEventListener('pointerleave', () => {
      hideConnectionTooltip();
    });

    connections.push(connection);
    applyConnectionStyle(connection);
    updateLine(connection);
  }

  function makeDraggable(node) {
    let offsetX = 0;
    let offsetY = 0;
    let dragging = false;

    node.addEventListener('pointerdown', (evt) => {
      closeConnectionMenu();
      selectNode(node);
      dragging = true;
      node.setPointerCapture(evt.pointerId);
      const rect = container.getBoundingClientRect();
      offsetX = evt.clientX - rect.left - node.offsetLeft;
      offsetY = evt.clientY - rect.top - node.offsetTop;
      node.classList.add('dragging');
    });

    node.addEventListener('pointermove', (evt) => {
      if (!dragging) return;
      const rect = container.getBoundingClientRect();
      const x = evt.clientX - rect.left - offsetX;
      const y = evt.clientY - rect.top - offsetY;
      const clampedX = Math.max(0, Math.min(rect.width - node.offsetWidth, x));
      const clampedY = Math.max(0, Math.min(rect.height - node.offsetHeight, y));
      node.style.left = `${clampedX}px`;
      node.style.top = `${clampedY}px`;
      updateConnectionsFor(node.dataset.id);
    });

    const stopDragging = (evt) => {
      if (!dragging) return;
      dragging = false;
      node.releasePointerCapture(evt.pointerId);
      node.classList.remove('dragging');
    };

    node.addEventListener('pointerup', stopDragging);
    node.addEventListener('pointercancel', stopDragging);
    node.addEventListener('lostpointercapture', stopDragging);
  }

  function createNode(title, description) {
    const node = document.createElement('div');
    const id = `node-${++nodeCounter}`;
    node.dataset.id = id;
    node.className = 'canvas-node';
    const rect = container.getBoundingClientRect();
    const basePaddingX = 80;
    const basePaddingY = 120;
    const spacingX = 240;
    const spacingY = 110;
    const cols = Math.max(1, Math.floor((rect.width - basePaddingX * 2) / spacingX));
    const index = nodeCounter - 1;
    const col = index % cols;
    const row = Math.floor(index / cols);
    const left = Math.max(
      basePaddingX,
      Math.min(rect.width - basePaddingX - node.offsetWidth, basePaddingX + col * spacingX),
    );
    const top = Math.max(
      basePaddingY,
      Math.min(rect.height - basePaddingY - node.offsetHeight, basePaddingY + row * spacingY),
    );
    node.style.left = `${left}px`;
    node.style.top = `${top}px`;
    node.innerHTML = `
      <div class="node-handle handle-top" data-direction="top"></div>
      <div class="node-handle handle-right" data-direction="right"></div>
      <div class="node-handle handle-bottom" data-direction="bottom"></div>
      <div class="node-handle handle-left" data-direction="left"></div>
      <div class="node-title text-base">${title}</div>
      <div class="node-description text-xs font-normal mt-1 text-slate-500 leading-snug">${description || ''}</div>
    `;

    node.querySelectorAll('.node-handle').forEach((handle) => {
      handle.addEventListener('pointerdown', (evt) => {
        evt.stopPropagation();
        evt.preventDefault();
        closeConnectionMenu();
        startConnection(node, handle, evt);
      });
    });

    makeDraggable(node);
    nodesLayer.appendChild(node);
    return id;
  }

  function handleKeydown(evt) {
    if (evt.key !== 'Delete' && evt.key !== 'Backspace') {
      return;
    }
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) {
      return;
    }
    if (!selectedNode) {
      return;
    }
    evt.preventDefault();
    removeNode(selectedNode);
  }

  window.addEventListener('keydown', handleKeydown);

  function startConnection(node, handle, evt) {
    cancelTempConnection();
    connectionStartNode = node;
    connectionStartHandle = handle;
    node.classList.add('node-connecting');

    const containerRect = container.getBoundingClientRect();
    const direction = handle?.dataset?.direction || 'top';
    const startPoint = getAnchorPoint(node, direction);
    const startX = startPoint.x;
    const startY = startPoint.y;

  tempLine = document.createElementNS(SVG_NS, 'line');
    tempLine.classList.add('canvas-connection', 'temp');
    tempLine.setAttribute('x1', startX);
    tempLine.setAttribute('y1', startY);
    tempLine.setAttribute('x2', startX);
    tempLine.setAttribute('y2', startY);
  tempLine.setAttribute('stroke-width', String(normalizeWidth(DEFAULT_WIDTH)));
    svg.appendChild(tempLine);

    const tempMarkerRef = ensureTempMarker();
    tempLine.setAttribute('marker-end', `url(#${tempMarkerId})`);
    syncMarkerWithLine(tempLine, tempMarkerRef);

    pointerMoveHandler = (moveEvt) => {
      const x = moveEvt.clientX - containerRect.left;
      const y = moveEvt.clientY - containerRect.top;
      tempLine.setAttribute('x2', x);
      tempLine.setAttribute('y2', y);
    };

    pointerUpHandler = (upEvt) => {
      const targetHandle = upEvt.target && upEvt.target.closest ? upEvt.target.closest('.node-handle') : null;
      if (targetHandle) {
        const targetNode = targetHandle.closest('.canvas-node');
        if (targetNode && targetNode !== node) {
          connectNodes(node, handle, targetNode, targetHandle);
        }
      }
      cancelTempConnection();
    };

    window.addEventListener('pointermove', pointerMoveHandler, true);
    window.addEventListener('pointerup', pointerUpHandler, true);
  }

  window.addEventListener('resize', () => connections.forEach(updateLine));

  window.board = {
    addNode(title, description) {
      return createNode(title, description);
    },
    reset() {
      nodesLayer.innerHTML = '';
      svg.innerHTML = '';
      connections = [];
      nodeCounter = 0;
      cancelTempConnection();
      closeConnectionMenu();
      clearSelectedNode();
    },
    getState() {
      const nodes = Array.from(nodesLayer.children).map((node) => ({
        id: node.dataset.id,
        title: node.querySelector('.node-title')?.textContent || '',
        description: node.querySelector('.node-description')?.textContent || '',
        x: node.offsetLeft,
        y: node.offsetTop,
      }));
      const edges = connections.map((connection) => ({
        id: connection.id,
        from: connection.from,
        to: connection.to,
        from_direction: connection.fromDirection,
        to_direction: connection.toDirection,
        type: connection.metadata?.type || 'direct',
        label: connection.metadata?.label || '',
        width: normalizeWidth(connection.metadata?.width),
      }));
      return { nodes, edges };
    },
  };

  if (Array.isArray(window.__boardPending) && window.__boardPending.length > 0) {
    window.__boardPending.forEach((payload) => {
      window.board.addNode(payload.title, payload.description);
    });
    delete window.__boardPending;
  }
})();
