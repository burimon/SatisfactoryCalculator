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
              <label for="planner-default-belt">Global Belt Limit</label>
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
            <h3>Workflow</h3>
            <div class="field">
              <label for="planner-workflow-name">Workflow Name</label>
              <input
                id="planner-workflow-name"
                type="text"
                maxlength="80"
                placeholder="My factory plan"
                autocomplete="off"
              >
            </div>
            <div class="field">
              <label for="planner-saved-workflows">Saved Workflows</label>
              <select id="planner-saved-workflows"></select>
            </div>
            <div id="planner-workflow-directory" class="planner-path"></div>
            <div class="button-row">
              <button id="new-workflow-button" type="button" class="secondary-button">
                New Plan
              </button>
              <button id="export-workflow-button" type="button">Export JSON</button>
              <button
                id="import-workflow-button"
                type="button"
                class="secondary-button"
              >
                Import JSON
              </button>
            </div>
            <div class="stack-gap">
              <button id="planner-refresh-workflows" type="button" class="secondary-button">
                Refresh Saved Workflows
              </button>
            </div>
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
            <div class="planner-heading-actions">
              <div class="planner-zoom-controls">
                <button id="planner-zoom-out" type="button" class="secondary-button">-</button>
                <button id="planner-zoom-reset" type="button" class="secondary-button">100%</button>
                <button id="planner-zoom-in" type="button" class="secondary-button">+</button>
              </div>
              <div id="planner-summary" class="planner-summary">No nodes yet.</div>
            </div>
          </div>
          <section class="planner-net-balance-section">
            <div class="planner-net-balance-header">
              <div>
                <h3>Plan Net Balance</h3>
                <p class="subtext planner-net-balance-subtext">
                  Combined output minus input rate across the full workflow.
                </p>
              </div>
            </div>
            <div id="planner-net-balance" class="planner-net-balance"></div>
          </section>
          <div id="planner-workspace" class="planner-workspace">
            <div id="planner-canvas" class="planner-canvas">
              <svg id="planner-connections-svg" class="planner-connections-svg"></svg>
            </div>
            <div id="planner-connection-labels" class="planner-connection-labels"></div>
            <div id="planner-target-popup" class="planner-target-popup" hidden>
              <div class="planner-target-popup-card">
                <h3 id="planner-target-popup-title">Target</h3>
                <div class="field">
                  <label for="planner-target-popup-rate">Amount</label>
                  <input
                    id="planner-target-popup-rate"
                    type="number"
                    min="0"
                    step="0.1"
                    autocomplete="off"
                  >
                </div>
                <div class="button-row">
                  <button id="planner-target-popup-save" type="button">Apply</button>
                  <button
                    id="planner-target-popup-cancel"
                    type="button"
                    class="secondary-button"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
            <div id="planner-add-popup" class="planner-add-popup" hidden>
              <div class="planner-add-popup-card">
                <h3>Add Node</h3>
                <div class="field">
                  <label for="planner-popup-output-input">Output Item</label>
                  <input
                    id="planner-popup-output-input"
                    list="planner-popup-output-options"
                    type="search"
                    autocomplete="off"
                  >
                  <datalist id="planner-popup-output-options"></datalist>
                </div>
                <div class="button-row">
                  <button id="planner-popup-search" type="button">Find Recipes</button>
                  <button id="planner-popup-cancel" type="button" class="secondary-button">
                    Cancel
                  </button>
                </div>
                <div class="field">
                  <label for="planner-popup-recipe">Recipe</label>
                  <select id="planner-popup-recipe"></select>
                </div>
                <div class="button-row">
                  <button id="planner-popup-confirm" type="button">Add Node</button>
                </div>
              </div>
            </div>
            <div id="planner-empty" class="planner-empty">
              Add a node from an output item to start a workflow.
            </div>
          </div>
        </section>
      </section>
    </section>
"""
