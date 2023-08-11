# -*- coding: utf-8 -*-
"""
Created on Tue Mar 7 12:26:46 2023


Este Script es la librería Python de fácil
uso y acceso a las carecterísticas de la DAQ, en los que destaco:
    -Cambios de voltaje de las diferentes salidas.
    -Medidas de voltaje de las diferentes entradas.
    -Temporizador.
    -Posibilidad de elección automática de tarjeta con get_connected_device
    -Generación de ondas cuadradas/triangulares/sinusoidales


@author: Julu

@version: v2.3

Esta nueva versión cuenta con todas las funcionalidades previstas, comentarios
aclaratorios acerca del uso de las funciones, tanto de su función como de 
qué parámetros se usan y su formato.

"""



import nidaqmx
import time
import math



def measure_frequency(counter_channel: str, input_terminal: str, duration: float) -> float:
    """
    Mide la frecuencia de una señal utilizando el contador.

    Esta función configura el contador para medir la frecuencia y conecta el
    terminal de entrada especificado a la señal que se desea medir. Después
    de medir la frecuencia durante la duración especificada, la función
    devuelve la frecuencia medida.

    Args:
        counter_channel (str): El número del canal del contador a utilizar.
        input_terminal (str): El nombre del terminal de entrada al que está conectada la señal que se desea medir.
        duration (float): La duración de la medición de la frecuencia en segundos.

    Returns:
        float: La frecuencia medida en Hz.
    """
    with nidaqmx.Task() as task:
        # Configura la medida de frecuencia
        task.ci_channels.add_ci_freq_meas_chan(counter_channel,
                                               '',
                                               min_val=1.0,
                                               max_val=10000.0,
                                               edge=nidaqmx.constants.Edge.RISING,
                                               meas_method=nidaqmx.constants.AcquisitionType.FINITE,
                                               meas_time=duration,
                                               timeout=10000.0,
                                               units=nidaqmx.constants.TimeUnits.SECONDS,
                                               custom_scale_name='',
                                               divisor=4
                                               )
        
        # Conecta el terminal de entrada a la señal que se desea medir
        task.ci_channels.all.connect_terms(input_terminal, '')

        # Lee y retorna la frecuencia medida
        frequency = task.read()
        return frequency


def daq_timer(chan_a: str, duration: float) -> None:
    """
    Configura una tarea de adquisición de datos que espera durante una cantidad de tiempo determinada.

    Args:
        chan_a (str): El nombre del canal de entrada analógica.
        duration (float): La duración de la adquisición de datos en segundos.
    """
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


# No he encontrado nada que haga esto de una manera mejor/más optimizada.
def all_digital_safe(device_name: str) -> None:
    """
    Establece todas las líneas de salida de un dispositivo NI en 0. 
    Pensado para ser usado en una función mayor que establezca todas las salidas en un estado seguro y conocido.

    Args:
        device_name (str): El nombre del dispositivo DAQ.
    """
    # Dado un device_name se recibe una lista con todas las líneas de salida
    available_channels = nidaqmx.system._collections.physical_channel_collection.DOLinesCollection(device_name)
    # Por cada canal en la lista cambiar el tipo a string para poder dividirlo y conseguir sólo el nombre
    for channel in available_channels:
        channel_name = str(channel).split('=')[1][:-1]
        # Una vez con el nombre de cada canal se ponen a 0 uno a uno
        set_voltage_digital(channel_name, False)




def all_analogic_safe(device_name: str) -> list:
    """
    Establece todos los canales analógicos de salida de un dispositivo NI en 0. 
    Pensado para ser usado en una función mayor que establezca todas las salidas en un estado seguro y conocido.

    Args:
        device_name (str): El nombre del dispositivo DAQ.

    Returns:
        list: Un array de los voltajes establecidos en los canales analógicos de salida del dispositivo.
    """
    voltajes = []
    for i in range(2):
        voltajes.append(set_voltage_analogic((device_name+"/ao{}".format(i)),0))      
    return voltajes
    


