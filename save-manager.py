import re
import yaml
from pathlib import Path
import vdf
import os
import ui
import variables
from simple_colors import red, blue, green, yellow
from rich import print
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout

console = Console()
layout = Layout()


class Game:
    app_id: str
    game_name: str
    pfx_path: str


class SteamGame(Game):

    def __init__(self, app_id, game_name, pfx_path) -> None:
        self.app_id = app_id
        self.game_name = game_name
        self.pfx_path = pfx_path

    def print(self):
        console.print(Panel(f"[b]Name:[/b] {self.game_name} | {
                      self.app_id} pfx_path: {self.pfx_path}"))

    def return_print(self) -> str:
        return f"[red]Name:[/red] {self.game_name} | {self.app_id} [blue]pfx_paths:[/blue] {self.pfx_path}\n"


class LutrisGame(Game):
    exe: str

    def __init__(self, game_name, exe, pfx_path) -> None:
        self.exe = exe
        self.game_name = game_name
        self.pfx_path = pfx_path

    def print(self):
        console.print(red("Name: "), self.game_name, yellow("Exe: "),
                      self.exe, blue("pfx_path"), self.pfx_path)

    def return_print(self) -> str:
        return f"[red]Name:[/red] {self.game_name} | {self.app_id} [blue]pfx_paths:[/blue] {self.pfx_path}\n"


class NonSteamGame(Game):
    def __init__(self, app_id, game_name, pfx_path) -> None:
        self.app_id = app_id
        self.game_name = game_name
        self.pfx_path = pfx_path

    def print(self):
        print(red("Name: "), f"{self.game_name} | {
              self.app_id}", blue("pfx_path: "), self.pfx_path)

    def return_print(self) -> str:
        return f"[red]Name:[/red] {self.game_name} | {self.app_id} [blue]pfx_paths:[/blue] {self.pfx_path}\n"

# functions


def get_shortcuts_path(path):
    path = os.path.expanduser(path)  # expands ~/ to /home/<username>

    for child_folder in os.listdir(path):
        child_path = os.path.join(path, child_folder)
        if os.path.isdir(child_path):  # and any(os.scandir(child_path)):
            config_path = os.path.join(child_path, "config")
            if os.path.exists(config_path):
                shortcuts_path = os.path.join(config_path, "shortcuts.vdf")
                if os.path.exists(shortcuts_path):
                    # print(f"Found: {shortcuts_path}")
                    variables.shortcuts_folders.append(shortcuts_path)


def read_vdf(path):
    path = os.path.expanduser(path)  # expands ~/ to /home/<username>
    with open(path, encoding='utf-8') as file:
        return vdf.parse(file)


def read_binary_vdf(path):
    path = os.path.expanduser(path)  # expands ~/ to /home/<username>
    with open(path, "rb") as file:
        return vdf.binary_load(file)


# Necessary as there can be multiple compatdatas
def get_pfx_paths(file, u_appid):
    pfx_paths = ""
    for file in variables.library_folders:
        path = os.path.join(file, f"steamapps/compatdata/{u_appid}")
        # print("Path: ", path)
        if os.path.exists(path):
            # for multiple paths
            pfx_paths = pfx_paths + " file://" + path
            # for single
            # pfx_paths = " file://" + path

    return pfx_paths

# MAIN


variables.library_data = read_vdf(
    "~/.local/share/Steam/config/libraryfolders.vdf")
variables.loginusers_data = read_vdf(
    "~/.local/share/Steam/config/loginusers.vdf")

default_pfx_renderable = Panel(
    title="Default Prefixes",
    renderable="[blue]Default wine prefix:[/blue] " +
    f"file://{os.path.expanduser("~/.wine")}" +

    "\n[blue]Default umu prefix:[/blue] " +
    f"file://{os.path.expanduser('~/Games/umu/umu-default/')}" +

    "\n[blue]Default Lutris prefix:[/blue] " +
    f"file://{os.path.expanduser('~/Games/')}"
)


# print(default_pfx_renderable)


steam_libraries_renderable = ""

for key, value in variables.library_data['libraryfolders'].items():
    variables.library_folders.append(value.get('path'))
    steam_libraries_renderable += f"[blue]Library {
        key}:[/blue] file://{value.get('path')} \n"
    # print(f"Library {key}: file://{value.get('path')}")


