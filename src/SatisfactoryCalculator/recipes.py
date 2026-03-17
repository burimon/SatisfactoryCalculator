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
    COAL = "coal"
    WATER = "water"
    LIMESTONE = "limestone"
    IRON_INGOT = "iron_ingot"
    COPPER_INGOT = "copper_ingot"
    STEEL_INGOT = "steel_ingot"
    CONCRETE = "concrete"
    IRON_PLATE = "iron_plate"
    IRON_ROD = "iron_rod"
    WIRE = "wire"
    CABLE = "cable"
    COPPER_SHEET = "copper_sheet"
    SCREW = "screw"
    STEEL_BEAM = "steel_beam"
    STEEL_PIPE = "steel_pipe"
    REINFORCED_IRON_PLATE = "reinforced_iron_plate"
    ROTOR = "rotor"
    MODULAR_FRAME = "modular_frame"
    SMART_PLATING = "smart_plating"
    VERSATILE_FRAMEWORK = "versatile_framework"
    ENCASED_INDUSTRIAL_BEAM = "encased_industrial_beam"
    STATOR = "stator"
    MOTOR = "motor"
    AUTOMATED_WIRING = "automated_wiring"
    RAW_QUARTZ = "raw_quartz"
    QUARTZ_CRYSTAL = "quartz_crystal"
    SILICA = "silica"
    CRYSTAL_OSCILLATOR = "crystal_oscillator"
    CATERIUM_ORE = "caterium_ore"
    CATERIUM_INGOT = "caterium_ingot"
    QUICKWIRE = "quickwire"
    AI_LIMITER = "ai_limiter"


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
    "mine_coal": Recipe(
        id="mine_coal",
        name="Mine Coal",
        inputs={},
        outputs={Item.COAL: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "extract_water": Recipe(
        id="extract_water",
        name="Extract Water",
        inputs={},
        outputs={Item.WATER: 2},
        duration_seconds=1.0,
        building="water_extractor",
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
    "power_coal": Recipe(
        id="power_coal",
        name="Power (Coal)",
        inputs={Item.COAL: 1, Item.WATER: 3},
        outputs={Item.POWER: 75},
        duration_seconds=4.0,
        building="coal_generator",
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
    "steel_ingot": Recipe(
        id="steel_ingot",
        name="Steel Ingot",
        inputs={Item.IRON_ORE: 3, Item.COAL: 3},
        outputs={Item.STEEL_INGOT: 3},
        duration_seconds=4.0,
        building="foundry",
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
    "steel_beam": Recipe(
        id="steel_beam",
        name="Steel Beam",
        inputs={Item.STEEL_INGOT: 4},
        outputs={Item.STEEL_BEAM: 1},
        duration_seconds=4.0,
        building="constructor",
    ),
    "steel_pipe": Recipe(
        id="steel_pipe",
        name="Steel Pipe",
        inputs={Item.STEEL_INGOT: 3},
        outputs={Item.STEEL_PIPE: 2},
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
    "versatile_framework": Recipe(
        id="versatile_framework",
        name="Versatile Framework",
        inputs={Item.MODULAR_FRAME: 1, Item.STEEL_BEAM: 12},
        outputs={Item.VERSATILE_FRAMEWORK: 2},
        duration_seconds=24.0,
        building="assembler",
    ),
    "encased_industrial_beam": Recipe(
        id="encased_industrial_beam",
        name="Encased Industrial Beam",
        inputs={Item.STEEL_BEAM: 3, Item.CONCRETE: 6},
        outputs={Item.ENCASED_INDUSTRIAL_BEAM: 1},
        duration_seconds=10.0,
        building="assembler",
    ),
    "stator": Recipe(
        id="stator",
        name="Stator",
        inputs={Item.STEEL_PIPE: 3, Item.WIRE: 8},
        outputs={Item.STATOR: 1},
        duration_seconds=12.0,
        building="assembler",
    ),
    "motor": Recipe(
        id="motor",
        name="Motor",
        inputs={Item.ROTOR: 2, Item.STATOR: 2},
        outputs={Item.MOTOR: 1},
        duration_seconds=12.0,
        building="assembler",
    ),
    "automated_wiring": Recipe(
        id="automated_wiring",
        name="Automated Wiring",
        inputs={Item.STATOR: 1, Item.CABLE: 20},
        outputs={Item.AUTOMATED_WIRING: 1},
        duration_seconds=24.0,
        building="assembler",
    ),
    "mine_raw_quartz": Recipe(
        id="mine_raw_quartz",
        name="Mine Raw Quartz",
        inputs={},
        outputs={Item.RAW_QUARTZ: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "quartz_crystal": Recipe(
        id="quartz_crystal",
        name="Quartz Crystal",
        inputs={Item.RAW_QUARTZ: 5},
        outputs={Item.QUARTZ_CRYSTAL: 3},
        duration_seconds=8.0,
        building="constructor",
    ),
    "silica": Recipe(
        id="silica",
        name="Silica",
        inputs={Item.RAW_QUARTZ: 3},
        outputs={Item.SILICA: 5},
        duration_seconds=8.0,
        building="constructor",
    ),
    "crystal_oscillator": Recipe(
        id="crystal_oscillator",
        name="Crystal Oscillator",
        inputs={Item.QUARTZ_CRYSTAL: 36, Item.CABLE: 28, Item.REINFORCED_IRON_PLATE: 5},
        outputs={Item.CRYSTAL_OSCILLATOR: 2},
        duration_seconds=120.0,
        building="manufacturer",
    ),
    "mine_caterium_ore": Recipe(
        id="mine_caterium_ore",
        name="Mine Caterium Ore",
        inputs={},
        outputs={Item.CATERIUM_ORE: 1},
        duration_seconds=1.0,
        building="miner",
    ),
    "caterium_ingot": Recipe(
        id="caterium_ingot",
        name="Caterium Ingot",
        inputs={Item.CATERIUM_ORE: 3},
        outputs={Item.CATERIUM_INGOT: 1},
        duration_seconds=4.0,
        building="smelter",
    ),
    "quickwire": Recipe(
        id="quickwire",
        name="Quickwire",
        inputs={Item.CATERIUM_INGOT: 1},
        outputs={Item.QUICKWIRE: 5},
        duration_seconds=5.0,
        building="constructor",
    ),
    "ai_limiter": Recipe(
        id="ai_limiter",
        name="AI Limiter",
        inputs={Item.QUICKWIRE: 5, Item.COPPER_SHEET: 2},
        outputs={Item.AI_LIMITER: 1},
        duration_seconds=12.0,
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
