# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:05:36 2023

@author: Julu
@version: 3.1.2

El archivo init.py es necesario para que Python reconozca que este es un paquete.
Debe estar vacío para evitar una dependencia cíclica.


Para utilizar la librería, se debe importar de la siguiente manera:
    "from art_daq import daq"


La siguiente es una lista de las funciones que se encuentran en este paquete:

    get_voltage_analogic(chan_a): lee el voltaje actual del canal analógico
        especificado en el parámetro chan_a.
        
    get_state_digital(chan_d): lee el estado actual del canal digital
        especificado en el parámetro chan_d.
        
    set_voltage_analogic(chan_a, voltage): establece el voltaje del canal
        analógico especificado en el parámetro chan_a en el valor especificadoç
        en el parámetro voltage (float).
        
    set_voltage_digital(chan_d, voltage): establece el voltaje del canal digital
        especificado en el parámetro chan_d en el valor especificado
        en el parámetro voltage (bool).
        
    daq_timer(chan_a, duration): configura una tarea de adquisición de datos
        que espera durante una cantidad de tiempo determinada.
        
    all_digital_safe(device_name): establece todas las líneas de salida a False.
    
    all_analogic_safe(device_name): configura todos los canales analógicos
        de salida a 0V.
        
    safe_state(device_name): establece un voltaje seguro en todas las salidas.
    
    read_digital_input(chan_d): lee el estado de un canal digital de entrada.


Además de estas funciones, también se incluyen las funciones extra para generar señales:

    generate_sine_wave(device_name, ao_channel, frequency, amplitude, duration, steps=100):
        genera una señal sinusoidal con la
        frecuencia, amplitud y duración especificadas en los parámetros.
    El parámetro opcional "steps" especifica la cantidad de pasos en la formación de la señal sinusoidal.
        
    generate_square_wave(device_name, ao_channel, frequency, amplitude, duration, steps==100):
        genera una señal cuadrada con la frecuencia, amplitud 
        y duración especificadas en los parámetros.
    El parámetro opcional "steps" especifica número de pasos para estar atento a la finalización.
        
    generate_triangle_wave(device_name, ao_channel, frequency, amplitude, duration, steps=100):
        genera una señal triangular con la frecuencia, amplitud
        y duración especificadas en los parámetros.
    El parámetro opcional "steps" especifica la cantidad de pasos en cada rampa de la señal triangular.
    
    generate_triangle_wave(device_name, ao_channel, frequency, amplitude, duration, steps=100):
        genera una señal de dientes de sierra con la frecuencia, amplitud
        y duración especificadas en los parámetros.
    El parámetro opcional "steps" especifica la cantidad de pasos en cada rampa de la señal de sierra .
    
"""

