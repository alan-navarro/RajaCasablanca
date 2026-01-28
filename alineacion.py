# from dataclasses import dataclass
# from typing import Set, Dict, List
# import matplotlib.pyplot as plt

# # =========================
# # DATA MODEL
# # =========================

# @dataclass(frozen=True)
# class Player:
#     name: str
#     features: Set[str]


# players: Dict[str, Player] = {
#     "Alan": Player("Alan", {"MF", "WN", "AT"}),
#     "Kevin": Player("Kevin", {"ML", "MC", "DF"}),
#     "Hieu": Player("Hieu", {"ML"}),
#     "Nam": Player("Nam", {"ML", "DF"}),
#     "Luis Soto": Player("Luis Soto", {"DF"}),
#     "Luis Quero": Player("Luis Quero", {"MF", "DF", "ML"}),
#     "Loco": Player("Loco", {"DF", "ML"}),
#     "Jaír": Player("Jaír", {"ML", "DF"}),
#     "JP": Player("JP", {"AT", "ML"}),
#     "Báez": Player("Báez", {"ML", "MC"}),
#     "Mario": Player("Mario", {"MC", "DF"}),
#     "Fer": Player("Fer", {"AT"}),
# }

# # =========================
# # CONTAINERS (EMPTY INIT)
# # =========================

# containers: Dict[str, List[str]] = {
#     "C1_DEF": [],
#     "C2_MID": [],
#     "C3_ATK": [],
# }

# # =========================
# # RULES
# # =========================

# def validate_container(container_name: str, player_names: List[str]) -> bool:
#     feats = [players[p].features for p in player_names]

#     if container_name == "C1_DEF":
#         return len(player_names) == 2 and all("DF" in f for f in feats)

#     if container_name == "C2_MID":
#         ml = sum("ML" in f for f in feats)
#         mc = sum("MC" in f for f in feats)
#         return len(player_names) == 3 and ml >= 1 and mc >= 1

#     if container_name == "C3_ATK":
#         return len(player_names) == 1 and "AT" in feats[0]

#     return False

# # =========================
# # BENCH
# # =========================

# def get_bench() -> List[str]:
#     busy = {p for plist in containers.values() for p in plist}
#     return sorted(set(players) - busy)

# # =========================
# # LINEUP SELECTION
# # =========================

# def select_container(container_name: str):
#     required = {"C1_DEF": 2, "C2_MID": 3, "C3_ATK": 1}[container_name]

#     while True:
#         available = get_bench()
#         print(f"\nSelecting for {container_name}")
#         print("Available players:")
#         for p in available:
#             print(f" - {p} {players[p].features}")

#         raw = input(f"Type {required} player names (comma separated): ")
#         selected = [x.strip() for x in raw.split(",")]

#         if len(selected) != required:
#             print("✖ Incorrect number of players")
#             continue

#         if any(p not in available for p in selected):
#             print("✖ One or more players unavailable")
#             continue

#         if validate_container(container_name, selected):
#             containers[container_name] = selected
#             print(f"✔ {container_name} confirmed")
#             break
#         else:
#             print("✖ Selection violates container rules")

# # =========================
# # SWAP LOGIC
# # =========================

# def find_container(player: str):
#     for cname, plist in containers.items():
#         if player in plist:
#             return cname
#     return None


# def valid_replacements(bench_player: str) -> List[str]:
#     matches = []
#     for cname, plist in containers.items():
#         for busy in plist:
#             updated = plist.copy()
#             updated[updated.index(busy)] = bench_player
#             if (
#                 players[bench_player].features & players[busy].features
#                 and validate_container(cname, updated)
#             ):
#                 matches.append(busy)
#     return sorted(set(matches))


# def apply_swap(bench_player: str, busy_player: str):
#     cname = find_container(busy_player)
#     plist = containers[cname]
#     plist[plist.index(busy_player)] = bench_player

# # =========================
# # VISUALIZATION
# # =========================

# def draw_state():
#     plt.close("all")
#     fig, ax = plt.subplots(figsize=(12, 5))
#     ax.axis("off")
#     ax.set_xlim(0, 13)
#     ax.set_ylim(0, 4)

#     pos = {"C1_DEF": 0.5, "C2_MID": 4.8, "C3_ATK": 9.3}

#     for cname, x in pos.items():
#         ax.add_patch(plt.Rectangle((x, 1), 3.5, 2, fill=False))
#         ax.text(x + 1.75, 2.8, cname, ha="center", fontweight="bold")
#         for i, p in enumerate(containers[cname]):
#             feats = ",".join(players[p].features)
#             ax.text(x + 0.2, 2.2 - i * 0.4, f"{p} ({feats})")

