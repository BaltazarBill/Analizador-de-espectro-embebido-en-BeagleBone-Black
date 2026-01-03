#!/usr/bin/env python

/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este software implementa una interfaz gráfica de usuario (GUI) basada en Qt (PyQt/PySide) para el análisis
 * de espectro radioeléctrico. Utiliza backends como 'soapy_power' para la adquisición de datos desde hardware SDR
 * (Software Defined Radio), permitiendo visualizar la densidad espectral de potencia (PSD) en tiempo real,
 * así como diagramas de cascada (waterfall).
 *
 * Funcionamiento general:
 * 1. Inicialización: Se carga la aplicación Qt y se aplica un tema visual oscuro.
 * 2. Configuración: El usuario configura parámetros de RF (frecuencia de inicio/parada, ganancia, ancho de banda)
 * y parámetros de procesamiento (FFT, intervalos).
 * 3. Adquisición (PowerThread): Se lanza un hilo secundario que interactúa con el backend SDR para obtener muestras.
 * 4. Almacenamiento (DataStorage): Los datos crudos se procesan y almacenan en un objeto centralizado.
 * 5. Visualización: Mediante un sistema de Señales y Slots, la GUI actualiza los gráficos (Espectro y Cascada)
 * cada vez que DataStorage notifica nuevos datos procesados.
 * 6. Herramientas: Incluye funciones de suavizado, persistencia visual, promedios y retención de picos (Max/Min Hold).
 *
 * Notas importantes:
 * - Interfaz personalizada por el equipo: Bill, Cosso, Rodriguez, Yaconangelo.
 * - El sistema es agnóstico al binding de Qt gracias a la librería 'Qt.py'.
 * - Se implementa manejo de señales del sistema (SIGINT) para permitir el cierre limpio desde terminal.
 ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

import sys, signal, time, argparse

# Importación de componentes de Qt mediante el shim 'Qt.py' para compatibilidad entre versiones (PyQt5/PySide2)
from Qt import QtCore, QtGui, QtWidgets, __binding__

# Importaciones específicas del paquete qspectrumanalyzer
from qspectrumanalyzer import backends
from qspectrumanalyzer.version import __version__
from qspectrumanalyzer.data import DataStorage
from qspectrumanalyzer.plot import SpectrumPlotWidget, WaterfallPlotWidget
from qspectrumanalyzer.utils import color_to_str, str_to_color

# Importaciones de las interfaces de usuario generadas (archivos compilados desde .ui)
from qspectrumanalyzer.ui_qspectrumanalyzer_settings import Ui_QSpectrumAnalyzerSettings
from qspectrumanalyzer.ui_qspectrumanalyzer_settings_help import Ui_QSpectrumAnalyzerSettingsHelp
from qspectrumanalyzer.ui_qspectrumanalyzer_smooth import Ui_QSpectrumAnalyzerSmooth
from qspectrumanalyzer.ui_qspectrumanalyzer_persistence import Ui_QSpectrumAnalyzerPersistence
from qspectrumanalyzer.ui_qspectrumanalyzer_colors import Ui_QSpectrumAnalyzerColors
from qspectrumanalyzer.ui_qspectrumanalyzer import Ui_QSpectrumAnalyzerMainWindow

# //===================================================================================================
# //========================== DEFINICIÓN DE CONSTANTES Y GLOBALES ====================================
# //===================================================================================================

debug = False

# Permitir que CTRL+C y/o SIGTERM maten el proceso.
# Por defecto, PyQt bloquea estas señales, impidiendo detener el script desde la terminal.
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)


# //===================================================================================================
# //========================== CLASES DE DIÁLOGOS DE CONFIGURACIÓN ====================================
# //===================================================================================================

