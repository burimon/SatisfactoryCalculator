from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from ..recipes import RECIPES, Item, Recipe

WORKFLOW_VERSION = 1


class WorkflowValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PlannerNode:
    id: str
    recipe_id: str
    target_item_id: str
    target_rate_per_minute: float
    belt_capacity: float | None
    width: float
    height: float
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class PlannerEdge:
    id: str
    source_node_id: str
    target_node_id: str
    item_id: str


@dataclass(frozen=True, slots=True)
class Workflow:
    name: str
    default_belt_capacity: float | None
    nodes: tuple[PlannerNode, ...]
    edges: tuple[PlannerEdge, ...]


class ScaledRecipe(TypedDict):
    multiplier: float
    machine_count: float
    per_machine_rate: float
    requested_target_rate: float
    inputs: dict[str, float]
    outputs: dict[str, float]


def recipe_entry_rate_per_minute(recipe: Recipe, item_id: str) -> float:
    for item, amount in recipe.outputs.items():
        if item.value == item_id:
            if item is Item.POWER:
                return amount
            return amount * 60 / recipe.duration_seconds
    for item, amount in recipe.inputs.items():
        if item.value == item_id:
            if item is Item.POWER:
                return amount
            return amount * 60 / recipe.duration_seconds
    raise WorkflowValidationError(f"Recipe {recipe.id} does not use {item_id}")


def scale_recipe_for_target(
    recipe: Recipe,
    target_item_id: str,
    target_rate_per_minute: float,
    belt_capacity: float | None = None,
) -> ScaledRecipe:
    base_rate = recipe_entry_rate_per_minute(recipe, target_item_id)
    multiplier = 0.0 if base_rate == 0 else target_rate_per_minute / base_rate

    def entry_rate(item: Item, amount: float) -> float:
        if item is Item.POWER:
            return amount
        return amount * 60 / recipe.duration_seconds

    scaled_requirements = []
    for item, amount in recipe.inputs.items():
        total_rate = entry_rate(item, amount) * multiplier
        capped_rate = _per_machine_rate(item.value, entry_rate(item, amount), belt_capacity)
        scaled_requirements.append(0.0 if capped_rate == 0 else total_rate / capped_rate)
    for item, amount in recipe.outputs.items():
        total_rate = entry_rate(item, amount) * multiplier
        capped_rate = _per_machine_rate(item.value, entry_rate(item, amount), belt_capacity)
        scaled_requirements.append(0.0 if capped_rate == 0 else total_rate / capped_rate)

    machine_count = max(scaled_requirements, default=0.0)
    per_machine_rate = _per_machine_rate(
        target_item_id=target_item_id,
        base_rate=base_rate,
        belt_capacity=belt_capacity,
    )

    def scale(amounts: dict[Item, float]) -> dict[str, float]:
        scaled: dict[str, float] = {}
        for item, amount in amounts.items():
            scaled[item.value] = entry_rate(item, amount) * multiplier
        return scaled

    return {
        "multiplier": multiplier,
        "machine_count": machine_count,
        "per_machine_rate": per_machine_rate,
        "requested_target_rate": target_rate_per_minute,
        "inputs": scale(recipe.inputs),
        "outputs": scale(recipe.outputs),
    }


def connection_imbalance(
    source_recipe: Recipe,
    source_target_item_id: str,
    source_target_rate_per_minute: float,
    target_recipe: Recipe,
    target_target_item_id: str,
    target_target_rate_per_minute: float,
    item_id: str,
) -> dict[str, float | str]:
    source_scaled = scale_recipe_for_target(
        source_recipe,
        source_target_item_id,
        source_target_rate_per_minute,
    )
    target_scaled = scale_recipe_for_target(
        target_recipe,
        target_target_item_id,
        target_target_rate_per_minute,
    )
    source_rate = float(source_scaled["outputs"].get(item_id, 0.0))
    target_rate = float(target_scaled["inputs"].get(item_id, 0.0))
    delta = source_rate - target_rate
    status = "balanced"
    if delta > 0.01:
        status = "source_surplus"
    elif delta < -0.01:
        status = "target_shortage"
    return {
        "status": status,
        "source_rate": source_rate,
        "target_rate": target_rate,
        "delta": delta,
    }


def aggregate_connection_imbalance(
    source_rates: list[float],
    target_rate: float,
) -> dict[str, float | str]:
    total_source_rate = sum(source_rates)
    delta = total_source_rate - target_rate
    status = "balanced"
    if delta > 0.01:
        status = "source_surplus"
    elif delta < -0.01:
        status = "target_shortage"
    return {
        "status": status,
        "total_source_rate": total_source_rate,
        "target_rate": target_rate,
        "delta": delta,
    }


def workflow_to_payload(workflow: Workflow) -> dict[str, object]:
    return {
        "version": WORKFLOW_VERSION,
        "name": workflow.name,
        "defaultBeltCapacity": workflow.default_belt_capacity,
        "nodes": [
            {
                "id": node.id,
                "recipeId": node.recipe_id,
                "targetItemId": node.target_item_id,
                "targetRatePerMinute": node.target_rate_per_minute,
                "beltCapacity": node.belt_capacity,
                "width": node.width,
                "height": node.height,
                "x": node.x,
                "y": node.y,
            }
            for node in workflow.nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "sourceNodeId": edge.source_node_id,
                "targetNodeId": edge.target_node_id,
                "itemId": edge.item_id,
            }
            for edge in workflow.edges
        ],
    }