#     bench = get_bench()
#     ax.text(0.5, 0.5, "BENCH:", fontweight="bold")
#     for i, p in enumerate(bench):
#         ax.text(0.5 + (i % 4) * 3.2, 0.1 - (i // 4) * 0.35,
#                 f"{p} ({','.join(players[p].features)})")

#     plt.show(block=False)
#     plt.pause(0.1)

# # =========================
# # MAIN LOOP
# # =========================

# def interactive_session():
#     print("\n--- STARTING LINE-UP SELECTION ---")
#     for cname in containers:
#         select_container(cname)
#         draw_state()

#     print("\n--- BENCH SWAP MODE ---")

#     while True:
#         bench = get_bench()
#         print("\nBench:", bench)
#         pick = input("Select BENCH player (or 'exit'): ").strip()
#         if pick == "exit":
#             break
#         if pick not in bench:
#             print("✖ Invalid bench player")
#             continue

#         options = valid_replacements(pick)
#         if not options:
#             print("✖ No valid replacements")
#             continue

#         print("Can replace:")
#         for p in options:
#             print(f" - {p} {players[p].features}")

#         target = input("Replace who?: ").strip()
#         if target not in options:
#             print("✖ Invalid choice")
#             continue

#         apply_swap(pick, target)
#         draw_state()


# if __name__ == "__main__":
#     interactive_session()

# # Prototipo 2
# import time
# import unicodedata
# from dataclasses import dataclass
# from typing import Dict, Set, List
# import matplotlib.pyplot as plt

# # =========================
# # UTILITIES
# # =========================

# def normalize(text: str) -> str:
#     """Lowercase + remove accents"""
#     return ''.join(
#         c for c in unicodedata.normalize("NFD", text.lower())
#         if unicodedata.category(c) != 'Mn'
#     )

# # =========================
# # DATA MODEL
# # =========================

# @dataclass
# class Player:
#     name: str
#     features: Set[str]
#     time_played: float = 0.0
#     last_entered: float | None = None


# players: Dict[str, Player] = {
#     "Alan": Player("Alan", {"MF", "WN", "AT"}),
#     "Kevin": Player("Kevin", {"ML", "MC", "DF"}),
#     "Hieu": Player("Hieu", {"ML"}),
#     "Nam": Player("Nam", {"ML", "DF"}),
#     "Luis Soto": Player("Luis Soto", {"DF"}),
#     "Luis Quero": Player("Luis Quero", {"MF", "DF", "ML"}),
#     "Loco": Player("Loco", {"DF", "ML"}),
#     "Jaír": Player("Jaír", {"ML", "DF"}),
#     "JP": Player("JP", {"AT", "ML"}),
#     "Báez": Player("Báez", {"ML", "MC"}),
#     "Mario": Player("Mario", {"MC", "DF"}),
#     "Fer": Player("Fer", {"AT"}),
# }

# NAME_LOOKUP = {normalize(p): p for p in players}

# # =========================
# # CONTAINERS
# # =========================

# containers = {
#     "C1_DEF": [],
#     "C2_MID": [],
#     "C3_ATK": [],
# }

# CONTAINER_SIZES = {"C1_DEF": 2, "C2_MID": 3, "C3_ATK": 1}

# # =========================
# # TIME CONTROL
# # =========================

# MATCH_START: float | None = None

# def start_playing(player_name: str):
#     players[player_name].last_entered = time.time()

# def stop_playing(player_name: str):
#     p = players[player_name]
#     if p.last_entered is not None:
#         p.time_played += time.time() - p.last_entered
#         p.last_entered = None

# def stop_all():
#     for cname in containers:
#         for p in containers[cname]:
#             stop_playing(p)

# # =========================
# # VALIDATION RULES
# # =========================

# def validate_container(cname: str, names: List[str]) -> bool:
#     feats = [players[n].features for n in names]

#     if cname == "C1_DEF":
#         return len(names) == 2 and all("DF" in f for f in feats)

#     if cname == "C2_MID":
#         return len(names) == 3 and sum("ML" in f for f in feats) >= 1 and sum("MC" in f for f in feats) >= 1

#     if cname == "C3_ATK":
#         return len(names) == 1 and "AT" in feats[0]

#     return False

# # =========================
# # BENCH
# # =========================

# def get_bench():
#     busy = {p for plist in containers.values() for p in plist}
#     return sorted(set(players) - busy)

# # =========================
# # VISUALIZATION
# # =========================

# def draw_state():
#     plt.close("all")
#     fig, ax = plt.subplots(figsize=(12, 5))
#     ax.axis("off")
#     ax.set_xlim(0, 13)
#     ax.set_ylim(0, 4)

