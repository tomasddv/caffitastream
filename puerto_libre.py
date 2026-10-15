"""Selecciona un puerto TCP local libre para el servidor Streamlit (8501-8599)."""
import socket
import sys

for port in range(8501, 8600):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", port))
        print(port)
        break
    except OSError:
        continue
else:
    print("ERROR: Ningun puerto libre entre 8501 y 8599", file=sys.stderr)
    sys.exit(1)
