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
      background:
        linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)),
        linear-gradient(90deg, rgba(45, 109, 163, 0.05) 1px, transparent 1px),
        linear-gradient(rgba(45, 109, 163, 0.05) 1px, transparent 1px);
      background-size: auto, 24px 24px, 24px 24px;
      overflow: hidden;
    }
    .planner-connections-svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
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
    .planner-node {
      position: absolute;
      width: 280px;
      background: rgba(251, 253, 255, 0.96);
      border: 1px solid var(--line-strong);
      border-radius: 16px;
      box-shadow: 0 16px 28px rgba(24, 34, 44, 0.12);
      overflow: hidden;
    }
    .planner-node.selected {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(45, 109, 163, 0.12), 0 16px 28px rgba(24, 34, 44, 0.12);
    }
    .planner-node-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 12px 14px;
      background: linear-gradient(135deg, rgba(31, 77, 116, 0.94), rgba(45, 109, 163, 0.94));
      color: white;
      cursor: grab;
    }
    .planner-node-header:active {
      cursor: grabbing;
    }
    .planner-node-title {
      font-weight: 700;
    }
    .planner-node-building {
      font-size: 0.82rem;
      color: rgba(255, 255, 255, 0.82);
      margin-top: 4px;
    }
    .planner-node-body {
      padding: 12px 14px 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .planner-node-meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .metric-card {
      background: var(--panel-alt);
      border-radius: 12px;
      padding: 10px;
    }
    .metric-card .label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }
    .metric-card .value {
      margin-top: 4px;
      font-weight: 700;
    }
    .planner-node-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .planner-io-column {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px;
      background: white;
    }
    .planner-io-column.inputs {
      background: var(--input);
    }
    .planner-io-column.outputs {
      background: var(--output);
    }
    .planner-io-column h4 {
      margin: 0 0 8px;
      font-size: 0.92rem;
      font-family: Georgia, serif;
    }
    .mini-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 0.9rem;
    }
    .mini-list-row {
      display: flex;
      justify-content: space-between;
      gap: 8px;
    }
    .planner-node-actions,
    .button-row {
      display: flex;
      gap: 10px;
    }
    .planner-node-actions button,
    .button-row button {
      flex: 1 1 0;
    }
    .planner-summary {
      color: var(--muted);
      font-size: 0.9rem;
      text-align: right;
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
    .edge-line.balanced { stroke: var(--ok); }
    .edge-line.source_surplus { stroke: var(--warn); }
    .edge-line.target_shortage { stroke: var(--danger); }
    .edge-label {
      font-size: 12px;
      font-weight: 700;
      fill: var(--text);
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
      .planner-node-actions,
      .button-row,
      .planner-heading {
        flex-direction: column;
      }
      .planner-summary {
        text-align: left;
      }
    }
"""
