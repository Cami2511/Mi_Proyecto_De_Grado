
#import time
#import math
#import board
#import busio
#import adafruit_ads1x15.ads1115 as ADS
#from adafruit_ads1x15.analog_in import AnalogIn

# --- CONFIGURACION DEL HARDWARE ---
# Resistencia de carga (RL) instalada en el modulo MQ-135 (normalmente 10k Ohios)
#RL_VALUE = 10.0  # kOhms

#  Valor de Ro en aire limpio (Debe calibrarse previamente; 3.6 es un valor estimado base)
#     RO_CLEAN_AIR = 3.6  

#  #Parametros de las curvas de aproximacion para cada gas (a, b) extraidos del datasheet:
#  PPM = a * (Rs/Ro)^b
# GAS_CURVES = {
#     "CO2":     {"a": 110.47, "b": -2.862},
#     "NH3":     {"a": 102.2,  "b": -2.473},
#     "Alcohol": {"a": 77.255, "b": -3.18},
#     "Humo":    {"a": 44.947, "b": -3.445}
# }

# def inicializar_ads():
#     """Inicializa la comunicacion I2C con el ADS1115."""
#     i2c = busio.I2C(board.SCL, board.SDA)
#     ads = ADS.ADS1115(i2c)
#     # Ganancia 1: rango de lectura de +/- 4.096V
#     ads.gain = 1
#     return AnalogIn(ads, ADS.P0)

# def obtener_resistencia_rs(voltaje_v):
#     """Calcula la resistencia actual del sensor (Rs) basandose en el voltaje medido."""
#     if voltaje_v <= 0:
#         return float('inf')
#     # Formula divisora de voltaje para MQ-135 (Vcc = 5.0V)
#     vcc = 5.0
#     return ((vcc - voltaje_v) / voltaje_v) * RL_VALUE

# def calcular_ppm(ratio_rs_ro, gas):
#     """Calcula las PPM estimadas para un gas especifico."""
#     if gas not in GAS_CURVES or ratio_rs_ro <= 0:
#         return 0.0
#     a = GAS_CURVES[gas]["a"]
#     b = GAS_CURVES[gas]["b"]
#     return a * math.pow(ratio_rs_ro, b)

# def calibrar_ro(canal_adc, muestras=50):
#     """
#     Funcion para calibrar Ro en un entorno de aire limpio conocido.
#     El sensor debe llevar encendido al menos 24 horas previo a la calibracion final.
#     """
#     print("Calibrando Ro en aire limpio... Por favor espere.")
#     suma_rs = 0.0
#     for _ in range(muestras):
#         voltaje = canal_adc.voltage
#         suma_rs += obtener_resistencia_rs(voltaje)
#         time.sleep(0.1)
    
#     rs_medio = suma_rs / muestras
#     # En aire limpio la relacion Rs/Ro es aproximadamente 3.6 para el MQ-135
#     ro_calculado = rs_medio / 3.6
#     print(f"Calibracion completada. Nuevo valor de Ro = {ro_calculado:.2f} kOhms")
#     return ro_calculado

# if __name__ == "__main__":
#     try:
#         canal = inicializar_ads()
#         print("ADS1115 detectado correctamente.")
#         print("Calentando sensor... (Espere unos segundos)")
#         time.sleep(2)

#         # Descomenta la siguiente linea si deseas ejecutar la calibracion automatica al iniciar:
#         # RO_CLEAN_AIR = calibrar_ro(canal)

#         while True:
#             voltaje = canal.voltage
#             rs = obtener_resistencia_rs(voltaje)
#             ratio = rs / RO_CLEAN_AIR

#             print("-" * 45)
#             print(f"Voltaje A0 (ADS1115): {voltaje:.4f} V | Rs: {rs:.2f} kOhm")
#             print("Estimacion de concentracion equivalente:")
            
#             for gas in GAS_CURVES:
#                 ppm = calcular_ppm(ratio, gas)
#                 print(f"  - {gas:<8}: {ppm:.2f} PPM")
            
#             time.sleep(2)

#     except KeyboardInterrupt:
#         print("\nLectura finalizada.")
#     except Exception as e:
#         print(f"Error al comunicar con el ADS1115: {e}")


import time
import math
import random

# --- SIMULACIÓN EN WINDOWS (SIN RASPBERRY PI) ---

class SimualdorADS:
    @property
    def voltage(self):
        # Simula una lectura de voltaje entre 0.5V y 2.5V
        return random.uniform(0.8, 1.8)

def inicializar_ads():
    print("[MODO SIMULACIÓN] ADS1115 simulado en Windows.")
    return SimualdorADS()

# --- FIN BLOQUE SIMULACIÓN ---

RL_VALUE = 10.0  
RO_CLEAN_AIR = 3.6  

GAS_CURVES = {
    "CO2":     {"a": 110.47, "b": -2.862},
    "NH3":     {"a": 102.2,  "b": -2.473},
    "Alcohol": {"a": 77.255, "b": -3.18},
    "Humo":    {"a": 44.947, "b": -3.445}
}

def obtener_resistencia_rs(voltaje_v):
    if voltaje_v <= 0:
        return float('inf')
    vcc = 5.0
    return ((vcc - voltaje_v) / voltaje_v) * RL_VALUE

def calcular_ppm(ratio_rs_ro, gas):
    if gas not in GAS_CURVES or ratio_rs_ro <= 0:
        return 0.0
    a = GAS_CURVES[gas]["a"]
    b = GAS_CURVES[gas]["b"]
    return a * math.pow(ratio_rs_ro, b)

if __name__ == "__main__":
    canal = inicializar_ads()
    
    while True:
        voltaje = canal.voltage
        rs = obtener_resistencia_rs(voltaje)
        ratio = rs / RO_CLEAN_AIR

        print("-" * 45)
        print(f"Voltaje A0: {voltaje:.4f} V | Rs: {rs:.2f} kOhm")
        print("Estimación de concentración equivalente:")
        
        for gas in GAS_CURVES:
            ppm = calcular_ppm(ratio, gas)
            print(f"  - {gas:<8}: {ppm:.2f} PPM")
        
        time.sleep(2)