class QSpectrumAnalyzerSettings(QtWidgets.QDialog, Ui_QSpectrumAnalyzerSettings):
    """
    Clase que gestiona el cuadro de diálogo de configuración principal del analizador.
    Hereda de QDialog y de la interfaz gráfica Ui_QSpectrumAnalyzerSettings.
    """

    def __init__(self, parent=None):
        """
        Inicializa el diálogo de configuración, carga los valores guardados y configura los widgets.
        
        Variables utilizadas:
            - parent: Widget padre (opcional).
            - settings: Instancia de QSettings para persistencia de datos.
        """
        # Inicialización de la interfaz de usuario (UI)
        super().__init__(parent)
        self.setupUi(self)
        self.params_help_dialog = None
        self.device_help_dialog = None

        # Carga de configuraciones previas almacenadas en el sistema (Registro o archivo .ini)
        settings = QtCore.QSettings()
        self.executableEdit.setText(settings.value("executable", "soapy_power"))
        self.deviceEdit.setText(settings.value("device", ""))
        # Conversión de unidades: Hz a MHz para la visualización del usuario
        self.lnbSpinBox.setValue(settings.value("lnb_lo", 0, float) / 1e6)
        self.waterfallHistorySizeSpinBox.setValue(settings.value("waterfall_history_size", 100, int))

        # Determinación del backend a utilizar (ej. soapy_power)
        backend = settings.value("backend", "soapy_power")
        try:
            backend_module = getattr(backends, backend)
        except AttributeError:
            backend_module = backends.soapy_power

        # Configuración de parámetros adicionales y límites de los controles numéricos (SpinBoxes)
        self.paramsEdit.setText(settings.value("params", backend_module.Info.additional_params))
        self.deviceHelpButton.setEnabled(bool(backend_module.Info.help_device))

        self.sampleRateSpinBox.setMinimum(backend_module.Info.sample_rate_min / 1e6)
        self.sampleRateSpinBox.setMaximum(backend_module.Info.sample_rate_max / 1e6)
        self.sampleRateSpinBox.setValue(settings.value("sample_rate", backend_module.Info.sample_rate, float) / 1e6)

        self.bandwidthSpinBox.setMinimum(backend_module.Info.bandwidth_min / 1e6)
        self.bandwidthSpinBox.setMaximum(backend_module.Info.bandwidth_max / 1e6)
        self.bandwidthSpinBox.setValue(settings.value("bandwidth", backend_module.Info.bandwidth, float) / 1e6)

        # Poblado del ComboBox de backends disponibles
        self.backendComboBox.blockSignals(True)
        self.backendComboBox.clear()
        for b in sorted(backends.__all__):
            self.backendComboBox.addItem(b)

        # Seleccionar el backend actual en la lista
        i = self.backendComboBox.findText(backend)
        if i == -1:
            self.backendComboBox.setCurrentIndex(0)
        else:
            self.backendComboBox.setCurrentIndex(i)
        self.backendComboBox.blockSignals(False)

    @QtCore.Slot()
    def on_executableButton_clicked(self):
        """
        Slot activado al hacer clic en el botón de selección de ejecutable.
        Abre un explorador de archivos para buscar el binario del backend.
        """
        filename = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Select executable - QSpectrumAnalyzer"))[0]
        if filename:
            self.executableEdit.setText(filename)

    @QtCore.Slot()
    def on_paramsHelpButton_clicked(self):
        """
        Slot para mostrar ayuda sobre los parámetros adicionales del backend seleccionado.
        Abre una ventana de diálogo con la información técnica.
        """
        try:
            backend_module = getattr(backends, self.backendComboBox.currentText())
        except AttributeError:
            backend_module = backends.soapy_power

        self.params_help_dialog = QSpectrumAnalyzerSettingsHelp(
            backend_module.Info.help_params(self.executableEdit.text()),
            parent=self
        )

        self.params_help_dialog.show()
        self.params_help_dialog.raise_()
        self.params_help_dialog.activateWindow()

    @QtCore.Slot()
    def on_deviceHelpButton_clicked(self):
        """
        Slot para mostrar ayuda sobre la selección del dispositivo SDR.
        Útil para conocer los strings de identificación de hardware conectado.
        """
        try:
            backend_module = getattr(backends, self.backendComboBox.currentText())
        except AttributeError:
            backend_module = backends.soapy_power

        self.device_help_dialog = QSpectrumAnalyzerSettingsHelp(
            backend_module.Info.help_device(self.executableEdit.text(), self.deviceEdit.text()),
            parent=self
        )

        self.device_help_dialog.show()
        self.device_help_dialog.raise_()
        self.device_help_dialog.activateWindow()

    @QtCore.Slot(str)
    def on_backendComboBox_currentIndexChanged(self, text):
        """
        Slot activado al cambiar el backend en el ComboBox.
        Actualiza los límites y valores por defecto según las capacidades del nuevo backend.
        
        Variables:
            - text: Nombre del nuevo backend seleccionado.
        """
        self.executableEdit.setText(text)
        self.deviceEdit.setText("")

        try:
            backend_module = getattr(backends, text)
        except AttributeError:
            backend_module = backends.soapy_power

        # Actualización de UI con información del módulo backend
        self.paramsEdit.setText(backend_module.Info.additional_params)
        self.deviceHelpButton.setEnabled(bool(backend_module.Info.help_device))
        self.sampleRateSpinBox.setMinimum(backend_module.Info.sample_rate_min / 1e6)
        self.sampleRateSpinBox.setMaximum(backend_module.Info.sample_rate_max / 1e6)
        self.sampleRateSpinBox.setValue(backend_module.Info.sample_rate / 1e6)
        self.bandwidthSpinBox.setMinimum(backend_module.Info.bandwidth_min / 1e6)
        self.bandwidthSpinBox.setMaximum(backend_module.Info.bandwidth_max / 1e6)
        self.bandwidthSpinBox.setValue(backend_module.Info.bandwidth / 1e6)

    def accept(self):
        """
        Sobreescritura del método accept (OK).
        Guarda todos los valores configurados en QSettings antes de cerrar el diálogo.
        """
        settings = QtCore.QSettings()
        settings.setValue("backend", self.backendComboBox.currentText())
        settings.setValue("executable", self.executableEdit.text())
        settings.setValue("params", self.paramsEdit.text())
        settings.setValue("device", self.deviceEdit.text())
        # Guardar valores multiplicando por 1e6 para volver a Hz
        settings.setValue("sample_rate", self.sampleRateSpinBox.value() * 1e6)
        settings.setValue("bandwidth", self.bandwidthSpinBox.value() * 1e6)
        settings.setValue("lnb_lo", self.lnbSpinBox.value() * 1e6)
        settings.setValue("waterfall_history_size", self.waterfallHistorySizeSpinBox.value())
        QtWidgets.QDialog.accept(self)