#     if MATCH_START:
#         elapsed = int(time.time() - MATCH_START)
#         ax.text(12.8, 3.8, f"⏱ {elapsed}s", ha="right", va="top", fontweight="bold")

#     positions = {"C1_DEF": 0.5, "C2_MID": 4.8, "C3_ATK": 9.3}

#     for cname, x in positions.items():
#         ax.add_patch(plt.Rectangle((x, 1), 3.5, 2, fill=False))
#         ax.text(x + 1.75, 2.8, cname, ha="center", fontweight="bold")
#         for i, p in enumerate(containers[cname]):
#             ax.text(x + 0.2, 2.2 - i * 0.4, f"{p}")

#     ax.text(0.5, 0.5, "BENCH:", fontweight="bold")
#     bench = get_bench()
#     for i, p in enumerate(bench):
#         ax.text(0.5 + (i % 4) * 3.2, 0.1 - (i // 4) * 0.35, p)

#     plt.show(block=False)
#     plt.pause(0.1)

# # =========================
# # INPUT HANDLING
# # =========================

# def resolve_name(inp: str):
#     return NAME_LOOKUP.get(normalize(inp))

# # =========================
# # LINEUP SELECTION
# # =========================

# def select_container(cname: str):
#     while True:
#         print(f"\nSelecting {CONTAINER_SIZES[cname]} for {cname}")
#         print("Available:", get_bench())

#         raw = input("> ").split(",")
#         chosen = [resolve_name(x.strip()) for x in raw]

#         if None in chosen or len(chosen) != CONTAINER_SIZES[cname]:
#             print("✖ Invalid selection")
#             continue

#         if not validate_container(cname, chosen):
#             print("✖ Rule violation")
#             continue

#         containers[cname] = chosen
#         for p in chosen:
#             start_playing(p)
#         break

# # =========================
# # SWAP LOGIC
# # =========================

# def valid_replacements(bench_player):
#     res = []
#     for cname, plist in containers.items():
#         for busy in plist:
#             updated = plist.copy()
#             updated[updated.index(busy)] = bench_player
#             if (
#                 players[bench_player].features & players[busy].features
#                 and validate_container(cname, updated)
#             ):
#                 res.append(busy)
#     return sorted(set(res))

# def apply_swap(bench_player, busy_player):
#     for cname, plist in containers.items():
#         if busy_player in plist:
#             stop_playing(busy_player)
#             start_playing(bench_player)
#             plist[plist.index(busy_player)] = bench_player

# # =========================
# # MAIN LOOP
# # =========================

# def interactive_session():
#     global MATCH_START

#     for cname in containers:
#         select_container(cname)
#         draw_state()

#     MATCH_START = time.time()
#     print("\n--- MATCH STARTED ---")

#     while True:
#         draw_state()
#         bench = get_bench()
#         pick = input("\nSelect BENCH player or EXIT: ")

#         if normalize(pick) == "exit":
#             break

#         bench_player = resolve_name(pick)
#         if bench_player not in bench:
#             print("✖ Invalid bench player")
#             continue

#         options = valid_replacements(bench_player)
#         if not options:
#             print("✖ No valid replacements")
#             continue

#         print("Can replace:", options)
#         target = resolve_name(input("Replace who?: "))
#         if target not in options:
#             print("✖ Invalid target")
#             continue

#         apply_swap(bench_player, target)

#     stop_all()

#     print("\nFINAL TIME PLAYED (seconds):")
#     final_times = {p.name: int(p.time_played) for p in players.values()}
#     print(final_times)

# # =========================
# # ENTRY POINT
# # =========================

# if __name__ == "__main__":
#     interactive_session()

# prototipo 3

# import unicodedata
# from dataclasses import dataclass
# from typing import Dict, Set, List
# import matplotlib.pyplot as plt

# # =========================
# # UTILITIES
# # =========================

# def normalize(text: str) -> str:
#     """Lowercase + remove accents"""
#     return ''.join(
#         c for c in unicodedata.normalize("NFD", text.lower())
#         if unicodedata.category(c) != 'Mn'
#     )

# # =========================
# # DATA MODEL
# # =========================

# @dataclass
# class Player:
#     name: str
#     features: Set[str]


# players: Dict[str, Player] = {
#     "Alan": Player("Alan", {"MF", "WN", "AT"}),
#     "Kevin": Player("Kevin", {"ML", "MC", "DF"}),
#     "Hieu": Player("Hieu", {"ML"}),
#     "Nam": Player("Nam", {"ML", "DF"}),
#     "Luis Soto": Player("Luis Soto", {"DF"}),
#     "Luis Quero": Player("Luis Quero", {"MF", "DF", "ML"}),
#     "Loco": Player("Loco", {"DF", "ML"}),
#     "Jaír": Player("Jaír", {"ML", "DF"}),
#     "JP": Player("JP", {"AT", "ML"}),
#     "Báez": Player("Báez", {"ML", "MC"}),
#     "Mario": Player("Mario", {"MC", "DF"}),
#     "Fer": Player("Fer", {"AT"}),
# }

