from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import _thread
from machine import sleep, SoftI2C, Pin, RTC
from utime import ticks_diff, ticks_us, mktime, localtime
import urequests
import ujson
import ntptime
import time
import sys # Para sys.print_exception

# --- Configuración NTP ---
NTP_GMT_OFFSET_SECONDS = -21600
NTP_SERVER = "time.google.com"

# --- Configuración del LED de estado ---
led = Pin(2, Pin.OUT)

# --- Parámetros del Sensor ---
MAX_HISTORY = 32
history = []
beats_history = []
spo2_history = []
beat = False
beats = 0
t_start = ticks_us()

# --- Inicialización del sensor ---
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
sensor = MAX30102(i2c=i2c)

# --- URL de la API (¡AHORA APUNTA A TU PROXY LOCAL EN TU PC!) ---
# ¡MUY IMPORTANTE! Reemplaza <IP_DE_TU_PC> con la IP local que anotaste (ej. 192.168.32.103)
# Y <PUERTO_DEL_PROXY> con el puerto que usaste para el proxy (ej. 5000).
API_URL = "http://192.168.182.125:5000/api/datos" # <--- ¡ACTUALIZA ESTO!
# Ejemplo: API_URL = "http://172.20.10.2:5000/api/datos"

# --- Funciones de Sincronización de Tiempo ---
def sync_time():
    print("Sincronizando tiempo con NTP...")
    try:
        ntptime.host = NTP_SERVER
        ntptime.settime()
        rtc = RTC()
        current_time_tuple = rtc.datetime()
        current_timestamp = mktime(current_time_tuple)
        adjusted_timestamp = current_timestamp + NTP_GMT_OFFSET_SECONDS
        new_time_tuple = localtime(adjusted_timestamp)
        rtc.datetime((new_time_tuple[0], new_time_tuple[1], new_time_tuple[2], new_time_tuple[6],
                      new_time_tuple[3], new_time_tuple[4], new_time_tuple[5], 0))
        print("Tiempo sincronizado y ajustado a GMT-6:", rtc.datetime())
        return True
    except Exception as e:
        print("¡Error al sincronizar tiempo con NTP!:", e)
        return False

# --- Inicialización principal (Setup) ---
def setup_app():
    global sensor
    import network
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("¡ERROR: Wi-Fi no conectado! Asegúrate de que boot.py funciona.")
        return False
    
    # La sincronización de tiempo sigue siendo útil para la hora interna del ESP32,
    # aunque la petición al proxy sea HTTP.
    if not sync_time():
        print("No se pudo sincronizar el tiempo.")

    if sensor.i2c_address not in i2c.scan():
        print("Error: Sensor no encontrado en el bus I2C")
        return False
    elif not sensor.check_part_id():
        print("Error: Dispositivo I2C no es un MAX30102 o MAX30105")
        return False
    else:
        print("Sensor MAX30102 conectado correctamente")

    sensor.setup_sensor()
    sensor.set_sample_rate(400)
    sensor.set_fifo_average(8)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
    sensor.set_led_mode(2)
    sleep(1)
    return True

# --- Funciones de Cálculo y Envío ---
def calculate_spo2(ir, red):
    try:
        if ir == 0 or red == 0:
            return 0.0
        ratio = red / ir
        spo2 = 104 - 17 * ratio
        return max(0, min(round(spo2, 2), 100))
    except:
        return 0.0

def send_data_to_api(bpm, spo2, temp):
    try:
        headers = {"Content-Type": "application/json"}
        payload = ujson.dumps({
            "BPM": bpm,
            "SPO2": spo2,
            "TEMP": temp
        })
        print(f"Enviando a PROXY LOCAL en: {API_URL}") # Para depuración
        response = urequests.post(API_URL, data=payload, headers=headers)
        
        # Opcional: Imprime la respuesta del proxy
        print(f"Respuesta del proxy (Status: {response.status_code}): {response.text}")
        
        response.close()
        print(" Datos enviados al proxy local")
    except Exception as e:
        print(" Error al enviar datos al proxy local:", e)
        sys.print_exception(e)

# --- Mostrar en consola ---
def print_sensor_data(bpm, temp, spo2):
    print("\n--- Datos del Sensor ---")
    print(f"BPM: {bpm:.2f}")
    print(f"Temperatura: {temp:.2f}°C")
    print(f"SpO₂: {spo2:.2f}%")
    print("-----------------------")

# --- Lógica principal de lectura y procesamiento ---
def get_max30102_values():
    global history, beats_history, spo2_history, beat, beats, t_start

    while True:
        sensor.check()

        if sensor.available():
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()

            value = red_reading
            history.append(value)
            history = history[-MAX_HISTORY:]
            
            minima, maxima = min(history), max(history)
            threshold_on = (minima + maxima * 3) // 4
            threshold_off = (minima + maxima) // 2

            if value > 1000:
                if not beat and value > threshold_on:
                    
                        beat = True
                        led.on()
                        
                        t_us = ticks_diff(ticks_us(), t_start)
                        t_s = t_us / 1000000
                        f = (1 / t_s)
                        bpm = f * 90

                        if bpm < 550:
                            t_start = ticks_us()
                            beats_history.append(bpm)
                            beats_history = beats_history[-MAX_HISTORY:]
                            beats = round(sum(beats_history) / len(beats_history), 2)

                            temp = round(sensor.read_temperature(), 2)
                            spo2 = calculate_spo2(ir_reading, red_reading)
                            spo2_history.append(spo2)
                            spo2_history = spo2_history[-MAX_HISTORY:]
                            avg_spo2 = round(sum(spo2_history) / len(spo2_history), 2)

                            print_sensor_data(beats, temp, avg_spo2)
                            send_data_to_api(beats, avg_spo2, temp)

                if beat and value < threshold_off:
                    beat = False
                    led.off()
            else:
                led.off()
                print('Dedo no detectado o lectura muy baja')
                # send_data_jkpto_api(0.00, 0.00, 0.00) # Opcional: enviar ceros si no hay dedo

# --- Inicio del Programa ---
if __name__ == "__main__":
    if setup_app():
        _thread.start_new_thread(get_max30102_values, ())
        print("Iniciando bucle principal...")
        while True:
            time.sleep(1)
    else:
        print("Fallo en la inicialización de la aplicación. El programa se detiene.")
