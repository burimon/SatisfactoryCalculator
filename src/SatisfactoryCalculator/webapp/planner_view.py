PLANNER_VIEW = """
    <section id="planner-view" class="mode-view">
      <section class="planner-layout">
        <section class="panel planner-sidebar">
          <h2>Planner Controls</h2>
          <p class="subtext">
            Build a workflow from output items, connect nodes by matching item flow,
            and export the result.
          </p>

          <div class="planner-section">
            <h3>Add Node</h3>
            <div class="field">
              <label for="planner-default-belt">Default Belt Limit</label>
              <select id="planner-default-belt"></select>
            </div>
            <div class="field">
              <label for="planner-output-input">Output Item</label>
              <input
                id="planner-output-input"
                list="planner-output-options"
                type="search"
                autocomplete="off"
              >
              <datalist id="planner-output-options"></datalist>
            </div>
            <div class="stack-gap">
              <button id="planner-search-button" type="button">Find Producer Recipes</button>
            </div>
            <div id="planner-recipe-results" class="results-list compact-results"></div>
          </div>

          <div class="planner-section">
            <h3>Connections</h3>
            <div class="field">
              <label for="connection-source">Source Node</label>
              <select id="connection-source"></select>
            </div>
            <div class="field">
              <label for="connection-target">Target Node</label>
              <select id="connection-target"></select>
            </div>
            <div class="field">
              <label for="connection-item">Item</label>
              <select id="connection-item"></select>
            </div>
            <div class="stack-gap">
              <button id="add-connection-button" type="button">Connect Nodes</button>
            </div>
            <div id="planner-connections" class="planner-connection-list"></div>
          </div>

          <div class="planner-section">
            <h3>Workflow</h3>
            <div class="button-row">
              <button id="export-workflow-button" type="button">Export JSON</button>
              <button
                id="import-workflow-button"
                type="button"
                class="secondary-button"
              >
                Import JSON
              </button>
            </div>
            <input id="import-workflow-input" type="file" accept="application/json" hidden>
          </div>
        </section>

        <section class="panel planner-workspace-panel">
          <div class="planner-heading">
            <div>
              <h2>Workflow Planner</h2>
              <p class="subtext planner-subtext">
                Drag nodes to arrange the flow. Edit target output rates per minute on each recipe.
              </p>
            </div>
            <div id="planner-summary" class="planner-summary">No nodes yet.</div>
          </div>
          <div id="planner-workspace" class="planner-workspace">
            <svg id="planner-connections-svg" class="planner-connections-svg"></svg>
            <div id="planner-empty" class="planner-empty">
              Add a node from an output item to start a workflow.
            </div>
          </div>
        </section>
      </section>
    </section>
"""
