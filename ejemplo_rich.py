#!/usr/bin/env python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
# ]
# ///
from dataclasses import dataclass
from enum import Enum

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ContentType(Enum):
    PLAYER = "player"
    ENEMY = "enemy"
    TREASURE = "treasure"


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Room:
    connections: list[Direction]
    content: ContentType | None = None
    initial: bool = False


class RoomMap:
    def __init__(self, rooms: dict[tuple[int, int], Room]):
        """Initialize the room map with given rooms.

        Args:
            rooms: Dictionary mapping grid coordinates to Room objects.
        """
        self.console = Console()
        self.grid_width = 5
        self.grid_height = 4
        self.room_size = 3

        self.content_symbols = {
            ContentType.PLAYER: "@",
            ContentType.ENEMY: "E",
            ContentType.TREASURE: "$",
        }

        self.rooms = rooms
        self.map_data = self.generate_map()

        self.colors = {
            " ": "on grey15",
            ".": "dim white",
            "@": "bright_green",
            "E": "bright_red",
            "$": "bright_yellow",
            "#": "white",
            "S": "bright_blue",
        }

    def generate_map(self):
        """Generate the dungeon map as a 2D array of characters.

        Returns:
            2D list representing the dungeon with walls, floors, and content.
        """
        # Calculate total map size
        map_width = self.grid_width * (self.room_size + 1) + 1
        map_height = self.grid_height * (self.room_size + 1) + 1

        # Initialize walls
        dungeon = [[" " for _ in range(map_width)] for _ in range(map_height)]

        # Create rooms
        for (grid_row, grid_col), room in self.rooms.items():
            # Calculate room position in dungeon
            start_row = grid_row * (self.room_size + 1) + 1
            start_col = grid_col * (self.room_size + 1) + 1

            # Create room
            for r in range(self.room_size):
                for c in range(self.room_size):
                    dungeon[start_row + r][start_col + c] = "."

            # Add connections
            center_row = start_row + 1
            center_col = start_col + 1

            if Direction.UP in room.connections:
                dungeon[start_row - 1][center_col] = "."
            if Direction.DOWN in room.connections:
                dungeon[start_row + self.room_size][center_col] = "."
            if Direction.LEFT in room.connections:
                dungeon[center_row][start_col - 1] = "."
            if Direction.RIGHT in room.connections:
                dungeon[center_row][start_col + self.room_size] = "."

            # Add room content
            if room.content:
                symbol = self.content_symbols[room.content]
                dungeon[center_row][center_col] = symbol
            elif room.initial:
                dungeon[center_row][center_col] = "S"

        return dungeon

    def create_legend(self):
        """Create the legend panel with symbol explanations.

        Returns:
            Panel containing formatted legend text.
        """
        legend_items = [
            ("Jugador", "@", "bright_green"),
            ("Enemigo", "E", "bright_red"),
            ("Tesoro", "$", "bright_yellow"),
            ("Inicio", "S", "bright_blue"),
        ]

        legend_text = "\n".join(
            [f"[{color}]{symbol}[/] = {name}" for name, symbol, color in legend_items]
        )

        return Panel(legend_text, title="Leyenda", border_style="yellow")

    def display(self, clear: bool = True):
        """Display the dungeon map and legend side by side."""
        map_text = Text()
        for row in self.map_data:
            for tile in row:
                color = self.colors.get(tile, "white")
                if tile == " ":
                    map_text.append("   ", style=color)
                else:
                    map_text.append(f" {tile} ", style=color)
            map_text.append("\n")
        map_text = map_text[:-1]  # remove last newline

        map_panel = Panel(
            Align.center(map_text),
            title="🗺  Mapa Dungeon",
            border_style="bright_blue",
            padding=(1, 2),
        )

        if clear:
            self.console.clear()
        self.console.print(Columns([map_panel, self.create_legend()], expand=False))


if __name__ == "__main__":
    rooms = {
        (0, 1): Room(connections=[Direction.DOWN, Direction.RIGHT], content=ContentType.PLAYER),
        (0, 2): Room(connections=[Direction.LEFT]),
        (0, 4): Room(connections=[Direction.DOWN]),
        (1, 0): Room(connections=[Direction.RIGHT], content=ContentType.ENEMY),
        (1, 1): Room(connections=[Direction.UP, Direction.LEFT, Direction.RIGHT]),
        (1, 2): Room(connections=[Direction.LEFT, Direction.DOWN]),
        (1, 4): Room(connections=[Direction.UP, Direction.DOWN], content=ContentType.ENEMY),
        (2, 1): Room(connections=[Direction.RIGHT]),
        (2, 2): Room(
            connections=[Direction.UP, Direction.LEFT, Direction.RIGHT],
            content=ContentType.TREASURE,
        ),
        (2, 3): Room(connections=[Direction.LEFT, Direction.DOWN]),
        (2, 4): Room(connections=[Direction.UP, Direction.LEFT]),
        (3, 1): Room(connections=[Direction.UP], initial=True),
        (3, 3): Room(connections=[Direction.UP], content=ContentType.TREASURE),
    }
    game_map = RoomMap(rooms)
    game_map.display(clear=False)