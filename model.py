"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from typing import List
from random import random
from projects.pj02 import constants
from math import sin, cos, pi, sqrt


__author__ = "730408522"


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, other: Point) -> float:
        """Calculates distance between two cells."""
        result: float = sqrt((other.x - self.x)**2 + (other.y - self.y)**2)
        return result


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    # Part 1) Define a method named `tick` with no parameters.
    # Its purpose is to reassign the object's location attribute
    # the result of adding the self object's location with its
    # direction. Hint: Look at the add method.
    def tick(self) -> None:
        """Determines where cell will go."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
        if self.sickness > constants.RECOVERY_PERIOD:
            self.immunize()
        
    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_infected() is True:
            return "red"
        elif self.is_immune() is True:
            return "green"
        else:
            return "gray"

    def contract_disease(self) -> None:
        """Gives a cell a disease."""
        self.sickness = constants.INFECTED

    def is_vulnerable(self) -> bool:
        """Checks if a cell is vulnerable."""
        if self.sickness == constants.VULNERABLE:
            return True
        else:
            return False

    def is_infected(self) -> bool:
        """Checks if cell is infected."""
        if self.sickness >= constants.INFECTED:
            return True
        else:
            return False

    def contact_with(self, other: Cell) -> None:
        """Gives the other cell disease if one cell has it."""
        if self.is_infected() and other.is_vulnerable():
            other.contract_disease()
        if self.is_vulnerable() and other.is_infected():
            self.contract_disease()

    def immunize(self) -> None:
        """Makes a cell immune."""
        self.sickness = constants.IMMUNE

    def is_immune(self) -> bool:
        """Check if a cell is immune."""
        if self.sickness == constants.IMMUNE:
            return True
        else:
            return False


class Model:
    """The state of the simulation."""

    population: List[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, ninfected: int, nimmune: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        if ninfected >= cells or ninfected <= 0:
            raise ValueError("Some number of the Cell objects must begin infected.")
        elif nimmune >= cells or nimmune < 0:
            raise ValueError("Improper number of immune or infected cells.")
        else:
            for _ in range(0, cells - ninfected - nimmune):
                start_loc = self.random_location()
                start_dir = self.random_direction(speed)
                self.population.append(Cell(start_loc, start_dir))
            for i in range(0, ninfected):
                self.population[i].contract_disease()
                start_loc = self.random_location()
                start_dir = self.random_direction(speed)
                self.population.append(Cell(start_loc, start_dir))
            for j in range(0, nimmune):
                self.population[j + ninfected].immunize()
                start_loc = self.random_location()
                start_dir = self.random_direction(speed)
                self.population.append(Cell(start_loc, start_dir))

    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle = 2.0 * pi * random()
        dir_x = cos(random_angle) * speed
        dir_y = sin(random_angle) * speed
        return Point(dir_x, dir_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1

    def check_contacts(self) -> None:
        """Check if two cells contact."""
        i: int = 0
        # for i in range(0, len(self.population)):
        while i < len(self.population):
            for j in range(1, len(self.population)):
                dist: float = Point.distance(self.population[i].location, self.population[j].location)
                # dist: float = self.population[i].location.distance(self.population[i].location)
                if self.population[j] != self.population[i]:
                    if dist < constants.CELL_RADIUS:
                        self.population[i].contact_with(self.population[j])
            i += 1

    def is_complete(self) -> bool:
        """Checks if vc should stop running."""
        k: int = 0
        while k < len(self.population):
            if self.population[k].is_infected():
                return False
            k += 1
        return True
