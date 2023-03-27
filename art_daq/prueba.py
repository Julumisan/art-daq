# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 12:26:46 2023


Este Script va a ser el intento de librería Python de fácil
uso y acceso a las carecterísticas de la DAQ, en los que destaco:
    -Cambios de voltaje de las diferentes salidas.
    -Medidas de voltaje de las diferentes entradas.
    -Temporizador.
    -Una medición de voltaje falsa para poder testear sin necesidad de tarjeta
    -Posibilidad de elección automática de tarjeta con get_connected_device
    -Generación de ondas cuadradas/triangulares/sinusoidales


@author: Julu

@version: v1.0.0

Esta nueva versión cuenta con todas las funcionalidades previstas, comentarios
aclaratorios acerca del uso de las funciones, tanto de su función como de 
qué parámetros se usan y su formato.

"""



import nidaqmx
import time
import math



def measure_frequency(counter_channel: str, input_terminal: str, duration: float) -> float:
    """
    Esta función mide la frecuencia de una señal utilizando el contador.
    La función configura el contador para medir la frecuencia y conecta el
    terminal de entrada especificado a la señal que se desea medir. Después
    de medir la frecuencia durante la duración especificada, la función
    devuelve la frecuencia medida.
    
    @param counter_channel: el número del canal del contador a utilizar.
    @param input_terminal: el nombre del terminal de entrada al que está conectada la señal que se desea medir.
    @param duration: la duración de la medición de la frecuencia en segundos.
    
    @return: la frecuencia medida en Hz.
    
    """
    with nidaqmx.Task() as task:
        # Configurar la medida de frecuencia
        task.ci_channels.add_ci_freq_meas_chan(counter_channel,
                                               '',
                                               min_val=1.0,
                                               max_val=10000.0,
                                               edge=nidaqmx.constants.Edge.RISING,
                                               meas_method=nidaqmx.constants.AcquisitionType.FINITE,
                                               meas_time=duration,
                                               timeout=10000.0,
                                               units=nidaqmx.constantsTimeUnits.SECONDS,
                                               custom_scale_name='',
                                               divisor=4
                                               )
        
        # Conectar el terminal de entrada a la señal que se desea medir
        task.ci_channels.all.connect_terms(input_terminal, '')

        # Leer y retornar la frecuencia medida
        frequency = task.read()
        return frequency



def daq_timer(chan_a: str, duration: float) -> None:
    """
    Esta función configura una tarea de adquisición de datos que espera durante
    una cantidad de tiempo determinada.
    
    
    @param chan_a: el nombre del canal de entrada analógica.
    @param duration: la duración de la adquisición de datos en segundos.
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
    Función para que todas las líneas de salida estén a 0. 
    Pensado para ser usado en una función mayor, la cual ponga
    todas las salidas a un estado seguro y conocido. 
    
    
    @param device_name: el nombre del dispositivo DAQ.
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
    Función para que todos los canales analógicos de salida estén a 0. 
    Pensado para ser usado en una función mayor, la cual ponga
    todas las salidas a un estado seguro y conocido. 
    Devuelve un array con los voltajes puestos.
    
    
    @param device_name: el nombre del dispositivo DAQ.
    @return: un array de los voltajes puestos en los canales analógicos de salida del dispositivo.
    """
    voltajes = []
    for i in range(2):
        voltajes.append(set_voltage_analogic((device_name+"/ao{}".format(i)),0))      
    return voltajes
    


def get_voltage_analogic(chan_a: str) -> float:
    """
    Acceso al voltaje del canal analógico de entrada. 
    chan_a tiene el formato " "Dev/aiX" "
    
    
    @param chan_a: el identificador del canal analógico de entrada, en el formato "Dev/aiX".
    @return: el voltaje actual en el canal analógico de entrada.
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
    Acceso al estado del canal digital. 
    chan_d tiene el formato " "Dev/portX/lineY" "
    
    
    @param chan_d: el identificador del canal digital de salida, en el formato "Dev/portX/lineY".
    @return: el estado actual del canal digital de salida (True si está activado, False si está desactivado).
    """
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d)
        state = task.read()
        return state



def set_voltage_analogic(chan_a: str, voltage: float) -> float:
    """
    Cambios de voltaje de un canal análogico.
    chan_a tiene el formato " "Dev/aoX" "
    Al no poder leerse el voltaje (por ser de salida), por si 
    se necesita saber algún cambio se fuerza a que devuelva el voltaje
    
    
    @param chan_a: el identificador del canal analógico de salida, en el formato "Dev/aoX".
    @param voltage: el voltaje a establecer en el canal analógico de salida.
    @return: el voltaje establecido en el canal analógico de salida.
    """
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(chan_a) # Especificar la salida analógica chanA del dispositivo DAQ
        task.write(voltage, auto_start=True) # Establecer el voltaje en chanA
        return voltage



def set_voltage_digital(chan_d: str, voltage: bool) -> None:
    """
    Cambios de voltaje de un canal digital.
    chan_d tiene el formato " "Dev/portX/lineY" "
    
    
    @param chan_d: el identificador del canal digital de salida, en el formato "Dev/portX/lineY".
    @param voltage: el estado a establecer en el canal digital de salida (True para encender, False para apagar).
    """   
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(chan_d) # Especificar la salida digital X.Y del dispositivo DAQ
        task.write(voltage) # Establecer el voltaje en el canal digital
        
    
        
def safe_state(device_name: str) -> None:
    """
    Función que va a servir para establecer un voltaje seguro y conocido en todas las salidas.
    Recomiendado el uso para iniciar y finalizar el programa.
    
    
    @param device_name: el nombre del dispositivo NI.
    """
    all_digital_safe(device_name)
    all_analogic_safe(device_name)
  
   
  
def get_connected_devices() -> list:
    """
    Función que crea una instancia de la clase nidaqmx.system.System que representa el
    sistema local. Luego, recopila los nombres de todos los dispositivos NI conectados
    en una lista llamada connected_devices y la devuelve.
    
    
    La función no recibe argumentos.
    @return: una lista de los nombres de todos los dispositivos NI conectados al sistema local.
    """
    system = nidaqmx.system.System.local()
    connected_devices = [dev.name for dev in system.devices]
    return connected_devices



def get_connected_device() -> str:
    """
    Función que crea una instancia de la función get_connected_devices() para comprobar
    que solo haya un device conectado, y, si lo hay, se devuelve. 
    Utilidad: No necesidad de interacción humana por si cambia el devicename.
    
    
    La función no recibe argumentos.

    @return: el nombre del único dispositivo NI conectado al sistema local, o None si no se detectó exactamente un 
         dispositivo.
    """
    listDev = get_connected_devices()
    if len(listDev) == 1:
        return listDev[0]
    else:
        print("Se necesita acción programativa")
        


def generate_square_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float) -> None:
    """
    Genera una onda cuadrada de la frecuencia y amplitud especificadas en el canal analógico de salida especificado en el 
    dispositivo NI especificado durante la duración especificada.

    La función recibe el nombre del dispositivo NI, el número del canal analógico de salida, la frecuencia de la onda 
    cuadrada, la amplitud de la onda cuadrada y la duración durante la cual se generará la onda cuadrada. No devuelve nada.

    @param device_name: el nombre del dispositivo NI.
    @param ao_channel: el número del canal analógico de salida.
    @param frequency: la frecuencia de la onda cuadrada en Hz.
    @param amplitude: la amplitud de la onda cuadrada en voltios.
    @param duration: la duración durante la cual se generará la onda cuadrada en segundos.
    """
    chan_a = f"{device_name}/ao{ao_channel}"
    
    period = 1 / frequency
    half_period = period / 2

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < duration:
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
        
        
        
def generate_triangle_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float, steps: int = 100) -> None:
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

    while current_time - start_time < duration:
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
        


def generate_sine_wave(device_name: str, ao_channel: int, frequency: float, amplitude: float, duration: float) -> None:
    """
    Genera una señal sinusoidal en el canal de salida analógica especificado durante la duración especificada.
    El voltaje sinusoidal se calcula en función del tiempo utilizando la frecuencia y la amplitud especificadas.
    
    @param device_name: el nombre del dispositivo DAQ.
    @param ao_channel: el número del canal de salida analógica en el que se generará la señal.
    @param frequency: la frecuencia de la señal sinusoidal en Hz.
    @param amplitude: la amplitud máxima de la señal sinusoidal en V.
    @param duration: la duración de la señal sinusoidal en segundos.
    """
    # NI PRECISO, NI ESTABLE. PARA ESTE TIPO DE SEÑALES MEJOR UN DAQ QUE PUEDA HACERLO
    # CONSUME MUCHA CPU debido a la creación y destrucción de tareas
    # en cada iteración del bucle.
    
    # Construir el nombre del canal de salida analógica
    chan_a = f"{device_name}/ao{ao_channel}"
    
    start_time = time.time()
    current_time = start_time

    while current_time - start_time < duration:
        # Calcular el voltaje sinusoidal en función del tiempo
        elapsed_time = current_time - start_time
        voltage = amplitude * math.sin(2 * math.pi * frequency * elapsed_time)
        
        # Establecer el voltaje en el canal de salida analógica
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(chan_a)
            task.write(voltage)
        
        # Esperar un corto período de tiempo antes de actualizar el voltaje nuevamente
        time.sleep(0.001)  # 1 ms
        current_time = time.time()