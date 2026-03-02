# phecs

![Icon](phecs_logo_small.png)

## What is it?
Phecs is an entity component system with a native python feeling api, and a simple implementation.
It is inspired by hecs in rust, but for python. python-hecs. phecs. 
Pronounced 'fecs' as in, what the phecs wrong with you.

## Why was it made?

Most ECS libraries sell themselves as being tools for performance.
Usually this comes at an ergonomic cost. Lots of boilerplate, component type pre-registration, and system abstractions.
However, as newer libraries came out with clever metaprogramming tricks, the boilerplate was heavily reduced, while still maintaining performance. People migrated to newer libraries, and so the desire for ease-of-use was clearly there.
In python, however, the ability to write a really performant ecs is limited.
Despite this, the existing popular ecs libraries are still unusually cumbersome.

If performance is only ever going to be good enough, then there shouldnt be any reason to sacrifice usability.
The library should be made to feel like it could be at home in the standard library.
Normal iteration, easily typed function names, no decorators, no type registration, no processor and system schedulers.
In Rust HECS does a good job of this, but has some funky query syntax that would look really weird in python.
This is a near direct port of the api surface of HECS, but with a python feel.

## But why should I use it?

Has the following advantages:

- Components are native python objects. No registration, decoration, or inheritance required.
- Zero boilerplate.
- No funky function names.
- Lower learning curve than other ECS libraries.
- Is fast enough. (100s of entities with 100s of components, 10s of systems, 30% of one 60fps frame.)
- Is only a couple hundred lines of code. (Hackable, Grokkable, Extendable if needed.)
- Is already written.
- Good for trying out an ECS for the first time.

## Why should I not use it?

- If you need more speed, honestly you should switch to a compiled language.


## How do?

### Installation

1. Install

   ```bash
   pip install phecs
   ```

2. Import

   ```python
   from phecs import World, Entity
   ```

### 1. Define Components

First, define some components.
In Phecs, any class is a component. You do not need to decorate them or subclass anything.

```python
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

class Health:
    def __init__(self, hp):
        self.hp = hp

class Burning:
    pass

class Dead:
    pass
```

Components can be any class, and can have any attributes or methods.
Compatable with dataclasses, and inheritance.

```python
from dataclasses import dataclass

@dataclass
class Position:
    x: float
    y: float

class Velocity(vec2):
    pass
```

You can put logic in your components, I'm not your dad. 

```python

class Shape:
    def __init__(self, vertices):
        self.vertices = vertices

    def area(self):
        return 0.5 * sum(
            (self.vertices[i].x * self.vertices[i + 1].y - self.vertices[i + 1].x * self.vertices[i].y)
            for i in range(len(self.vertices) - 1)
        )

```

Unless your mom was at $CONVENTION_NAME in 1998, in which case I might be your dad.


### 2. Make Your World, and Fill It With Entities

Create a world and spawn some entities with components.

```python
world = World() # initilizes a world object

# Create an entity with some components
entity = world.spawn(Position(0, 0), Velocity(1, 1), Health(100)) # add components at creation time
world.add(entity, Burning()) # or add another component later
world.despawn(entity) # remove the entity
```

world.spawn is variadic, so you can add as many components as you want, or just one, or none at all.

```python
world = World()
world.spawn(Position(0, 0), Velocity(1, 1), Health(100)) # valid
world.spawn(Position(1, 1)) # also valid
world.spawn()   # useful sometimes

```

A lot of the methods in phecs are variadic.

```python
world.remove(entity, Health) # remove a component
world.remove(entity, Health, Burning) # remove multiple components
```

### 3. Define Systems

Define some systems. In Phecs, a system is any function that operates on the world.
The main tool for iterating over entities is the `find` method.
Only entities with all the specified components will be iterated over.

```python
def physics(world): # this is a system
    for entity, position, velocity in world.find(Position, Velocity):
        position.x += velocity.dx
        position.y += velocity.dy

def burn(world): # also a system
    for entity, health, burning in world.find(Health, Burning):
        health.hp -= 1

def die_if_dead(world): # typical rpg system
    for entity, health in world.find(Health):
        if health.hp <= 0:
            world.add(entity, Dead())

def do_nothing_expensively(world):   # a very useful system
    for entity in world.iter():
        pass
```

### 4. Run Systems

Run the systems in your game loop.


```python
while True:
    physics(world)
    burn(world)
    die_if_dead(world)
draw(graphics_context, world)
```
Or just once, or whatever.

## Handy Features

### Filter Queries

In a find query entities can be filtered by components.

```python
for entity, position, velocity in world.find(Position, Velocity, without=Dead):
    pass    # only entities without a dead component

for entity, position, velocity in world.find(Position, Velocity, has=Health):
    pass    # only entities with a health component


```

Get complicated with it.

```python
for entity, position, velocity in world.find(Position, Velocity, has=(Player, Burning), without=Dead):
    pass    

for entity, position, health in world.find(Position, Health, has=(Burning, Desire), without=(Mercy, Fear)):
    pass
```

## See Also
Documentation at: www.eventually_a_link_to_documentation.com