def get_voltage_analogic(chan_a: str) -> float:
    """
    Accede al voltaje actual de un canal analógico de entrada especificado en el dispositivo NI.

    Args:
        chan_a (str): El identificador del canal analógico de entrada, en el formato "Dev/aiX".

    Returns:
        float: El voltaje actual en el canal analógico de entrada.
    """
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(chan_a, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        # Leer el voltaje actual del canal ai0 10 veces
        voltages = task.read(number_of_samples_per_channel=10)
        # Calcular la media de los valores leídos
        mean_voltage = sum(voltages)/len(voltages)
        return mean_voltage 



def get_state_digital(chan_d: str) -> bool:
    """
    Accede al estado actual de un canal digital de salida especificado en el dispositivo NI.

    Args:
        chan_d (str): El identificador del canal digital de salida, en el formato "Dev/portX/lineY".

    Returns:
        bool: El estado actual del canal digital de salida (True si está activado, False si está desactivado).
    """
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d)
        state = task.read()
        return state



def set_voltage_analogic(chan_a: str, voltage: float) -> float:
    """
    Establece el voltaje de un canal analógico de salida especificado en el dispositivo NI.

    Args:
        chan_a (str): El identificador del canal analógico de salida, en el formato "Dev/aoX".
        voltage (float): El voltaje a establecer en el canal analógico de salida.

    Returns:
        float: El voltaje establecido en el canal analógico de salida.
    """
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(chan_a) # Especificar la salida analógica chanA del dispositivo DAQ
        task.write(voltage, auto_start=True) # Establecer el voltaje en chanA
        return voltage



def set_voltage_digital(chan_d: str, voltage: bool) -> None:
    """
    Cambios de voltaje de un canal digital.
    chan_d tiene el formato " "Dev/portX/lineY" "
    
    Args:
        chan_d: el identificador del canal digital de salida, en el formato "Dev/portX/lineY".
        voltage: el estado a establecer en el canal digital de salida (True para encender, False para apagar).
    Returns:
        None
        
    """   
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d) # Especificar la salida digital X.Y del dispositivo DAQ
        task.write(voltage) # Establecer el voltaje en el canal digital
        
        
def read_digital_input(chan_d: str) -> bool:
    """
    Lee el estado de un canal digital de entrada.
    chan_d tiene el formato "Dev/portX/lineY"
    
    Args:
        chan_d: el identificador del canal digital de salida, en el formato "Dev/portX/lineY".
        
    Returns:
        bool: el estado del canal digital de entrada (True si está encendido, False si está apagado).
    """
    with nidaqmx.Task() as task:
        task.di_channels.add_di_chan(chan_d)  # Especificar la entrada digital X.Y del dispositivo DAQ
        return task.read()
        
    
        
def safe_state(device_name: str) -> None:
    """
    Establece un voltaje seguro y conocido en todas las salidas de un dispositivo NI. Se recomienda su uso para iniciar y
    finalizar el programa.

    Args:
        device_name (str): El nombre del dispositivo NI.
    """
    all_digital_safe(device_name)
    all_analogic_safe(device_name)
  
    
   
def get_connected_devices() -> list:
    """
    Crea una instancia de la clase nidaqmx.system.System que representa el sistema local. Luego, recopila los nombres de
    todos los dispositivos NI conectados en una lista llamada connected_devices y la devuelve.

    Returns:
        list: Una lista de los nombres de todos los dispositivos NI conectados al sistema local.
    """
    system = nidaqmx.system.System.local()
    connected_devices = [dev.name for dev in system.devices]
    return connected_devices


def get_connected_device() -> str:
    """
    Crea una instancia de la función get_connected_devices() para comprobar que solo hay un dispositivo conectado.
    Si hay exactamente un dispositivo conectado, devuelve su nombre.
    
    Utilidad: Permite automatizar la selección del dispositivo, sin necesidad de interacción humana en caso de cambio de 
    nombre del dispositivo.

    Returns:
        str: El nombre del único dispositivo NI conectado al sistema local, o None si no se detectó exactamente un 
        dispositivo.
    """
    list_dev = get_connected_devices()
    if len(list_dev) == 1:
        return list_dev[0]
    else:
        print("Se necesita acción programativa")
        


