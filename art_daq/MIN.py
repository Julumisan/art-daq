# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 22:34:59 2023

@author: Julu

Clase de testeo de la DAQ con iface gráfica para poder comprobar
de manera sencilla y clara cómo está la tarjeta.

v2.4.3

"""

import tkinter as tk
import numpy as np
import threading
import time
import nidaqmx
from threading import Event
from tkinter import ttk
from art_daq import daq
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
import pyvisa as visa

class MIN:

    def __init__(self):
        """
        Inicializa la aplicación y configura la interfaz gráfica de usuario, los gráficos y la comunicación con el hardware.
        """
        try:
            self.osciloscopio = None
            self.multimetro = None
            self.para = False
            self.abort_signal_generation = False
            self.conexion = True
            self.count = 0
            self.kill_signal = False
            self.previous_channel = None  # Para poder cambiar la gráfica si cambio el canal
            # self.find_visa_devices()
            self.start_multimetro_thread()
            self.start_osci_thread()
            self.setup_gui()
            daq.safe_state(self.device_name)
        finally:
            self.para = True
            daq.safe_state(self.device_name)
            self.check_thread_mult.join()
            self.check_thread_osci.join()
            self.rm.close()
            
            
    
    def setup_gui(self):
        """
        Configura la interfaz gráfica de usuario.
        """
        self.root = tk.Tk()
        self.root.title("MIN")
        # Expansion
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(1, weight=1)
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, padx=10, pady=10)
        
        frame = ttk.Frame(notebook)
        frame2 = ttk.Frame(notebook)
        frame3 = ttk.Frame(notebook)
        frame4 = ttk.Frame(notebook)
        
        notebook.add(frame, text="I/O DAQ")
        notebook.add(frame2, text="Osciloscopio SCPI")
        notebook.add(frame3, text="Multimetro SCPI")
        notebook.add(frame4, text="Señales")
        
        # Frame 2 (Text Box) osci
        frame2.columnconfigure(0, weight=10)
        text_box = tk.Text(frame2)
        text_box.config(height=10)
        # text_box.bind("<Return>", self.save_text)
        text_box.grid(row=0, column=0, padx=10, pady=10)
        # Respuesta
        self.script_text_box = tk.Text(frame2, state='disabled')
        self.script_text_box.config(height=10)
        self.script_text_box.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        
        # Frame 3 (Text Box) multi
        text_box2 = tk.Text(frame3)
        text_box2.config(height=10)
        # text_box2.bind("<Return>", self.save_text_mult)
        text_box2.grid(row=0, column=0, padx=10, pady=10)
        # Respuesta
        self.script_text_box2 = tk.Text(frame3, state='disabled')
        self.script_text_box2.config(height=10)
        self.script_text_box2.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        
        # Combobox para elegir la salida de señal
        tipos = ["Square Wave", "Triangular Wave", "Sinusoidal Wave"]
        
        self.signal_combobox = ttk.Combobox(frame4, values=tipos, state="readonly")
        self.signal_combobox.set(tipos[0])
        self.signal_combobox.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Salida analógica
        
        output_channel_label_frame4 = ttk.Label(frame4, text="Select analog output channel:", font=("", 13))
        output_channel_label_frame4.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        options_frame4 = ttk.Label(frame4, text="Necessary options for the creation of the waves: ", font=("Times New Roman Black", 16))
        options_frame4.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_channel_combobox_frame4 = ttk.Combobox(frame4, values=list(range(0,2)), state="readonly", width=3)
        self.output_channel_combobox_frame4.set("0")
        self.output_channel_combobox_frame4.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        freq_label = ttk.Label(frame4, text="Frequency [Hz]: ", font=("", 13))
        freq_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.text_box_freq = tk.Entry(frame4)
        self.text_box_freq.grid(row=3, column=1, padx=10, pady=1, sticky=tk.E)
        
        amp_label = ttk.Label(frame4, text="Amplitude [V] (0-5): ", font=("", 13))
        amp_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.text_box_amp = tk.Entry(frame4)
        self.text_box_amp.grid(row=4, column=1, padx=10, pady=10, sticky=tk.E)
        
        dur_label = ttk.Label(frame4, text="Duration [s]: ", font=("", 13))
        dur_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.text_box_dur = tk.Entry(frame4)
        self.text_box_dur.grid(row=5, column=1, padx=10, pady=10, sticky=tk.E)
        
        
        dur_label = ttk.Label(frame4, text="Steps: ", font=("", 13))
        dur_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.text_box_steps = tk.Entry(frame4)
        self.text_box_steps.grid(row=6, column=1, padx=10, pady=10, sticky=tk.E)
        
        
        self.activate_button = ttk.Button(frame4, text="Activar señal", command=lambda: self.start_signal_thread())
        self.activate_button.grid(row=7, column=1, padx=10, pady=10)
        
        
        self.deactivate_button = ttk.Button(frame4, text="Desactivar señal", command=lambda: self.kill_signal_thread(), style="Red.TButton")
        self.deactivate_button.grid(row=7, column=0, padx=10, pady=10)
        self.deactivate_button.config(state='disabled')
        
        # Final Frame 4
        

        
        self.save_button = ttk.Button(frame2, text="Send Command", command=lambda: self.save_text(text_box))
        text_box.bind("<Return>", lambda event: self.save_button.invoke())
        self.save_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.save_button2 = ttk.Button(frame3, text="Send Command", command=lambda: self.save_text_mult(text_box2))
        text_box2.bind("<Return>", lambda event: self.save_button2.invoke())
        self.save_button2.grid(row=2, column=0, padx=10, pady=10)
                

        # Configurar los widgets
        self.voltage_label = ttk.Label(frame, text="Voltage: -- V")
        self.voltage_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        input_channel_label = ttk.Label(frame, text="Select input channel:")
        input_channel_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.input_channel_combobox = ttk.Combobox(frame, values=list(range(0, 8)), state="readonly", width=3)
        self.input_channel_combobox.set("0")
        self.input_channel_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        spinbox_label = ttk.Label(frame, text="Output voltage (0-5V):")
        spinbox_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.spinbox = ttk.Spinbox(frame, from_=0, to=5, increment=0.1, width=10)
        self.spinbox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        output_channel_label = ttk.Label(frame, text="Select analog output channel:")
        output_channel_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        # Salida analógica
        self.output_channel_combobox = ttk.Combobox(frame, values=list(range(0,2)), state="readonly", width=3)
        self.output_channel_combobox.set("0")
        self.output_channel_combobox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        set_voltage_button = ttk.Button(frame, text="Set Analog Voltage", command=self.set_output_voltage)
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
        self.digital_output_checkbutton = tk.Checkbutton(frame, text="Digital output value (True/False)", variable=self.digital_output_value)
        self.digital_output_checkbutton.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        set_digital_output_button = ttk.Button(frame, text="Set Digital Output", command=self.set_digital_output)
        set_digital_output_button.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        
        
                
        digital_input_label = ttk.Label(frame, text="Select digital input channel:")
        digital_input_label.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Generar una lista de opciones para el Combobox en el formato "portX/lineY"
        digital_input_options = [f"port{p}/line{l}" for p in range(3) for l in range(8 if p == 0 else (4 if p == 1 else 1))]
        
        self.digital_input_combobox = ttk.Combobox(frame, values=digital_input_options, state="readonly", width=15)
        self.digital_input_combobox.set("port0/line0")  # Establecer el valor predeterminado en "port0/line0"
        self.digital_input_combobox.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.digital_input_indicator = tk.Label(frame, text="", width=2, bg="red")
        self.digital_input_indicator.grid(row=7, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.digital_input_value = tk.StringVar()
        self.digital_input_check = tk.Label(frame, text="Digital input value:", textvariable=self.digital_input_value)
        self.digital_input_check.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        
        set_digital_input_button = ttk.Button(frame, text="Set Digital Input", command=self.check_digital_input_state)
        set_digital_input_button.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)


        
        
        exit_button = ttk.Button(frame, text="Exit", command=self.confirm_exit, style="Red.TButton")
        exit_button.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)
        
        style = ttk.Style()
        style.configure("Red.TButton", foreground="red")
    
        self.update_digital_output_label()
        
        # Iniciar la actualización de la etiqueta de voltaje y el bucle principal
        self.root.after(1000, self.update_voltage_label)
        self.root.mainloop()
        
    def setup_plot(self):
        """
        Configura el gráfico y los ejes.
        """
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Analog Input")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.grid()
        self.plot_data = self.ax.plot([], [], 'r-')[0]
        self.plot_x = np.array([])
        self.plot_y = np.array([])
        self.time_counter = 0
       
        
    
    def update_plot(self, voltage):
        """
        Agrega nuevos datos al gráfico y lo actualiza.
        
        Args:
            voltage (float): Voltaje a cambiar.
        """
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
        print(self.check_thread_mult.is_alive())
        print(threading.active_count())
    
    def reset_plot(self):
        """
        Reinicia el gráfico.
        """
        self.plot_x = np.array([])
        self.plot_y = np.array([])
        self.time_counter = 0
        self.plot_data.set_data(self.plot_x, self.plot_y)
        self.ax.set_xlim(0, self.time_counter)
        self.canvas.draw()
    
    def update_voltage_label(self):
        """
        Actualiza la etiqueta de voltaje.
        """
        self.device_name = daq.get_connected_device()
        try:
            if self.device_name:
                self.conexion = True
                selected_channel = self.input_channel_combobox.get()
    
                # Comdaq si el canal seleccionado ha cambiado
                if self.previous_channel != selected_channel:
                    self.reset_plot()  # Reinicia la gráfica si el canal cambia
                    self.previous_channel = selected_channel
     
                chan_a = self.device_name + "/ai{}".format(selected_channel)
                voltage = daq.get_voltage_analogic(chan_a)
                self.voltage_label.config(text="Voltage: {:.6f} V".format(voltage))
                self.update_plot(voltage)
                # print(self.check_thread.is_alive())
                self.root.after(100, self.update_voltage_label)
                
                if self.fin_signal is False:
                    self.activate_button.config(state="disabled")
                    self.deactivate_button.config(state="normal")
                else:
                    self.activate_button.config(state="normal")
                    self.deactivate_button.config(state="disabled")
                
            else:
                self.conexion = False
                self.voltage_label.config(text="No hay dispositivos conectados")
                self.start_check_thread()
                self.set_digital_output()
                self.update_digital_output_label()
                self.check_digital_input_state()
                print(self.check_thread.is_alive())
        except nidaqmx.errors.DaqError as e:
            self.check_device_name()
            print("error", e)
        

    def set_output_voltage(self):
        """
        Establece el voltaje de salida.
        """
        device_name = daq.get_connected_device()
        if device_name:
            # Leer el canal de salida seleccionado
            selected_channel = self.output_channel_combobox.get()
            chan_a = device_name + "/ao{}".format(selected_channel)
            voltage = float(self.spinbox.get())
            daq.set_voltage_analogic(chan_a, voltage)
    
    def set_digital_output(self):
        """
        Establece la salida digital.
        """
        device_name = daq.get_connected_device()
        if device_name:
            selected_channel = self.digital_output_combobox.get()
            chan_d = device_name + "/" + selected_channel  # Actualizar el formato del canal
            state = self.digital_output_value.get()
            daq.set_voltage_digital(chan_d, state)
            self.update_digital_output_label()
    
    def update_digital_output_label(self, event=None):
        """
        Actualiza la etiqueta de salida digital.
        """
        device_name = daq.get_connected_device()
        if device_name:
            selected_channel = self.digital_output_combobox.get()
            chan_d = device_name + "/" + selected_channel  # Actualizar el formato del canal
            state = daq.get_state_digital(chan_d)
            self.digital_output_value.set(state)
            self.digital_output_checkbutton.config(text="Output value (True/False): {}".format(state))
        else:
            self.digital_output_checkbutton.config(text="Output value (True/False): --")
            
            
    def check_digital_input_state(self):
        """
        Checkea el input de la entrada del combobox.
        """
        device_name = daq.get_connected_device()
        if self.conexion:
            if device_name:
                selected_channel = self.digital_input_combobox.get()
                chan_d = device_name + "/" + selected_channel  # Actualizar el formato del canal
                state = daq.read_digital_input(chan_d)
                if state:
                    self.digital_input_indicator.config(bg="green")
                else:
                    self.digital_input_indicator.config(bg="red")
        else:
            self.digital_input_indicator.config(bg="yellow")

   
       
        
    # def find_visa_devices(self):
    #     rm = visa.ResourceManager()
        
    #     print(dispositivos)
    #     visa_devices = []
    #     for dispositivo in dispositivos:
    #         try:
    #             recurso = rm.open_resource(dispositivo)
    #             if recurso.resource_name.startswith('USB'):
    #                 visa_devices.append(dispositivo)
    #                 recurso.close()
    #             else:
    #                 pass
    #         except visa.VisaIOError:
    #             pass                  
    #     self.get_info_visa_devices(visa_devices)
    #     return visa_devices
    
    
    # Obtener información de los dispositivos Visa
    def find_visa_devices(self):
        self.rm = visa.ResourceManager()
        dispositivos = self.rm.list_resources()
        for device in dispositivos:         
            try:  
                resource = self.rm.open_resource(device)
                description = resource.query("*IDN?")
                print("Dispositivo Visa encontrado:")
                print(f"  Descripción: {description.strip()}")
                print(f"  Dirección: {device}")
                print("")   
                
                if "MSO" in description:
                    print("Creo que soy un Osci")
                    self.osciloscopio = resource
                if "PRO" in description:
                    print("Creo que soy un multimetro")
                    self.multimetro = resource
            except visa.VisaIOError:
                pass
                

                
    def save_text(self, text_box):
        self.text = text_box.get("1.0", tk.END).strip()  # Obtener el texto del cuadro de texto
        try:
            answer_osci = self.osciloscopio.query(self.text)  
        except:
            self.save_button.config(state='disabled')
            answer_osci = "Timeout"
            self.start_osci_thread()
            
        self.script_text_box.configure(state='normal')
        self.script_text_box.delete('1.0', 'end')
        self.script_text_box.insert('1.0', str(answer_osci))
        self.script_text_box.configure(state='disabled')
        print(answer_osci)
            
        
        
    def save_text_mult(self, text_box2):
        self.text2 = text_box2.get("1.0", tk.END).strip()  # Obtener el texto del cuadro de texto
        print("Envio el command: " + self.text2)
        try:
            answer_mult = self.multimetro.query(self.text2)
        except:
            self.save_button2.config(state='disabled')
            answer_mult = "Timeout"
            self.start_multimetro_thread()
            
        self.script_text_box2.configure(state='normal')
        self.script_text_box2.delete('1.0', 'end')
        self.script_text_box2.insert('1.0', answer_mult)
        self.script_text_box2.configure(state='disabled') 
        print(answer_mult)
        

        


    # def activate_signal(self):       
    #     # Si no se produjeron errores, se ejecuta el código relacionado con selected_index
    #     self.start_signal_thread(selected_index)
    #     self.activate_button.config(state='active')

            
    def check_device_name(self):
        while self.device_name is None and not self.para:
            self.device_name = daq.get_connected_device()
            time.sleep(0.3)
        self.update_voltage_label()
        
    def check_multi_connections(self):
        self.multimetro = None
        while self.multimetro is None and not self.para:
            self.find_visa_devices()
            self.count = self.count + 1
            print("COUNT ES: " + str(self.count))
            # time.sleep(1)
        self.save_button2.config(state='active')
            
    def check_osci_connections(self):
        print("Llego aqui (osci_conect)")
        self.osciloscopio = None
        while self.osciloscopio is None and not self.para:
            self.find_visa_devices()
            self.count = self.count + 1
            print(self.count)
            print("Miro las conexiones visa")
            # time.sleep(2)
        self.save_button.config(state='active')
        
    # Hilos
    def start_check_thread(self):
        """Inicia el hilo para verificar el nombre del dispositivo."""
        if not hasattr(self, 'check_thread') or not self.check_thread.is_alive():
            print("Entro al hilo")
            self.check_thread = threading.Thread(target=self.check_device_name)
            self.check_thread.daemon = True  # Hilo se ejecutará en segundo plano idealmente
            self.check_thread.start()
        else:
            print("El hilo ya está en ejecución")
    
    def start_multimetro_thread(self):
        print("Entro al hilo del multi")
        if not hasattr(self, 'check_thread_mult') or not self.check_thread_mult.is_alive():
            self.check_thread_mult = threading.Thread(target=self.check_multi_connections)
            self.check_thread_mult.daemon = True  # Hilo se ejecutará en segundo plano idealmente
            self.check_thread_mult.start() 
        else:
            print("El hilo ya está en ejecución")

    def start_osci_thread(self):
        print("Entro al hilo del osci")
        if not hasattr(self, 'check_thread_osci') or not self.check_thread_osci.is_alive():
            self.check_thread_osci = threading.Thread(target=self.check_osci_connections)
            self.check_thread_osci.daemon = True  # Hilo se ejecutará en segundo plano idealmente
            self.check_thread_osci.start() 
        else:
            print("El hilo ya está en ejecución")
        print("He terminado el hilo")
        
        
    def start_signal_thread(self):
        """Inicia el hilo para señales"""
        if not hasattr(self, 'signal_thread') or not self.signal_thread.is_alive():
            print("Entro al hilo señales")
            selected_index = self.signal_combobox.current()
            ao_channel = self.output_channel_combobox_frame4.current()
            frequency = self.text_box_freq.get()
            amplitude = self.text_box_amp.get()
            duration = self.text_box_dur.get()
            steps = self.text_box_steps.get()
            self.kill_signal = False
        
            if not (frequency.isnumeric() and amplitude.isnumeric() and duration.isnumeric()):
                messagebox.showerror("Error", "Please, check that everything is filled with valid numbers")
                return
        
            frequency = float(frequency)
            amplitude = float(amplitude)
            duration = float(duration)
            steps = int(steps)
            
            def squared_signal():
                self.fin_signal = daq.generate_square_wave(self.device_name, ao_channel, frequency, amplitude, duration, self.kill_signal)
                
            def triangular_signal():
                self.fin_signal = daq.generate_triangle_wave(self.device_name, ao_channel, frequency, amplitude, duration, self.kill_signal, steps)
                
            def sinu_wave():
                self.fin_signal = daq.generate_sine_wave(self.device_name, ao_channel, frequency, amplitude, duration,  self.kill_signal, steps)   
        
            if frequency < 0:
                messagebox.showerror("Error", "Negative frequency is not allowed")
                return
        
            if amplitude < 0:
                messagebox.showerror("Error", "Negative amplitude is not allowed")
                return
        
            if duration < 0:
                messagebox.showerror("Error", "Negative duration is not allowed")
                return
        
            if amplitude > 5:
                messagebox.showerror("Error", "Amplitude should be less than or equal to 5")
                return
            
            if steps < 0 :
                messagebox.showerror("Error", "Negative steps are not allowed")
                return
            
            if selected_index == 0:
                # Ejecutar el método asociado a la opción "Onda Cuadrada"
                self.fin_signal = False
                self.signal_thread = threading.Thread(target=squared_signal)
                print("a")
            elif selected_index == 1:
                self.fin_signal = False
                # Ejecutar el método asociado a la opción "Onda Triangular"     
                self.signal_thread = threading.Thread(target= triangular_signal)
                print("b")
            elif selected_index == 2:
                self.fin_signal = False
                # Ejecutar el método asociado a la opción "Onda Sinusoidal"
                self.signal_thread = threading.Thread(target= sinu_wave)
                print("c")
                

            
            # self.activate_button.config(state='disabled')
            self.signal_thread.daemon = True   # Hilo se ejecutará en segundo plano idealmente 
            self.signal_thread.start()
        else:
            print("El hilo ya está en ejecución")  
            
    def kill_signal_thread(self):

        self.kill_signal = True
        
    
    
            
    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()        
            
if __name__ == "__main__":
    min_app = MIN()
