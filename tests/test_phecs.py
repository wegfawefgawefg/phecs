import unittest
from dataclasses import dataclass

from phecs.phecs import Entity, Error, World


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Velocity:
    dx: int
    dy: int


@dataclass
class IsDead:
    value: bool


@dataclass
class Health:
    value: int


@dataclass
class Name:
    value: str


class TestPhecsWorld(unittest.TestCase):
    def test_world(self):
        world = World()

        entity = world.spawn()
        self.assertTrue(world.contains(entity))

        world.despawn(entity)
        self.assertFalse(world.contains(entity))

        entity = world.spawn()

        world.spawn_at(entity)
        self.assertTrue(world.contains(entity))

        world.clear()
        self.assertFalse(world.contains(entity))

        entity = world.spawn()

        world.spawn_at(entity)
        self.assertTrue(world.contains(entity))

        world.despawn(entity)
        self.assertFalse(world.contains(entity))


class PhecsWorldFind(unittest.TestCase):
    def test_find(self):
        world = World()

        entity = world.spawn(Position(1, 1))
        entity2 = world.spawn(Position(2, 2))

        self.assertEqual(
            list(world.find(Position)),
            [(entity, Position(1, 1)), (entity2, Position(2, 2))],
        )

    def test_find_has(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(0, 0))
        world.spawn(Position(2, 2))

        self.assertEqual(
            list(world.find(Position, has=Velocity)),
            [(entity, Position(1, 1))],
        )

    def test_find_without(self):
        world = World()

        world.spawn(Position(1, 1))
        world.spawn(Position(2, 2))

        self.assertEqual(
            list(world.find(Position, without=Position)),
            [],
        )

    def test_find_nonexistent_component(self):
        world = World()

        self.assertEqual(
            list(world.find(Position)),
            [],
        )

        self.assertEqual(
            list(world.find(Position, has=Velocity)),
            [],
        )

        self.assertEqual(
            list(world.find(Position, without=Position)),
            [],
        )

    def test_find_has_without(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1))
        world.spawn(Position(2, 2), IsDead(True))

        self.assertEqual(
            list(world.find(Position, has=Velocity, without=IsDead)),
            [(entity, Position(1, 1))],
        )

    def test_find_multiple(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1))
        world.spawn(Position(2, 2), IsDead(True))

        self.assertEqual(
            list(world.find(Position, Velocity)),
            [(entity, Position(1, 1), Velocity(1, 1))],
        )

    def test_find_has_multiple(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1), Health(100))
        world.spawn(Position(2, 2), Velocity(2, 2))

        self.assertEqual(
            list(world.find(Position, has=[Velocity, Health])),
            [(entity, Position(1, 1))],
        )

    def test_find_unpack_result(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1))

        result = world.find(Position, Velocity, has=Velocity, without=IsDead)

        e, p, v = next(result)

        self.assertEqual(e, entity)
        self.assertEqual(p, Position(1, 1))
        self.assertEqual(v, Velocity(1, 1))

    def test_find_no_result(self):
        world = World()

        self.assertEqual(
            list(world.find(Position, has=Velocity, without=IsDead)),
            [],
        )

    def test_satifies_empty(self):
        world = World()

        entity = world.spawn()

        self.assertTrue(world.satisfies(entity))

    def test_satisifes(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1))

        self.assertTrue(world.satisfies(entity, has=Position))
        self.assertTrue(world.satisfies(entity, has=Velocity))
        self.assertFalse(world.satisfies(entity, has=Position, without=Velocity))
        self.assertFalse(world.satisfies(entity, has=IsDead))

    def test_satisifes_has_without(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1))

        self.assertTrue(world.satisfies(entity, has=Velocity))
        self.assertFalse(world.satisfies(entity, has=IsDead))
        self.assertTrue(world.satisfies(entity, without=IsDead))

    def test_satisifes_multiple(self):
        world = World()

        entity = world.spawn(Position(1, 1), Velocity(1, 1), Health(100))

        self.assertTrue(world.satisfies(entity, has=[Velocity, Health]))
        self.assertFalse(world.satisfies(entity, has=[Velocity, IsDead]))
        self.assertTrue(world.satisfies(entity, without=[IsDead, Name]))
        self.assertFalse(world.satisfies(entity, without=[IsDead, Health]))


class PhecsEntity(unittest.TestCase):
    def test_entity(self):
        world = World()

        entity = world.spawn()
        self.assertEqual(entity, 0)
        entity = world.spawn()
        self.assertEqual(entity, 1)

    def test_add_one_component(self):
        world = World()
        entity = world.spawn()
        world.add(entity, Position(1, 1))

        result = world.find_on(entity, Position)
        e, p = next(result)
        self.assertEqual(e, entity)
        self.assertEqual(p, Position(1, 1))

    def test_add_multiple_components(self):
        world = World()
        entity = world.spawn()
        world.add(entity, Position(1, 1), Velocity(1, 1))

        result = world.find_on(entity, Position, Velocity)
        e, p, v = next(result)
        self.assertEqual(e, entity)
        self.assertEqual(p, Position(1, 1))
        self.assertEqual(v, Velocity(1, 1))

    def test_remove_components(self):
        world = World()
        entity = world.spawn()
        world.add(entity, Position(1, 1), Velocity(1, 1))

        self.assertTrue(world.satisfies(entity, Position))

        world.remove(entity, Position)

        self.assertFalse(world.satisfies(entity, Position))

    def test_is_empty(self):
        world = World()
        entity = world.spawn()

        self.assertTrue(world.is_empty(entity))

        world.add(entity, Position(1, 1))

        self.assertFalse(world.is_empty(entity))

    def test_find_on_missing_entity_returns_empty(self):
        world = World()
        world.spawn(Position(1, 1))

        self.assertEqual(list(world.find_on(999, Position)), [])

    def test_find_on_respects_has_filter(self):
        world = World()
        entity = world.spawn(Position(1, 1))

        self.assertEqual(list(world.find_on(entity, Position, has=Velocity)), [])

    def test_find_on_respects_without_filter(self):
        world = World()
        entity = world.spawn(Position(1, 1), IsDead(True))

        self.assertEqual(list(world.find_on(entity, Position, without=IsDead)), [])

    def test_entity_eq_unrelated_type_is_false(self):
        world = World()
        entity = world.spawn()

        self.assertFalse(entity == "not-an-entity")

    def test_remove_missing_entity_returns_error(self):
        world = World()

        self.assertEqual(world.remove(999, Position), Error.NoSuchEntity)

    def test_spawn_at_updates_next_entity_id(self):
        world = World()

        world.spawn_at(Entity(5), Position(5, 5))
        spawned = world.spawn(Position(0, 0))

        self.assertEqual(spawned, 6)
        self.assertEqual(world.get(Entity(5), Position), Position(5, 5))
