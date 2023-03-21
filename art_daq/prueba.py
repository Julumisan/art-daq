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



# Esta función configura una tarea de adquisición de datos que espera durante
# una cantidad de tiempo determinada.

def daq_timer(chan_a, duration):
    # Se crea una tarea vacía.
    with nidaqmx.Task() as task:
        # Se agrega un canal de entrada analógica al objeto de tarea. "Dev/aiX"
        # es el identificador del canal de entrada.
        ai_channel = task.ai_channels.add_ai_voltage_chan(chan_a)
        
        # Se configura el temporizador de la tarea para utilizar el reloj interno
        # del dispositivo. El temporizador espera durante la duración especificada
        # (en segundos), adquiriendo muestras a una tasa de 1000 muestras por segundo.
        # El modo de muestra es FINITE, lo que significa que la tarea se detendrá
        # automáticamente después de adquirir un número específico de muestras.
        task.timing.cfg_samp_clk_timing(
            rate=1000, 
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE, 
            samps_per_chan=duration*1000, 
            source="OnboardClock"
        )
        
        # Se inicia la tarea.
        task.start()
        
        # Se espera hasta que la tarea haya terminado de adquirir muestras.
        task.wait_until_done()


# Función para que todas las líneas de salida estén a 0. 
# Pensado para ser usado en una función mayor, la cual ponga
# todas las salidas a un estado seguro y conocido. 
# No he encontrado nada que haga esto de una manera mejor/más optimizada.

def all_digital_safe(device_name):
    # Dado un device_name se recibe una lista con todas las líneas de salida
    available_channels = nidaqmx.system._collections.physical_channel_collection.DOLinesCollection(device_name)
    # Por cada canal en la lista cambiar el tipo a string para poder dividirlo y conseguir sólo el nombre
    for channel in available_channels:
        channel_name = str(channel).split('=')[1][:-1]
        # Una vez con el nombre de cada canal se ponen a 0 uno a uno
        set_voltage_digital(channel_name, False)



# Función para que todos los canales analógicos de salida estén a 0. 
# Pensado para ser usado en una función mayor, la cual ponga
# todas las salidas a un estado seguro y conocido. 
# Devuelve un array con los voltajes puestos.

def all_analogic_safe(device_name):
    voltajes = []
    for i in range(2):
        voltajes.append(set_voltage_analogic((device_name+"/ao{}".format(i)),0))      
    return voltajes
    


# Acceso al voltaje del canal analógico de entrada. 
# chan_a tiene el formato " "Dev/aiX" "

def get_voltage_analogic(chan_a):
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(chan_a, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        # Leer el voltaje actual del canal ai0 10 veces
        voltages = task.read(number_of_samples_per_channel=10)
        # Calcular la media de los valores leídos
        mean_voltage = sum(voltages)/len(voltages)
        return mean_voltage
    
    
    


# Acceso al voltaje del canal digital. 
# chan_d tiene el formato " "Dev/portX/lineY" "

def get_state_digital(chan_d):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d)
        state = task.read()
        return state


# Cambios de voltaje de un canal análogico.
# chan_a tiene el formato " "Dev/aoX" "
# Al no poder leerse el voltaje (por ser de salida), por si 
# se necesita saber algún cambio se fuerza a que devuelva el voltaje

def set_voltage_analogic(chan_a, voltage):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(chan_a) # Especificar la salida analógica chanA del dispositivo DAQ
        task.write(voltage, auto_start=True) # Establecer el voltaje en chanA
        return voltage
        


# Cambios de voltaje de un canal digital.
# chan_d tiene el formato " "Dev/portX/lineY" "
        
def set_voltage_digital(chan_d, voltage):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d) # Especificar la salida digital X.Y del dispositivo DAQ
        task.write(voltage) # Establecer el voltaje en el canal digital
        
        
        
# Función que va a servir para establecer un voltaje seguro
# y conocido en todas las salidas.
# Recomiendado el uso para iniciar y finalizar el programar       
        
def safe_state(device_name):
    all_digital_safe(device_name)
    all_analogic_safe(device_name)
  