# NAME_LOOKUP = {normalize(p): p for p in players}

# # =========================
# # CONTAINERS
# # =========================

# containers = {
#     "C1_DEF": [],
#     "C2_MID": [],
#     "C3_ATK": [],
# }

# CONTAINER_SIZES = {
#     "C1_DEF": 2,
#     "C2_MID": 3,
#     "C3_ATK": 1,
# }

# # =========================
# # VALIDATION RULES
# # =========================

# def validate_container(cname: str, names: List[str]) -> bool:
#     feats = [players[n].features for n in names]

#     if cname == "C1_DEF":
#         return len(names) == 2 and all("DF" in f for f in feats)

#     if cname == "C2_MID":
#         return (
#             len(names) == 3
#             and sum("ML" in f for f in feats) >= 1
#             and sum("MC" in f for f in feats) >= 1
#         )

#     if cname == "C3_ATK":
#         return len(names) == 1 and "AT" in feats[0]

#     return False

# # =========================
# # BENCH
# # =========================

# def get_bench():
#     busy = {p for plist in containers.values() for p in plist}
#     return sorted(set(players) - busy)

# # =========================
# # VISUALIZATION
# # =========================

# def draw_state():
#     plt.close("all")
#     fig, ax = plt.subplots(figsize=(12, 5))
#     ax.axis("off")
#     ax.set_xlim(0, 13)
#     ax.set_ylim(0, 4)

#     positions = {
#         "C1_DEF": 0.5,
#         "C2_MID": 4.8,
#         "C3_ATK": 9.3,
#     }

#     for cname, x in positions.items():
#         ax.add_patch(plt.Rectangle((x, 1), 3.5, 2, fill=False))
#         ax.text(x + 1.75, 2.8, cname, ha="center", fontweight="bold")

#         for i, p in enumerate(containers[cname]):
#             ax.text(x + 0.2, 2.2 - i * 0.4, p)

#     ax.text(0.5, 0.5, "BENCH:", fontweight="bold")
#     bench = get_bench()
#     for i, p in enumerate(bench):
#         ax.text(
#             0.5 + (i % 4) * 3.2,
#             0.1 - (i // 4) * 0.35,
#             p
#         )

#     plt.show(block=False)
#     plt.pause(0.1)

# # =========================
# # INPUT HANDLING
# # =========================

# def resolve_name(inp: str):
#     return NAME_LOOKUP.get(normalize(inp))

# # =========================
# # LINEUP SELECTION
# # =========================

# def select_container(cname: str):
#     while True:
#         print(f"\nSelecting {CONTAINER_SIZES[cname]} for {cname}")
#         print("Available:", get_bench())

#         raw = input("> ").split(",")
#         chosen = [resolve_name(x.strip()) for x in raw]

#         if None in chosen or len(chosen) != CONTAINER_SIZES[cname]:
#             print("✖ Invalid selection")
#             continue

#         if not validate_container(cname, chosen):
#             print("✖ Rule violation")
#             continue

#         containers[cname] = chosen
#         break

# # =========================
# # SWAP LOGIC
# # =========================

# def valid_replacements(bench_player):
#     res = []
#     for cname, plist in containers.items():
#         for busy in plist:
#             updated = plist.copy()
#             updated[updated.index(busy)] = bench_player
#             if (
#                 players[bench_player].features & players[busy].features
#                 and validate_container(cname, updated)
#             ):
#                 res.append(busy)
#     return sorted(set(res))

# def apply_swap(bench_player, busy_player):
#     for cname, plist in containers.items():
#         if busy_player in plist:
#             plist[plist.index(busy_player)] = bench_player

# # =========================
# # MAIN LOOP
# # =========================

# def interactive_session():
#     for cname in containers:
#         select_container(cname)
#         draw_state()

#     print("\n--- LINEUP READY ---")

#     while True:
#         draw_state()
#         bench = get_bench()
#         pick = input("\nSelect BENCH player or EXIT: ")

#         if normalize(pick) == "exit":
#             break

#         bench_player = resolve_name(pick)
#         if bench_player not in bench:
#             print("✖ Invalid bench player")
#             continue

#         options = valid_replacements(bench_player)
#         if not options:
#             print("✖ No valid replacements")
#             continue

