# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 22:34:59 2023

@author: Julu

Clase de testeo de la DAQ con iface gráfica para poder comprobar
de manera sencilla y clara cómo está la tarjeta.

TO DO: Comentar mejor antes de que se me olvide qué he hecho.

"""

import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk
from art_daq import daq
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MIN:

    def __init__(self):
        try:
            self.previous_channel = None  # Para poder cambiar la gráfica si cambio el canal
            self.setup_gui()
        finally:
            daq.safe_state(self.device_name)



    # Configura la interfaz gráfica de usuario
    def setup_gui(self):
        # Configurar la ventana principal y el marco
        self.root = tk.Tk()
        self.root.title("DAQ Control")
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar los widgets
        self.voltage_label = ttk.Label(frame, text="Voltage: -- V")
        self.voltage_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        input_channel_label = ttk.Label(frame, text="Select input channel:")
        input_channel_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.input_channel_combobox = ttk.Combobox(frame, values=list(range(0, 9)), state="readonly", width=3)
        self.input_channel_combobox.set("0")
        self.input_channel_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        spinbox_label = ttk.Label(frame, text="Output voltage (0-5V):")
        spinbox_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.spinbox = ttk.Spinbox(frame, from_=0, to=5, increment=0.01, width=10)
        self.spinbox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        output_channel_label = ttk.Label(frame, text="Select output channel:")
        output_channel_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        # Salida analógica
        self.output_channel_combobox = ttk.Combobox(frame, values=list(range(0,2)), state="readonly", width=3)
        self.output_channel_combobox.set("0")
        self.output_channel_combobox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        set_voltage_button = ttk.Button(frame, text="Set Voltage", command=self.set_output_voltage)
        set_voltage_button.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Configurar el gráfico y el canvas
        self.setup_plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, rowspan=6)

        digital_output_label = ttk.Label(frame, text="Select digital output channel:")
        digital_output_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        # Generar una lista de opciones para el Combobox en el formato "portX/lineY"
        digital_output_options = [f"port{p}/line{l}" for p in range(3) for l in range(8 if p == 0 else (4 if p == 1 else 1))]

        self.digital_output_combobox = ttk.Combobox(frame, values=digital_output_options, state="readonly", width=15)
        self.digital_output_combobox.set("port0/line0")  # Establecer el valor predeterminado en "port0/line0"
        self.digital_output_combobox.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.digital_output_combobox.bind("<<ComboboxSelected>>", self.update_digital_output_label)

        self.digital_output_value = tk.BooleanVar()
        self.digital_output_checkbutton = tk.Checkbutton(frame, text="Output value (True/False)", variable=self.digital_output_value)
        self.digital_output_checkbutton.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        set_digital_output_button = ttk.Button(frame, text="Set Digital Output", command=self.set_digital_output)
        set_digital_output_button.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

        self.update_digital_output_label()
        
        # Iniciar la actualización de la etiqueta de voltaje y el bucle principal
        self.root.after(1000, self.update_voltage_label)
        self.root.mainloop()


        
    # Configura el gráfico
    def setup_plot(self):
        # Configurar el gráfico y los ejes
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.ax.set_title("Analog Input")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.grid()
        self.plot_data = self.ax.plot([], [], 'r-')[0]
        self.plot_x = np.array([])
        self.plot_y = np.array([])
        self.time_counter = 0
        


    # Actualizar la gráfica
    def update_plot(self, voltage):
        # Agregar nuevos datos al gráfico y actualizar
        self.plot_x = np.append(self.plot_x, self.time_counter)
        self.plot_y = np.append(self.plot_y, voltage)
        self.time_counter += 0.1
    
        self.plot_data.set_data(self.plot_x, self.plot_y)
        
        # Si el tiempo actual es mayor a 10 segundos
        if self.time_counter > 10:
            x_min = self.time_counter - 10  # Ajusta el límite inferior del eje x
        else:
            x_min = 0
        
        self.ax.set_xlim(x_min, self.time_counter)
        self.ax.relim()  # Recalcular los límites de los datos en el eje y
        self.ax.autoscale_view(True, True, True)  # Autoajustar el eje y
        self.canvas.draw()
        
        
        
    # Reiniciar la gráfica
    def reset_plot(self):
        self.plot_x = np.array([])
        self.plot_y = np.array([])
        self.time_counter = 0
        self.plot_data.set_data(self.plot_x, self.plot_y)
        self.ax.set_xlim(0, self.time_counter)
        self.canvas.draw()



    # Actualiza la etiqueta de voltaje
    def update_voltage_label(self):
        self.device_name = daq.get_connected_device()
        if self.device_name:
            selected_channel = self.input_channel_combobox.get()
            
            # Comdaq si el canal seleccionado ha cambiado
            if self.previous_channel != selected_channel:
                self.reset_plot()  # Reinicia la gráfica si el canal cambia
                self.previous_channel = selected_channel
            
            chan_a = self.device_name + "/ai{}".format(selected_channel)
            voltage = daq.get_voltage_analogic(chan_a)
            self.voltage_label.config(text="Voltage: {:.6f} V".format(voltage))
            self.update_plot(voltage)
        else:
            self.voltage_label.config(text="No hay dispositivos conectados")
        self.root.after(100, self.update_voltage_label)
        
        
        
    # Establece el voltaje de salida
    def set_output_voltage(self):
        device_name = daq.get_connected_device()
        if device_name:
            # Leer el canal de salida seleccionado
            selected_channel = self.output_channel_combobox.get()
            chan_a = device_name + "/ao{}".format(selected_channel)
            voltage = float(self.spinbox.get())
            daq.set_voltage_analogic(chan_a, voltage)



    # Establecer la salida digital
    def set_digital_output(self):
        device_name = daq.get_connected_device()
        if device_name:
            selected_channel = self.digital_output_combobox.get()
            chan_d = device_name + "/" + selected_channel  # Actualizar el formato del canal
            state = self.digital_output_value.get()
            daq.set_voltage_digital(chan_d, state)
            self.update_digital_output_label()



    # Actualizar la etiqueta de salida digital
    def update_digital_output_label(self, event=None):
        device_name = daq.get_connected_device()
        if device_name:
            selected_channel = self.digital_output_combobox.get()
            chan_d = device_name + "/" + selected_channel  # Actualizar el formato del canal
            state = daq.get_state_digital(chan_d)
            self.digital_output_value.set(state)
            self.digital_output_checkbutton.config(text="Output value (True/False): {}".format(state))
        else:
            self.digital_output_checkbutton.config(text="Output value (True/False): --")
            

if __name__ == "__main__":
    min_app = MIN()