def generate_square_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float, end: bool) -> bool:
    """
    Genera una onda cuadrada de la frecuencia y amplitud especificadas en el canal analógico de salida especificado en el 
    dispositivo NI especificado durante la duración especificada.

    Args:
        device_name (str): El nombre del dispositivo NI.
        ao_channel (int): El número del canal analógico de salida.
        frequency (float): La frecuencia de la onda cuadrada en Hz.
        amplitude (float): La amplitud de la onda cuadrada en voltios.
        duration (float): La duración durante la cual se generará la onda cuadrada en segundos.

    Returns:
        bool: True cuando la señal acabe.

    Notas:
        Esta función establece el voltaje en la amplitud deseada durante la mitad del periodo de la onda cuadrada y
        en -amplitud durante la otra mitad. Luego espera la mitad del periodo antes de repetir. La implementación asume
        que el periodo es mayor que el tiempo de espera.

    """
    chan_a = f"{device_name}/ao{ao_channel}"
    
    period = 1 / frequency
    half_period = period / 2

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < duration and not end:
        # Establecer el voltaje en la amplitud deseada
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(chan_a)
            task.write(amplitude)
        
        time.sleep(half_period)
        
        # Establecer el voltaje en -amplitud
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(chan_a)
            task.write(-amplitude)
        
        time.sleep(half_period)
        
        current_time = time.time()
        
    return True
        
        
def generate_triangle_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float, steps: int = 100, end: bool) -> bool:
    """
    Genera una onda triangular de la frecuencia y amplitud especificadas en el canal de salida analógica especificado 
    en el dispositivo especificado durante el tiempo especificado. La onda se genera con el número especificado de 
    pasos y, por defecto, se usan 100 pasos para generar una onda suave.
    
    Args:
        device_name (str): Nombre del dispositivo DAQ.
        ao_channel (int): Canal de salida analógica.
        frequency (float): Frecuencia de la onda.
        amplitude (float): Amplitud de la onda.
        duration (float): Duración de la onda en segundos.
        steps (int, optional): Número de pasos para generar la onda triangular. Valor por defecto: 100.
        
    Returns:
        bool: True cuando la señal acabe.
        
    """
    
    # Obtener el nombre completo del canal de salida analógica
    chan_a = f"{device_name}/ao{ao_channel}"
    
    # Calcular la longitud del periodo y el tiempo que lleva dar un paso
    period = 1 / frequency
    step_time = period / steps
    
    # Calcular el cambio en voltaje por paso
    volt_step = 2 * amplitude / steps

    # Establecer el tiempo de inicio
    start_time = time.time()
    current_time = start_time

    while current_time - start_time < duration and not end:
        # Incrementar el voltaje en pasos
        for i in range(steps):
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(chan_a)
                task.write(-amplitude + i * volt_step)
            time.sleep(step_time)
        
        # Decrementar el voltaje en pasos
        for i in range(steps):
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(chan_a)
                task.write(amplitude - i * volt_step)
            time.sleep(step_time)
        
        # Actualizar el tiempo actual
        current_time = time.time()
        
        
    return True



def generate_sine_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float, steps: float, end: bool) -> bool:
    """
    Genera una señal sinusoidal en el canal de salida analógica especificado durante la duración especificada.
    El voltaje sinusoidal se calcula en función del tiempo utilizando la frecuencia y la amplitud especificadas.

    Args:
        device_name (str): El nombre del dispositivo DAQ.
        ao_channel (int): El número del canal de salida analógica en el que se generará la señal.
        frequency (float): La frecuencia de la señal sinusoidal en Hz.
        amplitude (float): La amplitud máxima de la señal sinusoidal en V.
        duration (float): La duración de la señal sinusoidal en segundos.

    Returns:
        bool: True cuando la señal acabe.

    Notas:
        Esta implementación no es precisa ni estable. Para este tipo de señales, se recomienda usar un DAQ que pueda
        manejarlas eficientemente. Esta implementación también consume mucha CPU debido a la creación y destrucción de
        tareas en cada iteración del bucle.
    """
    chan_a = f"{device_name}/ao{ao_channel}"

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < duration and not end:
        # Calcular el voltaje sinusoidal en función del tiempo
        elapsed_time = current_time - start_time
        voltage = amplitude * math.sin(2 * math.pi * frequency * elapsed_time)

        # Establecer el voltaje en el canal de salida analógica
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(chan_a)
            task.write(voltage)

        # Esperar un corto período de tiempo antes de actualizar el voltaje nuevamente
        time.sleep((1/steps))  # Depende del steps para ver la calidad de la señal
        current_time = time.time()
        
    return True