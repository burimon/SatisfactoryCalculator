BROWSER_VIEW = """
    <section id="browser-view" class="mode-view active">
      <section class="content">
        <section class="panel">
          <h2>Recipe Details</h2>
          <p class="subtext">
            Inspect the selected recipe as structured data with readable inputs and outputs.
          </p>
          <div class="controls">
            <div class="field">
              <label for="recipe-input">Recipe</label>
              <input id="recipe-input" list="recipe-options" type="search" autocomplete="off">
              <datalist id="recipe-options"></datalist>
            </div>
            <div class="field">
              <label for="rate-select">Rate View</label>
              <select id="rate-select">
                <option value="per_cycle">Per Cycle</option>
                <option value="per_second">Per Second</option>
                <option value="per_minute">Per Minute</option>
              </select>
            </div>
            <label class="toggle"><input id="debug-toggle" type="checkbox"> Debug ids</label>
          </div>
          <div class="summary">
            <div>
              <div id="recipe-name" class="name"></div>
              <div id="recipe-id" class="debug-id"></div>
            </div>
            <div>
              <div class="metric-label">Building</div>
              <div id="recipe-building" class="metric-value"></div>
            </div>
            <div>
              <div class="metric-label">Cycle Time</div>
              <div id="recipe-cycle" class="metric-value"></div>
            </div>
            <div>
              <div class="metric-label">Rate View</div>
              <div id="recipe-rate" class="metric-value"></div>
            </div>
          </div>
          <div class="io-sections">
            <section class="io-card inputs">
              <h3>Inputs</h3>
              <div id="inputs-list" class="row-list"></div>
            </section>
            <section class="io-card outputs">
              <h3>Outputs</h3>
              <div id="outputs-list" class="row-list"></div>
            </section>
          </div>
        </section>
        <section class="panel">
          <h2>Find Recipes By Output</h2>
          <p class="subtext">
            Use official item labels in the UI, then load any result back into the detail view.
          </p>
          <div class="search-box">
            <div class="field">
              <label for="output-input">Output Item</label>
              <input id="output-input" list="output-options" type="search" autocomplete="off">
              <datalist id="output-options"></datalist>
            </div>
            <div class="stack-gap">
              <button id="search-button" type="button">Find Recipes</button>
            </div>
          </div>
          <div id="results-list" class="results-list"></div>
        </section>
      </section>
    </section>
"""
