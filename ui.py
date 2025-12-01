from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree, DataTable
from textual.containers import Horizontal, Vertical

import variables
import subprocess
import os

ROWS = [
    ("Number", "GameType", "GameName", "AppID", "PFX"),
]


class GameTree(Static):
    def compose(self) -> ComposeResult:
        tree = Tree("Tree")

        # pfx
        pfx_tree = tree.root.add("Defaults")

        wine_branch = pfx_tree.add("Wine prefix")
        wine_branch.add_leaf(f"file://{os.path.expanduser('~/.wine')}")

        lutris_branch = pfx_tree.add("Lutris prefix")
        lutris_branch.add_leaf(
            f"file://{os.path.expanduser('~/Games/')}")

        umu_branch = pfx_tree.add("Umu prefix")
        umu_branch.add_leaf(
            f"file://{os.path.expanduser('~/Games/umu/umu-default/')}")

        # games
        game_tree = tree.root.add("Games")

        steam_branch = game_tree.add("Steam Games")
        for g in variables.steam_games:
            game = steam_branch.add(f"{g.game_name} ({g.app_id})")
            game.add_leaf(g.pfx_path)

        nonsteam_branch = game_tree.add("Non‑Steam Games")
        for g in variables.non_steam_games:
            game = nonsteam_branch.add(f"{g.game_name} ({g.app_id})")
            game.add_leaf(g.pfx_path)

        lutris_branch = game_tree.add("Lutris Games")
        for g in variables.lutris_games:
            game = lutris_branch.add(f"{g.game_name}")
            game.add_leaf(g.pfx_path)

        yield tree


class GameUI(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    """
    BINDINGS = [("q", "quit", "Quit app")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                DataTable(),
            ),
        )

        def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
            label = event.node.label
            # Extract path from label if appended
            if "::" in label:
                name, path = label.split("::", 1)
                subprocess.Popen(["xdg-open", path])

        yield Footer()

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"
        table = self.query_one(DataTable)

        i = 1
        for g in variables.steam_games:
            ROWS.append(
                (i, "Steam", g.game_name, g.app_id, g.pfx_path)
            )
            i += 1

        for g in variables.non_steam_games:
            ROWS.append(
                (i, "NonSteam", g.game_name, g.app_id, g.pfx_path)
            )
            i += 1
        for g in variables.lutris_games:
            ROWS.append(
                (i, "Lutris", g.game_name, g.app_id, g.pfx_path)
            )
            i += 1
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        row_index = event.coordinate.row
        column_index = event.coordinate.column
        # we add one because of heading, 4 is the pfx column
        path = ROWS[row_index + 1][4]
        subprocess.Popen(["xdg-open", path])
