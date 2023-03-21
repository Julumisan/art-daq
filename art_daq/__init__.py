# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:05:36 2023

@author: julu

__init__.py para que python sepa que es un paquete.
TIENE QUE ESTAR VACÍO PARA QUE NO HAYA DEPENDENCIA CÍCLICA
Para usar la libreria tiene que tener importarse de la forma: "from art_daq import prueba"

La función get_voltage_analogic(chan_a) lee el voltaje actual del canal analógico especificado en el parámetro chanA.
La función get_state_digital(chan_d) lee el estado actual del canal digital especificado en el parámetro chanD.
La función set_voltage_anal(chan_a, voltage) establece el voltaje del canal analógico especificado en el parámetro chanA en el valor especificado en el parámetro voltage(Double).
La función set_voltage_digital(chan_d, voltage) establece el voltaje del canal digital especificado en el parámetro chanD en el valor especificado en el parámetro voltage(Boolean).
La función daq_timer(chan_a, duration) configura una tarea de adquisición de datos que espera durante una cantidad de tiempo determinada.
La función all_digital_safe(device_name) establece todas las líneas de salida estén a False.
La función all_analogic_safedevice_name configura todos los canales analógicos de salida a 0V. 
La función safe_state(device_name) establece un voltaje seguro en todas las salidas.
"""

