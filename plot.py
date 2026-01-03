/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa
 * Este módulo gestiona la visualización gráfica de los datos espectrales procesados. Implementa widgets personalizados
 * basados en la librería PyQtGraph para renderizar gráficos de alta velocidad y bajo consumo de recursos, adecuados
 * para sistemas embebidos o estaciones de trabajo.
 *
 * Funcionamiento general:
 * - SpectrumPlotWidget: Renderiza la Densidad Espectral de Potencia (PSD) en 2D (Potencia vs Frecuencia).
 * Implementa capas visuales para trazas auxiliares: Max Hold, Min Hold, Promedio y Persistencia (fósforo digital).
 * - WaterfallPlotWidget: Renderiza un espectrograma o diagrama de cascada (Tiempo vs Frecuencia vs Potencia)
 * utilizando mapas de bits (ImageItems) y tablas de búsqueda de color (LUT) para representar la intensidad.
 * - El sistema utiliza un mecanismo de "SingleShot" de Qt para agendar actualizaciones en el bucle de eventos,
 * evitando bloqueos en la interfaz durante el redibujado intensivo.
 *
 * Notas importantes:
 * - Se utiliza 'Qt.py' para abstracción entre PySide2/PyQt5.
 * - El manejo de coordenadas y escalado es crítico en el Waterfall para alinear los bins de la FFT con el eje de frecuencia.
 ****************************************************************************************************************************/

//===================================================================================================
//===================================== IMPORTS / LIBRERÍAS =========================================
//===================================================================================================

import collections, math

from Qt import QtCore
import pyqtgraph as pg

# Configuración global de PyQtGraph
# Se activa el antialiasing para mejorar la calidad visual de las líneas, aunque consuma más GPU/CPU.
pg.setConfigOptions(antialias=True)


//===================================================================================================
//================================ CLASE DE GRÁFICO DE ESPECTRO 2D ==================================
//===================================================================================================

