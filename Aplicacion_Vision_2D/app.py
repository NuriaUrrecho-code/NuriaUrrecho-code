from __future__ import annotations

import curses
import json
import sys
import textwrap

from app_state import (
    CALIBRATION_INFO_PATH,
    CONFIG_PATH,
    LAST_POSITION_PATH,
    POSITION_LOG_PATH,
    load_config,
    load_json,
    save_config,
)
from calibration.camera_calibration import calibrate_camera
from calibration.capture_calibration_images import capture_calibration_images
from calibration.homography import compute_homography
from calibration.select_points import select_points
from main_position import (
    capture_background_reference,
    preview_background_detection,
    preview_camera,
    run_tracking,
    run_tracking_background,
)


MENU_ITEMS = [
    ("Ver camara", preview_camera),
    ("Buscar y elegir camara", None),
    ("Capturar fondo de referencia", capture_background_reference),
    ("Probar deteccion por fondo", preview_background_detection),
    ("Capturar imagenes de calibracion", capture_calibration_images),
    ("Calibrar camara", calibrate_camera),
    ("Seleccionar 4 puntos del plano", select_points),
    ("Calcular homografia", compute_homography),
    ("Ejecutar deteccion y posicionamiento", run_tracking),
    ("Ejecutar deteccion por fondo + tracking", run_tracking_background),
    ("Salir", None),
]


MANDARIN_ART = [
    "⠀⠀⠀⠀⣀⣀⣀⣀⣀⠀⠀⠀⢀⣠⡴⢶⡾⣆⠀⠀⠀⠀⠀⠀",
    "⠀⠐⣾⠛⠋⠉⠛⠋⠙⢻⣦⣠⡟⠁⠀⢸⢠⡿⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠹⣦⡀⠀⠀⠀⠀⠀⢹⣿⣓⣠⣴⣵⠟⠁⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠘⠻⣦⣤⣤⣤⣤⣼⠾⠻⠿⠿⣷⣤⡀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⣠⡾⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠪⣽⢷⣄⠀⠀⠀⠀",
    "⠀⢠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢣⡙⢷⡄⠀⠀",
    "⢠⡟⠁⢰⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⡈⢿⡄⠀",
    "⣾⠃⠀⠀⠀⣀⡢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠘⣿⠀",
    "⣿⠀⠸⠜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⢿⡶",
    "⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⣿⠀",
    "⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⢠⡿⠀",
    "⠈⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⢁⣾⠃⠀",
    "⠀⠈⢻⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⣰⡟⠁⠀⠀",
    "⠀⠀⠀⠙⠷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣐⣥⠟⠋⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠈⠉⠛⠶⠶⠦⠤⠶⣶⠾⠛⠋⠁⠀⠀⠀⠀⠀⠀",
]


LEAF_POSITIONS = {
    0: set(range(22, 34)),
    1: set(range(24, 33)),
    2: set(range(25, 32)),
    3: set(range(27, 31)),
}


