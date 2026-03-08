CSS = """
    :root {
      --bg: #eef3f7;
      --panel: #fbfdff;
      --panel-alt: #e5edf5;
      --accent: #2d6da3;
      --accent-dark: #1f4d74;
      --text: #18222c;
      --muted: #5d6b79;
      --line: #c3d0db;
      --line-strong: #8ca4b8;
      --input: #e8f4ee;
      --output: #edf2fb;
      --danger: #a3472d;
      --warn: #9b6c18;
      --ok: #29734a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #f7fbff 0%, var(--bg) 48%, #e8eef4 100%);
      color: var(--text);
    }
    button,
    input,
    select {
      font: inherit;
    }
    .page {
      max-width: 1760px;
      margin: 0 auto;
      padding: 18px;
    }
    .hero {
      background: linear-gradient(135deg, var(--accent-dark), var(--accent));
      color: white;
      padding: 22px 24px;
      border-radius: 18px;
      box-shadow: 0 16px 32px rgba(31, 77, 116, 0.16);
    }
    .hero h1 {
      margin: 0 0 8px;
      font-family: Georgia, serif;
      font-size: 2rem;
    }
    .hero p {
      margin: 0;
      color: #e7f2fb;
      max-width: 980px;
      line-height: 1.5;
    }
    .mode-switch {
      display: inline-flex;
      gap: 8px;
      margin-top: 16px;
      padding: 8px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.12);
    }
    .mode-button {
      border: 1px solid rgba(255, 255, 255, 0.34);
      background: rgba(255, 255, 255, 0.08);
      color: white;
      border-radius: 12px;
      padding: 10px 16px;
      min-height: 0;
      width: auto;
      box-shadow: none;
    }
    .mode-button.active {
      background: white;
      color: var(--accent-dark);
    }
    .mode-view {
      display: none;
      margin-top: 18px;
    }
    .mode-view.active {
      display: block;
    }
    .content {
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.95fr);
      gap: 20px;
    }
    .panel {
      background: rgba(251, 253, 255, 0.92);
      border: 1px solid rgba(195, 208, 219, 0.95);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 24px rgba(24, 34, 44, 0.06);
      backdrop-filter: blur(10px);
    }
    .panel h2,
    .panel h3 {
      margin: 0;
      font-family: Georgia, serif;
    }
    .panel h2 {
      font-size: 1.35rem;
    }
    .panel h3 {
      font-size: 1.02rem;
    }
    .subtext {
      margin: 6px 0 16px;
      color: var(--muted);
      line-height: 1.45;
    }
    .controls {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) 160px auto;
      gap: 12px;
      align-items: end;
      margin-bottom: 14px;
    }
    .field label,
    .toggle {
      display: block;
      font-size: 0.82rem;
      color: var(--muted);
      margin-bottom: 6px;
    }
    select,
    input[list],
    input[type="number"],
    input[type="search"],
    button {
      width: 100%;
      min-height: 42px;
      border-radius: 12px;
      border: 1px solid var(--line);
      padding: 0 12px;
    }
    select,
    input[list],
    input[type="number"],
    input[type="search"] {
      background: white;
      color: var(--text);
    }
    button {
      background: linear-gradient(135deg, var(--accent), #4f8bc0);
      color: white;
      border: none;
      cursor: pointer;
      font-weight: 600;
      box-shadow: 0 10px 20px rgba(45, 109, 163, 0.18);
    }
    button:hover { filter: brightness(1.04); }
    .secondary-button {
      background: white;
      color: var(--accent-dark);
      border: 1px solid var(--line);
      box-shadow: none;
    }
    input[type="checkbox"] { transform: translateY(1px); }
    .summary {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) repeat(3, minmax(120px, 1fr));
      gap: 12px;
      background: var(--panel-alt);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 14px;
    }
    .summary .name {
      font-family: Georgia, serif;
      font-size: 1.2rem;
      font-weight: 700;
    }
    .summary .debug-id {
      margin-top: 4px;
      font-family: Consolas, monospace;
      font-size: 0.8rem;
      color: var(--muted);
      display: none;
    }
    .summary .metric-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }
    .summary .metric-value {
      margin-top: 4px;
      font-weight: 600;
    }
    .io-sections {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .io-card {
      border-radius: 14px;
      padding: 14px;
      border: 1px solid var(--line);
    }
    .io-card.inputs { background: var(--input); }
    .io-card.outputs { background: var(--output); }
    .io-card h3 {
      margin-bottom: 10px;
    }
    .row-list,
    .results-list,
    .planner-connection-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .row-item {
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(195, 208, 219, 0.9);
      border-radius: 12px;
      padding: 10px 12px;
    }
    .row-top,
    .planner-connection-top,
    .planner-heading {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: baseline;
    }
    .row-name {
      font-weight: 600;
    }
    .row-amount {
      color: var(--muted);
      white-space: nowrap;
    }
    .row-id {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.78rem;
      font-family: Consolas, monospace;
      display: none;
    }
    .search-box {
      background: var(--panel-alt);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 16px;
    }
    .stack-gap {
      margin-top: 10px;
    }
    .result-card {
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      color: var(--text);
      cursor: pointer;
      transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
      text-align: left;
    }
    .result-card:hover {
      transform: translateY(-1px);
      border-color: #8db0ce;
      box-shadow: 0 10px 18px rgba(24, 34, 44, 0.08);
    }
    .result-card.active {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(45, 109, 163, 0.12);
    }
    .result-card .title {
      font-weight: 700;
    }
    .result-card .meta {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.9rem;
    }
    .empty,
    .status {
      color: var(--muted);
    }
    .status {
      margin-top: 14px;
      font-size: 0.92rem;
    }
    .planner-layout {
      display: grid;
      grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
      gap: 20px;
    }
    .planner-section + .planner-section {
      margin-top: 18px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }
    .compact-results .result-card {
      min-height: 0;
    }
    .planner-workspace {
      position: relative;
      min-height: 920px;
      margin-top: 12px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9));
      overflow: hidden;
    }
    .planner-canvas {
      position: absolute;
      inset: 0;
      transform-origin: top left;
      overflow: visible;
      background:
        linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)),
        linear-gradient(90deg, rgba(45, 109, 163, 0.05) 1px, transparent 1px),
        linear-gradient(rgba(45, 109, 163, 0.05) 1px, transparent 1px);
      background-size: auto, 24px 24px, 24px 24px;
    }
    .planner-connections-svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      overflow: visible;
      z-index: 1;
    }
    .planner-connection-labels {
      position: absolute;
      inset: 0;
      pointer-events: none;
      overflow: hidden;
      z-index: 3;
    }
    .planner-empty {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--muted);
      font-size: 1rem;
    }
    .planner-add-popup {
      position: absolute;
      z-index: 5;
      width: 320px;
      max-width: calc(100% - 24px);
    }
    .planner-add-popup-card {
      background: rgba(251, 253, 255, 0.98);
      border: 1px solid var(--line-strong);
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 18px 30px rgba(24, 34, 44, 0.16);
    }
    .planner-add-popup-card h3 {
      margin-bottom: 12px;
      font-size: 1rem;
      font-family: Georgia, serif;
    }
    .planner-target-popup {
      position: absolute;
      z-index: 6;
      width: 220px;
      max-width: calc(100% - 24px);
    }
    .planner-target-popup-card {
      background: rgba(251, 253, 255, 0.98);
      border: 1px solid var(--line-strong);
      border-radius: 14px;
      padding: 12px;
      box-shadow: 0 18px 30px rgba(24, 34, 44, 0.16);
    }
    .planner-target-popup-card h3 {
      margin: 0 0 10px;
      font-size: 0.95rem;
      font-family: Georgia, serif;
    }
    .planner-node {
      position: absolute;
      width: 200px;
      background: rgba(251, 253, 255, 0.96);
      border: 1px solid var(--line-strong);
      border-radius: 12px;
      box-shadow: 0 8px 18px rgba(24, 34, 44, 0.1);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .planner-node.selected {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(45, 109, 163, 0.12), 0 10px 22px rgba(24, 34, 44, 0.12);
    }
    .planner-node-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      padding: 7px 8px;
      background: linear-gradient(135deg, rgba(31, 77, 116, 0.94), rgba(45, 109, 163, 0.94));
      color: white;
      cursor: grab;
    }
    .planner-node-header:active {
      cursor: grabbing;
    }
    .planner-node-title {
      font-weight: 700;
      font-size: 0.78rem;
      line-height: 1.05;
    }
    .planner-node-building {
      font-size: 0.62rem;
      color: rgba(255, 255, 255, 0.82);
      margin-top: 1px;
    }
    .planner-node-body {
      padding: 7px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      overflow: auto;
      flex: 1 1 auto;
    }
    .planner-node-meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
    }
    .planner-node-meta.compact {
      grid-template-columns: 1fr;
    }
    .metric-card {
      background: var(--panel-alt);
      border-radius: 10px;
      padding: 5px 7px;
    }
    .metric-card.wide {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 6px;
    }
    .metric-card .label {
      font-size: 0.54rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }
    .metric-card .value {
      font-weight: 700;
      font-size: 0.86rem;
    }
    .planner-balance-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-top: 4px;
    }
    .planner-balance-row {
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr) auto;
      gap: 5px;
      align-items: center;
      border-radius: 8px;
      padding: 4px 6px;
      background: rgba(255, 255, 255, 0.55);
      font-size: 0.68rem;
    }
    .planner-balance-row.balanced {
      border: 1px solid rgba(41, 115, 74, 0.2);
    }
    .planner-balance-row.source_surplus {
      border: 1px solid rgba(155, 108, 24, 0.26);
    }
    .planner-balance-row.target_shortage {
      border: 1px solid rgba(163, 71, 45, 0.26);
    }
    .planner-balance-side {
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .planner-balance-item {
      min-width: 0;
      overflow-wrap: anywhere;
      font-weight: 600;
      line-height: 1.05;
    }
    .planner-balance-rates {
      white-space: nowrap;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }
    .planner-node-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      align-items: start;
      min-width: 0;
    }
    .planner-io-column {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 5px;
      background: white;
      min-width: 0;
      overflow: hidden;
    }
    .planner-io-column.inputs {
      background: var(--input);
    }
    .planner-io-column.outputs {
      background: var(--output);
    }
    .planner-io-column h4 {
      margin: 0 0 4px;
      font-size: 0.74rem;
      font-family: Georgia, serif;
      line-height: 1;
    }
    .mini-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.72rem;
      min-width: 0;
    }
    .mini-list-row {
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
      border: 1px solid transparent;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.55);
      padding: 4px 5px;
      text-align: left;
      min-width: 0;
    }
    .planner-port {
      cursor: pointer;
      box-shadow: none;
      color: var(--text);
    }
    .planner-port:hover {
      border-color: rgba(45, 109, 163, 0.28);
      background: rgba(255, 255, 255, 0.82);
    }
    .planner-port.is-target {
      border-color: rgba(45, 109, 163, 0.32);
      background: rgba(45, 109, 163, 0.03);
      box-shadow: inset 3px 0 0 rgba(45, 109, 163, 0.4);
    }
    .planner-port-handle {
      flex: 0 0 8px;
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--line-strong);
    }
    .planner-port-handle.input {
      background: #5d8f76;
    }
    .planner-port-handle.output {
      background: #4d7ea8;
    }
    .planner-port-name {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1 1 auto;
      font-weight: 600;
      overflow-wrap: anywhere;
      line-height: 1.05;
    }
    .planner-port-amount {
      margin-left: auto;
      color: var(--muted);
      font-weight: 500;
      white-space: nowrap;
      flex: 0 0 auto;
      font-size: 0.68rem;
    }
    .node-remove-button {
      min-height: 0;
      padding: 4px 8px;
      font-size: 0.68rem;
      line-height: 1;
      border-radius: 999px;
      box-shadow: none;
    }
    .planner-resize-handle {
      position: absolute;
      background: transparent;
      z-index: 4;
    }
    .planner-resize-handle.left,
    .planner-resize-handle.right {
      top: 18px;
      bottom: 18px;
      width: 10px;
    }
    .planner-resize-handle.left {
      left: -5px;
      cursor: ew-resize;
    }
    .planner-resize-handle.right {
      right: -5px;
      cursor: ew-resize;
    }
    .planner-resize-handle.top,
    .planner-resize-handle.bottom {
      left: 18px;
      right: 18px;
      height: 10px;
    }
    .planner-resize-handle.top {
      top: -5px;
      cursor: ns-resize;
    }
    .planner-resize-handle.bottom {
      bottom: -5px;
      cursor: ns-resize;
    }
    .button-row {
      display: flex;
      gap: 10px;
    }
    .button-row button {
      flex: 1 1 0;
    }
    .planner-summary {
      color: var(--muted);
      font-size: 0.9rem;
      text-align: right;
    }
    .planner-path {
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.45;
      word-break: break-word;
    }
    .planner-heading-actions {
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: flex-end;
    }
    .planner-zoom-controls {
      display: inline-flex;
      gap: 8px;
      align-items: center;
    }
    .planner-zoom-controls button {
      min-height: 0;
      width: auto;
      padding: 8px 12px;
    }
    .planner-subtext {
      margin-bottom: 0;
    }
    .planner-connection-card {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      background: white;
    }
    .planner-connection-meta,
    .planner-connection-rates {
      margin-top: 6px;
      color: var(--muted);
      font-size: 0.9rem;
    }
    .planner-status-pill {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 0.78rem;
      font-weight: 700;
      background: var(--panel-alt);
      color: var(--text);
    }
    .planner-status-balanced {
      background: rgba(41, 115, 74, 0.14);
      color: var(--ok);
    }
    .planner-status-source-surplus {
      background: rgba(155, 108, 24, 0.14);
      color: var(--warn);
    }
    .planner-status-target-shortage {
      background: rgba(163, 71, 45, 0.14);
      color: var(--danger);
    }
    .edge-line {
      fill: none;
      stroke-width: 3;
      opacity: 0.88;
    }
    .edge-preview {
      stroke-dasharray: 8 6;
      opacity: 0.7;
    }
    .edge-line.balanced {
      stroke: var(--ok);
      color: var(--ok);
    }
    .edge-line.source_surplus {
      stroke: var(--warn);
      color: var(--warn);
    }
    .edge-line.target_shortage {
      stroke: var(--danger);
      color: var(--danger);
    }
    .edge-label {
      font-size: 15px;
      font-weight: 700;
      fill: var(--text);
    }
    .planner-connection-label {
      position: absolute;
      transform: translate(-50%, -50%);
      width: 26px;
      height: 26px;
      padding: 0;
      border-radius: 999px;
      border: 1px solid rgba(140, 164, 184, 0.9);
      background: rgba(251, 253, 255, 0.96);
      color: var(--text);
      box-shadow: 0 8px 18px rgba(24, 34, 44, 0.12);
      pointer-events: auto;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .planner-connection-label.balanced {
      border-color: rgba(41, 115, 74, 0.35);
    }
    .planner-connection-label.source_surplus {
      border-color: rgba(155, 108, 24, 0.42);
    }
    .planner-connection-label.target_shortage {
      border-color: rgba(163, 71, 45, 0.42);
    }
    .connection-delete-button {
      min-height: 0;
      width: 18px;
      height: 18px;
      padding: 0;
      box-shadow: none;
      border-radius: 999px;
      background: rgba(24, 34, 44, 0.08);
      color: var(--text);
    }
    .node-remove-button,
    .connection-remove-button {
      min-height: 0;
      width: auto;
      padding: 6px 10px;
      box-shadow: none;
      background: rgba(255, 255, 255, 0.18);
    }
    .connection-remove-button {
      color: var(--accent-dark);
      background: var(--panel-alt);
      border: 1px solid var(--line);
    }
    @media (max-width: 1120px) {
      .content,
      .planner-layout {
        grid-template-columns: 1fr;
      }
    }
    @media (max-width: 760px) {
      .controls,
      .summary,
      .io-sections,
      .planner-node-grid,
      .planner-node-meta {
        grid-template-columns: 1fr;
      }
      .page { padding: 12px; }
      .planner-node {
        width: min(280px, calc(100% - 24px));
      }
      .button-row,
      .planner-heading {
        flex-direction: column;
      }
      .planner-summary {
        text-align: left;
      }
    }
"""
