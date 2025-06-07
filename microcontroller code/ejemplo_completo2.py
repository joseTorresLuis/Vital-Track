from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import _thread
from machine import Pin, SoftI2C, SPI
from utime import ticks_diff, ticks_us, sleep_ms
import math
import time

# ----------------- CONFIGURACIÓN DE FUENTE 8x8 -----------------
font8x8 = [
    b"\x00\x00\x00\x00\x00\x00\x00\x00",  # espacio
    b"\x18\x3C\x66\x66\x7E\x66\x66\x00",  # A
    b"\x7C\x66\x66\x7C\x66\x66\x7C\x00",  # B
    b"\x3C\x66\x60\x60\x60\x66\x3C\x00",  # C
    b"\x78\x6C\x66\x66\x66\x6C\x78\x00",  # D
    b"\x7E\x60\x60\x7C\x60\x60\x7E\x00",  # E
    b"\x7E\x60\x60\x7C\x60\x60\x60\x00",  # F
    b"\x3C\x66\x60\x6E\x66\x66\x3E\x00",  # G
    b"\x66\x66\x66\x7E\x66\x66\x66\x00",  # H
    b"\x3C\x18\x18\x18\x18\x18\x3C\x00",  # I
    b"\x1E\x0C\x0C\x0C\x0C\x6C\x38\x00",  # J
    b"\x66\x6C\x78\x70\x78\x6C\x66\x00",  # K
    b"\x60\x60\x60\x60\x60\x60\x7E\x00",  # L
    b"\x63\x77\x7F\x6B\x63\x63\x63\x00",  # M
    b"\x66\x76\x7E\x7E\x6E\x66\x66\x00",  # N
    b"\x3C\x66\x66\x66\x66\x66\x3C\x00",  # O
    b"\x7C\x66\x66\x7C\x60\x60\x60\x00",  # P
    b"\x3C\x66\x66\x66\x6E\x6C\x36\x00",  # Q
    b"\x7C\x66\x66\x7C\x78\x6C\x66\x00",  # R
    b"\x3E\x60\x60\x3C\x06\x06\x7C\x00",  # S
    b"\x7E\x18\x18\x18\x18\x18\x18\x00",  # T
    b"\x66\x66\x66\x66\x66\x66\x3C\x00",  # U
    b"\x66\x66\x66\x66\x66\x3C\x18\x00",  # V
    b"\x63\x63\x63\x6B\x7F\x77\x63\x00",  # W
    b"\x66\x66\x3C\x18\x3C\x66\x66\x00",  # X
    b"\x66\x66\x66\x3C\x18\x18\x18\x00",  # Y
    b"\x7E\x06\x0C\x18\x30\x60\x7E\x00",  # Z
    b"\x3C\x66\x66\x66\x66\x66\x3C\x00",  # 0
    b"\x18\x38\x18\x18\x18\x18\x3C\x00",  # 1
    b"\x3C\x66\x06\x0C\x18\x30\x7E\x00",  # 2
    b"\x3C\x66\x06\x1C\x06\x66\x3C\x00",  # 3
    b"\x0C\x1C\x2C\x4C\x7E\x0C\x0C\x00",  # 4
    b"\x7E\x60\x7C\x06\x06\x66\x3C\x00",  # 5
    b"\x3C\x66\x60\x7C\x66\x66\x3C\x00",  # 6
    b"\x7E\x06\x0C\x18\x30\x30\x30\x00",  # 7
    b"\x3C\x66\x66\x3C\x66\x66\x3C\x00",  # 8
    b"\x3C\x66\x66\x3E\x06\x66\x3C\x00",  # 9
    b"\x00\x00\x18\x00\x00\x18\x00\x00",  # :
    b"\x6C\xFE\xFE\xFE\x7C\x38\x10\x00",  # Corazón
    b"\x18\x24\x24\x24\x3C\x5A\x5A\x3C",  # Termómetro
    b"\x00\x18\x3C\x7E\x7E\x3C\x18\x00",  # Gota de agua
    b"\x00\x63\x63\x63\x63\x63\x63\x00"   # %
]

