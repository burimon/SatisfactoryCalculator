# ruff: isort: skip_file

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from SatisfactoryCalculator.recipes import Item, Recipe, get_recipe
from SatisfactoryCalculator.webapp.planner import (
    PlannerEdge,
    PlannerNode,
    WORKFLOW_VERSION,
    Workflow,
    WorkflowValidationError,
    aggregate_connection_imbalance,
    connection_imbalance,
    scale_recipe_for_target,
    workflow_from_payload,
    workflow_to_payload,
)


class PlannerTests(unittest.TestCase):
    def test_scale_recipe_for_target_uses_target_output_rate(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("iron_plate"), "iron_plate", 40.0)
        self.assertEqual(scaled["multiplier"], 2.0)
        self.assertEqual(scaled["requested_target_rate"], 40.0)
        self.assertEqual(scaled["per_machine_rate"], 20.0)
        self.assertEqual(scaled["machine_count"], 2.0)
        self.assertEqual(scaled["outputs"]["iron_plate"], 40.0)
        self.assertEqual(scaled["inputs"]["iron_ingot"], 60.0)

    def test_scale_recipe_for_target_uses_belt_limit_for_machine_count(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("wire"), "wire", 90.0, belt_capacity=60.0)
        self.assertEqual(scaled["requested_target_rate"], 90.0)
        self.assertEqual(scaled["per_machine_rate"], 30.0)
        self.assertEqual(scaled["machine_count"], 3.0)
        self.assertEqual(scaled["outputs"]["wire"], 90.0)
        self.assertEqual(scaled["inputs"]["copper_ingot"], 45.0)

    def test_scale_recipe_for_target_uses_input_belt_limit_for_machine_count(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("iron_plate"), "iron_plate", 40.0, 20.0)
        self.assertEqual(scaled["requested_target_rate"], 40.0)
        self.assertEqual(scaled["per_machine_rate"], 20.0)
        self.assertEqual(scaled["machine_count"], 3.0)
        self.assertEqual(scaled["outputs"]["iron_plate"], 40.0)
        self.assertEqual(scaled["inputs"]["iron_ingot"], 60.0)

    def test_scale_recipe_for_target_handles_multiple_inputs(self) -> None:
        scaled = scale_recipe_for_target(
            get_recipe("reinforced_iron_plate"),
            "reinforced_iron_plate",
            10.0,
        )
        self.assertEqual(scaled["inputs"]["iron_plate"], 60.0)
        self.assertEqual(scaled["inputs"]["screw"], 120.0)

    def test_scale_recipe_for_target_handles_multiple_outputs(self) -> None:
        recipe = Recipe(
            id="test_dual_output",
            name="Test Dual Output",
            inputs={Item.IRON_ORE: 1},
            outputs={Item.IRON_INGOT: 2, Item.COPPER_INGOT: 1},
            duration_seconds=6.0,
            building="smelter",
        )
        scaled = scale_recipe_for_target(recipe, "copper_ingot", 20.0)
        self.assertEqual(scaled["multiplier"], 2.0)
        self.assertEqual(scaled["outputs"]["iron_ingot"], 40.0)
        self.assertEqual(scaled["outputs"]["copper_ingot"], 20.0)

    def test_scale_recipe_for_target_allows_input_item_targets(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("iron_plate"), "iron_ingot", 30.0)
        self.assertEqual(scaled["multiplier"], 1.0)
        self.assertEqual(scaled["inputs"]["iron_ingot"], 30.0)
        self.assertEqual(scaled["outputs"]["iron_plate"], 20.0)

    def test_scale_recipe_for_target_applies_belt_limit_to_input_targets(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("iron_plate"), "iron_ingot", 60.0, 20.0)
        self.assertEqual(scaled["per_machine_rate"], 20.0)
        self.assertEqual(scaled["machine_count"], 3.0)

    def test_scale_recipe_for_target_keeps_power_in_mw_units(self) -> None:
        scaled = scale_recipe_for_target(get_recipe("power_biomass"), "power", 30.0)
        self.assertEqual(scaled["multiplier"], 1.0)
        self.assertEqual(scaled["requested_target_rate"], 30.0)
        self.assertEqual(scaled["per_machine_rate"], 30.0)
        self.assertEqual(scaled["machine_count"], 1.0)
        self.assertEqual(scaled["outputs"]["power"], 30.0)
        self.assertEqual(scaled["inputs"]["biomass"], 10.0)

    def test_connection_imbalance_balanced(self) -> None:
        result = connection_imbalance(
            source_recipe=get_recipe("iron_ingot"),
            source_target_item_id="iron_ingot",
            source_target_rate_per_minute=30.0,
            target_recipe=get_recipe("iron_plate"),
            target_target_item_id="iron_plate",
            target_target_rate_per_minute=20.0,
            item_id="iron_ingot",
        )
        self.assertEqual(result["status"], "balanced")
        self.assertEqual(result["delta"], 0.0)

    def test_connection_imbalance_source_surplus(self) -> None:
        result = connection_imbalance(
            source_recipe=get_recipe("iron_ingot"),
            source_target_item_id="iron_ingot",
            source_target_rate_per_minute=60.0,
            target_recipe=get_recipe("iron_plate"),
            target_target_item_id="iron_plate",
            target_target_rate_per_minute=20.0,
            item_id="iron_ingot",
        )
        self.assertEqual(result["status"], "source_surplus")
        self.assertEqual(result["delta"], 30.0)

    def test_connection_imbalance_target_shortage(self) -> None:
        result = connection_imbalance(
            source_recipe=get_recipe("iron_ingot"),
            source_target_item_id="iron_ingot",
            source_target_rate_per_minute=15.0,
            target_recipe=get_recipe("iron_plate"),
            target_target_item_id="iron_plate",
            target_target_rate_per_minute=20.0,
            item_id="iron_ingot",
        )
        self.assertEqual(result["status"], "target_shortage")
        self.assertEqual(result["delta"], -15.0)

    def test_aggregate_connection_imbalance_allows_multiple_sources(self) -> None:
        result = aggregate_connection_imbalance([20.0, 10.0], 30.0)
        self.assertEqual(result["status"], "balanced")
        self.assertEqual(result["total_source_rate"], 30.0)
        self.assertEqual(result["delta"], 0.0)

    def test_workflow_round_trip(self) -> None:
        workflow = Workflow(
            name="Starter Iron Line",
            default_belt_capacity=120.0,
            nodes=(
                PlannerNode(
                    id="node_1",
                    recipe_id="iron_ingot",
                    target_item_id="iron_ingot",
                    target_rate_per_minute=30.0,
                    belt_capacity=60.0,
                    width=280.0,
                    height=210.0,
                    x=10.0,
                    y=20.0,
                ),
                PlannerNode(
                    id="node_2",
                    recipe_id="iron_plate",
                    target_item_id="iron_plate",
                    target_rate_per_minute=20.0,
                    belt_capacity=120.0,
                    width=320.0,
                    height=240.0,
                    x=240.0,
                    y=20.0,
                ),
            ),
            edges=(
                PlannerEdge(
                    id="edge_1",
                    source_node_id="node_1",
                    target_node_id="node_2",
                    item_id="iron_ingot",
                ),
            ),
        )
        payload = workflow_to_payload(workflow)
        self.assertEqual(payload["version"], WORKFLOW_VERSION)
        restored = workflow_from_payload(payload)
        self.assertEqual(restored, workflow)

    def test_workflow_rejects_unknown_recipe(self) -> None:
        with self.assertRaisesRegex(WorkflowValidationError, "Unknown recipe id: does_not_exist"):
            workflow_from_payload(
                {
                    "version": WORKFLOW_VERSION,
                    "name": "Broken workflow",
                    "defaultBeltCapacity": 120,
                    "nodes": [
                        {
                            "id": "node_1",
                            "recipeId": "does_not_exist",
                            "targetItemId": "iron_ingot",
                            "targetRatePerMinute": 30,
                            "beltCapacity": 60,
                            "width": 280,
                            "height": 210,
                            "x": 0,
                            "y": 0,
                        }
                    ],
                    "edges": [],
                }
            )

    def test_workflow_rejects_unknown_item(self) -> None:
        with self.assertRaisesRegex(WorkflowValidationError, "Unknown item id: bad_item"):
            workflow_from_payload(
                {
                    "version": WORKFLOW_VERSION,
                    "name": "Broken workflow",
                    "defaultBeltCapacity": 120,
                    "nodes": [
                        {
                            "id": "node_1",
                            "recipeId": "iron_ingot",
                            "targetItemId": "bad_item",
                            "targetRatePerMinute": 30,
                            "beltCapacity": 60,
                            "width": 280,
                            "height": 210,
                            "x": 0,
                            "y": 0,
                        }
                    ],
                    "edges": [],
                }
            )

    def test_workflow_rejects_unknown_edge_reference(self) -> None:
        with self.assertRaisesRegex(WorkflowValidationError, "Unknown target node: node_2"):
            workflow_from_payload(
                {
                    "version": WORKFLOW_VERSION,
                    "name": "Broken workflow",
                    "defaultBeltCapacity": 120,
                    "nodes": [
                        {
                            "id": "node_1",
                            "recipeId": "iron_ingot",
                            "targetItemId": "iron_ingot",
                            "targetRatePerMinute": 30,
                            "beltCapacity": 60,
                            "width": 280,
                            "height": 210,
                            "x": 0,
                            "y": 0,
                        }
                    ],
                    "edges": [
                        {
                            "id": "edge_1",
                            "sourceNodeId": "node_1",
                            "targetNodeId": "node_2",
                            "itemId": "iron_ingot",
                        }
                    ],
                }
            )

    def test_workflow_rejects_incompatible_connection(self) -> None:
        with self.assertRaisesRegex(
            WorkflowValidationError,
            "Nodes node_1 and node_2 are not compatible for copper_ingot",
        ):
            workflow_from_payload(
                {
                    "version": WORKFLOW_VERSION,
                    "name": "Broken workflow",
                    "defaultBeltCapacity": 120,
                    "nodes": [
                        {
                            "id": "node_1",
                            "recipeId": "iron_ingot",
                            "targetItemId": "iron_ingot",
                            "targetRatePerMinute": 30,
                            "beltCapacity": 60,
                            "width": 280,
                            "height": 210,
                            "x": 0,
                            "y": 0,
                        },
                        {
                            "id": "node_2",
                            "recipeId": "iron_plate",
                            "targetItemId": "iron_plate",
                            "targetRatePerMinute": 20,
                            "beltCapacity": 120,
                            "width": 280,
                            "height": 210,
                            "x": 100,
                            "y": 0,
                        },
                    ],
                    "edges": [
                        {
                            "id": "edge_1",
                            "sourceNodeId": "node_1",
                            "targetNodeId": "node_2",
                            "itemId": "copper_ingot",
                        }
                    ],
                }
            )

    def test_workflow_round_trip_preserves_default_belt_capacity(self) -> None:
        payload = workflow_to_payload(
            Workflow(
                name="Steel Expansion",
                default_belt_capacity=270.0,
                nodes=(),
                edges=(),
            )
        )
        self.assertEqual(payload["name"], "Steel Expansion")
        self.assertEqual(payload["defaultBeltCapacity"], 270.0)
        restored = workflow_from_payload(payload)
        self.assertEqual(restored.name, "Steel Expansion")
        self.assertEqual(restored.default_belt_capacity, 270.0)

    def test_workflow_defaults_missing_node_dimensions(self) -> None:
        restored = workflow_from_payload(
            {
                "version": WORKFLOW_VERSION,
                "name": "Legacy",
                "defaultBeltCapacity": 60,
                "nodes": [
                    {
                        "id": "node_1",
                        "recipeId": "iron_ingot",
                        "targetItemId": "iron_ingot",
                        "targetRatePerMinute": 30,
                        "beltCapacity": 60,
                        "x": 0,
                        "y": 0,
                    }
                ],
                "edges": [],
            }
        )
        self.assertEqual(restored.nodes[0].width, 280.0)
        self.assertEqual(restored.nodes[0].height, 210.0)


if __name__ == "__main__":
    unittest.main()
