# art-daq
Librería dedicada al uso de la tarjeta USB-6001. Se pretende que sea una librería de uso sencillo y accesible.  
Library dedicated to the use of the USB-6001 daq. It is intended to be a simple and accessible library.  

La instalación de este paquete se puede realizar a través del comando pip install art-daq. Si se necesita actualizarla, se usará el comando pip install --upgrade art-daq. 
Para poder usar este paquete se usará la estructura "from art_daq import prueba".   
The installation of this package can be done through the pip install art-daq command. If you need to upgrade it, use the command pip install --upgrade art-daq.   
In order to use this package the structure "from art_daq import prueba" will be used.

La siguiente es una lista de las funciones que se encuentran en este paquete:

    get_voltage_analogic(chan_a): lee el voltaje actual del canal analógico especificado en el parámetro chan_a.
    get_state_digital(chan_d): lee el estado actual del canal digital especificado en el parámetro chan_d.
    set_voltage_analogic(chan_a, voltage): establece el voltaje del canal analógico especificado en el parámetro chan_a en el valor especificado en el parámetro voltage (float).
    set_voltage_digital(chan_d, voltage): establece el voltaje del canal digital especificado en el parámetro chan_d en el valor especificado en el parámetro voltage (bool).
    daq_timer(chan_a, duration): configura una tarea de adquisición de datos que espera durante una cantidad de tiempo determinada.
    all_digital_safe(device_name): establece todas las líneas de salida a False.
    all_analogic_safe(device_name): configura todos los canales analógicos de salida a 0V.
    safe_state(device_name): establece un voltaje seguro en todas las salidas.

Además de estas funciones, también se incluyen las funciones para generar señales:

    generate_sine_wave(device_name, ao_channel, frequency, amplitude, duration): genera una señal sinusoidal con la frecuencia, amplitud y duración especificadas en los parámetros.
    generate_square_wave(device_name, ao_channel, frequency, amplitude, duration): genera una señal cuadrada con la frecuencia, amplitud y duración especificadas en los parámetros.
    generate_triangle_wave(device_name, ao_channel, frequency, amplitude, duration, steps=100): genera una señal triangular con la frecuencia, amplitud y duración especificadas en 
        los parámetros. El parámetro opcional "steps" especifica la cantidad de pasos en cada rampa de la señal triangular.

The following is a list of functions found in this package:

    get_voltage_analogic(chan_a): reads the current voltage of the specified analog channel in the chan_a parameter.
    get_state_digital(chan_d): reads the current state of the specified digital channel in the chan_d parameter.
    set_voltage_analogic(chan_a, voltage): sets the voltage of the specified analog channel in the chan_a parameter to the value specified in the voltage parameter (float).
    set_voltage_digital(chan_d, voltage): sets the voltage of the specified digital channel in the chan_d parameter to the value specified in the voltage parameter (bool).
    daq_timer(chan_a, duration): sets up a data acquisition task that waits for a specified amount of time.
    all_digital_safe(device_name): sets all output lines to False.
    all_analogic_safe(device_name): sets all analog output channels to 0V.
    safe_state(device_name): sets a safe voltage on all outputs.


In addition to these functions, the following functions for generating signals are also included:

    generate_sine_wave(device_name, ao_channel, frequency, amplitude, duration): generates a sine wave signal with the specified frequency, amplitude, and duration in the parameters.
    generate_square_wave(device_name, ao_channel, frequency, amplitude, duration): generates a square wave signal with the specified frequency, amplitude, and duration in the parameters.
    generate_triangle_wave(device_name, ao_channel, frequency, amplitude, duration, steps=100): generates a triangle wave signal with the specified frequency, amplitude, and duration in
        the parameters. The optional "steps" parameter specifies the number of steps in each ramp of the triangle signal.
