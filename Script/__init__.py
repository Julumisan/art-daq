# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:05:36 2023

@author: julu

__init__.py para que python sepa que es un paquete.
TIENE QUE ESTAR VACÍO PARA QUE NO HAYA DEPENDENCIA CÍCLICA
Para usar la libreria tiene que tener ser import Script.prueba

La función get_voltage_analogic(chanA) lee el voltaje actual del canal analógico especificado en el parámetro chanA.
La función get_state_digital(chanD) lee el estado actual del canal digital especificado en el parámetro chanD.
La función set_voltage_anal(chanA, voltage) establece el voltaje del canal analógico especificado en el parámetro chanA en el valor especificado en el parámetro voltage(Double).
La función set_voltage_digital(chanD, voltage) establece el voltaje del canal digital especificado en el parámetro chanD en el valor especificado en el parámetro voltage(Boolean).
"""