def workflow_from_payload(payload: dict[str, object]) -> Workflow:
    if payload.get("version") != WORKFLOW_VERSION:
        raise WorkflowValidationError(f"Unsupported workflow version: {payload.get('version')}")

    nodes_payload = payload.get("nodes")
    edges_payload = payload.get("edges")
    if not isinstance(nodes_payload, list) or not isinstance(edges_payload, list):
        raise WorkflowValidationError("Workflow must contain nodes and edges arrays")
    raw_name = payload.get("name", "")
    workflow_name = raw_name if isinstance(raw_name, str) else str(raw_name)
    parsed_default_belt_capacity = _parse_optional_float(payload.get("defaultBeltCapacity"))

    nodes = tuple(_parse_node_payload(node_payload) for node_payload in nodes_payload)
    node_ids = {node.id for node in nodes}
    if len(node_ids) != len(nodes):
        raise WorkflowValidationError("Workflow node ids must be unique")

    for node in nodes:
        recipe = RECIPES.get(node.recipe_id)
        if recipe is None:
            raise WorkflowValidationError(f"Unknown recipe id: {node.recipe_id}")
        try:
            Item(node.target_item_id)
        except ValueError as exc:
            raise WorkflowValidationError(f"Unknown item id: {node.target_item_id}") from exc
        if all(item.value != node.target_item_id for item in recipe.outputs) and all(
            item.value != node.target_item_id for item in recipe.inputs
        ):
            raise WorkflowValidationError(
                f"Recipe {node.recipe_id} does not use {node.target_item_id}"
            )

    edges = tuple(_parse_edge_payload(edge_payload) for edge_payload in edges_payload)
    if len({edge.id for edge in edges}) != len(edges):
        raise WorkflowValidationError("Workflow edge ids must be unique")

    nodes_by_id = {node.id: node for node in nodes}
    for edge in edges:
        if edge.source_node_id not in node_ids:
            raise WorkflowValidationError(f"Unknown source node: {edge.source_node_id}")
        if edge.target_node_id not in node_ids:
            raise WorkflowValidationError(f"Unknown target node: {edge.target_node_id}")
        try:
            Item(edge.item_id)
        except ValueError as exc:
            raise WorkflowValidationError(f"Unknown item id: {edge.item_id}") from exc
        source_node = nodes_by_id[edge.source_node_id]
        target_node = nodes_by_id[edge.target_node_id]
        if edge.item_id not in _compatible_items(source_node, target_node):
            raise WorkflowValidationError(
                "Nodes "
                f"{edge.source_node_id} and {edge.target_node_id} "
                f"are not compatible for {edge.item_id}"
            )

    return Workflow(
        name=workflow_name,
        default_belt_capacity=parsed_default_belt_capacity,
        nodes=nodes,
        edges=edges,
    )


def _parse_node_payload(payload: object) -> PlannerNode:
    if not isinstance(payload, dict):
        raise WorkflowValidationError("Workflow nodes must be objects")
    try:
        return PlannerNode(
            id=str(payload["id"]),
            recipe_id=str(payload["recipeId"]),
            target_item_id=str(payload["targetItemId"]),
            target_rate_per_minute=float(payload["targetRatePerMinute"]),
            belt_capacity=_parse_optional_float(payload.get("beltCapacity")),
            width=float(payload.get("width", 280.0)),
            height=float(payload.get("height", 210.0)),
            x=float(payload["x"]),
            y=float(payload["y"]),
        )
    except KeyError as exc:
        raise WorkflowValidationError(f"Missing node field: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise WorkflowValidationError("Workflow node fields have invalid types") from exc


def _parse_edge_payload(payload: object) -> PlannerEdge:
    if not isinstance(payload, dict):
        raise WorkflowValidationError("Workflow edges must be objects")
    try:
        return PlannerEdge(
            id=str(payload["id"]),
            source_node_id=str(payload["sourceNodeId"]),
            target_node_id=str(payload["targetNodeId"]),
            item_id=str(payload["itemId"]),
        )
    except KeyError as exc:
        raise WorkflowValidationError(f"Missing edge field: {exc.args[0]}") from exc


def _compatible_items(source_node: PlannerNode, target_node: PlannerNode) -> set[str]:
    source_recipe = RECIPES[source_node.recipe_id]
    target_recipe = RECIPES[target_node.recipe_id]
    source_scaled = scale_recipe_for_target(
        source_recipe,
        source_node.target_item_id,
        source_node.target_rate_per_minute,
        source_node.belt_capacity,
    )
    target_scaled = scale_recipe_for_target(
        target_recipe,
        target_node.target_item_id,
        target_node.target_rate_per_minute,
        target_node.belt_capacity,
    )
    source_items = set(source_scaled["outputs"])
    target_items = set(target_scaled["inputs"])
    return source_items & target_items


def _per_machine_rate(
    target_item_id: str,
    base_rate: float,
    belt_capacity: float | None,
) -> float:
    if target_item_id == Item.POWER.value or belt_capacity is None:
        return base_rate
    return min(base_rate, belt_capacity)


def _parse_optional_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    if isinstance(value, (int, float, str)):
        return float(value)
    raise WorkflowValidationError("Expected a numeric value")
