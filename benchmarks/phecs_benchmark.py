from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Dict, List

from phecs import World


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    dx: float
    dy: float


@dataclass
class Health:
    hp: int


@dataclass
class Team:
    value: int


@dataclass
class Name:
    value: str


class Dead:
    pass


class Burning:
    pass


def build_world(entity_count: int) -> World:
    world = World()
    for i in range(entity_count):
        components = [
            Position(float(i), float(-i)),
            Velocity(0.25, -0.25),
            Health(100),
            Team(i % 4),
            Name(f"entity-{i}"),
        ]
        if i % 5 == 0:
            components.append(Burning())
        if i % 11 == 0:
            components.append(Dead())
        world.spawn(*components)
    return world


def benchmark_spawn(entity_count: int) -> float:
    start = time.perf_counter()
    build_world(entity_count)
    return time.perf_counter() - start


def benchmark_physics_query(entity_count: int) -> float:
    world = build_world(entity_count)
    start = time.perf_counter()
    for _, position, velocity in world.find(Position, Velocity, without=Dead):
        position.x += velocity.dx
        position.y += velocity.dy
    return time.perf_counter() - start


def benchmark_component_churn(entity_count: int) -> float:
    world = build_world(entity_count)
    entity = world.spawn(Position(0.0, 0.0))
    start = time.perf_counter()
    for i in range(entity_count):
        world.add(entity, Health(i))
        world.remove(entity, Health)
    return time.perf_counter() - start


def benchmark_despawn_all(entity_count: int) -> float:
    world = build_world(entity_count)
    entities = list(world.iter())
    start = time.perf_counter()
    for entity in entities:
        world.despawn(entity)
    return time.perf_counter() - start


def benchmark_frame_step(entity_count: int) -> float:
    world = build_world(entity_count)
    start = time.perf_counter()
    for entity, health in world.find(Health, without=Dead):
        if health.hp <= 1:
            world.add(entity, Dead())
        else:
            health.hp -= 1

    for _, position, velocity in world.find(Position, Velocity, without=Dead):
        position.x += velocity.dx
        position.y += velocity.dy

    for entity, health, burning in world.find(Health, Burning, without=Dead):
        health.hp -= 2
        if health.hp <= 0:
            world.add(entity, Dead())
    return time.perf_counter() - start


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * pct))))
    return ordered[idx]


def summarize(samples: List[float]) -> Dict[str, float]:
    return {
        "min_ms": min(samples) * 1000.0,
        "median_ms": statistics.median(samples) * 1000.0,
        "mean_ms": statistics.mean(samples) * 1000.0,
        "p95_ms": percentile(samples, 0.95) * 1000.0,
        "max_ms": max(samples) * 1000.0,
    }


def run_case(
    fn: Callable[[int], float], entity_count: int, repeats: int, warmup: int
) -> Dict[str, float]:
    for _ in range(warmup):
        fn(entity_count)

    samples = [fn(entity_count) for _ in range(repeats)]
    return summarize(samples)


def run_benchmarks(entity_count: int, repeats: int, warmup: int) -> Dict[str, Dict[str, float]]:
    cases: Dict[str, Callable[[int], float]] = {
        "spawn_mixed": benchmark_spawn,
        "query_physics": benchmark_physics_query,
        "component_churn": benchmark_component_churn,
        "despawn_all": benchmark_despawn_all,
        "frame_step": benchmark_frame_step,
    }
    return {
        name: run_case(fn, entity_count, repeats, warmup)
        for name, fn in cases.items()
    }


def print_report(entity_count: int, repeats: int, warmup: int, report: Dict[str, Dict[str, float]]) -> None:
    print(f"phecs benchmark")
    print(f"entities={entity_count}, repeats={repeats}, warmup={warmup}")
    print("")
    print(
        f"{'case':<18} {'min_ms':>10} {'median_ms':>10} {'mean_ms':>10} {'p95_ms':>10} {'max_ms':>10}"
    )
    for case, metrics in report.items():
        print(
            f"{case:<18} "
            f"{metrics['min_ms']:>10.3f} "
            f"{metrics['median_ms']:>10.3f} "
            f"{metrics['mean_ms']:>10.3f} "
            f"{metrics['p95_ms']:>10.3f} "
            f"{metrics['max_ms']:>10.3f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reproducible phecs benchmarks.")
    parser.add_argument("--entities", type=int, default=10_000)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument(
        "--json",
        dest="json_path",
        default="",
        help="Optional path to write benchmark metrics as JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_benchmarks(
        entity_count=args.entities,
        repeats=args.repeats,
        warmup=args.warmup,
    )
    print_report(args.entities, args.repeats, args.warmup, report)
    if args.json_path:
        payload = {
            "entities": args.entities,
            "repeats": args.repeats,
            "warmup": args.warmup,
            "results": report,
        }
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()

