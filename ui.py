from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree
from textual.containers import Horizontal, Vertical

# Assuming you have lists in variables: steam_games, non_steam_games, lutris_games
import variables
import subprocess


class GameTree(Static):
    def compose(self) -> ComposeResult:
        tree = Tree("Games")

        steam_branch = tree.root.add("Steam Games")
        for g in variables.steam_games:
            game = steam_branch.add(f"{g.game_name} ({g.app_id})")
            leaf = game.add_leaf(g.pfx_path)

        nonsteam_branch = tree.root.add("Non‑Steam Games")
        for g in variables.non_steam_games:
            game = nonsteam_branch.add_leaf(f"{g.game_name} ({g.app_id})")
            leaf = game.add_leaf(g.pfx_path)

        lutris_branch = tree.root.add("Lutris Games")
        for g in variables.lutris_games:
            game = lutris_branch.add_leaf(f"{g.game_name}")
            leaf = game.add_leaf(g.pfx_path)

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

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static("Default Prefixes", id="pfx_title"),
                Static(variables.default_pfx_renderable, id="pfx"),
            ),
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
