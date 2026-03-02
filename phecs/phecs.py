from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type


class Error(Enum):
    NoSuchEntity = auto()
    NoSuchComponent = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class NoSuchEntity(Exception):
    pass


class NoSuchComponent(Exception):
    pass


class Entity:
    def __init__(self, id):
        self.__id = id

    def __hash__(self) -> int:
        return hash(self.__id)

    def __repr__(self) -> str:
        return f"Entity(id={self.__id})"

    def __eq__(self, other_entity: Entity | int) -> bool:
        if isinstance(other_entity, int):
            return self.__id == other_entity
        if not isinstance(other_entity, Entity):
            return False
        return self.__id == other_entity.__id


class InternalEntity:
    def __init__(self, entity: Entity):
        self.entity: Entity = entity
        self.components: dict[Type[Any], Any] = {}


"""
Naming Guide for if you really must shorten a variable in a comprehension or something:
e = entity
ie = internal_entity
es = entities
c = component
cs = components
"""


class World:
    """
    Represents the game world that contains entities and their components.
    """

    def __init__(self) -> None:
        self.next_entity_id: int = 0
        self.entities: Dict[Entity, InternalEntity] = {}

    def spawn(self, *components: Any) -> Entity:
        """
        Creates a new entity and adds the specified components to it.

        Args:
            *components: The components to add to the entity.

        Returns:
            The newly created entity.

        """
        entity = Entity(self.next_entity_id)
        self.next_entity_id += 1
        internal_entity = InternalEntity(entity)
        self.entities[entity] = internal_entity
        for component in components:
            internal_entity.components[type(component)] = component
        return entity

    def spawn_at(self, entity: Entity, *components: Any) -> None:
        """
        Add the specified components to an existing entity in the world.

        Args:
            entity (Entity): The entity to add components to.
            *components (Any): The components to add to the entity.
        """
        internal_entity = InternalEntity(entity)
        self.entities[entity] = internal_entity
        for component in components:
            internal_entity.components[type(component)] = component

    def despawn(self, entity: Entity) -> Optional[Error]:
        """
        Remove an entity from the world.

        Args:
            entity (Entity): The entity to remove.

        Returns:
            Optional[Error]: An error if the entity does not exist in the world, None otherwise.
        """
        if entity in self.entities:
            del self.entities[entity]
        else:
            return Error.NoSuchEntity

    def clear(self) -> None:
        """
        Remove all entities from the world.
        """
        self.entities.clear()

    def contains(self, entity: Entity) -> bool:
        """
        Check if the world contains the specified entity.

        Args:
            entity (Entity): The entity to check.

        Returns:
            bool: True if the entity exists in the world, False otherwise.
        """
        return entity in self.entities

    def find(
        self,
        *component_types: Type,
        has: Optional[Type | List[Type] | Tuple[Type, ...]] = None,
        without: Optional[Type | List[Type] | Tuple[Type, ...]] = None,
    ) -> Iterator[Tuple[Any, ...]]:
        """
        Find entities that have the specified component types and meet the optional conditions.

        Args:
            *component_types (Type): The component types to search for.
            has (Optional[Type | List[Type] | Tuple[Type, ...]]): The component types that the entities must have.
            without (Optional[Type | List[Type] | Tuple[Type, ...]]): The component types that the entities must not have.

        Yields:
            Iterator[Tuple[Any, ...]]: An iterator of tuples representing the found entities and their components.
        """
        has = (
            has
            if isinstance(has, (list, tuple))
            else [has]
            if has is not None
            else None
        )
        without = (
            without
            if isinstance(without, (list, tuple))
            else [without]
            if without is not None
            else None
        )

        for internal_entity in self.entities.values():
            if has and any(c not in internal_entity.components for c in has):
                continue
            if without and any(c in internal_entity.components for c in without):
                continue
            if all(c in internal_entity.components for c in component_types):
                yield (
                    internal_entity.entity,
                    *(internal_entity.components[c] for c in component_types),
                )
        yield from []

    def find_on(
        self,
        entity: Entity,
        *component_types: Type,
        has: Optional[Type | List[Type] | Tuple[Type, ...]] = None,
        without: Optional[Type | List[Type] | Tuple[Type, ...]] = None,
    ) -> Iterator[Tuple[Any, ...]]:
        """
        Find and retrieve components associated with the given entity that match the specified criteria.

        Args:
            entity (Entity): The entity to search for.
            *component_types (Type): The types of components to retrieve.
            has (Optional[Type | List[Type] | Tuple[Type, ...]], optional): Components that the entity must have. Defaults to None.
            without (Optional[Type | List[Type] | Tuple[Type, ...]], optional): Components that the entity must not have. Defaults to None.

        Returns:
            Tuple[Any, ...] | None: A tuple containing the entity and the retrieved components, or None if no matching components are found.
        """
        if entity not in self.entities:
            return
        internal_entity = self.entities[entity]

        if has:
            if isinstance(has, (list, tuple)):
                if any(c not in internal_entity.components for c in has):
                    return
            elif has not in internal_entity.components:
                return

        if without:
            if isinstance(without, (list, tuple)):
                if any(c in internal_entity.components for c in without):
                    return
            elif without in internal_entity.components:
                return

        if all(c in internal_entity.components for c in component_types):
            yield (
                internal_entity.entity,
                *(internal_entity.components[c] for c in component_types),
            )

    def get(self, entity: Entity, component_type: Type) -> Any | None:
        """
        Get the component of the specified type associated with the entity.

        Args:
            entity (Entity): The entity to retrieve the component from.
            component_type (Type): The type of the component to retrieve.

        Returns:
            Any | None: The component if found, None otherwise.
        """
        if (
            entity in self.entities
            and component_type in self.entities[entity].components
        ):
            return self.entities[entity].components[component_type]
        return None

    def satisfies(
        self,
        entity: Entity,
        has: Optional[Type | List[Type]] | Tuple[Type, ...] = None,
        without: Optional[Type | List[Type]] | Tuple[Type, ...] = None,
    ) -> bool:
        """
        Check if the entity satisfies the specified conditions.

        Args:
            entity (Entity): The entity to check.
            has (Optional[Type | List[Type]] | Tuple[Type, ...], optional): Components that the entity must have. Defaults to None.
            without (Optional[Type | List[Type]] | Tuple[Type, ...], optional): Components that the entity must not have. Defaults to None.

        Returns:
            bool: True if the entity satisfies the conditions, False otherwise.
        """
        if entity not in self.entities:
            return False
        internal_entity = self.entities[entity]

        if has:
            if isinstance(has, (list, tuple)):
                if any(c not in internal_entity.components for c in has):
                    return False
            elif has not in internal_entity.components:
                return False

        if without:
            if isinstance(without, (list, tuple)):
                if any(c in internal_entity.components for c in without):
                    return False
            elif without in internal_entity.components:
                return False

        return True

    def is_empty(self, entity: Entity) -> bool:
        """
        Check if the entity has no components.

        Args:
            entity (Entity): The entity to check.

        Returns:
            bool: True if the entity has no components, False otherwise.
        """
        return entity in self.entities and not self.entities[entity].components

    def insert(self, entity: Entity, *components: Any) -> None | Error:
        """
        Insert the specified components into an existing entity in the world.

        Args:
            entity (Entity): The entity to insert components into.
            *components (Any): The components to insert.

        Returns:
            None | Error: None if successful, or an error if the entity does not exist in the world.
        """
        if entity in self.entities:
            for component in components:
                self.entities[entity].components[type(component)] = component
        else:
            return Error.NoSuchEntity

    def remove(self, entity: Entity, *component_types: Type) -> None:
        """
        Remove the specified components from an existing entity in the world.

        Args:
            entity (Entity): The entity to remove components from.
            *component_types (Type): The types of components to remove.
        """
        if entity in self.entities:
            internal_entity = self.entities[entity]
            for component_type in component_types:
                if component_type in internal_entity.components:
                    del internal_entity.components[component_type]

    def take(self, entity: Entity) -> tuple:
        """
        Remove an entity from the world and return its components.

        Args:
            entity (Entity): The entity to remove.

        Returns:
            tuple: A tuple containing the components of the entity.
        """
        if entity in self.entities:
            internal_entity = self.entities[entity]
            components = tuple(internal_entity.components.values())
            self.despawn(entity)
            return components
        return ()

    def iter(self) -> Iterator[Entity]:
        """
        Iterate over all entities in the world.

        Yields:
            Iterator[Entity]: An iterator of entities.
        """
        for _, internal_entity in self.entities.items():
            yield internal_entity.entity

    def iter_every(self) -> Iterator[Tuple[Entity, Tuple[Any, ...]]]:
        """
        Iterate over all entities and their components in the world.

        Yields:
            Iterator[Tuple[Entity, Tuple[Any, ...]]]: An iterator of tuples representing the entities and their components.
        """
        for entity, internal_entity in self.entities.items():
            yield entity, tuple(internal_entity.components.values())