steam_libraries_renderable = Panel(
    title="Steam Libraries",
    renderable=steam_libraries_renderable)

# print(Columns([default_pfx_renderable,
#      steam_libraries_renderable], expand=True, equal=True))
# print("LibraryDATA: ", library_data)
# print("LoginUsers: ", loginusers_data)

steam_games_renderable = ""


# Search for app manifests in steamapps
for file in variables.library_folders:
    path = os.path.join(file, "steamapps")
    for child_folder in os.listdir(path):
        if child_folder.__contains__("appmanifest"):
            # print("Children: ", child_folder)

            appmanifest_path = os.path.join(path, child_folder)

            appmanifest_data = read_vdf(appmanifest_path)

            variables.appmanifests.append(appmanifest_data)

            appid = appmanifest_data["AppState"]["appid"]
            game_name = appmanifest_data["AppState"]["name"]

            pfx_path = get_pfx_paths(file, appid)
            steam_game = SteamGame(appid, game_name, pfx_path)
            variables.steam_games.append(steam_game)
            steam_games_renderable += steam_game.return_print()

steam_games_renderable = Panel(
    title="Steam Games",
    renderable=steam_games_renderable
)
# print(steam_games_renderable)

non_steam_games_renderable = ""
get_shortcuts_path("~/.local/share/Steam/userdata/")

for file in variables.shortcuts_folders:
    # shortcut_data = read_binary_vdf(file)
    # print("NonSteamGames: ", vdf.dumps(shortcut_data, pretty=True))
    with open(file, "rb") as sf:
        shortcuts = vdf.binary_load(sf)
    root = shortcuts['shortcuts']
    for key, entry in root.items():
        # Uncomment to see everything in each shortcut:
        # print(entry)

        exe = entry.get('Exe')
        name = entry.get('AppName')
        appid = entry.get('appid')  # signed
        u_appid = appid & 0xFFFFFFFF  # unsigned

        pfx_path = get_pfx_paths(file, u_appid)

        non_steam_game = NonSteamGame(appid, name, pfx_path)
        variables.non_steam_games.append(non_steam_game)
        non_steam_games_renderable += non_steam_game.return_print()


non_steam_games_renderable = Panel(
    title="Non Steam Games",
    renderable=non_steam_games_renderable)

# print(non_steam_games_renderable)


lutris_games_renderable = ""
lutris_path = os.path.expanduser("~/.local/share/lutris/games/")

for yaml_file in os.listdir(lutris_path):
    yaml_path = os.path.join(lutris_path, yaml_file)
    with open(yaml_path, "r") as f:
        yaml_data = yaml.safe_load(f)

        # removes .yml
        stem = Path(yaml_file).stem

        # regular expression to remove dash and numbers
        game_name = re.sub(r'-\d+$', '', stem)
        exe = f"file://{yaml_data.get("game", {}).get("exe", "")}"
        if exe == "file://":
            exe = ""

        pfx_path = f"file://{yaml_data.get("game", {}).get(
            "prefix", "")}"
        if pfx_path == "file://":
            pfx_path = ""

        lutris_game = LutrisGame(game_name, exe, pfx_path)

        variables.lutris_games.append(lutris_game)
        lutris_games_renderable += lutris_game.return_print()

lutris_games_renderable = Panel(
    title="Lutris Games",
    renderable=lutris_games_renderable
)
# print(lutris_games_renderable)


layout.split_row(
    Layout(name="left"),
    Layout(name="right")
)
layout["left"].split_column(
    Layout(default_pfx_renderable),
    Layout(steam_libraries_renderable)
)
layout["right"].split_column(
    Layout(steam_games_renderable),
    Layout(non_steam_games_renderable),
)
layout["left"].size = 50
print(layout)
print(lutris_games_renderable)
# if __name__ == "__main__":
# app = ui.SaveManagerApp()
# app.run()
