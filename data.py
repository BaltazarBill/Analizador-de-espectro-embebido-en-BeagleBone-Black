/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este módulo implementa la lógica central para el almacenamiento, procesamiento y gestión de buffers
 * de datos provenientes de un analizador de espectro. Utiliza estructuras eficientes (NumPy) para manejar
 * grandes volúmenes de datos en tiempo real y concurrencia mediante Qt (QThreadPool) para no bloquear la interfaz gráfica.
 *
 * Funcionamiento general:
 * 1. Recepción de datos: La clase DataStorage recibe datos crudos (PSD - Power Spectral Density).
 * 2. Buffer Circular: Se utiliza la clase HistoryBuffer para mantener un historial deslizante (waterfall).
 * 3. Procesamiento concurrente: Las tareas pesadas (actualización de historial, cálculos matemáticos) se delegan
 * a hilos trabajadores (Workers) mediante QRunnable y QThreadPool.
 * 4. Operaciones matemáticas: Se calculan en tiempo real el promedio (Average), retención de picos (Max/Min Hold)
 * y suavizado de señal (Smoothing).
 * 5. Señalización: El sistema emite señales (Signals) de Qt cuando los datos están listos para ser graficados.
 *
 * Notas importantes:
 * - Se hace uso intensivo de NumPy para vectorización y rendimiento.
 * - El sistema implementa un mecanismo de "Baseline Subtraction" para calibración de piso de ruido.
 ****************************************************************************************************************************/

//===================================================================================================
//===================================== IMPORTS / LIBRERÍAS =========================================
//===================================================================================================

import time, sys, os

# Importación de Qt a través de un wrapper para compatibilidad (PyQt/PySide)
from Qt import QtCore
import numpy as np

# Importaciones específicas del paquete qspectrumanalyzer para utilidades matemáticas y backend
from qspectrumanalyzer.utils import smooth
from qspectrumanalyzer.backends import soapy_power


//===================================================================================================
//================================ CLASES DE ESTRUCTURAS DE DATOS ===================================
//===================================================================================================

class HistoryBuffer:
    """
    Buffer circular (Ring Buffer) de tamaño fijo implementado sobre arreglos de NumPy.
    Se utiliza principalmente para almacenar el historial de espectros para el gráfico de cascada (Waterfall).
    """
    def __init__(self, data_size, max_history_size, dtype=float):
        """
        Constructor del Buffer Circular.
        
        Variables:
            - data_size: Número de bins (puntos de frecuencia) por muestra.
            - max_history_size: Cantidad máxima de filas (tiempo) que almacenará el buffer.
            - buffer: Matriz Numpy pre-asignada para evitar reallocations dinámicos costosos.
        """
        self.data_size = data_size
        self.max_history_size = max_history_size
        self.history_size = 0
        self.counter = 0
        # Inicialización de la matriz vacía con las dimensiones especificadas
        self.buffer = np.empty(shape=(max_history_size, data_size), dtype=dtype)

    def append(self, data):
        """
        Agrega nuevos datos al buffer circular.
        
        Funcionamiento:
            - Desplaza (roll) todo el array una posición hacia "atrás".
            - Inserta los nuevos datos en la última posición.
            - Mantiene un contador del llenado real del buffer.
        """
        self.counter += 1
        # Incrementa el tamaño lógico hasta alcanzar la capacidad máxima física
        if self.history_size < self.max_history_size:
            self.history_size += 1
        
        # Desplazamiento eficiente de memoria en el eje 0 (filas)
        # np.roll mueve los elementos: el primero pasa al final, pero luego sobrescribimos el final.
        self.buffer = np.roll(self.buffer, -1, axis=0)
        self.buffer[-1] = data

    def get_buffer(self):
        """
        Retorna el buffer recortado al tamaño de los datos reales disponibles.
        
        Devuelve:
            - Un slice del array numpy conteniendo solo los datos válidos si el buffer no está lleno.
            - El buffer completo si ya se alcanzó la capacidad máxima.
        """
        if self.history_size < self.max_history_size:
            # Retorna solo las últimas 'history_size' filas
            return self.buffer[-self.history_size:]
        else:
            return self.buffer

    def __getitem__(self, key):
        """Sobrecarga del operador de indexación [] para acceso directo al buffer numpy."""
        return self.buffer[key]


//===================================================================================================
//================================ CLASES PARA MANEJO DE HILOS ======================================
//===================================================================================================