class SpectrumPlotWidget:
    """
    Widget principal para la visualización del espectro de frecuencia.
    Gestiona múltiples curvas (Traza principal, Promedio, Max/Min Hold, Persistencia) sobre un mismo eje.
    """

    def __init__(self, layout):
        """
        Constructor de la clase SpectrumPlotWidget.
        Inicializa las variables de estado visual y configura el lienzo de dibujo.

        Variables:
            - layout: Instancia de GraphicsLayoutWidget donde se insertará el gráfico.
            - persistence_*: Variables para controlar el efecto de persistencia visual (fósforo).
            - peak_hold_*: Variables para las trazas de retención de máximos y mínimos.
        """
        # Validación estricta del tipo de layout recibido para asegurar compatibilidad con PyQtGraph
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout

        # --- Configuración de Estado y Colores ---
        self.main_curve = True
        self.main_color = pg.mkColor("y") # Color Amarillo (Yellow)
        
        # Configuración de persistencia (efecto de decaimiento visual)
        self.persistence = False
        self.persistence_length = 5
        self.persistence_decay = "exponential"
        self.persistence_color = pg.mkColor("g") # Color Verde (Green)
        self.persistence_data = None
        self.persistence_curves = None

        # Configuración de herramientas de análisis
        self.peak_hold_max = False
        self.peak_hold_max_color = pg.mkColor("r") # Rojo
        self.peak_hold_min = False
        self.peak_hold_min_color = pg.mkColor("b") # Azul
        self.average = False
        self.average_color = pg.mkColor("c") # Cian

        # Inicialización de los elementos gráficos
        self.create_plot()

    def create_plot(self):
        """
        Crea y configura el objeto PlotItem principal dentro del layout.
        Define ejes, unidades, grillas y cursores.
        """
        # Etiqueta para mostrar coordenadas del cursor (Crosshair readout)
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        
        # Creación del gráfico en la grilla del layout
        self.plot = self.layout.addPlot(row=1, col=0)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLabel("left", "Power", units="dB")
        self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLimits(xMin=0) # La frecuencia no puede ser negativa
        self.plot.showButtons() # Muestra botón "A" para autoescala

        # Opciones comentadas para optimización en sistemas muy limitados:
        #self.plot.setDownsampling(mode="peak") # Reducción de puntos para renderizado rápido
        #self.plot.setClipToView(True) # No renderizar lo que está fuera del zoom

        # Creación de las curvas (objetos gráficos) en orden específico
        self.create_persistence_curves()
        self.create_average_curve()
        self.create_peak_hold_min_curve()
        self.create_peak_hold_max_curve()
        self.create_main_curve()

        # --- Configuración del Crosshair (Líneas cruzadas) ---
        # Línea vertical (frecuencia)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.vLine.setZValue(1000) # Z-index alto para estar siempre encima
        # Línea horizontal (potencia)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.vLine.setZValue(1000)
        
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)

        # Proxy para capturar eventos de movimiento del mouse sin saturar el procesador (Rate Limit)
        self.mouseProxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                         rateLimit=60, slot=self.mouse_moved)

    def create_main_curve(self):
        """Crea la curva principal de espectro (tiempo real)."""
        self.curve = self.plot.plot(pen=self.main_color)
        self.curve.setZValue(900) # Capa superior (debajo del crosshair)

    def create_peak_hold_max_curve(self):
        """Crea la curva de retención de pico máximo."""
        self.curve_peak_hold_max = self.plot.plot(pen=self.peak_hold_max_color)
        self.curve_peak_hold_max.setZValue(800)

    def create_peak_hold_min_curve(self):
        """Crea la curva de retención de pico mínimo."""
        self.curve_peak_hold_min = self.plot.plot(pen=self.peak_hold_min_color)
        self.curve_peak_hold_min.setZValue(800)

    def create_average_curve(self):
        """Crea la curva de promedio espectral."""
        self.curve_average = self.plot.plot(pen=self.average_color)
        self.curve_average.setZValue(700) # Capa inferior a los picos

    def create_persistence_curves(self):
        """
        Genera un conjunto de curvas para simular persistencia (fósforo digital).
        Cada curva representa un instante 't' pasado con una opacidad (alpha) decreciente.
        """
        z_index_base = 600
        decay = self.get_decay() # Obtiene función matemática de decaimiento
        self.persistence_curves = []
        
        for i in range(self.persistence_length):
            # Cálculo de canal Alpha (transparencia) basado en la antigüedad de la curva
            alpha = 255 * decay(i + 1, self.persistence_length + 1)
            color = self.persistence_color
            
            # Creación de curva con color RGBA
            curve = self.plot.plot(pen=(color.red(), color.green(), color.blue(), alpha))
            
            # Asignación de Z-Value decreciente para que las más antiguas queden al fondo
            curve.setZValue(z_index_base - i)
            self.persistence_curves.append(curve)

    def set_colors(self):
        """
        Aplica la configuración de colores actual a todos los objetos gráficos.
        Útil cuando el usuario cambia la paleta desde la configuración.
        """
        self.curve.setPen(self.main_color)
        self.curve_peak_hold_max.setPen(self.peak_hold_max_color)
        self.curve_peak_hold_min.setPen(self.peak_hold_min_color)
        self.curve_average.setPen(self.average_color)

        decay = self.get_decay()
        for i, curve in enumerate(self.persistence_curves):
            alpha = 255 * decay(i + 1, self.persistence_length + 1)
            color = self.persistence_color
            curve.setPen((color.red(), color.green(), color.blue(), alpha))

    # --- Funciones matemáticas de decaimiento para persistencia ---

    def decay_linear(self, x, length):
        """
        Calcula el factor de opacidad usando decaimiento lineal.
        Retorna valor entre 0.0 y 1.0.
        """
        return (-x / length) + 1

    def decay_exponential(self, x, length, const=1 / 3):
        """
        Calcula el factor de opacidad usando decaimiento exponencial (curva natural de fósforo).
        """
        return math.e**(-x / (length * const))

    def get_decay(self):
        """Selecciona la función de decaimiento activa según configuración."""
        if self.persistence_decay == 'exponential':
            return self.decay_exponential
        else:
            return self.decay_linear

    # --- Métodos de actualización de datos (Slots) ---

    def update_plot(self, data_storage, force=False):
        """
        Actualiza los datos de la curva principal.
        
        Variables:
            - data_storage: Objeto contenedor de datos (ejes x, y).
            - force: Booleano para forzar el redibujado de visibilidad.
        """
        if data_storage.x is None:
            return

        if self.main_curve or force:
            self.curve.setData(data_storage.x, data_storage.y)
            if force:
                self.curve.setVisible(self.main_curve)

    def update_peak_hold_max(self, data_storage, force=False):
        """Actualiza los datos de la curva Max Hold."""
        if data_storage.x is None:
            return

        if self.peak_hold_max or force:
            self.curve_peak_hold_max.setData(data_storage.x, data_storage.peak_hold_max)
            if force:
                self.curve_peak_hold_max.setVisible(self.peak_hold_max)

    def update_peak_hold_min(self, data_storage, force=False):
        """Actualiza los datos de la curva Min Hold."""
        if data_storage.x is None:
            return

        if self.peak_hold_min or force:
            self.curve_peak_hold_min.setData(data_storage.x, data_storage.peak_hold_min)
            if force:
                self.curve_peak_hold_min.setVisible(self.peak_hold_min)

    def update_average(self, data_storage, force=False):
        """Actualiza los datos de la curva Promedio."""
        if data_storage.x is None:
            return

        if self.average or force:
            self.curve_average.setData(data_storage.x, data_storage.average)
            if force:
                self.curve_average.setVisible(self.average)

    def update_persistence(self, data_storage, force=False):
        """
        Maneja la lógica del buffer de persistencia.
        Desplaza los datos antiguos y agrega el nuevo al principio (Deque).
        """
        if data_storage.x is None:
            return

        if self.persistence or force:
            # Inicialización del buffer si es la primera vez
            if self.persistence_data is None:
                self.persistence_data = collections.deque(maxlen=self.persistence_length)
            else:
                # Iterar sobre las curvas y asignar datos históricos
                for i, y in enumerate(self.persistence_data):
                    curve = self.persistence_curves[i]
                    curve.setData(data_storage.x, y)
                    if force:
                        curve.setVisible(self.persistence)
            # Agregar nuevos datos al buffer circular
            self.persistence_data.appendleft(data_storage.y)

    def recalculate_plot(self, data_storage):
        """
        Fuerza un redibujado completo de todas las curvas activas.
        Utiliza QTimer.singleShot(0, ...) para encolar la tarea en el Event Loop
        y evitar congelamiento de la UI.
        """
        if data_storage.x is None:
            return

        QtCore.QTimer.singleShot(0, lambda: self.update_plot(data_storage, force=True))
        QtCore.QTimer.singleShot(0, lambda: self.update_average(data_storage, force=True))
        QtCore.QTimer.singleShot(0, lambda: self.update_peak_hold_max(data_storage, force=True))
        QtCore.QTimer.singleShot(0, lambda: self.update_peak_hold_min(data_storage, force=True))

    def recalculate_persistence(self, data_storage):
        """
        Reconstruye el buffer de persistencia a partir del historial global de datos.
        Útil cuando se cambian parámetros de visualización (ej. longitud de suavizado).
        """
        if data_storage.x is None:
            return

        self.clear_persistence()
        self.persistence_data = collections.deque(maxlen=self.persistence_length)
        
        # Recuperar datos históricos del objeto DataStorage
        for i in range(min(self.persistence_length, data_storage.history.history_size - 1)):
            data = data_storage.history[-i - 2]
            if data_storage.smooth:
                data = data_storage.smooth_data(data)
            self.persistence_data.append(data)
            
        QtCore.QTimer.singleShot(0, lambda: self.update_persistence(data_storage, force=True))

    def mouse_moved(self, evt):
        """
        Slot ejecutado al mover el mouse sobre el gráfico.
        Actualiza la posición del Crosshair y la etiqueta de texto con valores reales.
        """
        pos = evt[0]
        # Verificar si el mouse está dentro del área de dibujo
        if self.plot.sceneBoundingRect().contains(pos):
            # Mapear coordenadas de escena (pixeles) a coordenadas de vista (MHz, dB)
            mousePoint = self.plot.vb.mapSceneToView(pos)
            self.posLabel.setText(
                "<span style='font-size: 12pt'>f={:0.3f} MHz, P={:0.3f} dB</span>".format(
                    mousePoint.x() / 1e6,
                    mousePoint.y()
                )
            )
            # Mover líneas guías
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    # --- Métodos de limpieza ---

    def clear_plot(self):
        """Limpia los datos de la curva principal."""
        self.curve.clear()

    def clear_peak_hold_max(self):
        """Limpia los datos de Max Hold."""
        self.curve_peak_hold_max.clear()

    def clear_peak_hold_min(self):
        """Limpia los datos de Min Hold."""
        self.curve_peak_hold_min.clear()

    def clear_average(self):
        """Limpia los datos de Promedio."""
        self.curve_average.clear()

    def clear_persistence(self):
        """Reinicia completamente el sistema de persistencia y sus curvas."""
        self.persistence_data = None
        for curve in self.persistence_curves:
            curve.clear()
            self.plot.removeItem(curve)
        self.create_persistence_curves()