class QSpectrumAnalyzerSettingsHelp(QtWidgets.QDialog, Ui_QSpectrumAnalyzerSettingsHelp):
    """
    Diálogo simple para mostrar texto de ayuda en formato monoespaciado.
    """
    def __init__(self, text, parent=None):
        """
        Inicializa el diálogo de ayuda con el texto proporcionado.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Configuración de fuente monoespaciada para correcta alineación de tablas/logs
        monospace_font = QtGui.QFont('monospace')
        monospace_font.setStyleHint(QtGui.QFont.Monospace)
        self.helpTextEdit.setFont(monospace_font)
        self.helpTextEdit.setPlainText(text)


class QSpectrumAnalyzerSmooth(QtWidgets.QDialog, Ui_QSpectrumAnalyzerSmooth):
    """
    Diálogo para configurar el suavizado (smoothing) del espectro.
    Permite elegir el tipo de ventana (Hanning, Hamming, etc.) y la longitud.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Cargar configuración previa
        settings = QtCore.QSettings()
        self.windowLengthSpinBox.setValue(settings.value("smooth_length", 11, int))

        window_function = settings.value("smooth_window", "hanning")
        i = self.windowFunctionComboBox.findText(window_function)
        if i == -1:
            self.windowFunctionComboBox.setCurrentIndex(0)
        else:
            self.windowFunctionComboBox.setCurrentIndex(i)

    def accept(self):
        """Guarda la configuración de suavizado al aceptar."""
        settings = QtCore.QSettings()
        settings.setValue("smooth_length", self.windowLengthSpinBox.value())
        settings.setValue("smooth_window", self.windowFunctionComboBox.currentText())
        QtWidgets.QDialog.accept(self)


class QSpectrumAnalyzerPersistence(QtWidgets.QDialog, Ui_QSpectrumAnalyzerPersistence):
    """
    Diálogo para configurar la persistencia visual del espectro.
    Define cómo decaen las señales antiguas en pantalla.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        settings = QtCore.QSettings()
        self.persistenceLengthSpinBox.setValue(settings.value("persistence_length", 5, int))

        decay_function = settings.value("persistence_decay", "exponential")
        i = self.decayFunctionComboBox.findText(decay_function)
        if i == -1:
            self.decayFunctionComboBox.setCurrentIndex(0)
        else:
            self.decayFunctionComboBox.setCurrentIndex(i)

    def accept(self):
        """Guarda la configuración de persistencia al aceptar."""
        settings = QtCore.QSettings()
        settings.setValue("persistence_length", self.persistenceLengthSpinBox.value())
        settings.setValue("persistence_decay", self.decayFunctionComboBox.currentText())
        QtWidgets.QDialog.accept(self)


class QSpectrumAnalyzerColors(QtWidgets.QDialog, Ui_QSpectrumAnalyzerColors):
    """
    Diálogo para personalizar los colores de las diferentes curvas del gráfico.
    (Curva principal, pico máximo, pico mínimo, promedio, persistencia).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Cargar colores guardados transformando el string "R,G,B,A" a objeto QColor
        settings = QtCore.QSettings()
        self.mainColorButton.setColor(str_to_color(settings.value("main_color", "255, 255, 0, 255")))
        self.peakHoldMaxColorButton.setColor(str_to_color(settings.value("peak_hold_max_color", "255, 0, 0, 255")))
        self.peakHoldMinColorButton.setColor(str_to_color(settings.value("peak_hold_min_color", "0, 0, 255, 255")))
        self.averageColorButton.setColor(str_to_color(settings.value("average_color", "0, 255, 255, 255")))
        self.persistenceColorButton.setColor(str_to_color(settings.value("persistence_color", "0, 255, 0, 255")))

    def accept(self):
        """Guarda los colores seleccionados transformando QColor a string."""
        settings = QtCore.QSettings()
        settings.setValue("main_color", color_to_str(self.mainColorButton.color()))
        settings.setValue("peak_hold_max_color", color_to_str(self.peakHoldMaxColorButton.color()))
        settings.setValue("peak_hold_min_color", color_to_str(self.peakHoldMinColorButton.color()))
        settings.setValue("average_color", color_to_str(self.averageColorButton.color()))
        settings.setValue("persistence_color", color_to_str(self.persistenceColorButton.color()))
        QtWidgets.QDialog.accept(self)


# //===================================================================================================
# //============================== CLASE PRINCIPAL / MAIN WINDOW ======================================
# //===================================================================================================

