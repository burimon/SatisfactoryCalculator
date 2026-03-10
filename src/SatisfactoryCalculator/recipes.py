from dataclasses import dataclass
from enum import Enum


class Item(str, Enum):
    LEAVES = "leaves"
    WOOD = "wood"
    MYCELIA = "mycelia"
    ALIEN_PROTEIN = "alien_protein"
    BIOMASS = "biomass"
    SOLID_BIOFUEL = "solid_biofuel"
    POWER = "power"
    IRON_ORE = "iron_ore"
    COPPER_ORE = "copper_ore"
    LIMESTONE = "limestone"
    IRON_INGOT = "iron_ingot"
    COPPER_INGOT = "copper_ingot"
    CONCRETE = "concrete"
    IRON_PLATE = "iron_plate"
    IRON_ROD = "iron_rod"
    WIRE = "wire"
    CABLE = "cable"
    COPPER_SHEET = "copper_sheet"
    SCREW = "screw"
    REINFORCED_IRON_PLATE = "reinforced_iron_plate"
    ROTOR = "rotor"
    MODULAR_FRAME = "modular_frame"
    SMART_PLATING = "smart_plating"


ItemAmounts = dict[Item, float]


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    name: str
    inputs: ItemAmounts
    outputs: ItemAmounts
    duration_seconds: float
    building: str | None = None
    alternate: bool = False


RECIPES: dict[str, Recipe] = {
    "mine_iron_ore": Recipe(
        id="mine_iron_ore",
        name="Mine Iron Ore",
        inputs={},
        outputs={Item.IRON_ORE: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "mine_copper_ore": Recipe(
        id="mine_copper_ore",
        name="Mine Copper Ore",
        inputs={},
        outputs={Item.COPPER_ORE: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "mine_limestone": Recipe(
        id="mine_limestone",
        name="Mine Limestone",
        inputs={},
        outputs={Item.LIMESTONE: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "biomass_leaves": Recipe(
        id="biomass_leaves",
        name="Biomass (Leaves)",
        inputs={Item.LEAVES: 10},
        outputs={Item.BIOMASS: 5},
        duration_seconds=5.0,
        building="constructor",
    ),
    "biomass_wood": Recipe(
        id="biomass_wood",
        name="Biomass (Wood)",
        inputs={Item.WOOD: 4},
        outputs={Item.BIOMASS: 20},
        duration_seconds=4.0,
        building="constructor",
    ),
    "biomass_mycelia": Recipe(
        id="biomass_mycelia",
        name="Biomass (Mycelia)",
        inputs={Item.MYCELIA: 1},
        outputs={Item.BIOMASS: 10},
        duration_seconds=4.0,
        building="constructor",
    ),
    "biomass_alien_protein": Recipe(
        id="biomass_alien_protein",
        name="Biomass (Alien Protein)",
        inputs={Item.ALIEN_PROTEIN: 1},
        outputs={Item.BIOMASS: 100},
        duration_seconds=4.0,
        building="constructor",
    ),
    "solid_biofuel": Recipe(
        id="solid_biofuel",
        name="Solid Biofuel",
        inputs={Item.BIOMASS: 8},
        outputs={Item.SOLID_BIOFUEL: 4},
        duration_seconds=4.0,
        building="constructor",
    ),
    "power_biomass": Recipe(
        id="power_biomass",
        name="Power (Biomass)",
        inputs={Item.BIOMASS: 1},
        outputs={Item.POWER: 30},
        duration_seconds=6.0,
        building="biomass_burner",
    ),
    "power_solid_biofuel": Recipe(
        id="power_solid_biofuel",
        name="Power (Solid Biofuel)",
        inputs={Item.SOLID_BIOFUEL: 1},
        outputs={Item.POWER: 30},
        duration_seconds=15.0,
        building="biomass_burner",
    ),
    "iron_ingot": Recipe(
        id="iron_ingot",
        name="Iron Ingot",
        inputs={Item.IRON_ORE: 1},
        outputs={Item.IRON_INGOT: 1},
        duration_seconds=2.0,
        building="smelter",
    ),
    "copper_ingot": Recipe(
        id="copper_ingot",
        name="Copper Ingot",
        inputs={Item.COPPER_ORE: 1},
        outputs={Item.COPPER_INGOT: 1},
        duration_seconds=2.0,
        building="smelter",
    ),
    "concrete": Recipe(
        id="concrete",
        name="Concrete",
        inputs={Item.LIMESTONE: 3},
        outputs={Item.CONCRETE: 1},
        duration_seconds=4.0,
        building="constructor",
    ),
    "iron_plate": Recipe(
        id="iron_plate",
        name="Iron Plate",
        inputs={Item.IRON_INGOT: 3},
        outputs={Item.IRON_PLATE: 2},
        duration_seconds=6.0,
        building="constructor",
    ),
    "iron_rod": Recipe(
        id="iron_rod",
        name="Iron Rod",
        inputs={Item.IRON_INGOT: 1},
        outputs={Item.IRON_ROD: 1},
        duration_seconds=4.0,
        building="constructor",
    ),
    "wire": Recipe(
        id="wire",
        name="Wire",
        inputs={Item.COPPER_INGOT: 1},
        outputs={Item.WIRE: 2},
        duration_seconds=4.0,
        building="constructor",
    ),
    "cable": Recipe(
        id="cable",
        name="Cable",
        inputs={Item.WIRE: 2},
        outputs={Item.CABLE: 1},
        duration_seconds=2.0,
        building="constructor",
    ),
    "copper_sheet": Recipe(
        id="copper_sheet",
        name="Copper Sheet",
        inputs={Item.COPPER_INGOT: 2},
        outputs={Item.COPPER_SHEET: 1},
        duration_seconds=6.0,
        building="constructor",
    ),
    "screw": Recipe(
        id="screw",
        name="Screw",
        inputs={Item.IRON_ROD: 1},
        outputs={Item.SCREW: 4},
        duration_seconds=6.0,
        building="constructor",
    ),
    "reinforced_iron_plate": Recipe(
        id="reinforced_iron_plate",
        name="Reinforced Iron Plate",
        inputs={Item.IRON_PLATE: 6, Item.SCREW: 12},
        outputs={Item.REINFORCED_IRON_PLATE: 1},
        duration_seconds=12.0,
        building="assembler",
    ),
    "rotor": Recipe(
        id="rotor",
        name="Rotor",
        inputs={Item.IRON_ROD: 5, Item.SCREW: 25},
        outputs={Item.ROTOR: 1},
        duration_seconds=15.0,
        building="assembler",
    ),
    "modular_frame": Recipe(
        id="modular_frame",
        name="Modular Frame",
        inputs={Item.REINFORCED_IRON_PLATE: 3, Item.IRON_ROD: 12},
        outputs={Item.MODULAR_FRAME: 2},
        duration_seconds=60.0,
        building="assembler",
    ),
    "smart_plating": Recipe(
        id="smart_plating",
        name="Smart Plating",
        inputs={Item.REINFORCED_IRON_PLATE: 1, Item.ROTOR: 1},
        outputs={Item.SMART_PLATING: 1},
        duration_seconds=30.0,
        building="assembler",
    ),
}


def get_recipe(recipe_id: str) -> Recipe:
    try:
        return RECIPES[recipe_id]
    except KeyError as exc:
        raise KeyError(f"Unknown recipe id: {recipe_id}") from exc


def find_recipes_by_output(item: Item) -> list[Recipe]:
    return [recipe for recipe in RECIPES.values() if item in recipe.outputs]
