#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from nicegui import ui

try:
    from .templates import AGENT_TEMPLATES
except ImportError:  # pragma: no cover - allows direct script execution
    from templates import AGENT_TEMPLATES

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
STYLES_CSS = (ASSETS_DIR / 'styles.css').read_text(encoding='utf-8')
BOARD_SCRIPT_TEMPLATE = (ASSETS_DIR / 'board.js').read_text(encoding='utf-8')


def _format_select_options(agents: Iterable[dict[str, str]]) -> dict[str, str]:
    return {agent['id']: agent['name'] for agent in agents}


class AgentsBoardPage:
    def __init__(self, agents: list[dict[str, str]]) -> None:
        self.agents = agents
        self.reset_dialog: ui.dialog | None = None
        self.export_dialog: ui.dialog | None = None
        self.export_textarea: ui.textarea | None = None
        self.copy_status_label: ui.label | None = None
        self.selected_agent: ui.select | None = None

        self.board_container_id = f'board-container-{uuid4().hex}'
        self.connection_layer_id = f'board-connection-{uuid4().hex}'
        self.nodes_layer_id = f'board-nodes-{uuid4().hex}'

    async def render(self) -> None:
        self._apply_styles()
        self._build_layout()
        self._build_footer()

        await ui.context.client.connected()
        self._initialize_board()

    def _apply_styles(self) -> None:
        ui.add_css(STYLES_CSS)

    def _build_layout(self) -> None:
        with ui.column().classes('absolute inset-0 w-full h-full overflow-hidden gap-0'):
            with ui.row().classes('w-full flex-1 no-wrap overflow-hidden items-stretch'):
                self._build_left_panel()
                self._build_canvas_panel()
                self._build_right_panel()

            self._build_export_dialog()
            self._build_reset_dialog()

    def _build_left_panel(self) -> None:
        with ui.column().classes('w-full max-w-xs h-full p-6 gap-4 bg-white column-border border-r flex-none'):
            ui.label('Choose/Build Agent').classes('mt-0 text-xl font-semibold text-slate-800')

            default_agent_id = self.agents[0]['id'] if self.agents else None
            self.selected_agent = (
                ui.select(
                    _format_select_options(self.agents),
                    label='Choose from Agent Templates',
                    value=default_agent_id,
                    with_input=True,
                )
                .props('dense outlined rounded use-input fill-input input-debounce="0" clearable')
                .classes('w-full')
            )

            with ui.row().classes('w-full gap-2'):
                export_button = ui.button('Export\nAGENTs code', on_click=self.export_agents_pipeline, color='primary')
                reset_button = ui.button('Reset\nAGENTs canvas', on_click=self.prompt_reset_canvas, color='grey')
                export_button.classes('flex-1 mt-2').style('font-size: 0.75rem; white-space: pre-line; line-height: 1.2;')
                reset_button.classes('flex-1 mt-2').style('font-size: 0.75rem; white-space: pre-line; line-height: 1.2;')

            ui.separator()
            ui.label('Agent Templates List').classes('text-base font-medium text-slate-700')

            with ui.column().classes('gap-3 overflow-y-auto pr-1 flex-1'):
                for agent in self.agents:
                    card = ui.card().classes('agent-card w-full cursor-pointer hover:shadow-lg transition')
                    card.on('click', lambda _=None, data=agent: self._handle_agent_card_click(data))
                    with card:
                        ui.label(agent['name']).classes('agent-name')
                        ui.label(agent['description']).classes('agent-desc')

    def _build_canvas_panel(self) -> None:
        with ui.column().classes('flex-1 h-full p-6'):
            ui.label('AGENTs Flow Canvas').classes('mt-0 text-xl font-semibold text-slate-800 mb-2')

            board_container = (
                ui.element('div')
                .props(f'id={self.board_container_id}')
                .classes('canvas-container w-full h-full')
                .style('height: 100%;')
            )

            with board_container:
                ui.element('svg').props(f'id={self.connection_layer_id}').classes('w-full h-full')
                ui.element('div').props(f'id={self.nodes_layer_id}').classes('canvas-nodes')

    def _build_right_panel(self) -> None:
        with ui.column().classes('w-full max-w-xs h-full p-6 gap-4 bg-white column-border border-l flex-none'):
            ui.label('右侧栏预留').classes('mt-0 text-xl font-semibold text-slate-800')
            ui.label('此区域可用于显示 Agent 状态、日志或配置。').classes('text-sm text-slate-500')
            ui.element('div').classes('canvas-placeholder flex-1')

    def _build_export_dialog(self) -> None:
        with ui.dialog().props('persistent') as self.export_dialog:
            with ui.card().classes('max-w-5xl w-full flex flex-col gap-4 p-6 bg-white overflow-hidden').style(
                'width: min(90vw, 960px); max-height: 80vh;'
            ):
                with ui.row().classes('w-full items-center justify-between gap-3'):
                    ui.label('Agents Pipeline Code').classes('text-xl font-semibold text-slate-800')
                    with ui.row().classes('items-center gap-2'):
                        self.copy_status_label = ui.label('').classes('text-sm text-slate-500').style('min-width: 160px;')
                        ui.button('Copy code', on_click=self.copy_pipeline_to_clipboard, color='primary').props('flat')
                        ui.button('Close', on_click=self.export_dialog.close, color='grey').props('flat')
                self.export_textarea = (
                    ui.textarea()
                    .props('readonly')
                    .classes('flex-1 w-full text-sm font-mono bg-slate-50 rounded border border-slate-200')
                    .style('min-height: 420px;')
                )

    def _build_reset_dialog(self) -> None:
        with ui.dialog() as self.reset_dialog, ui.card().classes('w-80 gap-3'):
            ui.label('Clear canvas?').classes('text-base font-semibold text-slate-800')
            ui.label('Are you sure you want to clear the canvas? Clearing will also remove your prompt.').classes(
                'text-sm text-slate-600 leading-snug'
            )
            with ui.row().classes('w-full justify-end gap-2 mt-2'):
                ui.button('Cancel', on_click=self.reset_dialog.close, color='grey')
                ui.button('Clear', color='red', on_click=self.confirm_clear_canvas)

    def _build_footer(self) -> None:
        with ui.footer().classes('bg-white border-t border-gray-200').style('padding: 5px 75px;'):
            with ui.row().classes('w-full justify-between items-center'):
                with ui.row().classes('gap-5 items-center text-xs text-gray-600'):
                    ui.label('AGI Agents Studio').classes('font-medium text-gray-800')
                    ui.label('•').classes('text-gray-300')
                    ui.label('Template lead: YvonneYS-DU')
                    ui.label('•').classes('text-gray-300')
                    with ui.row().classes('gap-1 items-center'):
                        ui.label('Email:')
                        ui.link('yvdu.ai2077@gmail.com', 'mailto:yvdu.ai2077@gmail.com').classes(
                            'text-blue-600 hover:text-blue-700 no-underline'
                        )
                with ui.row().classes('gap-5 items-center text-xs text-gray-600'):
                    with ui.row().classes('gap-1 items-center'):
                        ui.label('Portfolio:')
                        ui.link('GitHub', 'https://github.com/YvonneYS-DU', new_tab=True).classes(
                            'text-blue-600 hover:text-blue-700 no-underline'
                        )
                    ui.label('•').classes('text-gray-300')
                    ui.label('Location: Remote')

    def _initialize_board(self) -> None:
        script = (
            BOARD_SCRIPT_TEMPLATE
            .replace('__BOARD_CONTAINER_ID__', self.board_container_id)
            .replace('__CONNECTION_LAYER_ID__', self.connection_layer_id)
            .replace('__NODES_LAYER_ID__', self.nodes_layer_id)
        )
        ui.run_javascript(script)

    def _handle_agent_card_click(self, agent_data: dict[str, str]) -> None:
        if self.selected_agent:
            self.selected_agent.value = agent_data['id']
        self.spawn_agent(agent_data)

    def prompt_reset_canvas(self) -> None:
        if self.reset_dialog:
            self.reset_dialog.open()

    def confirm_clear_canvas(self) -> None:
        ui.run_javascript('window.board?.reset()')
        ui.run_javascript("window.dispatchEvent(new CustomEvent('canvas-cleared'))")
        ui.notify('Canvas has been cleared. Your prompt has been removed.', type='info', position='top')
        if self.reset_dialog:
            self.reset_dialog.close()

    async def export_agents_pipeline(self) -> None:
        if self.export_dialog:
            self.export_dialog.open()
        if self.copy_status_label:
            self.copy_status_label.set_text('Agents canvas python code loaded...')

        try:
            result = await ui.run_javascript(
                'return window.board?.getState?.() || {nodes: [], edges: []};',
                respond=True,
            )
        except RuntimeError:
            if self.copy_status_label:
                self.copy_status_label.set_text('Failed to read canvas. Please try again.')
            ui.notify('Failed to read canvas state.', type='negative', position='top')
            return

        formatted = json.dumps(result, ensure_ascii=False, indent=2)
        if self.export_textarea:
            self.export_textarea.value = formatted
        if self.copy_status_label:
            self.copy_status_label.set_text('Ready to copy.')

    async def copy_pipeline_to_clipboard(self) -> None:
        if not self.export_textarea:
            return
        text_value = self.export_textarea.value or ''
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

        if self.copy_status_label:
            self.copy_status_label.set_text(
                'Copied to clipboard.' if success else 'Copy failed. Please copy manually.'
            )

    def spawn_agent(self, agent_item: dict[str, str]) -> None:
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
                const push = () => window.board?.addNode?.(payload.title, payload.description);
                if (typeof window.board?.addNode === 'function') {{
                    push();
                }} else {{
                    window.__boardPending = window.__boardPending || [];
                    window.__boardPending.push(payload);
                }}
            }})();
            '''
        )


@ui.page('/')
async def main() -> None:
    page = AgentsBoardPage(AGENT_TEMPLATES)
    await page.render()


if __name__ in {'__main__', '__mp_main__'}:
    ui.run()