class QSpectrumAnalyzerMainWindow(QtWidgets.QMainWindow, Ui_QSpectrumAnalyzerMainWindow):
    """
    Ventana principal del analizador de espectro.
    Coordina la visualización, la configuración y el hilo de adquisición de datos.
    """
    def __init__(self, parent=None):
        """
        Constructor de la ventana principal.
        Inicializa la UI, los widgets de ploteo y el hilo de procesamiento.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Creación e inserción de los widgets gráficos personalizados
        self.spectrumPlotWidget = SpectrumPlotWidget(self.mainPlotLayout)
        self.waterfallPlotWidget = WaterfallPlotWidget(self.waterfallPlotLayout, self.histogramPlotLayout)

        # Vincular el eje X (Frecuencia) del plot principal con el de cascada para zoom sincronizado
        self.spectrumPlotWidget.plot.setXLink(self.waterfallPlotWidget.plot)

        # Inicialización de variables de estado y control
        self.prev_data_timestamp = None
        self.data_storage = None
        self.power_thread = None
        self.backend = None
        
        # Configuración inicial del hilo de adquisición
        self.setup_power_thread()

        self.update_buttons()
        self.load_settings()

    def setup_power_thread(self):
        """
        Configura el hilo de adquisición de potencia (PowerThread).
        Conecta las señales de 'DataStorage' con los slots de actualización de gráficos.
        Se llama al inicio o cuando se cambia la configuración del backend.
        """
        # Si el hilo ya existe, detenerlo antes de reconfigurar
        if self.power_thread:
            self.stop()

        settings = QtCore.QSettings()
        
        # Inicializar el almacenamiento de datos
        self.data_storage = DataStorage(max_history_size=settings.value("waterfall_history_size", 100, int))
        
        # --- CONEXIÓN DE SEÑALES Y SLOTS CRÍTICOS ---
        # Cuando hay nuevos datos -> Actualizar métricas, gráfico de espectro y persistencia
        self.data_storage.data_updated.connect(self.update_data)
        self.data_storage.data_updated.connect(self.spectrumPlotWidget.update_plot)
        self.data_storage.data_updated.connect(self.spectrumPlotWidget.update_persistence)
        
        # Cuando se recalculan datos (ej. cambio de suavizado) -> Refrescar gráficos
        self.data_storage.data_recalculated.connect(self.spectrumPlotWidget.recalculate_plot)
        self.data_storage.data_recalculated.connect(self.spectrumPlotWidget.recalculate_persistence)
        
        # Actualizaciones específicas de curvas auxiliares
        self.data_storage.history_updated.connect(self.waterfallPlotWidget.update_plot)
        self.data_storage.average_updated.connect(self.spectrumPlotWidget.update_average)
        self.data_storage.peak_hold_max_updated.connect(self.spectrumPlotWidget.update_peak_hold_max)
        self.data_storage.peak_hold_min_updated.connect(self.spectrumPlotWidget.update_peak_hold_min)

        # Obtener configuración del backend
        backend = settings.value("backend", "soapy_power")
        try:
            backend_module = getattr(backends, backend)
        except AttributeError:
            backend_module = backends.soapy_power

        # Si el backend cambió, actualizar los límites de los SpinBoxes según las capacidades del hardware
        if self.backend is None or backend != self.backend:
            self.backend = backend
            self.gainSpinBox.setMinimum(backend_module.Info.gain_min)
            self.gainSpinBox.setMaximum(backend_module.Info.gain_max)
            self.gainSpinBox.setValue(backend_module.Info.gain)
            
            self.startFreqSpinBox.setMinimum(backend_module.Info.start_freq_min)
            self.startFreqSpinBox.setMaximum(backend_module.Info.start_freq_max)
            self.startFreqSpinBox.setValue(backend_module.Info.start_freq)
            
            self.stopFreqSpinBox.setMinimum(backend_module.Info.stop_freq_min)
            self.stopFreqSpinBox.setMaximum(backend_module.Info.stop_freq_max)
            self.stopFreqSpinBox.setValue(backend_module.Info.stop_freq)
            
            self.binSizeSpinBox.setMinimum(backend_module.Info.bin_size_min)
            self.binSizeSpinBox.setMaximum(backend_module.Info.bin_size_max)
            self.binSizeSpinBox.setValue(backend_module.Info.bin_size)
            
            # Configuración de otros parámetros (intervalo, ppm, crop)
            self.intervalSpinBox.setMinimum(backend_module.Info.interval_min)
            self.intervalSpinBox.setMaximum(backend_module.Info.interval_max)
            self.intervalSpinBox.setValue(backend_module.Info.interval)
            self.ppmSpinBox.setMinimum(backend_module.Info.ppm_min)
            self.ppmSpinBox.setMaximum(backend_module.Info.ppm_max)
            self.ppmSpinBox.setValue(backend_module.Info.ppm)
            self.cropSpinBox.setMinimum(backend_module.Info.crop_min)
            self.cropSpinBox.setMaximum(backend_module.Info.crop_max)
            self.cropSpinBox.setValue(backend_module.Info.crop)

        # Ajuste de límites considerando el oscilador local del LNB (LNB LO)
        lnb_lo = settings.value("lnb_lo", 0, float) / 1e6

        start_freq_min = backend_module.Info.start_freq_min + lnb_lo
        start_freq_max = backend_module.Info.start_freq_max + lnb_lo
        start_freq = self.startFreqSpinBox.value()
        stop_freq_min = backend_module.Info.stop_freq_min + lnb_lo
        stop_freq_max = backend_module.Info.stop_freq_max + lnb_lo
        stop_freq = self.stopFreqSpinBox.value()

        # Validación final de rangos de frecuencia
        self.startFreqSpinBox.setMinimum(start_freq_min if start_freq_min > 0 else 0)
        self.startFreqSpinBox.setMaximum(start_freq_max)
        if start_freq < start_freq_min or start_freq > start_freq_max:
            self.startFreqSpinBox.setValue(start_freq_min)

        self.stopFreqSpinBox.setMinimum(stop_freq_min if stop_freq_min > 0 else 0)
        self.stopFreqSpinBox.setMaximum(stop_freq_max)
        if stop_freq < stop_freq_min or stop_freq > stop_freq_max:
            self.stopFreqSpinBox.setValue(stop_freq_max)

        # Instanciación del hilo de potencia (pero no inicio)
        self.power_thread = backend_module.PowerThread(self.data_storage)
        self.power_thread.powerThreadStarted.connect(self.update_buttons)
        self.power_thread.powerThreadStopped.connect(self.update_buttons)

    def set_dock_size(self, dock, width, height):
        """
        Hack para forzar el tamaño de un QDockWidget.
        Qt Designer a veces no respeta el minimumSize/sizePolicy en Docks.
        Esta función fuerza el tamaño y luego lo restaura mediante un Timer.
        """
        old_min_size = dock.minimumSize()
        old_max_size = dock.maximumSize()

        if width >= 0:
            if dock.width() < width:
                dock.setMinimumWidth(width)
            else:
                dock.setMaximumWidth(width)

        if height >= 0:
            if dock.height() < height:
                dock.setMinimumHeight(height)
            else:
                dock.setMaximumHeight(height)

        QtCore.QTimer.singleShot(0, lambda: self.set_dock_size_callback(dock, old_min_size, old_max_size))

    def set_dock_size_callback(self, dock, old_min_size, old_max_size):
        """Callback para restaurar las restricciones de tamaño originales del Dock."""
        dock.setMinimumSize(old_min_size)
        dock.setMaximumSize(old_max_size)

    def load_settings(self):
        """
        Restaura la configuración del analizador y la geometría de la ventana
        desde el almacenamiento persistente (QSettings).
        """
        settings = QtCore.QSettings()
        
        # Carga de parámetros numéricos de control
        self.startFreqSpinBox.setValue(settings.value("start_freq", 87.0, float))
        self.stopFreqSpinBox.setValue(settings.value("stop_freq", 108.0, float))
        self.binSizeSpinBox.setValue(settings.value("bin_size", 10.0, float))
        self.intervalSpinBox.setValue(settings.value("interval", 10.0, float))
        self.gainSpinBox.setValue(settings.value("gain", 0, int))
        self.ppmSpinBox.setValue(settings.value("ppm", 0, int))
        self.cropSpinBox.setValue(settings.value("crop", 0, int))
        
        # Carga de estados de CheckBoxes (curvas visibles)
        self.mainCurveCheckBox.setChecked(settings.value("main_curve", 1, int))
        self.peakHoldMaxCheckBox.setChecked(settings.value("peak_hold_max", 0, int))
        self.peakHoldMinCheckBox.setChecked(settings.value("peak_hold_min", 0, int))
        self.averageCheckBox.setChecked(settings.value("average", 0, int))
        self.smoothCheckBox.setChecked(settings.value("smooth", 0, int))
        self.persistenceCheckBox.setChecked(settings.value("persistence", 0, int))

        # Restaurar estado de docks y toolbars
        if settings.value("window_state"):
            self.restoreState(settings.value("window_state"))
        if settings.value("plotsplitter_state"):
            self.plotSplitter.restoreState(settings.value("plotsplitter_state"))

        # Migración de configuraciones antiguas (versión 1 a 2)
        if settings.value("config_version", 1, int) < 2:
            self.tabifyDockWidget(self.settingsDockWidget, self.levelsDockWidget)
            self.settingsDockWidget.raise_()
            self.set_dock_size(self.controlsDockWidget, 0, 0)
            self.set_dock_size(self.frequencyDockWidget, 0, 0)
            settings.setValue("config_version", 2)

        # Restaurar geometría de la ventana (posición y tamaño)
        # Se hace después de show() para asegurar compatibilidad con gestores de ventanas X11
        self.show()
        if settings.value("window_geometry"):
            self.restoreGeometry(settings.value("window_geometry"))

    def save_settings(self):
        """
        Guarda el estado actual de la aplicación (controles y geometría) en QSettings.
        """
        settings = QtCore.QSettings()
        settings.setValue("start_freq", self.startFreqSpinBox.value())
        settings.setValue("stop_freq", self.stopFreqSpinBox.value())
        settings.setValue("bin_size", self.binSizeSpinBox.value())
        settings.setValue("interval", self.intervalSpinBox.value())
        settings.setValue("gain", self.gainSpinBox.value())
        settings.setValue("ppm", self.ppmSpinBox.value())
        settings.setValue("crop", self.cropSpinBox.value())
        
        # Conversión de booleanos a int para almacenamiento
        settings.setValue("main_curve", int(self.mainCurveCheckBox.isChecked()))
        settings.setValue("peak_hold_max", int(self.peakHoldMaxCheckBox.isChecked()))
        settings.setValue("peak_hold_min", int(self.peakHoldMinCheckBox.isChecked()))
        settings.setValue("average", int(self.averageCheckBox.isChecked()))
        settings.setValue("smooth", int(self.smoothCheckBox.isChecked()))
        settings.setValue("persistence", int(self.persistenceCheckBox.isChecked()))

        # Guardado de geometría y estado de los docks
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.setValue("plotsplitter_state", self.plotSplitter.saveState())

    def show_status(self, message, timeout=2000):
        """
        Muestra un mensaje temporal en la barra de estado inferior.
        
        Variables:
            - message: Texto a mostrar.
            - timeout: Duración en ms (default 2000).
        """
        self.statusbar.showMessage(message, timeout)

    def update_buttons(self):
        """
        Actualiza el estado (Habilitado/Deshabilitado) de los botones Start/Stop/SingleShot
        dependiendo de si el hilo de potencia está activo.
        """
        self.startButton.setEnabled(not self.power_thread.alive)
        self.singleShotButton.setEnabled(not self.power_thread.alive)
        self.stopButton.setEnabled(self.power_thread.alive)

    def update_data(self, data_storage):
        """
        Callback ejecutado cuando llega nueva data desde el hilo.
        Calcula el tiempo de barrido (sweep time) y los FPS, y actualiza la barra de estado.
        """
        timestamp = time.time()
        sweep_time = timestamp - self.prev_data_timestamp
        self.prev_data_timestamp = timestamp

        status = []
        if self.power_thread.params["hops"]:
            status.append(self.tr("Frequency hops: {}").format(self.power_thread.params["hops"]))
        
        # Cálculo de FPS (Frames Per Second) inverso al tiempo de barrido
        status.append(self.tr("Sweep time: {:.2f} s | FPS: {:.2f}").format(sweep_time, 1 / sweep_time))
        self.show_status(" | ".join(status), timeout=0)

    def start(self, single_shot=False):
        """
        Inicia el proceso de adquisición de datos.
        Configura el backend con los parámetros actuales de la UI y lanza el hilo.
        
        Variables:
            - single_shot: Si es True, realiza un solo barrido y se detiene.
        """
        settings = QtCore.QSettings()
        self.prev_data_timestamp = time.time()

        # Reseteo de buffers de datos
        self.data_storage.reset()
        
        # Configuración de suavizado
        self.data_storage.set_smooth(
            bool(self.smoothCheckBox.isChecked()),
            settings.value("smooth_length", 11, int),
            settings.value("smooth_window", "hanning"),
            recalculate=False
        )

        # Configuración y limpieza de Waterfall
        self.waterfallPlotWidget.history_size = settings.value("waterfall_history_size", 100, int)
        self.waterfallPlotWidget.clear_plot()

        # Configuración y limpieza de curvas del Espectro
        self.spectrumPlotWidget.main_curve = bool(self.mainCurveCheckBox.isChecked())
        self.spectrumPlotWidget.main_color = str_to_color(settings.value("main_color", "255, 255, 0, 255"))
        self.spectrumPlotWidget.peak_hold_max = bool(self.peakHoldMaxCheckBox.isChecked())
        self.spectrumPlotWidget.peak_hold_max_color = str_to_color(settings.value("peak_hold_max_color", "255, 0, 0, 255"))
        self.spectrumPlotWidget.peak_hold_min = bool(self.peakHoldMinCheckBox.isChecked())
        self.spectrumPlotWidget.peak_hold_min_color = str_to_color(settings.value("peak_hold_min_color", "0, 0, 255, 255"))
        self.spectrumPlotWidget.average = bool(self.averageCheckBox.isChecked())
        self.spectrumPlotWidget.average_color = str_to_color(settings.value("average_color", "0, 255, 255, 255"))
        self.spectrumPlotWidget.persistence = bool(self.persistenceCheckBox.isChecked())
        self.spectrumPlotWidget.persistence_length = settings.value("persistence_length", 5, int)
        self.spectrumPlotWidget.persistence_decay = settings.value("persistence_decay", "exponential")
        self.spectrumPlotWidget.persistence_color = str_to_color(settings.value("persistence_color", "0, 255, 0, 255"))
        
        self.spectrumPlotWidget.clear_plot()
        self.spectrumPlotWidget.clear_peak_hold_max()
        self.spectrumPlotWidget.clear_peak_hold_min()
        self.spectrumPlotWidget.clear_average()
        self.spectrumPlotWidget.clear_persistence()

        # Lanzamiento del hilo si no está vivo
        if not self.power_thread.alive:
            self.power_thread.setup(float(self.startFreqSpinBox.value()),
                                    float(self.stopFreqSpinBox.value()),
                                    float(self.binSizeSpinBox.value()),
                                    interval=float(self.intervalSpinBox.value()),
                                    gain=int(self.gainSpinBox.value()),
                                    ppm=int(self.ppmSpinBox.value()),
                                    crop=int(self.cropSpinBox.value()) / 100.0,
                                    single_shot=single_shot,
                                    device=settings.value("device", ""),
                                    sample_rate=settings.value("sample_rate", 2560000, float),
                                    bandwidth=settings.value("bandwidth", 0, float),
                                    lnb_lo=settings.value("lnb_lo", 0, float))
            self.power_thread.start()

    def stop(self):
        """Detiene el hilo de adquisición de datos."""
        if self.power_thread.alive:
            self.power_thread.stop()

    # --- SLOTS PARA BOTONES DE CONTROL DE FLUJO ---
    @QtCore.Slot()
    def on_startButton_clicked(self):
        self.start()

    @QtCore.Slot()
    def on_singleShotButton_clicked(self):
        self.start(single_shot=True)

    @QtCore.Slot()
    def on_stopButton_clicked(self):
        self.stop()

    # --- SLOTS PARA CHECKBOXES DE VISUALIZACIÓN ---
    @QtCore.Slot(bool)
    def on_mainCurveCheckBox_toggled(self, checked):
        """Activa/Desactiva la curva principal en tiempo real."""
        self.spectrumPlotWidget.main_curve = checked
        if self.spectrumPlotWidget.curve.xData is None:
            self.spectrumPlotWidget.update_plot(self.data_storage)
        self.spectrumPlotWidget.curve.setVisible(checked)

    @QtCore.Slot(bool)
    def on_peakHoldMaxCheckBox_toggled(self, checked):
        """Activa/Desactiva la curva de retención de picos máximos."""
        self.spectrumPlotWidget.peak_hold_max = checked
        if self.spectrumPlotWidget.curve_peak_hold_max.xData is None:
            self.spectrumPlotWidget.update_peak_hold_max(self.data_storage)
        self.spectrumPlotWidget.curve_peak_hold_max.setVisible(checked)

    @QtCore.Slot(bool)
    def on_peakHoldMinCheckBox_toggled(self, checked):
        """Activa/Desactiva la curva de retención de picos mínimos."""
        self.spectrumPlotWidget.peak_hold_min = checked
        if self.spectrumPlotWidget.curve_peak_hold_min.xData is None:
            self.spectrumPlotWidget.update_peak_hold_min(self.data_storage)
        self.spectrumPlotWidget.curve_peak_hold_min.setVisible(checked)

    @QtCore.Slot(bool)
    def on_averageCheckBox_toggled(self, checked):
        """Activa/Desactiva la curva de promedio."""
        self.spectrumPlotWidget.average = checked
        if self.spectrumPlotWidget.curve_average.xData is None:
            self.spectrumPlotWidget.update_average(self.data_storage)
        self.spectrumPlotWidget.curve_average.setVisible(checked)

    @QtCore.Slot(bool)
    def on_persistenceCheckBox_toggled(self, checked):
        """Activa/Desactiva la visualización de persistencia."""
        self.spectrumPlotWidget.persistence = checked
        if self.spectrumPlotWidget.persistence_curves[0].xData is None:
            self.spectrumPlotWidget.recalculate_persistence(self.data_storage)
        for curve in self.spectrumPlotWidget.persistence_curves:
            curve.setVisible(checked)

    # --- SLOTS PARA FUNCIONES DE PROCESAMIENTO ---
    @QtCore.Slot(bool)
    def on_smoothCheckBox_toggled(self, checked):
        """Activa/Desactiva el suavizado y recalcula los datos."""
        settings = QtCore.QSettings()
        self.data_storage.set_smooth(
            checked,
            settings.value("smooth_length", 11, int),
            settings.value("smooth_window", "hanning"),
            recalculate=True
        )

    @QtCore.Slot()
    def on_smoothButton_clicked(self):
        """Abre el diálogo de configuración de suavizado."""
        dialog = QSpectrumAnalyzerSmooth(self)
        if dialog.exec_():
            settings = QtCore.QSettings()
            self.data_storage.set_smooth(
                bool(self.smoothCheckBox.isChecked()),
                settings.value("smooth_length", 11, int),
                settings.value("smooth_window", "hanning"),
                recalculate=True
            )

    @QtCore.Slot()
    def on_persistenceButton_clicked(self):
        """Abre el diálogo de configuración de persistencia."""
        prev_persistence_length = self.spectrumPlotWidget.persistence_length
        dialog = QSpectrumAnalyzerPersistence(self)
        if dialog.exec_():
            settings = QtCore.QSettings()
            persistence_length = settings.value("persistence_length", 5, int)
            self.spectrumPlotWidget.persistence_length = persistence_length
            self.spectrumPlotWidget.persistence_decay = settings.value("persistence_decay", "exponential")

            # Si solo cambió el decaimiento, resetear colores; si cambió la longitud, recalcular todo
            if persistence_length == prev_persistence_length:
                self.spectrumPlotWidget.set_colors()
            else:
                self.spectrumPlotWidget.recalculate_persistence(self.data_storage)

    @QtCore.Slot()
    def on_colorsButton_clicked(self):
        """Abre el diálogo de configuración de colores."""
        dialog = QSpectrumAnalyzerColors(self)
        if dialog.exec_():
            settings = QtCore.QSettings()
            self.spectrumPlotWidget.main_color = str_to_color(settings.value("main_color", "255, 255, 0, 255"))
            self.spectrumPlotWidget.peak_hold_max_color = str_to_color(settings.value("peak_hold_max_color", "255, 0, 0, 255"))
            self.spectrumPlotWidget.peak_hold_min_color = str_to_color(settings.value("peak_hold_min_color", "0, 0, 255, 255"))
            self.spectrumPlotWidget.average_color = str_to_color(settings.value("average_color", "0, 255, 255, 255"))
            self.spectrumPlotWidget.persistence_color = str_to_color(settings.value("persistence_color", "0, 255, 0, 255"))
            self.spectrumPlotWidget.set_colors()

    # --- SLOTS DE MENÚ SUPERIOR ---
    @QtCore.Slot()
    def on_action_Settings_triggered(self):
        """Abre el menú principal de configuración y reinicia el hilo al aceptar."""
        dialog = QSpectrumAnalyzerSettings(self)
        if dialog.exec_():
            self.setup_power_thread()

    @QtCore.Slot()
    def on_action_About_triggered(self):
        """Muestra la ventana 'Acerca de' con información de los autores y versión."""
        QtWidgets.QMessageBox.information(self,
        self.tr("Analizador de espectro – Medidas II 2025"),
        self.tr(
            "<b>Analizador basado en Beaglebone Black y SDR</b><br>"
            "Interfaz personalizada por <b>Bill - Cosso - Rodriguez - Yaconangelo</b>.<br>"
            "<br>"
            "Versión base: Analizador de espectro {}<br>"
            "<small>© Autor original xMikos y contribución de Ing. Maggiolo Gustavo, Ing. Dachary Alejandro y Garcia Leandro.</small>"
        ).format(__version__)
    )

    @QtCore.Slot()
    def on_action_Quit_triggered(self):
        """Cierra la aplicación."""
        self.close()

    def closeEvent(self, event):
        """
        Evento del sistema al cerrar la ventana.
        Detiene el hilo de manera segura y guarda la configuración.
        """
        self.stop()
        self.save_settings()


# //===================================================================================================
# //===================================== FUNCIÓN PRINCIPAL / MAIN ====================================
# //===================================================================================================

def main():
    global debug

    # Parsing de argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        prog="qspectrumanalyzer",
        description="Spectrum analyzer for multiple SDR platforms",
    )
    parser.add_argument("--debug", action="store_true",
                        help="detailed debugging messages")
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(__version__))
    args, unparsed_args = parser.parse_known_args()
    debug = args.debug

    # Inicialización de la aplicación Qt
    app = QtWidgets.QApplication(sys.argv[:1] + unparsed_args)
    
    # --- CONFIGURACIÓN DE TEMA OSCURO (PALETA DE COLORES) ---
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18, 18, 18))
    pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(10, 10, 10))
    pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(22, 22, 22))
    pal.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(30, 30, 30))
    pal.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(28, 28, 28))
    pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    pal.setColor(QtGui.QPalette.Link, QtGui.QColor(100, 149, 237))
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45, 120, 200))
    pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    if hasattr(QtGui.QPalette, "PlaceholderText"):
        pal.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(200, 200, 200, 140))
    app.setPalette(pal)

    # --- ESTILOS FINOS MEDIANTE HOJA DE ESTILOS (CSS-like) ---
    app.setStyleSheet(
        "QToolTip { color: #fff; background-color: #202020; border: 1px solid #404040; }"
        "QMenu { background-color: #181818; color: #eee; }"
        "QMenu::item:selected { background: #2a2a2a; }"
        "QStatusBar { background: #111; color: #ddd; }"
        "QLabel, QCheckBox, QRadioButton { color: #ddd; }"
        "QLineEdit, QTextEdit, QPlainTextEdit { background: #121212; color: #eee; border: 1px solid #333; }"
        "QComboBox, QSpinBox, QDoubleSpinBox { background: #171717; color: #eee; border: 1px solid #333; }"
        "QPushButton { background: #1e1e1e; color: #eee; border: 1px solid #333; padding: 4px 8px; }"
        "QPushButton:hover { background: #262626; }"
        "QGroupBox { border: 1px solid #333; margin-top: 6px; }"
        "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
    )

    # Identificación de la organización para el guardado de settings
    app.setOrganizationName("AnalizadorEspectro")
    app.setOrganizationDomain("qspectrumanalyzer.eutopia.cz")
    
    # Creación y ejecución de la ventana principal
    window = QSpectrumAnalyzerMainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()