"""Iniciador confiable para Windows (evita los problemas de comillas de CMD)."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent


def encontrar_puerto(inicio: int = 8501, fin: int = 8599) -> int:
    """Identifica un puerto TCP local libre; Streamlit lo reservará al iniciarse."""
    for puerto in range(inicio, fin + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
                conexion.bind(("127.0.0.1", puerto))
            return puerto
        except OSError:
            continue
    raise RuntimeError(f"No hay puertos libres entre {inicio} y {fin}.")


def main() -> int:
    os.chdir(CARPETA)
    if not (CARPETA / "app.py").is_file():
        print("ERROR: No encuentro app.py junto a iniciar_dashboard.py.", flush=True)
        return 1
    try:
        puerto = encontrar_puerto()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    url = f"http://127.0.0.1:{puerto}"
    print("\n----------------------------------------------", flush=True)
    print("  TABLERO DDV - Streamlit", flush=True)
    print(f"  Abrir en el navegador: {url}", flush=True)
    print("  NO CIERRES ESTA VENTANA mientras lo uses.", flush=True)
    print("  Para detenerlo, presiona Ctrl+C.", flush=True)
    print("----------------------------------------------\n", flush=True)
    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(CARPETA / "app.py"),
        "--server.address=127.0.0.1",
        f"--server.port={puerto}",
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]
    try:
        return subprocess.call(comando, cwd=str(CARPETA))
    except KeyboardInterrupt:
        return 0
    except OSError as exc:
        print(f"ERROR: No pude iniciar Streamlit: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