#         print("Can replace:", options)
#         target = resolve_name(input("Replace who?: "))
#         if target not in options:
#             print("✖ Invalid target")
#             continue

#         apply_swap(bench_player, target)

# # =========================
# # ENTRY POINT
# # =========================

# if __name__ == "__main__":
#     interactive_session()

# prototipo 4

import unicodedata
from dataclasses import dataclass
from typing import Dict, Set, List
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# =========================
# CONFIG
# =========================

PITCH_IMAGE_PATH = "campo2.png"  # <-- put your local pitch image here

# Fixed positions per container (x, y in pitch coordinates)
PITCH_POSITIONS = {
    "C1_DEF": [(0.25, 0.80), (0.25, 0.50)],
    "C2_MID": [(0.5, 0.90), (0.5, 0.65), (0.5, 0.40)],
    "C3_ATK": [(0.75, 0.65)],
}

# =========================
# UTILITIES
# =========================

def normalize(text: str) -> str:
    """Lowercase + remove accents"""
    return ''.join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != 'Mn'
    )

# =========================
# DATA MODEL
# =========================

@dataclass
class Player:
    name: str
    features: Set[str]

players: Dict[str, Player] = {
    "Alan": Player("Alan", {"ML", "MC", "AT"}),
    "Kevin": Player("Kevin", {"ML", "MC", "DF"}),
    "Hieu": Player("Hieu", {"ML"}),
    "Nam": Player("Nam", {"ML", "DF"}),
    "Luis": Player("Luis Soto", {"DF"}),
    "Quero": Player("Quero", {"MC", "DF", "ML"}),
    "Loco": Player("Loco", {"DF", "ML"}),
    "Jaír": Player("Jaír", {"ML", "DF"}),
    "JP": Player("JP", {"AT", "ML"}),
    "Báez": Player("Báez", {"ML", "MC"}),
    "Mario": Player("Mario", {"MC", "DF"}),
    "Fer": Player("Fer", {"AT"}),
}

NAME_LOOKUP = {normalize(p): p for p in players}

# =========================
# CONTAINERS
# =========================

containers = {
    "C1_DEF": [],
    "C2_MID": [],
    "C3_ATK": [],
}

CONTAINER_SIZES = {
    "C1_DEF": 2,
    "C2_MID": 3,
    "C3_ATK": 1,
}

# =========================
# VALIDATION RULES
# =========================

def validate_container(cname: str, names: List[str]) -> bool:
    feats = [players[n].features for n in names]

    if cname == "C1_DEF":
        return len(names) == 2 and all("DF" in f for f in feats)

    if cname == "C2_MID":
        return (
            len(names) == 3
            and sum("ML" in f for f in feats) >= 1
            and sum("MC" in f for f in feats) >= 1
        )

    if cname == "C3_ATK":
        return len(names) == 1 and "AT" in feats[0]

    return False

# =========================
# BENCH
# =========================

def get_bench():
    busy = {p for plist in containers.values() for p in plist}
    return sorted(set(players) - busy)

# =========================
# VISUALIZATION (PITCH)
# =========================

def draw_state():
    plt.close("all")

    img = mpimg.imread(PITCH_IMAGE_PATH)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(img)
    ax.axis("off")

    h, w = img.shape[:2]

    # Draw players on pitch
    for cname, plist in containers.items():
        positions = PITCH_POSITIONS[cname]

        for i, player_name in enumerate(plist):
            x_norm, y_norm = positions[i]
            x = x_norm * w
            y = y_norm * h

            ax.scatter(x, y, s=1100, c="#4da6ff", edgecolors="black", zorder=3)
            ax.text(
                x,
                y,
                player_name,
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="black",
                zorder=4
            )

    # Bench (bottom)
    bench = get_bench()
    ax.text(w * 0.02, h * 0.1, "Banca:", fontsize=11, fontweight="bold")

    for i, p in enumerate(bench):
        ax.text(
            w * (0.12 + i * 0.12),
            h * 0.15,
            p,
            fontsize=10
        )

    plt.show(block=False)
    plt.pause(0.1)

# =========================
# INPUT HANDLING
# =========================

def resolve_name(inp: str):
    return NAME_LOOKUP.get(normalize(inp))

# =========================
# LINEUP SELECTION
# =========================

def select_container(cname: str):
    while True:
        print(f"\nSelecting {CONTAINER_SIZES[cname]} for {cname}")
        print("Available:", get_bench())

        raw = input("> ").split(",")
        chosen = [resolve_name(x.strip()) for x in raw]

        if None in chosen or len(chosen) != CONTAINER_SIZES[cname]:
            print("✖ Invalid selection")
            continue

        if not validate_container(cname, chosen):
            print("✖ Rule violation")
            continue

        containers[cname] = chosen
        break