class TaskSignals(QtCore.QObject):
    """
    Clase contenedora de señales para las tareas asíncronas.
    Necesaria porque QRunnable no hereda de QObject y no puede emitir señales directamente.
    """
    result = QtCore.Signal(object)


class Task(QtCore.QRunnable):
    """
    Tarea ejecutable en un hilo (Worker Thread).
    Diseñada para ser lanzada dentro de un QThreadPool.
    """
    def __init__(self, task, *args, **kwargs):
        """
        Prepara la tarea con la función a ejecutar y sus argumentos.
        
        Variables:
            - task: La función o método a ejecutar.
            - args, kwargs: Argumentos para dicha función.
        """
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()

    def run(self):
        """
        Método ejecutado automáticamente por el QThreadPool.
        Corre la función objetivo y emite el resultado mediante una señal.
        """
        #print('Running', self.task, 'in thread', QtCore.QThread.currentThreadId())
        result = self.task(*self.args, **self.kwargs)
        self.signals.result.emit(result)


//===================================================================================================
//=============================== LÓGICA PRINCIPAL DE ALMACENAMIENTO ================================
//===================================================================================================

class DataStorage(QtCore.QObject):
    """
    Clase principal para el almacenamiento y procesamiento de mediciones espectrales.
    Actúa como el modelo de datos en la arquitectura, gestionando el estado, 
    el historial y los cálculos estadísticos.
    """
    
    # Definición de señales Qt para notificar actualizaciones a la GUI
    history_updated = QtCore.Signal(object)       # Historial (waterfall) actualizado
    data_updated = QtCore.Signal(object)          # Datos principales actualizados
    history_recalculated = QtCore.Signal(object)  # Historial recalculado (ej. cambio de baseline)
    data_recalculated = QtCore.Signal(object)     # Datos actuales recalculados
    average_updated = QtCore.Signal(object)       # Promedio actualizado
    baseline_updated = QtCore.Signal(object)      # Línea base actualizada
    peak_hold_max_updated = QtCore.Signal(object) # Pico máximo retenido actualizado
    peak_hold_min_updated = QtCore.Signal(object) # Pico mínimo retenido actualizado

    def __init__(self, max_history_size=100, parent=None):
        """
        Inicializa el almacenamiento de datos y el pool de hilos.
        """
        super().__init__(parent)
        self.max_history_size = max_history_size
        
        # Parámetros de configuración de procesamiento
        self.smooth = False
        self.smooth_length = 11
        self.smooth_window = "hanning"
        self.subtract_baseline = False
        self.prev_baseline = None
        self.baseline = None
        self.baseline_x = None

        # Configuración del ThreadPool.
        # Se limita a 1 hilo porque para operaciones vectorizadas (NumPy) y la sobrecarga de GIL (Python),
        # usar más hilos a menudo incrementa el consumo de memoria sin mejorar significativamente la velocidad.
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.reset()

    def reset(self):
        """Reinicia todos los datos, incluyendo ejes y buffers históricos."""
        self.wait() # Esperar a que terminen tareas pendientes
        self.x = None
        self.history = None
        self.reset_data()

    def reset_data(self):
        """Reinicia solo los datos estadísticos actuales (Promedios, Picos), manteniendo configuración."""
        self.wait()
        self.y = None
        self.average_counter = 0
        self.average = None
        self.peak_hold_max = None
        self.peak_hold_min = None

    def start_task(self, fn, *args, **kwargs):
        """
        Lanza una función para ser ejecutada asíncronamente en el pool de hilos.
        Ayuda a mantener la interfaz gráfica fluida (non-blocking).
        """
        task = Task(fn, *args, **kwargs)
        self.threadpool.start(task)

    def wait(self):
        """Bloquea la ejecución hasta que todos los hilos trabajadores terminen sus tareas."""
        self.threadpool.waitForDone()

    def update(self, data):
        """
        Método principal de entrada de datos. Recibe un diccionario con 'x' (frecuencias) e 'y' (potencias).
        
        Proceso:
            1. Validación de dimensiones.
            2. Asignación inicial de eje X.
            3. Resta de línea base (Baseline subtraction) si está activa.
            4. Lanzamiento de tareas asíncronas para actualizar historial y métricas.
        """
        # Validación de consistencia en el tamaño de los datos
        if self.y is not None and len(data["y"]) != len(self.y):
            print("{:d} bins coming from backend, expected {:d}".format(len(data["y"]), len(self.y)))
            return

        self.average_counter += 1

        # Inicialización del eje de frecuencias si es la primera ejecución
        if self.x is None:
            self.x = data["x"]

        # Resta de la línea base (calibración) a los datos entrantes
        data["y"] = np.asarray(data["y"])
        if self.subtract_baseline and self.baseline is not None and len(data["y"]) == len(self.baseline):
            data["y"] -= self.baseline

        # Despacho de tareas paralelas
        self.start_task(self.update_history, data.copy())
        self.start_task(self.update_data, data)

    def update_data(self, data):
        """
        Actualiza los datos del espectro principal y aplica suavizado si es necesario.
        Se ejecuta en un hilo separado.
        """
        if self.smooth:
            data["y"] = self.smooth_data(data["y"])

        self.y = data["y"]
        self.data_updated.emit(self)

        # Lanzar actualizaciones de sub-procesos estadísticos
        self.start_task(self.update_average, data)
        self.start_task(self.update_peak_hold_max, data)
        self.start_task(self.update_peak_hold_min, data)

    def update_history(self, data):
        """
        Actualiza el buffer circular de historial.
        Si el buffer no existe, lo crea con las dimensiones de los datos entrantes.
        """
        if self.history is None:
            self.history = HistoryBuffer(len(data["y"]), self.max_history_size)

        self.history.append(data["y"])
        self.history_updated.emit(self)

    def update_average(self, data):
        """
        Actualiza el cálculo del promedio acumulativo.
        Utiliza promedio ponderado para incorporar la nueva muestra al promedio histórico.
        """
        if self.average is None:
            self.average = data["y"].copy()
        else:
            # Cálculo de promedio iterativo: (Promedio_anterior * N + Nuevo_dato) / (N + 1)
            self.average = np.average((self.average, data["y"]), axis=0, weights=(self.average_counter - 1, 1))
            self.average_updated.emit(self)

    def update_peak_hold_max(self, data):
        """Actualiza la retención de picos máximos (Max Hold) comparando elemento a elemento."""
        if self.peak_hold_max is None:
            self.peak_hold_max = data["y"].copy()
        else:
            self.peak_hold_max = np.maximum(self.peak_hold_max, data["y"])
            self.peak_hold_max_updated.emit(self)

    def update_peak_hold_min(self, data):
        """Actualiza la retención de picos mínimos (Min Hold) comparando elemento a elemento."""
        if self.peak_hold_min is None:
            self.peak_hold_min = data["y"].copy()
        else:
            self.peak_hold_min = np.minimum(self.peak_hold_min, data["y"])
            self.peak_hold_min_updated.emit(self)

    def smooth_data(self, y):
        """Aplica la función de suavizado (convolución con ventana) a los datos."""
        return smooth(y, window_len=self.smooth_length, window=self.smooth_window)

    def set_smooth(self, toggle, length=11, window="hanning", **kwargs):
        """
        Activa/desactiva el suavizado y configura sus parámetros.
        Si hay cambios, dispara un recálculo de los datos actuales.
        """
        if toggle != self.smooth or length != self.smooth_length or window != self.smooth_window:
            self.smooth = toggle
            self.smooth_length = length
            self.smooth_window = window
            self.start_task(self.recalculate_data)

    def set_subtract_baseline(self, toggle, baseline_file=None):
        """
        Activa/desactiva la resta de línea base y carga el archivo de referencia si se provee.
        """
        baseline = None
        baseline_x = None

        # Carga la línea base desde archivo (calcula promedio si hay múltiples trazas)
        if baseline_file and os.path.isfile(baseline_file):
            average_counter = 0
            with open(baseline_file, 'rb') as f:
                for data in soapy_power.read_from_file(f):
                    average_counter += 1
                    if baseline is None:
                        baseline = data['y'].copy()
                        baseline_x = data['x'].copy()
                    else:
                        baseline = np.average((baseline, data['y']), axis=0, weights=(average_counter - 1, 1))

        # Validación: No restar si el número de bins no coincide
        if self.y is not None and baseline is not None and len(self.y) != len(baseline):
            print("Can't subtract baseline (expected {:d} bins, but baseline has {:d} bins)".format(
                len(self.y), len(baseline)
            ))
            #baseline = None

        # Guardar la baseline anterior para poder restaurar los datos si se desactiva
        if self.subtract_baseline:
            self.prev_baseline = self.baseline

        #if not np.array_equal(baseline, self.baseline):
        self.baseline = baseline
        self.baseline_x = baseline_x
        self.baseline_updated.emit(self)

        self.subtract_baseline = toggle
        self.start_task(self.recalculate_history)
        self.start_task(self.recalculate_data)

    def recalculate_history(self):
        """
        Recalcula todo el historial de mediciones.
        Útil cuando se activa/desactiva la resta de línea base para corregir los datos pasados.
        """
        if self.history is None:
            return

        history = self.history.get_buffer()
        # Restaurar datos originales sumando la baseline previa si existía
        if self.prev_baseline is not None and len(history[-1]) == len(self.prev_baseline):
            history += self.prev_baseline
            self.prev_baseline = None
        # Aplicar la nueva baseline restándola
        if self.subtract_baseline and self.baseline is not None and len(history[-1]) == len(self.baseline):
            history -= self.baseline

        self.history_recalculated.emit(self)

    def recalculate_data(self):
        """
        Recalcula los datos actuales y estadísticos (Avg, Max, Min) basándose en el historial.
        Se utiliza cuando cambian parámetros de post-procesamiento (suavizado o baseline).
        """
        if self.history is None:
            return

        history = self.history.get_buffer()
        
        if self.smooth:
            # Si hay suavizado, aplicarlo a la última muestra y reconstruir estadísticas suavizadas
            self.y = self.smooth_data(history[-1])
            self.average_counter = 0
            self.average = self.y.copy()
            self.peak_hold_max = self.y.copy()
            self.peak_hold_min = self.y.copy()
            
            # Recorrer el historial para reconstruir los promedios y picos con los datos suavizados
            for y in history[:-1]:
                self.average_counter += 1
                y = self.smooth_data(y)
                self.average = np.average((self.average, y), axis=0, weights=(self.average_counter - 1, 1))
                self.peak_hold_max = np.maximum(self.peak_hold_max, y)
                self.peak_hold_min = np.minimum(self.peak_hold_min, y)
        else:
            # Sin suavizado, cálculo directo vectorizado sobre el buffer histórico
            self.y = history[-1]
            self.average_counter = self.history.history_size
            self.average = np.average(history, axis=0)
            self.peak_hold_max = history.max(axis=0)
            self.peak_hold_min = history.min(axis=0)

        self.data_recalculated.emit(self)
        # Líneas comentadas originales para debug o futuras implementaciones
        #self.data_updated.emit({"x": self.x, "y": self.y})
        #self.average_updated.emit({"x": self.x, "y": self.average})
        #self.peak_hold_max_updated.emit({"x": self.x, "y": self.peak_hold_max})
        #self.peak_hold_min_updated.emit({"x": self.x, "y": self.peak_hold_min})