def wrap_prefixed_text(prefix: str, content: str, width: int) -> list[str]:
    """Wrap a label/value line preserving the initial prefix on the first row."""
    if width <= len(prefix) + 1:
        return [f"{prefix}{content[:max(0, width - len(prefix))]}"]

    wrapped = textwrap.wrap(
        content,
        width=max(1, width - len(prefix)),
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not wrapped:
        return [prefix.rstrip()]

    lines = [f"{prefix}{wrapped[0]}"]
    indent = " " * len(prefix)
    lines.extend(f"{indent}{line}" for line in wrapped[1:])
    return lines


def show_last_saved_data() -> None:
    """Print the last stored position and the current calibration summary."""
    last_position = load_json(LAST_POSITION_PATH, None)
    calibration_info = load_json(CALIBRATION_INFO_PATH, {})

    print("\n--- Ultimo dato de posicion ---")
    if last_position is None:
        print("No hay posiciones guardadas todavia.")
    else:
        print(json.dumps(last_position, indent=2, ensure_ascii=False))

    print("\n--- Estado de calibracion ---")
    if not calibration_info:
        print("No hay informacion de calibracion guardada.")
    else:
        print(json.dumps(calibration_info, indent=2, ensure_ascii=False))

    print(f"\nHistorial de posiciones: {POSITION_LOG_PATH}")


def show_config() -> None:
    """Print the persisted application configuration."""
    config = load_config()
    print(f"\nConfiguracion actual ({CONFIG_PATH}):")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def update_camera_index() -> None:
    config = load_config()
    raw_value = input("Nuevo indice de camara: ").strip()
    try:
        config["camera_index"] = int(raw_value)
    except ValueError:
        print("Indice no valido.")
        return

    save_config(config)
    print(f"Indice de camara guardado: {config['camera_index']}")


def choose_camera() -> None:
    """Allow the user to persist the camera index used by the app."""
    config = load_config()
    raw_value = input("Indice de camara a usar: ").strip()
    try:
        selected = int(raw_value)
    except ValueError:
        print("Indice no valido.")
        return

    config["camera_index"] = selected
    save_config(config)
    print(f"Camara guardada: indice {selected}")

def draw_menu(stdscr, selected_idx: int) -> None:
    """Render the curses main menu and the current runtime configuration."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    config = load_config()
    title = config.get("project_title", "Posicionamiento planar de mandarinas")
    authors = config.get("authors", ["Por definir"])
    author_text = ", ".join(authors) if authors else "Por definir"
    subtitle = "Usa flechas y Enter para seleccionar"
    state_info = f"Persistencia: {CONFIG_PATH.parent.name}/"
    camera_info = f"Camara activa: {config.get('camera_index', 0)}"
    correction_info = "Correccion altura: pose estimada"
    detection_info = "Deteccion: automatica"
    tracking_info = "Seguimiento: primer frame"
    tracker_info = "Tracker OpenCV: KCF"

    panel_width = min(92, max(72, width - 4))
    panel_height = min(height - 2, 30)
    panel_x = max(2, (width - panel_width) // 2)
    panel_y = max(1, (height - panel_height) // 2)

    for x in range(panel_x, panel_x + panel_width):
        stdscr.attron(curses.color_pair(5))
        stdscr.addch(panel_y, x, " ")
        stdscr.addch(panel_y + panel_height - 1, x, " ")
        stdscr.attroff(curses.color_pair(5))
    for y in range(panel_y, panel_y + panel_height):
        stdscr.attron(curses.color_pair(5))
        stdscr.addch(y, panel_x, " ")
        stdscr.addch(y, panel_x + panel_width - 1, " ")
        stdscr.attroff(curses.color_pair(5))

    art_x = panel_x + 3
    art_y = panel_y + 2
    max_art_width = max(0, min(max(len(line) for line in MANDARIN_ART), panel_width - 8))
    for idx, line in enumerate(MANDARIN_ART):
        row = art_y + idx
        if row >= panel_y + panel_height - 3:
            break

        for offset, char in enumerate(line[:max_art_width]):
            color = 7 if offset in LEAF_POSITIONS.get(idx, set()) else 6
            stdscr.attron(curses.color_pair(color) | curses.A_BOLD)
            stdscr.addstr(row, art_x + offset, char)
            stdscr.attroff(curses.color_pair(color) | curses.A_BOLD)

    art_block_width = min(max(len(line) for line in MANDARIN_ART), max_art_width)
    text_x = art_x + art_block_width + 3
    text_width = panel_x + panel_width - 3 - text_x

    if text_width >= 26:
        title_y = art_y + 2
        meta_y = art_y + 4
    else:
        text_x = art_x + 2
        text_width = panel_width - 8
        title_y = art_y + len(MANDARIN_ART) + 1
        meta_y = title_y + 2

    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addnstr(title_y, text_x, title, max(0, text_width))
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    meta_lines = [subtitle]
    meta_lines.extend(wrap_prefixed_text("Autores: ", author_text, max(10, text_width)))
    meta_lines.append(camera_info)
    meta_lines.append(correction_info)
    meta_lines.append(detection_info)
    meta_lines.append(tracking_info)
    meta_lines.append(tracker_info)
    meta_lines.append(state_info)

    stdscr.attron(curses.color_pair(3))
    for offset, line in enumerate(meta_lines):
        stdscr.addnstr(meta_y + offset, text_x, line, max(0, text_width))
    stdscr.attroff(curses.color_pair(3))

    art_bottom = art_y + len(MANDARIN_ART)
    text_bottom = meta_y + len(meta_lines)
    divider_y = max(art_bottom, text_bottom) + 1

    divider_x = panel_x + 4
    divider_width = panel_width - 8
    if divider_width > 12:
        divider_text = "***"
        middle_width = max(0, divider_width - (len(divider_text) * 2) - 2)
        left_fill = "*" * (middle_width // 2)
        right_fill = "*" * (middle_width - len(left_fill))
        divider_line = f"{divider_text}{left_fill}·{right_fill}{divider_text}"
        divider_line = divider_line[:divider_width].ljust(divider_width, "*")
        stdscr.attron(curses.color_pair(8) | curses.A_BOLD)
        stdscr.addstr(divider_y, divider_x, divider_line)
        stdscr.attroff(curses.color_pair(8) | curses.A_BOLD)

    start_row = divider_y + 2
    visible_rows = max(1, panel_y + panel_height - 3 - start_row)
    scroll_offset = 0
    if selected_idx >= visible_rows:
        scroll_offset = selected_idx - visible_rows + 1

    visible_items = MENU_ITEMS[scroll_offset : scroll_offset + visible_rows]
    for local_idx, (label, _) in enumerate(visible_items):
        idx = scroll_offset + local_idx
        row = start_row + local_idx

        marker_x = panel_x + 4
        text_x = panel_x + 7
        item_width = panel_width - 11
        padded = label.ljust(item_width)

        x = panel_x + 4
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr(row, marker_x, ">")
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)

            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(row, text_x, padded[:item_width])
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(row, marker_x, " ")
            stdscr.addstr(row, text_x, padded[:item_width])
            stdscr.attroff(curses.color_pair(4))

    if scroll_offset > 0:
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(start_row - 1, panel_x + panel_width - 10, "↑ mas")
        stdscr.attroff(curses.color_pair(3))
    if scroll_offset + visible_rows < len(MENU_ITEMS):
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(panel_y + panel_height - 3, panel_x + panel_width - 10, "↓ mas")
        stdscr.attroff(curses.color_pair(3))

    footer = "[Enter] abrir   [q/Esc] salir"
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(panel_y + panel_height - 2, panel_x + 4, footer[: panel_width - 8])
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()


def curses_menu(stdscr) -> str:
    """Interactive curses menu loop."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    if curses.can_change_color():
        try:
            curses.init_color(20, 1000, 550, 0)
            orange_color = 20
        except curses.error:
            orange_color = curses.COLOR_YELLOW
    else:
        orange_color = curses.COLOR_YELLOW

    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    curses.init_pair(5, curses.COLOR_BLUE, -1)
    curses.init_pair(6, orange_color, -1)
    curses.init_pair(7, curses.COLOR_GREEN, -1)
    curses.init_pair(8, curses.COLOR_WHITE, -1)

    selected_idx = 0
    while True:
        draw_menu(stdscr, selected_idx)
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            selected_idx = (selected_idx - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected_idx = (selected_idx + 1) % len(MENU_ITEMS)
        elif key in (10, 13, curses.KEY_ENTER):
            return MENU_ITEMS[selected_idx][0]
        elif key in (27, ord("q")):
            return "Salir"


def fallback_numeric_menu() -> str:
    """Text fallback menu for environments without a compatible TTY."""
    print("\n=== Menu principal ===")
    for index, (label, _) in enumerate(MENU_ITEMS, start=1):
        print(f"{index}. {label}")

    raw = input("Selecciona una opcion: ").strip()
    try:
        selected = int(raw) - 1
    except ValueError:
        return ""

    if 0 <= selected < len(MENU_ITEMS):
        return MENU_ITEMS[selected][0]
    return ""


def main() -> None:
    """Run the top-level application menu and dispatch user actions."""
    actions = {
        "Ver camara": preview_camera,
        "Buscar y elegir camara": choose_camera,
        "Capturar fondo de referencia": capture_background_reference,
        "Probar deteccion por fondo": preview_background_detection,
        "Capturar imagenes de calibracion": capture_calibration_images,
        "Calibrar camara": calibrate_camera,
        "Seleccionar 4 puntos del plano": select_points,
        "Calcular homografia": compute_homography,
        "Ejecutar deteccion y posicionamiento": run_tracking,
        "Ejecutar deteccion por fondo + tracking": run_tracking_background,
    }

    while True:
        if sys.stdin.isatty() and sys.stdout.isatty():
            option = curses.wrapper(curses_menu)
        else:
            option = fallback_numeric_menu()

        if option == "Salir":
            print("Saliendo.")
            return

        action = actions.get(option)
        if action is None:
            print("Opcion no valida.")
            continue

        try:
            action()
        except FileNotFoundError as exc:
            print(exc)
        except Exception as exc:
            print(f"Error ejecutando la opcion: {exc}")


if __name__ == "__main__":
    main()
