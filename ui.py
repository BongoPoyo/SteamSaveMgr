from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree
from textual.containers import Horizontal, Vertical

import variables
import subprocess
import os


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

    # Left panel
    # Right panel
    """
    BINDINGS = [("q", "quit", "Quit app")]

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(

            Vertical(
                GameTree(),
            ),
        )

        def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
            label = event.node.label
            # Extract path from label if appended
            if "::" in label:
                name, path = label.split("::", 1)
                subprocess.Popen(["xdg-open", path])

        yield Footer()
