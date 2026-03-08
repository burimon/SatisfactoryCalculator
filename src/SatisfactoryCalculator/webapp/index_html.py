from .app_script import SCRIPT
from .browser_view import BROWSER_VIEW
from .planner_view import PLANNER_VIEW
from .styles import CSS

HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Satisfactory Recipe Browser</title>
  <style>
{CSS}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>Satisfactory Recipe Browser</h1>
      <p>
        Browse recipe details, compare production rates, and build a local workflow plan by
        connecting recipe nodes with explicit item flow.
      </p>
      <div class="mode-switch" role="tablist" aria-label="Application mode">
        <button type="button" class="mode-button active" data-mode="browser">Browser</button>
        <button type="button" class="mode-button" data-mode="planner">Planner</button>
      </div>
    </section>
{BROWSER_VIEW}
{PLANNER_VIEW}
    <div id="status" class="status">Loading recipes...</div>
  </div>
  <script>
{SCRIPT}
  </script>
</body>
</html>
"""