# =========================
# SWAP LOGIC
# =========================

def valid_replacements(bench_player):
    res = []
    for cname, plist in containers.items():
        for busy in plist:
            updated = plist.copy()
            updated[updated.index(busy)] = bench_player
            if (
                players[bench_player].features & players[busy].features
                and validate_container(cname, updated)
            ):
                res.append(busy)
    return sorted(set(res))

def apply_swap(bench_player, busy_player):
    for cname, plist in containers.items():
        if busy_player in plist:
            plist[plist.index(busy_player)] = bench_player

# =========================
# MAIN LOOP
# =========================

def interactive_session():
    for cname in containers:
        select_container(cname)
        draw_state()

    print("\n--- LINEUP READY ---")

    while True:
        draw_state()
        bench = get_bench()
        print("Available:", get_bench())
        pick = input("\nSelecciona un jugador de la banca: ")

        if normalize(pick) == "exit":
            break

        bench_player = resolve_name(pick)
        if bench_player not in bench:
            print("✖ Cambio no válido")
            continue

        options = valid_replacements(bench_player)
        if not options:
            print("✖ Cambio no válido")
            continue

        print("Can replace:", options)
        target = resolve_name(input("A quién reemplaza?: "))
        if target not in options:
            print("✖ Jugador no válido")
            continue

        apply_swap(bench_player, target)

# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    interactive_session()

# prototipo 5
# import time
# from dash import Dash, dcc, html, Input, Output, State
# import plotly.graph_objects as go

# # =========================
# # DATA
# # =========================

# players = {
#     "Alan": {"ML", "MC", "AT"},
#     "Kevin": {"ML", "MC", "DF"},
#     "Hieu": {"ML"},
#     "Nam": {"ML", "DF"},
#     "Luis Soto": {"DF"},
#     "Luis Quero": {"MC", "DF", "ML"},
#     "Loco": {"DF", "ML"},
#     "Jaír": {"ML", "DF"},
#     "JP": {"AT", "ML"},
#     "Báez": {"ML", "MC"},
#     "Mario": {"MC", "DF"},
#     "Fer": {"AT"},
# }

# # Cambio de alineación
# LIMITS = {
#     "C1_DEF": 2,
#     "C2_MID": 3,
#     "C3_ATK": 1,
# }

# # =========================
# # TIMER STATE
# # =========================

# player_time = {p: 0.0 for p in players}
# lap_running = False
# lap_start = None
# last_active = set()

# # =========================
# # OPTIONS
# # =========================

# def options_for(required, used):
#     return [
#         {"label": p, "value": p}
#         for p, feats in players.items()
#         if required & feats and p not in used
#     ]
# # =========================
# # FORMATO DEL TIEMPO
# # =========================
# def format_mm_ss(seconds: float) -> str:
#     minutes = int(seconds) // 60
#     secs = int(seconds) % 60
#     return f"{minutes:02d}:{secs:02d}"


# # =========================
# # PITCH
# # =========================

# def pitch_figure(c1, c2, c3, elapsed):
#     fig = go.Figure()

#     fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=60)

#     zones = [
#         ("DEF (2)", 20, c1),
#         ("MID (3)", 50, c2),
#         ("ATK (1)", 80, c3),
#     ]

#     for label, x, plist in zones:
#         fig.add_annotation(
#             x=x, y=55,
#             text=label,
#             showarrow=False,
#             font=dict(size=16)
#         )
#         for i, p in enumerate(plist):
#             fig.add_annotation(
#                 x=x,
#                 y=45 - i * 7,
#                 text=p,
#                 showarrow=False,
#                 font=dict(size=14)
#             )

#     # LIVE TIMER
#     fig.add_annotation(
#         x=98, y=58,
#         text=f"⏱ {format_mm_ss(elapsed)}",
#         showarrow=False,
#         xanchor="right",
#         font=dict(size=18)
#     )

#     fig.update_layout(
#         height=420,
#         margin=dict(l=10, r=10, t=10, b=10),
#         xaxis=dict(visible=False, range=[0, 100]),
#         yaxis=dict(visible=False, range=[0, 60]),
#     )
#     return fig

# # =========================
# # APP
# # =========================

# app = Dash(__name__)

# app.layout = html.Div(
#     style={"width": "900px", "margin": "auto"},
#     children=[
#         html.H3("⚽ Line-up Builder"),

#         dcc.Store(id="timer-start"),
#         dcc.Store(id="elapsed", data=0),
#         dcc.Interval(id="tick", interval=500, disabled=True),

#         html.Label("C1_DEF"),
#         dcc.Dropdown(id="c1", multi=True),