//===================================================================================================
//================================ CLASE DE GRÁFICO DE CASCADA (WATERFALL) ==========================
//===================================================================================================

class WaterfallPlotWidget:
    """
    Widget para la visualización de espectrograma (Waterfall).
    Muestra la evolución del espectro en el tiempo usando un mapa de calor.
    """

    def __init__(self, layout, histogram_layout=None):
        """
        Constructor de la clase WaterfallPlotWidget.
        
        Variables:
            - layout: Layout gráfico principal.
            - histogram_layout: Layout opcional para la barra de control de gradiente (LUT).
            - history_size: Cantidad de líneas de tiempo a mostrar verticalmente.
        """
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        if histogram_layout and not isinstance(histogram_layout, pg.GraphicsLayoutWidget):
            raise ValueError("histogram_layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        self.histogram_layout = histogram_layout

        self.history_size = 100
        self.counter = 0

        self.create_plot()

    def create_plot(self):
        """
        Configura el PlotItem y el ImageItem para el Waterfall.
        También inicializa el histograma de control de niveles si está disponible.
        """
        self.plot = self.layout.addPlot()
        self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLabel("left", "Time") # Eje Y representa el historial temporal

        # Configuración de límites y rangos iniciales
        self.plot.setYRange(-self.history_size, 0)
        self.plot.setLimits(xMin=0, yMax=0)
        self.plot.showButtons()
        #self.plot.setAspectLocked(True) # Descomentar para relación 1:1 de pixeles

        # Optimizaciones opcionales:
        #self.plot.setDownsampling(mode="peak")
        #self.plot.setClipToView(True)

        # Configuración del widget de histograma (LUT - Look Up Table)
        # Permite al usuario ajustar el brillo/contraste y el mapa de colores (termal, llama, etc.)
        if self.histogram_layout:
            self.histogram = pg.HistogramLUTItem()
            self.histogram_layout.addItem(self.histogram)
            self.histogram.gradient.loadPreset("flame")
            # Rangos iniciales en dBm (ajustables por el usuario)
            #self.histogram.setHistogramRange(-50, 0)
            #self.histogram.setLevels(-50, 0)

    def update_plot(self, data_storage):
        """
        Actualiza el gráfico de cascada con una nueva línea de datos espectrales.
        
        Funcionamiento:
            - Si es la primera ejecución, escala y posiciona el ImageItem.
            - En cada ciclo, actualiza la imagen completa usando el buffer de historial transpuesto.
        """
        self.counter += 1

        # Inicialización del ImageItem en la primera actualización
        if self.counter == 1:
            self.waterfallImg = pg.ImageItem()
            # Escalar el eje X para que coincida con el ancho de banda real (Hz por bin)
            self.waterfallImg.scale((data_storage.x[-1] - data_storage.x[0]) / len(data_storage.x), 1)
            self.plot.clear()
            self.plot.addItem(self.waterfallImg)

        # Actualización de la imagen:
        # Se toman los últimos 'counter' datos del buffer, se transponen (.T) porque
        # ImageItem espera (x, y) pero el buffer está en (tiempo, frecuencia).
        self.waterfallImg.setImage(data_storage.history.buffer[-self.counter:].T,
                                   autoLevels=False, autoRange=False)

        # Desplazamiento de la imagen para simular el "scroll" hacia abajo
        # La posición Y se ajusta para que la línea nueva siempre esté en 0 o arriba.
        self.waterfallImg.setPos(
            data_storage.x[0],
            -self.counter if self.counter < self.history_size else -self.history_size
        )

        # Vincular el histograma a la imagen generada (solo una vez)
        if self.counter == 1 and self.histogram_layout:
            self.histogram.setImageItem(self.waterfallImg)

    def clear_plot(self):
        """Resetea el contador del Waterfall, limpiando efectivamente el historial visual."""
        self.counter = 0