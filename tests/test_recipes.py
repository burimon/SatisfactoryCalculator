import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from SatisfactoryCalculator import RECIPES, Item, Recipe, find_recipes_by_output, get_recipe


class RecipeRegistryTests(unittest.TestCase):
    def test_registry_values_are_recipe_instances(self) -> None:
        self.assertTrue(RECIPES)
        for recipe_id, recipe in RECIPES.items():
            self.assertIsInstance(recipe, Recipe)
            self.assertEqual(recipe.id, recipe_id)

    def test_each_recipe_has_required_fields_and_outputs(self) -> None:
        for recipe in RECIPES.values():
            self.assertTrue(recipe.id)
            self.assertTrue(recipe.name)
            self.assertGreater(recipe.duration_seconds, 0)
            self.assertTrue(recipe.outputs)
            for item, amount in recipe.inputs.items():
                self.assertIsInstance(item, Item)
                self.assertIsInstance(amount, (int, float))
                self.assertGreater(amount, 0)
            for item, amount in recipe.outputs.items():
                self.assertIsInstance(item, Item)
                self.assertIsInstance(amount, (int, float))
                self.assertGreater(amount, 0)

    def test_registry_ids_are_unique(self) -> None:
        recipe_ids = list(RECIPES)
        self.assertEqual(len(recipe_ids), len(set(recipe_ids)))

    def test_get_recipe_returns_expected_recipe(self) -> None:
        recipe = get_recipe("iron_ingot")
        self.assertEqual(recipe.name, "Iron Ingot")
        self.assertEqual(recipe.outputs, {Item.IRON_INGOT: 1})

    def test_get_recipe_raises_for_unknown_recipe(self) -> None:
        with self.assertRaisesRegex(KeyError, "Unknown recipe id: does_not_exist"):
            get_recipe("does_not_exist")

    def test_find_recipes_by_output_returns_matching_recipes(self) -> None:
        recipes = find_recipes_by_output(Item.IRON_INGOT)
        self.assertEqual([recipe.id for recipe in recipes], ["iron_ingot"])

    def test_find_recipes_by_output_returns_all_biomass_variants(self) -> None:
        recipes = find_recipes_by_output(Item.BIOMASS)
        self.assertEqual(
            [recipe.id for recipe in recipes],
            [
                "biomass_leaves",
                "biomass_wood",
                "biomass_mycelia",
                "biomass_alien_protein",
            ],
        )


if __name__ == "__main__":
    unittest.main()