#         html.Label("C2_MID"),
#         dcc.Dropdown(id="c2", multi=True),

#         html.Label("C3_ATK"),
#         dcc.Dropdown(id="c3", multi=True),

#         dcc.Graph(id="pitch"),

#         html.Button("START / STOP LAP", id="lap-btn"),
#     ]
# )

# # =========================
# # OPTIONS UPDATE
# # =========================

# @app.callback(
#     Output("c1", "options"),
#     Output("c2", "options"),
#     Output("c3", "options"),
#     Input("c1", "value"),
#     Input("c2", "value"),
#     Input("c3", "value"),
# )
# def update_options(c1, c2, c3):
#     c1, c2, c3 = c1 or [], c2 or [], c3 or []
#     used = set(c1 + c2 + c3)

#     return (
#         options_for({"DF"}, used - set(c1)),
#         options_for({"ML", "MC"}, used - set(c2)),
#         options_for({"AT"}, used - set(c3)),
#     )

# # =========================
# # LIMIT SELECTIONS
# # =========================

# @app.callback(
#     Output("c1", "value"),
#     Output("c2", "value"),
#     Output("c3", "value"),
#     Input("c1", "value"),
#     Input("c2", "value"),
#     Input("c3", "value"),
# )
# def enforce_limits(c1, c2, c3):
#     return (
#         (c1 or [])[:2],
#         (c2 or [])[:3],
#         (c3 or [])[:1],
#     )

# # =========================
# # TIMER BUTTON
# # =========================

# @app.callback(
#     Output("tick", "disabled"),
#     Output("timer-start", "data"),
#     Input("lap-btn", "n_clicks"),
#     State("timer-start", "data"),
#     prevent_initial_call=True
# )
# def toggle_timer(_, start):
#     global lap_running, lap_start, last_active

#     now = time.time()

#     if not lap_running:
#         lap_running = True
#         lap_start = now
#         return False, now

#     lap_running = False
#     elapsed = now - lap_start
#     for p in last_active:
#         player_time[p] += elapsed

#     print("\nFINAL TIMES:")
#     for p, t in player_time.items():
#         print(f"{p}: {round(t, 1)}s")

#     return True, None

# # =========================
# # TIMER TICK
# # =========================

# @app.callback(
#     Output("elapsed", "data"),
#     Input("tick", "n_intervals"),
#     State("timer-start", "data"),
#     State("c1", "value"),
#     State("c2", "value"),
#     State("c3", "value"),
# )
# def update_time(_, start, c1, c2, c3):
#     global last_active

#     if not start:
#         return 0

#     last_active = set((c1 or []) + (c2 or []) + (c3 or []))
#     return time.time() - start

# # =========================
# # DRAW
# # =========================

# @app.callback(
#     Output("pitch", "figure"),
#     Input("c1", "value"),
#     Input("c2", "value"),
#     Input("c3", "value"),
#     Input("elapsed", "data"),
# )
# def draw(c1, c2, c3, elapsed):
#     return pitch_figure(c1 or [], c2 or [], c3 or [], elapsed)

# # =========================
# # RUN
# # =========================

# if __name__ == "__main__":
#     app.run(debug=True)
# proptotipo 6
# from dash import Dash, html, dcc, Input, Output, State, callback_context
# import plotly.graph_objects as go
# import time

# # ----------------------------------
# # PLAYERS
# # ----------------------------------

# players = {
#     "Alan": {"ML", "MC", "AT"},
#     "Kevin": {"ML", "MC", "DF"},
#     "Hieu": {"ML"},
#     "Nam": {"ML", "DF"},
#     "Luis Soto": {"DF"},
#     "Luis Quero": {"MC", "DF", "ML"},
#     "Loco": {"DF", "ML"},
#     "Jaír": {"ML", "DF"},
#     "JP": {"AT", "ML"},
#     "Báez": {"ML", "MC"},
#     "Mario": {"MC", "DF"},
#     "Fer": {"AT"},
# }

# # ----------------------------------
# # FILTERS
# # ----------------------------------

# DEF_PLAYERS = [p for p, f in players.items() if "DF" in f]
# MID_PLAYERS = [p for p, f in players.items() if f & {"ML", "MC"}]
# ATK_PLAYERS = [p for p, f in players.items() if "AT" in f]

# # ----------------------------------
# # PITCH POSITIONS
# # ----------------------------------

# COLUMN_X = {
#     "C1_DEF": 0.2,
#     "C2_MID": 0.5,
#     "C3_ATK": 0.8,
# }

# ROW_Y = [0.7, 0.5, 0.3]

# # ----------------------------------
# # DASH APP
# # ----------------------------------

