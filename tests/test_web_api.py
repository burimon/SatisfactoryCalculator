import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from SatisfactoryCalculator.webapp.api import (
    find_recipe_payloads_by_output,
    get_recipe_payload,
    list_items,
    list_recipes,
)
from SatisfactoryCalculator.webapp.index_html import HTML


class WebApiTests(unittest.TestCase):
    def test_get_recipe_payload_includes_typed_io_data(self) -> None:
        payload = get_recipe_payload("iron_ingot")
        self.assertEqual(payload["id"], "iron_ingot")
        self.assertEqual(payload["name"], "Iron Ingot")
        self.assertEqual(
            payload["inputs"],
            [{"item": {"id": "iron_ore", "name": "Iron Ore"}, "amount": 1}],
        )
        self.assertEqual(
            payload["outputs"],
            [{"item": {"id": "iron_ingot", "name": "Iron Ingot"}, "amount": 1}],
        )

    def test_find_recipe_payloads_by_output_returns_matching_recipe_payloads(self) -> None:
        payloads = find_recipe_payloads_by_output("biomass")
        self.assertEqual(
            [payload["id"] for payload in payloads],
            [
                "biomass_leaves",
                "biomass_wood",
                "biomass_mycelia",
                "biomass_alien_protein",
            ],
        )

    def test_find_recipe_payloads_by_output_returns_power_recipe_payloads(self) -> None:
        payloads = find_recipe_payloads_by_output("power")
        self.assertEqual(
            [payload["id"] for payload in payloads],
            ["power_biomass", "power_solid_biofuel"],
        )

    def test_find_recipe_payloads_by_output_returns_mining_payloads(self) -> None:
        payloads = find_recipe_payloads_by_output("iron_ore")
        self.assertEqual([payload["id"] for payload in payloads], ["mine_iron_ore"])

    def test_get_recipe_payload_includes_tier_two_recipe(self) -> None:
        payload = get_recipe_payload("rotor")
        self.assertEqual(payload["name"], "Rotor")
        self.assertEqual(
            payload["inputs"],
            [
                {"item": {"id": "iron_rod", "name": "Iron Rod"}, "amount": 5},
                {"item": {"id": "screw", "name": "Screw"}, "amount": 25},
            ],
        )
        self.assertEqual(
            payload["outputs"],
            [{"item": {"id": "rotor", "name": "Rotor"}, "amount": 1}],
        )

    def test_recipe_and_item_lists_are_sorted_by_display_name(self) -> None:
        recipe_names = [payload["name"] for payload in list_recipes()]
        item_names = [payload["name"] for payload in list_items()]
        self.assertEqual(recipe_names, sorted(recipe_names))
        self.assertEqual(item_names, sorted(item_names))

    def test_html_includes_planner_net_balance_table_mount(self) -> None:
        self.assertIn('id="planner-net-balance"', HTML)
        self.assertIn('data-net-sort-key="item"', HTML)
        self.assertIn('data-net-sort-key="net"', HTML)
        self.assertIn("Hide balanced", HTML)


if __name__ == "__main__":
    unittest.main()
