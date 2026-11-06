import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import urllib.request
import threading
import time
from PIL import Image, ImageTk

class HMICrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HMI - Control y Telemetría de Crawler")
        self.root.geometry("1220x750")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(True, True)

        # Variables de IP y Comunicación Ethernet
        self.ip_raspberry_var = tk.StringVar(value="192.168.1.50")
        self.conexion_activa = False
        self.camara_activa = False
        self.robot_encendido = False
        self.en_movimiento_avanzar = False
        
        self.url_stream = ""
        self.url_comando = ""
        self.url_sensor = ""

        # Hilos secundarios
        self.hilo_video = None
        self.hilo_telemetria = None

        # Colores personalizados
        self.COLOR_AZUL = "#1976D2"
        self.COLOR_AZUL_DARK = "#0D47A1"
        self.COLOR_ROJO = "#D32F2F"
        self.COLOR_ROJO_DARK = "#B71C1C"

        # Estilo Tkinter (Fondo Blanco)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#FFFFFF', foreground='#000000')

        self.crear_interfaz()

    def crear_interfaz(self):
        # Header / Título Principal
        header_frame = tk.Frame(self.root, bg="#FFFFFF", highlightbackground="#E0E0E0", highlightthickness=1)
        header_frame.pack(fill="x", padx=15, pady=10)

        titulo = tk.Label(
            header_frame, 
            text="SISTEMA DE INSPECCIÓN CRAWLER - HMI", 
            font=("Helvetica", 16, "bold"), 
            bg="#FFFFFF", 
            fg="#1A237E"
        )
        titulo.pack(side="left", padx=10, pady=5)

        self.lbl_estado_conexion = tk.Label(
            header_frame, 
            text="ESTADO: DESCONECTADO", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFE0B2", 
            fg="#E65100", 
            padx=10, 
            pady=3
        )
        self.lbl_estado_conexion.pack(side="right", padx=10, pady=5)

        # Contenedor Principal (2 Columnas)
        main_container = tk.Frame(self.root, bg="#FFFFFF")
        main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # --- COLUMNA IZQUIERDA: Panel de Video ---
        video_panel = tk.LabelFrame(
            main_container, 
            text=" Transmisión de Video en Vivo (Ethernet - OV5647) ", 
            font=("Helvetica", 11, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=10
        )
        video_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_video = tk.Label(video_panel, bg="#000000")
        self.lbl_video.pack(fill="both", expand=True)

        # --- COLUMNA DERECHA: Controles e Instrumentación ---
        control_panel = tk.Frame(main_container, bg="#FFFFFF", width=360)
        control_panel.pack(side="right", fill="y", expand=False)

        # 1. Grupo: Configuración Ethernet
        frame_enlace = tk.LabelFrame(
            control_panel, 
            text=" Comunicación Ethernet ", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=6
        )
        frame_enlace.pack(fill="x", pady=(0, 8))

        lbl_ip_prompt = tk.Label(frame_enlace, text="IP Raspberry Pi:", font=("Helvetica", 9, "bold"), bg="#FFFFFF")
        lbl_ip_prompt.pack(anchor="w")

        self.txt_ip = tk.Entry(frame_enlace, textvariable=self.ip_raspberry_var, font=("Consolas", 10), justify="center")
        self.txt_ip.pack(fill="x", pady=(2, 4))

        self.btn_conectar_pi = tk.Button(
            frame_enlace, 
            text="🔌 CONECTAR ETHERNET", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLOR_AZUL, 
            fg="#FFFFFF", 
            disabledforeground="#FFFFFF",
            activebackground=self.COLOR_AZUL_DARK, 
            activeforeground="#FFFFFF",
            command=self.toggle_conexion_pi, 
            cursor="hand2",
            pady=3
        )
        self.btn_conectar_pi.pack(fill="x")

        # 2. Grupo: Control de Cámara
        frame_camara = tk.LabelFrame(
            control_panel, 
            text=" Control de Cámara ", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=6
        )
        frame_camara.pack(fill="x", pady=(0, 8))

        self.btn_toggle_camara = tk.Button(
            frame_camara, 
            text="📷 ACTIVAR CÁMARA", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLOR_AZUL, 
            fg="#FFFFFF", 
            disabledforeground="#FFFFFF",
            activebackground=self.COLOR_AZUL_DARK, 
            activeforeground="#FFFFFF",
            command=self.toggle_camara, 
            cursor="hand2",
            state="disabled",
            pady=3
        )
        self.btn_toggle_camara.pack(fill="x")

        # 3. Grupo: Control de Energía del Robot
        frame_power = tk.LabelFrame(
            control_panel, 
            text=" Control de Energía ", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=6
        )
        frame_power.pack(fill="x", pady=(0, 8))

        self.btn_encender = tk.Button(
            frame_power, 
            text="ENCENDER ROBOT", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLOR_AZUL, 
            fg="#FFFFFF", 
            disabledforeground="#FFFFFF",
            activebackground=self.COLOR_AZUL_DARK, 
            activeforeground="#FFFFFF",
            command=self.toggle_encendido, 
            cursor="hand2",
            state="disabled",
            pady=3
        )
        self.btn_encender.pack(fill="x")

        # 4. Grupo: PARADA DE EMERGENCIA (Fondo Rojo)
        frame_emergencia = tk.Frame(control_panel, bg="#FFFFFF")
        frame_emergencia.pack(fill="x", pady=(0, 8))

        btn_parada_emergencia = tk.Button(
            frame_emergencia, 
            text="🚨 PARADA DE EMERGENCIA 🚨", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLOR_ROJO, 
            fg="#FFFFFF", 
            disabledforeground="#FFFFFF",
            activebackground=self.COLOR_ROJO_DARK, 
            activeforeground="#FFFFFF",
            command=self.parada_emergencia, 
            cursor="hand2", 
            pady=6
        )
        btn_parada_emergencia.pack(fill="x")

        # 5. Grupo: Tracción / Avance
        frame_movimiento = tk.LabelFrame(
            control_panel, 
            text=" Tracción y Avance ", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=6
        )
        frame_movimiento.pack(fill="x", pady=(0, 8))

        self.btn_avanzar = tk.Button(
            frame_movimiento, 
            text="▲ AVANZAR (Adelante)", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLOR_AZUL, 
            fg="#FFFFFF", 
            disabledforeground="#FFFFFF",
            activebackground=self.COLOR_AZUL_DARK, 
            activeforeground="#FFFFFF",
            command=self.toggle_avanzar, 
            cursor="hand2", 
            state="disabled",
            pady=3
        )
        self.btn_avanzar.pack(fill="x")

        # 6. Grupo: Sensor MQ-135 con Detalle de Gases
        frame_sensor = tk.LabelFrame(
            control_panel, 
            text=" Monitoreo MQ-135 (Gases / Calidad Aire) ", 
            font=("Helvetica", 10, "bold"), 
            bg="#FFFFFF", 
            fg="#333333", 
            padx=10, 
            pady=6
        )
        frame_sensor.pack(fill="x")

        lbl_gases_info = tk.Label(
            frame_sensor, 
            text="Detecta: NH₃, NOx, Alcohol, Benceno, CO₂, Humo", 
            font=("Helvetica", 8, "italic"), 
            bg="#FFFFFF", 
            fg="#616161"
        )
        lbl_gases_info.pack(anchor="w")

        self.lbl_mq135_val = tk.Label(
            frame_sensor, 
            text="--- PPM", 
            font=("Helvetica", 18, "bold"), 
            bg="#FFFFFF", 
            fg="#0288D1"
        )
        self.lbl_mq135_val.pack(pady=2)

        self.progress_mq135 = ttk.Progressbar(frame_sensor, orient="horizontal", length=200, mode="determinate")
        self.progress_mq135.pack(fill="x", pady=4)

        self.lbl_alerta_gas = tk.Label(
            frame_sensor, 
            text="ENLACE DESCONECTADO", 
            font=("Helvetica", 9, "bold"), 
            bg="#FFFFFF", 
            fg="#757575"
        )
        self.lbl_alerta_gas.pack()

    # --- LÓGICA ETHERNET DE CONEXIÓN / DESCONEXIÓN ---
    def toggle_conexion_pi(self):
        if not self.conexion_activa:
            ip_ingresada = self.ip_raspberry_var.get().strip()
            if not ip_ingresada:
                messagebox.showerror("Error de Red", "Por favor ingresa la dirección IP de la Raspberry Pi.")
                return

            self.url_stream = f"http://{ip_ingresada}:8000/stream"
            self.url_comando = f"http://{ip_ingresada}:8000/cmd"
            self.url_sensor = f"http://{ip_ingresada}:8000/mq135"

            self.conexion_activa = True
            self.btn_conectar_pi.config(text="❌ DESCONECTAR ETHERNET")
            self.btn_encender.config(state="normal")
            self.btn_toggle_camara.config(state="normal")
            self.txt_ip.config(state="disabled")

            self.hilo_telemetria = threading.Thread(target=self.leer_sensor_mq135, daemon=True)
            self.hilo_telemetria.start()
        else:
            self.desconectar_pi()

    def desconectar_pi(self):
        self.conexion_activa = False
        if self.camara_activa:
            self.desactivar_camara()
            
        if self.robot_encendido:
            self.apagar_sistema()

        self.btn_conectar_pi.config(text="🔌 CONECTAR ETHERNET")
        self.btn_encender.config(state="disabled")
        self.btn_toggle_camara.config(state="disabled")
        self.txt_ip.config(state="normal")
        self.lbl_estado_conexion.config(text="ESTADO: DESCONECTADO", bg="#FFE0B2", fg="#E65100")

        self.lbl_video.config(image='')
        self.lbl_mq135_val.config(text="--- PPM")
        self.progress_mq135['value'] = 0
        self.lbl_alerta_gas.config(text="ENLACE DESCONECTADO", fg="#757575")

    # --- LÓGICA DE CONTROL DE CÁMARA ---
    def toggle_camara(self):
        if not self.conexion_activa:
            return

        if not self.camara_activa:
            self.camara_activa = True
            self.btn_toggle_camara.config(text="📷 DESACTIVAR CÁMARA")
            self.hilo_video = threading.Thread(target=self.actualizar_video, daemon=True)
            self.hilo_video.start()
        else:
            self.desactivar_camara()

    def desactivar_camara(self):
        self.camara_activa = False
        self.btn_toggle_camara.config(text="📷 ACTIVAR CÁMARA")
        self.lbl_video.config(image='')

    # --- LÓGICA DE CONTROL DEL ROBOT ---
    def toggle_encendido(self):
        if not self.robot_encendido:
            self.robot_encendido = True
            self.btn_encender.config(text="APAGAR ROBOT")
            self.btn_avanzar.config(state="normal")
            self.enviar_comando("POWER_ON")
        else:
            self.apagar_sistema()

    def apagar_sistema(self):
        self.robot_encendido = False
        self.en_movimiento_avanzar = False
        self.btn_encender.config(text="ENCENDER ROBOT")
        self.btn_avanzar.config(text="▲ AVANZAR (Adelante)", state="disabled")
        self.enviar_comando("POWER_OFF")

    def toggle_avanzar(self):
        if not self.robot_encendido or not self.conexion_activa:
            return

        if not self.en_movimiento_avanzar:
            self.en_movimiento_avanzar = True
            self.btn_avanzar.config(text="⏹ DETENER AVANCE")
            self.enviar_comando("MOVE_FORWARD")
        else:
            self.en_movimiento_avanzar = False
            self.btn_avanzar.config(text="▲ AVANZAR (Adelante)")
            self.enviar_comando("MOVE_STOP")

    def parada_emergencia(self):
        self.en_movimiento_avanzar = False
        if self.conexion_activa:
            self.enviar_comando("EMERGENCY_STOP")
        self.apagar_sistema()
        messagebox.showwarning("PARADA DE EMERGENCIA", "¡Parada de emergencia ejecutada vía Ethernet!")

    def enviar_comando(self, cmd):
        def _send():
            if not self.conexion_activa:
                return
            try:
                url = f"{self.url_comando}?action={cmd}"
                urllib.request.urlopen(url, timeout=2)
            except Exception as e:
                print(f"Error al enviar comando Ethernet '{cmd}': {e}")
        threading.Thread(target=_send, daemon=True).start()

    # --- TRANSMISIÓN DE VIDEO INDEPENDIENTE ---
    def actualizar_video(self):
        while self.conexion_activa and self.camara_activa:
            try:
                stream = urllib.request.urlopen(self.url_stream, timeout=5)
                self.lbl_estado_conexion.config(text="ESTADO: CONECTADO (ETHERNET)", bg="#C8E6C9", fg="#2E7D32")
                bytes_buffer = b''

                while self.conexion_activa and self.camara_activa:
                    bytes_buffer += stream.read(4096)
                    a = bytes_buffer.find(b'\xff\xd8')
                    b = bytes_buffer.find(b'\xff\xd9')

                    if a != -1 and b != -1:
                        jpg = bytes_buffer[a:b+2]
                        bytes_buffer = bytes_buffer[b+2:]
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                        if frame is not None:
                            ancho_target = self.lbl_video.winfo_width()
                            alto_target = self.lbl_video.winfo_height()

                            if ancho_target > 10 and alto_target > 10:
                                frame = cv2.resize(frame, (ancho_target, alto_target), interpolation=cv2.INTER_AREA)

                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img_pil = Image.fromarray(frame_rgb)
                            img_tk = ImageTk.PhotoImage(image=img_pil)

                            self.lbl_video.img_tk = img_tk
                            self.lbl_video.config(image=img_tk)

            except Exception:
                if self.conexion_activa and self.camara_activa:
                    self.lbl_estado_conexion.config(text="ESTADO: BUSCANDO CÁMARA...", bg="#FFCDD2", fg="#C62828")
                time.sleep(2)

    def leer_sensor_mq135(self):
        while self.conexion_activa:
            if self.robot_encendido:
                try:
                    resp = urllib.request.urlopen(self.url_sensor, timeout=2)
                    valor_str = resp.read().decode('utf-8')
                    val_ppm = float(valor_str)

                    self.lbl_mq135_val.config(text=f"{val_ppm:.1f} PPM")
                    self.progress_mq135['value'] = min(val_ppm / 10.0, 100)

                    if val_ppm > 400.0:
                        self.lbl_alerta_gas.config(text="⚠️ ALERTA: CONCENTRACIÓN ELEVADA DE GAS", fg="#D32F2F")
                    else:
                        self.lbl_alerta_gas.config(text="ESTADO: NIVELES NORMALES DE GAS", fg="#2E7D32")
                except Exception:
                    pass
            else:
                self.lbl_mq135_val.config(text="--- PPM")
                self.progress_mq135['value'] = 0
                self.lbl_alerta_gas.config(text="ROBOT APAGADO", fg="#757575")

            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = HMICrawlerApp(root)
    root.mainloop()