# app = Dash(__name__)

# app.layout = html.Div([
#     dcc.Store(id="game-state", data={
#         "on_pitch": {"C1_DEF": [], "C2_MID": [], "C3_ATK": []},
#         "time": {},
#         "running": False,
#         "last_tick": None,
#         "seconds": 0
#     }),

#     dcc.Interval(id="interval", interval=1000, disabled=True),

#     html.H2("⏱️ Time: 00:00", id="timer", style={
#         "position": "absolute",
#         "top": "10px",
#         "right": "20px"
#     }),

#     html.Div([
#         dcc.Dropdown(
#             id="def-dd",
#             options=[{"label": p, "value": p} for p in DEF_PLAYERS],
#             multi=True,
#             placeholder="Select DEF (2)"
#         ),
#         dcc.Dropdown(
#             id="mid-dd",
#             options=[{"label": p, "value": p} for p in MID_PLAYERS],
#             multi=True,
#             placeholder="Select MID (3)"
#         ),
#         dcc.Dropdown(
#             id="atk-dd",
#             options=[{"label": p, "value": p} for p in ATK_PLAYERS],
#             multi=True,
#             placeholder="Select ATK (1)"
#         ),
#     ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "10px"}),

#     html.Br(),

#     dcc.Graph(id="pitch", style={"height": "400px"}),

#     html.Button("▶ START / STOP", id="lap-btn")
# ])

# # ----------------------------------
# # HELPERS
# # ----------------------------------

# def build_pitch_figure(on_pitch):
#     fig = go.Figure()

#     fig.add_shape(
#         type="rect",
#         x0=0, y0=0, x1=1, y1=1,
#         fillcolor="#1e7f34",
#         line=dict(width=0)
#     )

#     for cname, players_list in on_pitch.items():
#         x = COLUMN_X[cname]

#         for i, player in enumerate(players_list):
#             fig.add_trace(go.Scatter(
#                 x=[x],
#                 y=[ROW_Y[i]],
#                 mode="markers+text",
#                 text=[player],
#                 textposition="bottom center",
#                 marker=dict(
#                     size=38,
#                     color="#4da6ff",
#                     line=dict(color="black", width=2)
#                 ),
#                 showlegend=False
#             ))

#     fig.update_xaxes(visible=False, range=[0, 1])
#     fig.update_yaxes(visible=False, range=[0, 1])
#     fig.update_layout(
#         margin=dict(l=10, r=10, t=10, b=10),
#         plot_bgcolor="#1e7f34"
#     )

#     return fig

# def format_time(seconds):
#     m, s = divmod(seconds, 60)
#     return f"{m:02d}:{s:02d}"

# # ----------------------------------
# # MAIN CALLBACK (SINGLE SOURCE OF TRUTH)
# # ----------------------------------

# @app.callback(
#     Output("game-state", "data"),
#     Output("pitch", "figure"),
#     Output("timer", "children"),
#     Output("interval", "disabled"),
#     Input("def-dd", "value"),
#     Input("mid-dd", "value"),
#     Input("atk-dd", "value"),
#     Input("lap-btn", "n_clicks"),
#     Input("interval", "n_intervals"),
#     State("game-state", "data"),
#     prevent_initial_call=True
# )
# def game_loop(defs, mids, atks, clicks, ticks, state):
#     ctx = callback_context.triggered_id

#     defs = (defs or [])[:2]
#     mids = (mids or [])[:3]
#     atks = (atks or [])[:1]

#     new_on_pitch = {
#         "C1_DEF": defs,
#         "C2_MID": mids,
#         "C3_ATK": atks
#     }

#     now = time.time()

#     # INIT TIME KEYS
#     for group in new_on_pitch.values():
#         for p in group:
#             state["time"].setdefault(p, 0)

#     if ctx == "lap-btn":
#         state["running"] = not state["running"]
#         state["last_tick"] = now

#         if not state["running"]:
#             print("⏹ FINAL TIMES")
#             for p, t in state["time"].items():
#                 print(p, format_time(t))

#     elif ctx == "interval" and state["running"]:
#         elapsed = int(now - state["last_tick"])
#         state["last_tick"] = now
#         state["seconds"] += elapsed

#         active = sum(new_on_pitch.values(), [])
#         for p in active:
#             state["time"][p] += elapsed

#     state["on_pitch"] = new_on_pitch

#     fig = build_pitch_figure(state["on_pitch"])

#     return (
#         state,
#         fig,
#         f"⏱️ Time: {format_time(state['seconds'])}",
#         not state["running"]
#     )

# # ----------------------------------
# # RUN
# # ----------------------------------

# if __name__ == "__main__":
#     app.run(debug=True)
