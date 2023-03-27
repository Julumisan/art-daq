# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 00:06:10 2023

@author: jumis
"""

import tkinter as tk
from tkinter import ttk
from art_daq import prueba

class MIN:

    def __init__(self):
        self.setup_gui()

    def update_voltage_label(self):
        device_name = prueba.get_connected_device()
        if device_name:
            chan_a = device_name + "/ai0"
            voltage = prueba.get_voltage_analogic(chan_a)
            self.voltage_label.config(text="Voltage: {:.6f} V".format(voltage))
        else:
            self.voltage_label.config(text="No hay dispositivos conectados")
        self.root.after(1000, self.update_voltage_label)

    def set_output_voltage(self):
        device_name = prueba.get_connected_device()
        if device_name:
            chan_a = device_name + "/ao0"
            voltage = float(self.spinbox.get())
            prueba.set_voltage_analogic(chan_a, voltage)

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("DAQ Control")

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.voltage_label = ttk.Label(frame, text="Voltage: -- V")
        self.voltage_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        spinbox_label = ttk.Label(frame, text="Output voltage (0-5V):")
        spinbox_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.spinbox = ttk.Spinbox(frame, from_=0, to=5, increment=0.01, width=10)
        self.spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        set_voltage_button = ttk.Button(frame, text="Set Voltage", command=self.set_output_voltage)
        set_voltage_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.root.after(1000, self.update_voltage_label)
        self.root.mainloop()

if __name__ == "__main__":
    app = MIN()