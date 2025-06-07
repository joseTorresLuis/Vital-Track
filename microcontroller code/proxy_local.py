# proxy_local.py
# Este script debe correr en tu computadora (PC)

from flask import Flask, request, jsonify
import requests
import os  # Importar para leer variables de entorno si las usas

app = Flask(__name__)

# --- CONFIGURACIÓN CRÍTICA ---
# ¡IMPORTANTE! Reemplaza esto con la URL HTTPS ACTUAL de Ngrok.
# Esta URL cambia cada vez que inicias Ngrok.
# Ejemplo: NGROK_HTTPS_URL = "https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app"
NGROK_HTTPS_URL = "https://c7c0-200-63-43-153.ngrok-free.app"  # <--- ¡ACTUALIZA ESTO!

# Si tu API de Laravel tiene una ruta base diferente, ajústala aquí.
# Por ejemplo, si tu ruta completa en Laravel es "/api/v1/datos", pon "/api/v1"
# La ruta que el ESP32 enviará, y que será conc-atenada a NGROK_HTTPS_URL
API_BASE_PATH = "/api/datos"


@app.route(API_BASE_PATH, methods=['POST'])
def forward_data():
    if request.method == 'POST':
        try:
            # Captura los datos JSON que envía el ESP32
            data_from_esp32 = request.json
            print(f"Recibido del ESP32: {data_from_esp32}")

            # Construye la URL completa para reenviar a Ngrok
            full_ngrok_url = f"{NGROK_HTTPS_URL}{API_BASE_PATH}"
            print(f"Reenviando a Ngrok: {full_ngrok_url}")

            # Reenvía la petición a Ngrok usando HTTPS (requests de Python no tiene problemas aquí)
            response_from_ngrok = requests.post(
                full_ngrok_url, json=data_from_esp32)
            # Lanza un error para códigos de estado 4xx/5xx
            response_from_ngrok.raise_for_status()

            # Imprime la respuesta de Ngrok/Laravel
            print(
                f"Respuesta de Ngrok/Laravel (Status: {response_from_ngrok.status_code}): {response_from_ngrok.text}")

            # Devuelve la respuesta de Ngrok/Laravel al ESP32
            return jsonify(response_from_ngrok.json()), response_from_ngrok.status_code

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Falló el reenvío a Ngrok: {e}")
            # Devuelve un error 500 al ESP32 si falla el reenvío
            return jsonify({"error": f"Error al reenviar la petición a la API externa: {e}"}), 500
        except Exception as e:
            print(f"ERROR: Error inesperado en el proxy: {e}")
            return jsonify({"error": f"Error interno del proxy: {e}"}), 500

    # Manejar otros métodos si se accede directamente
    return jsonify({"message": "Solo se permiten peticiones POST a esta ruta."}), 405


if __name__ == '__main__':
    # --- CONFIGURACIÓN DEL SERVIDOR PROXY ---
    # La IP de tu PC en la red local. Puedes encontrarla con 'ipconfig' (Windows) o 'ifconfig' (Linux/macOS).
    # Busca la IP de tu adaptador Wi-Fi o Ethernet (ej. 192.168.32.103 como en tu log)
    # Si no estás seguro, '0.0.0.0' permite que escuche en todas las interfaces de red,
    # pero asegúrate de que el firewall de tu PC permita el puerto.
    LOCAL_IP_ADDRESS = '0.0.0.0'  # O tu IP específica, ej. '192.168.32.103'

    # Un puerto que NO esté en uso por Laravel (8000) o Ngrok (4040).
    LOCAL_PORT = 5000

    print(
        f"Iniciando proxy local en http://{LOCAL_IP_ADDRESS}:{LOCAL_PORT}{API_BASE_PATH}")
    print(f"Reenviando peticiones a {NGROK_HTTPS_URL}{API_BASE_PATH}")
    print("Asegúrate de que Ngrok esté corriendo y dando la URL HTTPS correcta.")
    print("Asegúrate de que el firewall de tu PC permita las conexiones entrantes en el puerto", LOCAL_PORT)

    # debug=True es útil para desarrollo
    app.run(host=LOCAL_IP_ADDRESS, port=LOCAL_PORT, debug=True)
