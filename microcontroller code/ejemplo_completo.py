from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM, MAX30105_PULSE_AMP_HIGH
import _thread
from machine import Pin, SoftI2C, SPI
from utime import ticks_diff, ticks_us, sleep_ms
import math
import time
import uarray as np

# ----------------- CONFIGURACIÓN AVANZADA -----------------
FILTER_WINDOW = 15       # Tamaño para filtro de mediana
MIN_BPM = 40            # Límites fisiológicos realistas
MAX_BPM = 200
SPO2_SAMPLES = 30       # Muestras para cálculo de SpO2
SIGNAL_HISTORY = 100    # Profundidad del histórico de señal
SAMPLE_RATE = 400       # Hz de muestreo del sensor

# ----------------- FUENTE 8x8 MEJORADA -----------------

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
    b"\x6C\xFE\xFE\xFE\x7C\x38\x10\x00",  # Corazón (índice 38)
    b"\x18\x24\x24\x24\x3C\x5A\x5A\x3C",  # Termómetro (índice 39)
    b"\x00\x18\x3C\x7E\x7E\x3C\x18\x00",  # Gota de agua (índice 40)
    b"\x00\x63\x63\x63\x63\x63\x63\x00",  # Porcentaje % (índice 41)
]


# ----------------- CLASE PANTALLA MEJORADA -----------------
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
            
    def draw_border(self, color=0xFFFF, thickness=3):
        for i in range(thickness):
            for x in range(i, self.width - i):
                self.draw_pixel(x, i, color)
                self.draw_pixel(x, self.height - 1 - i, color)
            for y in range(i, self.height - i):
                self.draw_pixel(i, y, color)
                self.draw_pixel(self.width - 1 - i, y, color)



        
    def fill_rect(self, x, y, w, h, color):
        """Dibuja un rectángulo relleno"""
        self.set_window(x, y, x + w - 1, y + h - 1)
        hi = color >> 8
        lo = color & 0xFF
        buf = bytearray([hi, lo] * w)
        for _ in range(h):
            self.write_data(buf)
    
    def draw_waveform(self, y_base, height, color):
        """Dibuja la forma de onda de la señal"""
        if len(self.signal_buffer) < 2:
            return
            
        for i in range(1, min(self.width-20, len(self.signal_buffer))):
            y1 = y_base - self.signal_buffer[i-1]//height
            y2 = y_base - self.signal_buffer[i]//height
            self.draw_line(20+i-1, y1, 20+i, y2, color)
    
    def draw_line(self, x0, y0, x1, y1, color):
        """Algoritmo de Bresenham para líneas"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.draw_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

# ----------------- INICIALIZACIÓN HARDWARE -----------------
spi = SPI(1, baudrate=30000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13))
tft = ST7789(spi, dc=27, res=18)
tft.fill_screen(0x0000)
tft.draw_border()

i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
sensor = MAX30102(i2c=i2c)

# ----------------- CONFIGURACIÓN SENSOR AVANZADA -----------------
if sensor.i2c_address in i2c.scan():
    sensor.setup_sensor(
        led_mode=2,                  # Modo SpO2 (rojo + IR)
        sample_rate=SAMPLE_RATE, 
        led_current_red=MAX30105_PULSE_AMP_HIGH,
        led_current_ir=MAX30105_PULSE_AMP_HIGH,
        adc_range=4096,
        sample_average=8
    )
    sensor.set_pulse_amplitude_red(0x1F)
    sensor.set_pulse_amplitude_ir(0x1F)

# ----------------- VARIABLES GLOBALES MEJORADAS -----------------
history_red = np.array([0] * SIGNAL_HISTORY)
history_ir = np.array([0] * SIGNAL_HISTORY)
beats_history = []
beat = False
beats = 0
spo2 = 0
temp = 0
signal_quality = 0

# ----------------- ALGORITMOS DE PROCESAMIENTO -----------------
def moving_median(values):
    """Filtro de mediana para reducir ruido"""
    return sorted(values)[len(values)//2]

def calculate_quality(signal):
    """Calcula calidad de señal (0-100%)"""
    if len(signal) < 10:
        return 0
    std_dev = np.std(signal[-10:])
    return min(100, max(0, int((std_dev - 5) * 10)))

def improved_spo2(red, ir):
    """Algoritmo mejorado de SpO2 con coeficientes calibrados"""
    red_ac = np.ptp(red[-SPO2_SAMPLES:])  # Peak-to-peak
    red_dc = np.mean(red[-SPO2_SAMPLES:])
    ir_ac = np.ptp(ir[-SPO2_SAMPLES:])
    ir_dc = np.mean(ir[-SPO2_SAMPLES:])
    
    if red_dc == 0 or ir_dc == 0:
        return 0
    
    r = (red_ac/red_dc)/(ir_ac/ir_dc)
    spo2 = 110 - 25 * r  # Fórmula calibrada
    
    return max(70, min(100, spo2))  # Limitar a rango fisiológico

def detect_peaks(signal):
    """Detección mejorada de picos cardíacos"""
    peaks = []
    avg = np.mean(signal)
    std = np.std(signal)
    threshold = avg + std * 1.5
    
    for i in range(1, len(signal)-1):
        if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)
    
    return peaks

# ----------------- VISUALIZACIÓN MEJORADA -----------------
def update_advanced_display():
    tft.fill_screen(0x0000)
    
    # Barra de calidad de señal
    tft.fill_rect(10, 10, int(2.2 * signal_quality), 5, 
                  0x07E0 if signal_quality > 70 else 
                  (0xFFE0 if signal_quality > 30 else 0xF800))
    
    # Sección BPM
    tft.draw_text(20, 30, "BPM", 0xFFFF, scale=1)
    tft.draw_text(80, 25, f"{int(beats)}", 0x07E0, scale=3)
    tft.draw_heart(160, 30, 0xF800, scale=2)
    
    # Sección SpO2
    spo2_color = 0xF800 if spo2 < 90 else (0xFD20 if spo2 < 95 else 0x07E0)
    tft.draw_text(20, 80, "SpO2", 0xFFFF, scale=1)
    tft.draw_text(80, 75, f"{int(spo2)}%", spo2_color, scale=3)
    
    # Sección Temperatura
    temp_color = 0x001F if temp < 37.5 else (0xFD20 if temp < 38.5 else 0xF800)
    tft.draw_text(20, 130, "TEMP", 0xFFFF, scale=1)
    tft.draw_text(80, 125, f"{temp:.1f}C", temp_color, scale=3)
    tft.draw_thermometer(160, 130, temp_color, scale=2)
    
    # Gráfico de señal en tiempo real
    tft.signal_buffer = history_red[-100:] if len(history_red) > 100 else history_red
    tft.draw_waveform(180, 50, 0xF800)

# ----------------- HILO DE ADQUISICIÓN MEJORADO -----------------
def advanced_acquisition():
    global history_red, history_ir, beats, spo2, temp, signal_quality, beat
    
    t_start = ticks_us()
    while True:
        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            ir = sensor.pop_ir_from_storage()
            
            # Actualizar buffers con filtrado
            history_red = np.roll(history_red, -1)
            history_ir = np.roll(history_ir, -1)
            history_red[-1] = red
            history_ir[-1] = ir
            
            # Calcular calidad de señal
            signal_quality = calculate_quality(history_red)
            
            if signal_quality > 30:  # Solo procesar si señal es buena
                # Detección de picos
                peaks = detect_peaks(history_red[-50:])
                
                if len(peaks) >= 2:
                    # Calcular BPM
                    t_us = ticks_diff(ticks_us(), t_start)
                    t_s = t_us / 1_000_000
                    ibi = t_s / len(peaks)
                    current_bpm = min(MAX_BPM, max(MIN_BPM, 60 / ibi))
                    
                    # Filtrado de BPM
                    beats_history.append(current_bpm)
                    if len(beats_history) > 5:
                        beats_history.pop(0)
                    beats = moving_median(beats_history)
                    
                    # Calcular SpO2 y temperatura
                    spo2 = improved_spo2(history_red, history_ir)
                    temp = sensor.read_temperature()
                    
                    t_start = ticks_us()
            
            # Actualizar pantalla
            update_advanced_display()

# ----------------- INICIO DEL SISTEMA -----------------
# Iniciar hilo de adquisición
_thread.start_new_thread(advanced_acquisition, ())

# Bucle principal
while True:
    # Aquí puedes añadir lógica adicional si es necesario
    sleep_ms(1000)