# ----------------- CLASE PANTALLA ST7789 -----------------
class ST7789:
    def __init__(self, spi, dc, res, cs=None):
        self.spi = spi
        self.dc = Pin(dc, Pin.OUT)
        self.res = Pin(res, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT) if cs else None
        self.width = 240
        self.height = 240
        self.init_display()

    def write_cmd(self, cmd):
        if self.cs: self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        if self.cs: self.cs(1)

    def write_data(self, data):
        if self.cs: self.cs(0)
        self.dc(1)
        self.spi.write(bytearray(data))
        if self.cs: self.cs(1)

    def init_display(self):
        self.res(0)
        time.sleep_ms(50)
        self.res(1)
        time.sleep_ms(50)
        self.write_cmd(0x36)
        self.write_data([0x00])
        self.write_cmd(0x3A)
        self.write_data([0x05])
        self.write_cmd(0x21)
        self.write_cmd(0x11)
        time.sleep_ms(120)
        self.write_cmd(0x29)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.write_cmd(0x2B)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.write_cmd(0x2C)

    def fill_screen(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        hi = color >> 8
        lo = color & 0xFF
        buf = bytearray([hi, lo] * self.width)
        for _ in range(self.height):
            self.write_data(buf)

    def draw_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            hi = color >> 8
            lo = color & 0xFF
            self.write_data([hi, lo])

    def draw_char(self, x, y, char, color, scale=1):
        index = 0
        if char == ' ':
            index = 0
        elif char == ':':
            index = 36
        elif char.isdigit():
            index = 26 + int(char)
        elif char.isalpha():
            index = ord(char.upper()) - ord('A') + 1
        
        if 0 <= index < len(font8x8):
            char_data = font8x8[index]
            for row in range(8):
                for col in range(8):
                    if char_data[row] & (0x80 >> col):
                        for dx in range(scale):
                            for dy in range(scale):
                                self.draw_pixel(x + col * scale + dx, y + row * scale + dy, color)

    def draw_text(self, x, y, text, color, scale=1):
        for i, char in enumerate(text):
            self.draw_char(x + i * 8 * scale, y, char, color, scale)

    def draw_heart(self, x, y, color, scale=2):
        heart = [
            [0, 1, 1, 0, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self._draw_bitmap(x, y, heart, color, scale)

    def draw_thermometer(self, x, y, color, scale=2):
        thermo = [
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0]
        ]
        self._draw_bitmap(x, y, thermo, color, scale)

    def _draw_bitmap(self, x, y, bitmap, color, scale=1):
        for row in range(8):
            for col in range(8):
                if bitmap[row][col]:
                    for dx in range(scale):
                        for dy in range(scale):
                            self.draw_pixel(x + col*scale + dx, y + row*scale + dy, color)

    def draw_border(self, color=0xFFFF, thickness=3):
        for i in range(thickness):
            for x in range(i, self.width - i):
                self.draw_pixel(x, i, color)
                self.draw_pixel(x, self.height - 1 - i, color)
            for y in range(i, self.height - i):
                self.draw_pixel(i, y, color)
                self.draw_pixel(self.width - 1 - i, y, color)

    def fill_rect(self, x, y, w, h, color):
        for i in range(x, x + w):
            for j in range(y, y + h):
                self.draw_pixel(i, j, color)

# ----------------- VARIABLES GLOBALES -----------------
MAX_HISTORY = 32
history = []
beats_history = []
beat = False
beats = 0
spo2 = 0
temp = 0
sensor = None
last_bpm = -1
last_spo2 = -1
last_temp = -1

# ----------------- INICIALIZACIÓN PANTALLA -----------------
spi = SPI(1, baudrate=40000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13))
tft = ST7789(spi, dc=27, res=18)
tft.fill_screen(0x0000)

# Dibujar elementos estáticos
def draw_static_elements():
    tft.draw_border()
    
    text_x = 20
    value_x = 100
    icon_x = 180
    row_height = 50
    start_y = 30
    
    # Textos fijos
    tft.draw_text(text_x, start_y, "BPM:", 0xFFFF, scale=2)
    tft.draw_heart(icon_x, start_y, 0xF800, scale=2)
    
    tft.draw_text(text_x, start_y + row_height, "SPO2:", 0xFFFF, scale=2)
    tft.draw_text(value_x + 40, start_y + row_height, "%", 0xF800, scale=2)
    
    tft.draw_text(text_x, start_y + 2*row_height, "TEMP:", 0xFFFF, scale=2)
    tft.draw_text(value_x + 60, start_y + 2*row_height, "C", 0x001F, scale=2)
    tft.draw_thermometer(icon_x, start_y + 2*row_height, 0x001F, scale=2)

draw_static_elements()

# ----------------- CONFIGURACIÓN SENSOR -----------------
def init_sensor():
    global sensor
    
    led = Pin(2, Pin.OUT)
    i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
    sensor = MAX30102(i2c=i2c)

    if sensor.i2c_address not in i2c.scan():
        print("Sensor no encontrado.")
        tft.draw_text(20, 130, "NO SENSOR", 0xF800, scale=2)
        return False
    else:
        print("Sensor conectado")
        sensor.setup_sensor()
        sensor.set_sample_rate(400)
        sensor.set_fifo_average(8)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
        sensor.set_led_mode(2)
        time.sleep(1)
        return True

# Actualizar solo valores numéricos
def update_values(bpm, spo2, temp):
    global last_bpm, last_spo2, last_temp
    print(f"Datos crudos - BPM: {bpm} (tipo: {type(bpm)}), SpO2: {spo2}, Temp: {temp}")  # Depuración
    
    value_x = 100
    row_height = 50
    start_y = 30
    
    # Asegurar que los valores sean numéricos
    try:
        bpm = int(bpm)
        spo2 = int(spo2)
        temp = float(temp)
    except (ValueError, TypeError) as e:
        print(f"Error en conversión: {e}")
        return
    
    if bpm != last_bpm:
        tft.fill_rect(value_x, start_y, 60, 20, 0x0000)
        tft.draw_text(value_x, start_y, str(int(bpm)), 0x07E0, scale=2)
        last_bpm = bpm
    
    if spo2 != last_spo2:
        tft.fill_rect(value_x, start_y + row_height, 30, 20, 0x0000)
        tft.draw_text(value_x, start_y + row_height, str(int(spo2)), 0xF800, scale=2)
        last_spo2 = spo2
    
    if temp != last_temp:
        tft.fill_rect(value_x, start_y + 2*row_height, 50, 20, 0x0000)
        tft.draw_text(value_x, start_y + 2*row_height, str(temp), 0x001F, scale=2)
        last_temp = temp

# ----------------- HILO DE LECTURA -----------------
def get_max30102_values():
    global history, beats_history, beat, beats, spo2, temp, sensor
    
    if sensor is None:
        print("Error: Sensor no inicializado")
        return
    
    t_start = ticks_us()
    
    while True:
        try:
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
                        Pin(2, Pin.OUT).on()

                        t_us = ticks_diff(ticks_us(), t_start)
                        t_s = t_us / 1_000_000
                        f = 1 / t_s
                        bpm = f * 60

                        if bpm < 500:
                            t_start = ticks_us()
                            beats_history.append(bpm)
                            beats_history = beats_history[-MAX_HISTORY:]
                            beats = round(sum(beats_history) / len(beats_history), 2)
                            temp = round(sensor.read_temperature(), 2)
                            spo2 = 95 + (maxima - minima) % 5  # Simulación
                            
                            update_values(beats, spo2, temp)

                    if beat and value < threshold_off:
                        beat = False
                        Pin(2, Pin.OUT).off()
                else:
                    Pin(2, Pin.OUT).off()
                    update_values(0, 0, 0)
                    
        except Exception as e:
            print("Error en lectura:", e)
            time.sleep(1)

# ----------------- PROGRAMA PRINCIPAL -----------------
if init_sensor():
    _thread.start_new_thread(get_max30102_values, ())

while True:
    sleep_ms(1000)