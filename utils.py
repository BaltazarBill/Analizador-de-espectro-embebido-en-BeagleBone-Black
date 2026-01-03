/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este módulo (utils.py) proporciona funciones de utilidad matemática y de interfaz gráfica para el sistema.
 * Contiene algoritmos de Procesamiento Digital de Señales (DSP) para el suavizado de curvas espectrales
 * y herramientas de conversión de tipos de datos para la gestión de colores en la interfaz Qt.
 *
 * Funcionamiento general:
 * - La función de suavizado implementa una convolución discreta utilizando ventanas estándar (Hanning, Hamming, etc.)
 * para reducir el ruido de alta frecuencia en la visualización del espectro (FFT).
 * - Las funciones de color permiten serializar y deserializar objetos QColor a cadenas de texto, facilitando
 * el almacenamiento de la configuración de usuario en archivos o bases de datos.
 *
 * Notas importantes:
 * - El algoritmo de suavizado maneja los bordes de la señal mediante una extensión por reflexión especular
 * para evitar artefactos de borde durante la convolución.
 * ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

import numpy as np
from Qt import QtGui

# //===================================================================================================
# //=========================== FUNCIONES DE PROCESAMIENTO DE SEÑAL (DSP) =============================
# //===================================================================================================

def smooth(x, window_len=11, window='hanning'):
    """
    Realiza el suavizado de una señal 1D mediante convolución con una ventana específica.
    Este método es fundamental para mejorar la visualización de espectros ruidosos.

    Variables:
        - x: Array de entrada (la señal a suavizar).
        - window_len: Longitud de la ventana de suavizado (debe ser un entero impar).
        - window: Tipo de ventana ('rectangular', 'hanning', 'hamming', 'bartlett', 'blackman').

    Devuelve:
        - Un array de NumPy con la señal suavizada del mismo tamaño que la entrada.
    """
    # Asegurar que la entrada sea un array de NumPy para operaciones vectorizadas
    x = np.array(x)

    # Si la ventana es muy pequeña, el suavizado es despreciable o nulo; se retorna la original
    if window_len < 3:
        return x

    # Validación: La señal debe ser más grande que la ventana de convolución
    if x.size < window_len:
        raise ValueError("Input data length must be greater than window size")

    # Validación: El tipo de ventana debe ser uno de los soportados por NumPy o 'rectangular'
    if window not in ['rectangular', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window must be 'rectangular', 'hanning', 'hamming', 'bartlett' or 'blackman'")

    # --- Generación del Kernel (Ventana) ---
    if window == 'rectangular':
        # Ventana rectangular: Equivale a un promedio móvil (Moving Average)
        # Se crea un vector de unos.
        w = np.ones(window_len, 'd')
    else:
        # Ventanas apodizadas: Se obtiene la función correspondiente de la librería NumPy dinámicamente
        w = getattr(np, window)(window_len)

    # --- Tratamiento de Bordes (Padding) ---
    # Para evitar efectos de borde donde la convolución pierde datos o asume ceros,
    # se extiende la señal original en ambos extremos reflejándola (efecto espejo).
    # np.r_ concatena a lo largo del primer eje.
    # 2*x[0] - ... invierte la señal alrededor del punto inicial y final para continuidad de la derivada.
    s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

    # --- Convolución Discreta ---
    # Se realiza la convolución de la señal extendida 's' con la ventana normalizada 'w'.
    # La normalización (w / w.sum()) asegura que la amplitud/energía total de la señal se mantenga (ganancia unitaria).
    # mode='same' devuelve una salida del mismo tamaño que 's'.
    y = np.convolve(w / w.sum(), s, mode='same')

    # --- Recorte Final ---
    # Se recorta el resultado para eliminar los segmentos de padding agregados anteriormente,
    # devolviendo un array del mismo tamaño que el 'x' original.
    return y[window_len - 1:-window_len + 1]


# //===================================================================================================
# //=========================== FUNCIONES DE UTILIDAD PARA GUI (COLORES) ==============================
# //===================================================================================================

def str_to_color(color_string):
    """
    Convierte una cadena de texto con formato RGBA en un objeto QColor de Qt.
    Utilizada para restaurar configuraciones guardadas en archivos de texto/ini.

    Variables:
        - color_string: Cadena en formato "R, G, B, A" (ej. "255, 0, 0, 255").

    Devuelve:
        - Objeto QtGui.QColor inicializado.
    """
    # 1. split(','): Divide la cadena por comas.
    # 2. int(c.strip()): Elimina espacios y convierte cada componente a entero.
    # 3. *[...]: Desempaqueta la lista como argumentos para el constructor de QColor(r, g, b, a).
    return QtGui.QColor(*[int(c.strip()) for c in color_string.split(',')])


def color_to_str(color):
    """
    Serializa un objeto QColor de Qt a una cadena de texto formato RGBA.
    Utilizada para guardar la configuración de colores del usuario.

    Variables:
        - color: Objeto QtGui.QColor a convertir.

    Devuelve:
        - Cadena de texto "R, G, B, A".
    """
    # Se extraen los componentes Rojo, Verde, Azul y Alpha (Transparencia),
    # se convierten a string y se unen con comas.
    return ", ".join([str(color.red()), str(color.green()), str(color.blue()), str(color.alpha())])