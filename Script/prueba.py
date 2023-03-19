# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 12:26:46 2023


Este Script va a ser el intento de librería Python de fácil
uso y acceso a las carecterísticas de la DAQ, en los que destaco:
    -Cambios de voltaje de las diferentes salidas.
    -Medidas de voltaje de las diferentes entradas.
    -Temporizador.


@author: Julu
"""

import nidaqmx


# Acceso al voltaje del canal analógico. 
# chanA tiene el formato " "Dev/aoX" "

def get_voltage_analogic(chanA):
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("PFG/ai0", terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        # Leer el voltaje actual del canal ai0 10 veces
        voltages = task.read(number_of_samples_per_channel=10)
        # Calcular la media de los valores leídos
        mean_voltage = sum(voltages)/len(voltages)



# Acceso al voltaje del canal digital. 
# chanD tiene el formato " "Dev/portX/lineY" "

def get_state_digital(chanD):
    with nidaqmx.Task() as task:
        task.di_channels.add_di_chan(chanD)
        state = task.read_digital_u8()
        return state


# Cambios de voltaje de un canal análogico.
# chanA tiene el formato " "Dev/aoX" "

def set_voltage_anal(chanA, voltage):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(chanA) # Especificar la salida analógica chanA del dispositivo DAQ
        task.write(voltage, auto_start=True) # Establecer el voltaje en chanA
        


# Cambios de voltaje de un canal digital.
# chanD tiene el formato " "Dev/portX/lineY" "
        
def set_voltage_digital(chanD, voltage):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chanD) # Especificar la salida digital X.Y del dispositivo DAQ
        task.write(voltage) # Establecer el voltaje en el canal digital