//===================================================================================================
//===================================== CLASE DE PRUEBAS / TEST =====================================
//===================================================================================================

class Test:
    """
    Clase de prueba de rendimiento (Benchmark).
    Genera datos aleatorios y mide la velocidad de actualización (FPS) del DataStorage.
    """
    def __init__(self, data_size=100000, max_history_size=100):
        self.data_size = data_size
        self.data = {"x": np.arange(data_size),
                     "y": None}
        self.datastorage = DataStorage(max_history_size)

    def run_one(self):
        """Genera un set de datos aleatorios (distribución normal) y actualiza el storage."""
        self.data["y"] = np.random.normal(size=self.data_size)
        self.datastorage.update(self.data)

    def run(self, runs=1000):
        """
        Ejecuta el bucle de prueba y calcula métricas de tiempo.
        
        Variables:
            - runs: Número de iteraciones de prueba.
        """
        t = time.time()
        for i in range(runs):
            self.run_one()
        self.datastorage.wait() # Asegurar que el hilo termine antes de medir tiempo final
        total_time = time.time() - t
        print("Total time:", total_time)
        print("FPS:", runs / total_time)


//===================================================================================================
//===================================== FUNCIÓN PRINCIPAL / MAIN ====================================
//===================================================================================================

if __name__ == "__main__":
    # Punto de entrada para pruebas desde línea de comandos.
    # Argumentos esperados:
    # 1. Tamaño de datos (bins)
    # 2. Tamaño del historial
    # 3. Cantidad de corridas (runs)
    test = Test(int(sys.argv[1]), int(sys.argv[2]))
    test.run(int(sys.argv[3]))