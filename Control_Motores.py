#Librerias necesarias para el control de motores en la rasberry
#sudo apt update
#sudo apt install python3-gpiozero python3-rpi.gpio

#CODIGO DE PYTHON PARA CONTROLAR LOS MOTORES
import time
from gpiozero import PWMOutputDevice, DigitalOutputDevice


ENA_PIN = 12  # Hardware PWM (GPIO 12)
IN1_PIN = 17
IN2_PIN = 27

ENB_PIN = 13  # Hardware PWM (GPIO 13)
IN3_PIN = 22
IN4_PIN = 23

in1 = DigitalOutputDevice(IN1_PIN)
in2 = DigitalOutputDevice(IN2_PIN)
in3 = DigitalOutputDevice(IN3_PIN)
in4 = DigitalOutputDevice(IN4_PIN)


ena = PWMOutputDevice(ENA_PIN, frequency=1000)
enb = PWMOutputDevice(ENB_PIN, frequency=1000)

def detener():
    """Detiene la rotacion de ambos motores."""
    in1.off()
    in2.off()
    in3.off()
    in4.off()
    ena.value = 0
    enb.value = 0

def avanzar(velocidad=1.0):
    """
    Avanza ambos motores hacia adelante.
    :param velocidad: Valor float entre 0.0 (0%) y 1.0 (100%)
    """
    in1.on()
    in2.off()
    in3.on()
    in4.off()
    ena.value = velocidad
    enb.value = velocidad

def retroceder(velocidad=1.0):
    """
    Retrocede ambos motores.
    :param velocidad: Valor float entre 0.0 (0%) y 1.0 (100%)
    """
    in1.off()
    in2.on()
    in3.off()
    in4.on()
    ena.value = velocidad
    enb.value = velocidad

def girar_izquierda(velocidad=0.8):
    """Gira el robot sobre su propio eje a la izquierda."""
    in1.off()
    in2.on()
    in3.on()
    in4.off()
    ena.value = velocidad
    enb.value = velocidad

def girar_derecha(velocidad=0.8):
    """Gira el robot sobre su propio eje a la derecha."""
    in1.on()
    in2.off()
    in3.off()
    in4.on()
    ena.value = velocidad
    enb.value = velocidad

if __name__ == "__main__":
    try:
        print("Probando movimiento hacia adelante a 50% de velocidad...")
        avanzar(velocidad=0.5)
        time.sleep(2)

        print("Aumentando al 100% de velocidad...")
        avanzar(velocidad=1.0)
        time.sleep(2)

        print("Girando a la izquierda...")
        girar_izquierda(velocidad=0.7)
        time.sleep(1.5)

        print("Retrocediendo a 60% de velocidad...")
        retroceder(velocidad=0.6)
        time.sleep(2)

        print("Deteniendo motores...")
        detener()

    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario.")
    finally:
        detener()
        print("Pines GPIO liberados.")