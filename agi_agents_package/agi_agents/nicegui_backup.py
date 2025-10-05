#!/usr/bin/env python3
from __future__ import annotations

import json
from uuid import uuid4

from nicegui import ui


@ui.page('/')
async def main() -> None:
    agents = [
        {
            'id': 'planner',
            'name': 'Planner',
            'description': 'Task planning and workflow design specialist.',
        },
        {
            'id': 'tool_call_planner',
            'name': 'Tool Call Planner',
            'description': 'Responsible for planning and coordinating tool usage.',
        },
        {
            'id': 'web_searcher',
            'name': 'Web Searcher',
            'description': 'Web search and information gathering expert.',
        },
        {
            'id': 'chat_history',
            'name': 'Chat History',
            'description': 'Responsible for managing and retrieving chat history.',
        },
        {
            'id': 'summarizer',
            'name': 'Summarizer',
            'description': 'quickly digests information and produces concise summaries.',
        },

    ]

    ui.add_css(
        r'''
    html {height: 100%;}
    
    body {margin: 0; height: 100%; background: #f5f7fa; overflow: hidden;}
        .column-border {border-color: rgba(15, 23, 42, 0.08);}
        .canvas-container {position: relative; width: 100%; height: 100%; background: linear-gradient(135deg, #f8fafc 0%, #e7eff9 100%); border-radius: 18px; overflow: hidden; border: 1px solid rgba(15, 23, 42, 0.08);}
        .canvas-container svg .canvas-connection {pointer-events: stroke;}
        .canvas-container svg .canvas-label {pointer-events: none;}
        .canvas-container svg {position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: auto;}
        .canvas-nodes {position: absolute; inset: 0; pointer-events: none;}
        .canvas-node {position: absolute; pointer-events: auto; width: 220px; padding: 12px 16px; border-radius: 12px; background: white; box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08); cursor: grab; user-select: none; border: 1px solid rgba(15, 23, 42, 0.08); transition: box-shadow 0.2s ease, transform 0.2s ease; font-weight: 600; color: #1f2937;}
        .canvas-node.dragging {cursor: grabbing; transform: scale(1.02); box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);}
        .canvas-node.connecting {box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3); border-color: rgba(59, 130, 246, 0.6);}
        .canvas-node.selected {box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.45); border-color: rgba(59, 130, 246, 0.75);}
        .canvas-connection {stroke: rgba(59, 130, 246, 0.65); stroke-width: 2.5;}
        .canvas-placeholder {height: 100%; border-radius: 18px; border: 1px dashed rgba(15, 23, 42, 0.12); display: flex; align-items: center; justify-content: center; color: rgba(15, 23, 42, 0.4); font-size: 0.9rem;}
        .canvas-connection.direct {stroke-dasharray: none;}
        .canvas-connection.rule {stroke-dasharray: 6 6;}
        .canvas-connection.custom {stroke-dasharray: 2 6; stroke: rgba(99, 102, 241, 0.75);}
        .canvas-label {fill: rgba(30, 41, 59, 0.85); font-size: 12px; font-weight: 500; pointer-events: none;}
        .canvas-connection.temp {stroke: rgba(59, 130, 246, 0.4); stroke-dasharray: 4 4;}
        .agent-card {display: flex; flex-direction: column; justify-content: flex-start; gap: 2px; border-radius: 14px; border: 1px solid rgba(15, 23, 42, 0.08); background: white; box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04); padding: 8px 12px; height: 72px; transition: transform 0.2s ease, box-shadow 0.2s ease;}
        .agent-card .agent-desc {font-size: 0.72rem; color: #475569; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;}
        .agent-card .agent-name {font-size: 0.9rem; font-weight: 600; color: #1f2937;}
        .agent-card:hover {transform: translateY(-2px); box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);}
        .node-handle {position: absolute; width: 14px; height: 14px; border-radius: 999px; background: #2563eb; border: 2px solid white; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35); cursor: crosshair; opacity: 0; transition: opacity 0.2s ease, transform 0.2s ease; pointer-events: none;}
        .canvas-node:hover .node-handle,
        .node-connecting .node-handle {opacity: 1; pointer-events: auto;}
        .node-handle::after {content: ''; position: absolute; inset: -6px; border-radius: 999px; background: rgba(37, 99, 235, 0.14); opacity: 0; transition: opacity 0.2s ease;}
        .node-handle:hover::after {opacity: 1;}
        .node-handle.handle-top {top: -12px; left: 50%; transform: translate(-50%, 0);}
        .node-handle.handle-bottom {bottom: -12px; left: 50%; transform: translate(-50%, 0);}
        .node-handle.handle-left {left: -12px; top: 50%; transform: translate(0, -50%);}
        .node-handle.handle-right {right: -12px; top: 50%; transform: translate(0, -50%);}
        .node-connecting .node-handle {background: #16a34a;}
        .node-connecting {box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.25);}
        .connection-menu {position: absolute; z-index: 20; min-width: 170px; padding: 10px; border-radius: 10px; background: white; box-shadow: 0 14px 30px rgba(15, 23, 42, 0.18); border: 1px solid rgba(15, 23, 42, 0.08); display: flex; flex-direction: column; gap: 8px;}
        .connection-menu h4 {margin: 0; font-size: 0.85rem; font-weight: 600; color: #1f2937;}
        .connection-menu .menu-options {display: flex; gap: 6px;}
        .connection-menu .menu-options button {flex: 1; padding: 6px 8px; border-radius: 8px; border: 1px solid rgba(15, 23, 42, 0.1); background: #f8fafc; color: #1f2937; font-size: 0.78rem; cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;}
        .connection-menu .menu-options button.active {background: #2563eb; color: white; border-color: #2563eb;}
        .connection-menu .menu-options button:hover {background: #e0e7ff; border-color: rgba(59, 130, 246, 0.6);}
        .connection-menu .menu-info {font-size: 0.75rem; color: #475569; line-height: 1.4; padding: 2px 0 4px;}
        .connection-menu .menu-info.hidden {display: none;}
        .connection-menu .menu-input {display: flex; gap: 6px;}
        .connection-menu .menu-input.hidden {display: none;}
        .connection-menu .menu-input input {flex: 1; padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(15, 23, 42, 0.15); font-size: 0.75rem;}
        .connection-menu .menu-input button {padding: 6px 10px; border-radius: 6px; border: none; background: #2563eb; color: white; font-size: 0.75rem; cursor: pointer; transition: background 0.2s ease;}
        .connection-menu .menu-input button:hover {background: #1d4ed8;}
        '''
    )

    reset_dialog: ui.dialog | None = None
    export_dialog: ui.dialog | None = None
    export_textarea: ui.textarea | None = None
    copy_status_label: ui.label | None = None

    def confirm_clear_canvas() -> None:
        ui.run_javascript('window.board?.reset()')
        ui.run_javascript("window.dispatchEvent(new CustomEvent('canvas-cleared'))")
        ui.notify('Canvas has been cleared. Your prompt has been removed.', type='info', position='top')
        if reset_dialog:
            reset_dialog.close()

    def prompt_reset_canvas() -> None:
        if reset_dialog:
            reset_dialog.open()

    async def export_agents_pipeline() -> None:
        if export_dialog:
            export_dialog.open()
        if copy_status_label:
            copy_status_label.set_text('Agents canvas python code loaded...')

        try:
            result = await ui.run_javascript(
                'return window.board?.getState?.() || {nodes: [], edges: []};',
                respond=True,
            )
        except RuntimeError:
            if copy_status_label:
                copy_status_label.set_text('Failed to read canvas. Please try again.')
            ui.notify('Failed to read canvas state.', type='negative', position='top')
            return

        formatted = json.dumps(result, ensure_ascii=False, indent=2)
        if export_textarea:
            export_textarea.value = formatted
        if copy_status_label:
            copy_status_label.set_text('Ready to copy.')

    async def copy_pipeline_to_clipboard() -> None:
        if not export_textarea:
            return
        text_value = export_textarea.value or ''
        encoded_text = json.dumps(text_value)
        success: bool = False
        try:
            success = bool(
                await ui.run_javascript(
                    f"""
                    (async () => {{
                        try {{
                            if (!navigator.clipboard || !navigator.clipboard.writeText) {{
                                return false;
                            }}
                            await navigator.clipboard.writeText({encoded_text});
                            return true;
                        }} catch (error) {{
                            console.warn('Copy to clipboard failed:', error);
                            return false;
                        }}
                    }})()
                    """,
                    respond=True,
                )
            )
        except RuntimeError:
            success = False

        if copy_status_label:
            copy_status_label.set_text(
                'Copied to clipboard.' if success else 'Copy failed. Please copy manually.'
            )

    board_container_id = f'board-container-{uuid4().hex}'
    connection_layer_id = f'board-connection-{uuid4().hex}'
    nodes_layer_id = f'board-nodes-{uuid4().hex}'

    with ui.column().classes('absolute inset-0 w-full h-full overflow-hidden gap-0'):
        with ui.row().classes('w-full flex-1 no-wrap overflow-hidden items-stretch'):
            with ui.column().classes('w-full max-w-xs h-full p-6 gap-4 bg-white column-border border-r flex-none'):
                ui.label('Choose/Build Agent').classes('mt-0 text-xl font-semibold text-slate-800')

                selected_agent = ui.select(
                    {agent['id']: agent['name'] for agent in agents},
                    label='Choose from Agent Templates',
                    value=agents[0]['id'],
                    with_input=True,
                ).props('dense outlined rounded use-input fill-input input-debounce="0" clearable').classes('w-full')

                def spawn_agent(agent_item: dict[str, str]) -> None:
                    if not agent_item:
                        return
                    payload = {
                        'id': agent_item['id'],
                        'title': agent_item['name'],
                        'description': agent_item['description'],
                    }
                    ui.run_javascript(
                        f'''
                        (function() {{
                            const payload = {json.dumps(payload, ensure_ascii=False)};
                            const push = () => window.board.addNode(payload.title, payload.description);
                            if (window.board?.addNode) {{
                                push();
                            }} else {{
                                window.__boardPending = window.__boardPending || [];
                                window.__boardPending.push(payload);
                            }}
                        }})();
                        '''
                    )

                with ui.row().classes('w-full gap-2'):
                    export_button = ui.button('Export\nAGENTs code', on_click=export_agents_pipeline, color='primary').classes('flex-1 mt-2').style('font-size: 0.75rem;')
                    reset_button = ui.button('Reset\nAGENTs canvas', on_click=prompt_reset_canvas, color='grey').classes('flex-1 mt-2').style('font-size: 0.75rem;')
                    export_button.style('white-space: pre-line; line-height: 1.2;')
                    reset_button.style('white-space: pre-line; line-height: 1.2;')

                ui.separator()
                ui.label('Agent Templates List').classes('text-base font-medium text-slate-700')
                with ui.column().classes('gap-3 overflow-y-auto pr-1 flex-1'):
                    for agent in agents:
                        card = ui.card().classes('agent-card w-full cursor-pointer hover:shadow-lg transition')

                        def handle_agent_click(_: object = None, agent_data: dict[str, str] = agent) -> None:
                            selected_agent.value = agent_data['id']
                            spawn_agent(agent_data)

                        card.on('click', handle_agent_click)
                        with card:
                            ui.label(agent['name']).classes('agent-name')
                            ui.label(agent['description']).classes('agent-desc')

            with ui.column().classes('flex-1 h-full p-6'):
                ui.label('AGENTs Flow Canvas').classes('mt-0 text-xl font-semibold text-slate-800 mb-2')

                board_container = (
                    ui.element('div')
                    .props(f'id={board_container_id}')
                    .classes('canvas-container w-full h-full')
                )
                board_container.style('height: 100%;')
                with board_container:
                    connection_layer = (
                        ui.element('svg')
                        .props(f'id={connection_layer_id}')
                        .classes('w-full h-full')
                    )
                    nodes_layer = (
                        ui.element('div')
                        .props(f'id={nodes_layer_id}')
                        .classes('canvas-nodes')
                    )

            with ui.column().classes('w-full max-w-xs h-full p-6 gap-4 bg-white column-border border-l flex-none'):
                ui.label('右侧栏预留').classes('mt-0 text-xl font-semibold text-slate-800')
                ui.label('此区域可用于显示 Agent 状态、日志或配置。').classes('text-sm text-slate-500')
                ui.element('div').classes('canvas-placeholder flex-1') #no .text('功能待添加') not a actual function yet
            

        # code export dialog
        with ui.dialog().props('persistent') as export_dialog:
            with ui.card().classes('max-w-5xl w-full flex flex-col gap-4 p-6 bg-white overflow-hidden').style('width: min(90vw, 960px); max-height: 80vh;'):
                with ui.row().classes('w-full items-center justify-between gap-3'):
                    ui.label('Agents Pipeline Code').classes('text-xl font-semibold text-slate-800')
                    with ui.row().classes('items-center gap-2'):
                        copy_status_label = ui.label('').classes('text-sm text-slate-500').style('min-width: 160px;')
                        ui.button('Copy code', on_click=copy_pipeline_to_clipboard, color='primary').props('flat')
                        ui.button('Close', on_click=export_dialog.close, color='grey').props('flat')
                export_textarea = (
                    ui.textarea()
                    .props('readonly')
                    .classes('flex-1 w-full text-sm font-mono bg-slate-50 rounded border border-slate-200')
                    .style('min-height: 420px;')
                )

        with ui.dialog() as reset_dialog, ui.card().classes('w-80 gap-3'):
            ui.label('Clear canvas?').classes('text-base font-semibold text-slate-800')
            ui.label('Are you sure you want to clear the canvas? Clearing will also remove your prompt.').classes('text-sm text-slate-600 leading-snug')
            with ui.row().classes('w-full justify-end gap-2 mt-2'):
                ui.button('Cancel', on_click=reset_dialog.close, color='grey')
                ui.button('Clear', color='red', on_click=confirm_clear_canvas)

        await ui.context.client.connected()

        setup_script = f"""
        (function() {{
            const container = document.getElementById('{board_container_id}');
            const svg = document.getElementById('{connection_layer_id}');
            const nodesLayer = document.getElementById('{nodes_layer_id}');
            if (!container || !svg || !nodesLayer) return;
            if (container.dataset.initialized === '1') return;
            container.dataset.initialized = '1';

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

            function cancelTempConnection() {{
                if (tempLine && tempLine.parentNode) {{
                    tempLine.parentNode.removeChild(tempLine);
                }}
                tempLine = null;
                if (connectionStartNode) {{
                    connectionStartNode.classList.remove('node-connecting');
                }}
                connectionStartNode = null;
                connectionStartHandle = null;
                if (pointerMoveHandler) {{
                    window.removeEventListener('pointermove', pointerMoveHandler, true);
                    pointerMoveHandler = null;
                }}
                if (pointerUpHandler) {{
                    window.removeEventListener('pointerup', pointerUpHandler, true);
                    pointerUpHandler = null;
                }}
            }}

            function closeConnectionMenu() {{
                if (activeConnectionMenu && activeConnectionMenu.parentNode) {{
                    activeConnectionMenu.parentNode.removeChild(activeConnectionMenu);
                }}
                activeConnectionMenu = null;
                activeConnectionForMenu = null;
                if (outsideMenuHandler) {{
                    window.removeEventListener('pointerdown', outsideMenuHandler, true);
                    outsideMenuHandler = null;
                }}
            }}

            function clearSelectedNode() {{
                if (selectedNode && selectedNode.parentNode) {{
                    selectedNode.classList.remove('selected');
                }}
                selectedNode = null;
            }}

            function selectNode(node) {{
                if (!node) {{
                    clearSelectedNode();
                    return;
                }}
                if (selectedNode === node) {{
                    return;
                }}
                if (selectedNode && selectedNode.parentNode) {{
                    selectedNode.classList.remove('selected');
                }}
                selectedNode = node;
                selectedNode.classList.add('selected');
            }}

            function removeNode(node) {{
                if (!node) {{
                    return;
                }}
                const nodeId = node.dataset.id;
                closeConnectionMenu();
                connections = connections.filter((connection) => {{
                    if (connection.from === nodeId || connection.to === nodeId) {{
                        if (connection.line && connection.line.parentNode) {{
                            connection.line.parentNode.removeChild(connection.line);
                        }}
                        if (connection.label && connection.label.parentNode) {{
                            connection.label.parentNode.removeChild(connection.label);
                        }}
                        return false;
                    }}
                    return true;
                }});
                node.classList.remove('selected');
                if (node.parentNode) {{
                    node.parentNode.removeChild(node);
                }}
                clearSelectedNode();
            }}

            container.addEventListener('pointerdown', (evt) => {{
                if (evt.target.closest('.canvas-node') || evt.target.closest('.connection-menu')) {{
                    return;
                }}
                clearSelectedNode();
                closeConnectionMenu();
            }});

            function applyConnectionStyle(connection) {{
                const type = connection.metadata?.type || 'direct';
                connection.line.classList.remove('direct', 'rule', 'custom');
                connection.line.classList.add(type);

                const labelText = connection.metadata?.label || '';
                if (labelText) {{
                    if (!connection.label) {{
                        connection.label = createConnectionLabel(labelText);
                    }}
                    if (connection.label) {{
                        connection.label.textContent = labelText;
                    }}
                }} else if (connection.label) {{
                    connection.label.remove();
                    connection.label = null;
                }}
            }}

            function setConnectionMode(connection, mode, labelText = '') {{
                if (!connection) {{
                    return;
                }}
                switch (mode) {{
                    case 'direct':
                        connection.metadata = {{ type: 'direct' }};
                        break;
                    case 'rule':
                        connection.metadata = {{ type: 'rule', label: labelText || '规则' }};
                        break;
                    case 'custom':
                        connection.metadata = {{ type: 'custom', label: labelText || '自定义' }};
                        break;
                    default:
                        connection.metadata = {{ type: 'direct' }};
                        break;
                }}
                applyConnectionStyle(connection);
                updateLine(connection);
            }}

            function openConnectionMenu(connection, evt) {{
                if (!connection) {{
                    return;
                }}
                closeConnectionMenu();
                activeConnectionForMenu = connection;

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

                const repositionMenu = () => {{
                    const menuRect = menu.getBoundingClientRect();
                    let left = evt.clientX - containerRect.left + 12;
                    let top = evt.clientY - containerRect.top - menuRect.height / 2;
                    const maxLeft = containerRect.width - menuRect.width - 12;
                    const maxTop = containerRect.height - menuRect.height - 12;
                    left = Math.max(12, Math.min(left, maxLeft));
                    top = Math.max(12, Math.min(top, maxTop));
                    menu.style.left = left + 'px';
                    menu.style.top = top + 'px';
                }};
                repositionMenu();

                const buttons = menu.querySelectorAll('[data-mode]');
                const inputWrapper = menu.querySelector('.menu-input');
                const infoLine = menu.querySelector('.menu-info');
                const inputField = inputWrapper.querySelector('input');
                const confirmButton = inputWrapper.querySelector('[data-action="confirm"]');

                const currentType = connection.metadata?.type || 'direct';
                buttons.forEach((button) => {{
                    const mode = button.dataset.mode;
                    if (mode === currentType) {{
                        button.classList.add('active');
                    }}
                    button.addEventListener('click', () => {{
                        buttons.forEach((btn) => btn.classList.remove('active'));
                        button.classList.add('active');

                        if (mode === 'direct') {{
                            infoLine.classList.remove('hidden');
                            inputWrapper.classList.add('hidden');
                            delete inputWrapper.dataset.mode;
                            inputField.value = '';
                            setConnectionMode(connection, 'direct');
                            return;
                        }}

                        infoLine.classList.add('hidden');
                        inputWrapper.classList.remove('hidden');
                        inputWrapper.dataset.mode = mode;
                        inputField.placeholder = mode === 'rule' ? '输入规则或条件说明' : '输入自定义标签';
                        inputField.value = connection.metadata?.label || '';
                        requestAnimationFrame(() => inputField.focus());
                    }});
                }});

                if (currentType !== 'direct') {{
                    infoLine.classList.add('hidden');
                    inputWrapper.classList.remove('hidden');
                    inputWrapper.dataset.mode = currentType;
                    inputField.placeholder = currentType === 'rule' ? '输入规则或条件说明' : '输入自定义标签';
                    inputField.value = connection.metadata?.label || '';
                }} else {{
                    infoLine.classList.remove('hidden');
                    inputWrapper.classList.add('hidden');
                    delete inputWrapper.dataset.mode;
                }}

                const commitSelection = () => {{
                    const pendingMode = inputWrapper.dataset.mode;
                    if (!pendingMode) {{
                        return;
                    }}
                    const value = inputField.value.trim();
                    const label = value || (pendingMode === 'rule' ? '规则' : '自定义');
                    setConnectionMode(connection, pendingMode, label);
                    closeConnectionMenu();
                }};

                confirmButton.addEventListener('click', commitSelection);
                inputField.addEventListener('keydown', (event) => {{
                    if (event.key === 'Enter') {{
                        event.preventDefault();
                        commitSelection();
                    }} else if (event.key === 'Escape') {{
                        event.preventDefault();
                        closeConnectionMenu();
                    }}
                }});

                outsideMenuHandler = (event) => {{
                    if (menu.contains(event.target)) {{
                        return;
                    }}
                    closeConnectionMenu();
                }};
                window.addEventListener('pointerdown', outsideMenuHandler, true);

                activeConnectionMenu = menu;
            }}

            function getAnchorPoint(node, direction) {{
                const containerRect = container.getBoundingClientRect();
                if (direction) {{
                    const handle = node.querySelector(`.node-handle.handle-${{direction}}`);
                    if (handle) {{
                        const handleRect = handle.getBoundingClientRect();
                        return {{
                            x: handleRect.left + handleRect.width / 2 - containerRect.left,
                            y: handleRect.top + handleRect.height / 2 - containerRect.top,
                        }};
                    }}
                }}

                const rect = node.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2 - containerRect.left;
                const centerY = rect.top + rect.height / 2 - containerRect.top;

                switch (direction) {{
                    case 'top':
                        return {{ x: centerX, y: rect.top - containerRect.top }};
                    case 'bottom':
                        return {{ x: centerX, y: rect.bottom - containerRect.top }};
                    case 'left':
                        return {{ x: rect.left - containerRect.left, y: centerY }};
                    case 'right':
                        return {{ x: rect.right - containerRect.left, y: centerY }};
                    default:
                        return {{ x: centerX, y: centerY }};
                }}
            }}

            function createConnectionLabel(textContent) {{
                if (!textContent) return null;
                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.classList.add('canvas-label');
                label.textContent = textContent;
                svg.appendChild(label);
                return label;
            }}

            function updateLine(connection) {{
                const nodeA = nodesLayer.querySelector(`[data-id="${{connection.from}}"]`);
                const nodeB = nodesLayer.querySelector(`[data-id="${{connection.to}}"]`);
                if (!nodeA || !nodeB) return;

                const pointA = getAnchorPoint(nodeA, connection.fromDirection || 'top');
                const pointB = getAnchorPoint(nodeB, connection.toDirection || 'top');

                connection.line.setAttribute('x1', pointA.x);
                connection.line.setAttribute('y1', pointA.y);
                connection.line.setAttribute('x2', pointB.x);
                connection.line.setAttribute('y2', pointB.y);

                if (connection.label) {{
                    const midX = (pointA.x + pointB.x) / 2;
                    const midY = (pointA.y + pointB.y) / 2 - 6;
                    connection.label.setAttribute('x', midX);
                    connection.label.setAttribute('y', midY);
                }}
            }}

            function updateConnectionsFor(nodeId) {{
                connections
                    .filter((connection) => connection.from === nodeId || connection.to === nodeId)
                    .forEach(updateLine);
            }}

            function connectNodes(nodeA, handleA, nodeB, handleB) {{
                if (!nodeA || !nodeB || nodeA === nodeB) return;

                const fromDirection = handleA?.dataset?.direction || 'top';
                const toDirection = handleB?.dataset?.direction || 'top';

                const existing = connections.find(
                    (connection) =>
                        (connection.from === nodeA.dataset.id && connection.to === nodeB.dataset.id) ||
                        (connection.from === nodeB.dataset.id && connection.to === nodeA.dataset.id),
                );
                if (existing) {{
                    return;
                }}

                const metadata = {{ type: 'direct' }};

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.classList.add('canvas-connection', metadata.type || 'direct');
                svg.appendChild(line);
                const connection = {{
                    id: ++connectionIdCounter,
                    from: nodeA.dataset.id,
                    to: nodeB.dataset.id,
                    fromDirection,
                    toDirection,
                    line,
                    metadata,
                }};

                line.addEventListener('click', (evt) => {{
                    evt.stopPropagation();
                    openConnectionMenu(connection, evt);
                }});

                connections.push(connection);
                applyConnectionStyle(connection);
                updateLine(connection);
            }}

            function makeDraggable(node) {{
                let offsetX = 0;
                let offsetY = 0;
                let dragging = false;

                node.addEventListener('pointerdown', (evt) => {{
                    closeConnectionMenu();
                    selectNode(node);
                    dragging = true;
                    node.setPointerCapture(evt.pointerId);
                    const rect = container.getBoundingClientRect();
                    offsetX = evt.clientX - rect.left - node.offsetLeft;
                    offsetY = evt.clientY - rect.top - node.offsetTop;
                    node.classList.add('dragging');
                }});

                node.addEventListener('pointermove', (evt) => {{
                    if (!dragging) return;
                    const rect = container.getBoundingClientRect();
                    const x = evt.clientX - rect.left - offsetX;
                    const y = evt.clientY - rect.top - offsetY;
                    const clampedX = Math.max(0, Math.min(rect.width - node.offsetWidth, x));
                    const clampedY = Math.max(0, Math.min(rect.height - node.offsetHeight, y));
                    node.style.left = clampedX + 'px';
                    node.style.top = clampedY + 'px';
                    updateConnectionsFor(node.dataset.id);
                }});

                const stopDragging = (evt) => {{
                    if (!dragging) return;
                    dragging = false;
                    node.releasePointerCapture(evt.pointerId);
                    node.classList.remove('dragging');
                }};

                node.addEventListener('pointerup', stopDragging);
                node.addEventListener('pointercancel', stopDragging);
                node.addEventListener('lostpointercapture', stopDragging);
            }}

            function createNode(title, description) {{
                const node = document.createElement('div');
                const id = `node-${{++nodeCounter}}`;
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
                node.style.left = `${{left}}px`;
                node.style.top = `${{top}}px`;
                node.innerHTML = `
                    <div class="node-handle handle-top" data-direction="top"></div>
                    <div class="node-handle handle-right" data-direction="right"></div>
                    <div class="node-handle handle-bottom" data-direction="bottom"></div>
                    <div class="node-handle handle-left" data-direction="left"></div>
                    <div class="node-title text-base">${{title}}</div>
                    <div class="node-description text-xs font-normal mt-1 text-slate-500 leading-snug">${{description || ''}}</div>
                `;

                node.querySelectorAll('.node-handle').forEach((handle) => {{
                    handle.addEventListener('pointerdown', (evt) => {{
                        evt.stopPropagation();
                        evt.preventDefault();
                        closeConnectionMenu();
                        startConnection(node, handle, evt);
                    }});
                }});

                makeDraggable(node);
                nodesLayer.appendChild(node);
                return id;
            }}

            function handleKeydown(evt) {{
                if (evt.key !== 'Delete' && evt.key !== 'Backspace') {{
                    return;
                }}
                const active = document.activeElement;
                if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) {{
                    return;
                }}
                if (!selectedNode) {{
                    return;
                }}
                evt.preventDefault();
                removeNode(selectedNode);
            }}

            window.addEventListener('keydown', handleKeydown);

            function startConnection(node, handle, evt) {{
                cancelTempConnection();
                connectionStartNode = node;
                connectionStartHandle = handle;
                node.classList.add('node-connecting');

                const containerRect = container.getBoundingClientRect();
                const direction = handle?.dataset?.direction || 'top';
                const startPoint = getAnchorPoint(node, direction);
                const startX = startPoint.x;
                const startY = startPoint.y;

                tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                tempLine.classList.add('canvas-connection', 'temp');
                tempLine.setAttribute('x1', startX);
                tempLine.setAttribute('y1', startY);
                tempLine.setAttribute('x2', startX);
                tempLine.setAttribute('y2', startY);
                svg.appendChild(tempLine);

                pointerMoveHandler = (moveEvt) => {{
                    const x = moveEvt.clientX - containerRect.left;
                    const y = moveEvt.clientY - containerRect.top;
                    tempLine.setAttribute('x2', x);
                    tempLine.setAttribute('y2', y);
                }};

                pointerUpHandler = (upEvt) => {{
                    const targetHandle = upEvt.target && upEvt.target.closest ? upEvt.target.closest('.node-handle') : null;
                    if (targetHandle) {{
                        const targetNode = targetHandle.closest('.canvas-node');
                        if (targetNode && targetNode !== node) {{
                            connectNodes(node, handle, targetNode, targetHandle);
                        }}
                    }}
                    cancelTempConnection();
                }};

                window.addEventListener('pointermove', pointerMoveHandler, true);
                window.addEventListener('pointerup', pointerUpHandler, true);
            }}

            window.addEventListener('resize', () => connections.forEach(updateLine));

            window.board = {{
                addNode(title, description) {{
                    return createNode(title, description);
                }},
                reset() {{
                    nodesLayer.innerHTML = '';
                    svg.innerHTML = '';
                    connections = [];
                    nodeCounter = 0;
                    cancelTempConnection();
                    closeConnectionMenu();
                    clearSelectedNode();
                }},
                getState() {{
                    const nodes = Array.from(nodesLayer.children).map((node) => ({{
                        id: node.dataset.id,
                        title: node.querySelector('.node-title')?.textContent || '',
                        description: node.querySelector('.node-description')?.textContent || '',
                        x: node.offsetLeft,
                        y: node.offsetTop,
                    }}));
                    const edges = connections.map((connection) => ({{
                        id: connection.id,
                        from: connection.from,
                        to: connection.to,
                        from_direction: connection.fromDirection,
                        to_direction: connection.toDirection,
                        type: connection.metadata?.type || 'direct',
                        label: connection.metadata?.label || '',
                    }}));
                    return {{ nodes, edges }};
                }},
            }};
        }})();
        """

        ui.run_javascript(setup_script)

    # Footer
    with ui.footer().classes('bg-white border-t border-gray-200').style('padding: 5px 75px;'):
        with ui.row().classes('w-full justify-between items-center'):
            # Left side
            with ui.row().classes('gap-5 items-center text-xs text-gray-600'):
                ui.label('AGI Agents Studio').classes('font-medium text-gray-800')
                ui.label('•').classes('text-gray-300')
                ui.label('Template lead: YvonneYS-DU')
                ui.label('•').classes('text-gray-300')
                with ui.row().classes('gap-1 items-center'):
                    ui.label('Email:')
                    ui.link('yvdu.ai2077@gmail.com', 'mailto:yvdu.ai2077@gmail.com').classes('text-blue-600 hover:text-blue-700 no-underline')            
            # Right side
            with ui.row().classes('gap-5 items-center text-xs text-gray-600'):
                with ui.row().classes('gap-1 items-center'):
                    ui.label('Portfolio:')
                    ui.link('GitHub', 'https://github.com/YvonneYS-DU', new_tab=True).classes('text-blue-600 hover:text-blue-700 no-underline')
                ui.label('•').classes('text-gray-300')
                ui.label('Location: Remote')

        
if __name__ in {'__main__', '__mp_main__'}:
    ui.run()