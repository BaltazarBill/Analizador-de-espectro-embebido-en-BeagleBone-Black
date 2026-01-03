/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este módulo define la interfaz gráfica de usuario (GUI) para el cuadro de diálogo de configuración general
 * del analizador de espectro. Permite al usuario seleccionar el backend de adquisición (soapy_power, rtl_power, etc.),
 * configurar parámetros del dispositivo SDR (tasa de muestreo, ancho de banda) y ajustar el tamaño del historial
 * para el gráfico de cascada.
 *
 * Funcionamiento general:
 * - La clase Ui_QSpectrumAnalyzerSettings construye un diálogo modal complejo.
 * - Utiliza un QFormLayout para alinear etiquetas descriptivas con campos de entrada (ComboBox, SpinBox, LineEdit).
 * - Proporciona botones de ayuda (?) para consultar parámetros específicos del backend seleccionado.
 * - Permite la configuración de convertidores de frecuencia (LNB LO) para upconverters/downconverters.
 *
 * Notas importantes:
 * - Código generado automáticamente por Qt Designer y comentado manualmente para docencia.
 * - Se utiliza la abstracción 'Qt' para mantener compatibilidad entre diferentes bindings (PySide/PyQt).
 * ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

from Qt import QtCore, QtGui, QtWidgets

# //===================================================================================================
# //=========================== CLASE DE CONFIGURACIÓN DEL ANALIZADOR =================================
# //===================================================================================================

class Ui_QSpectrumAnalyzerSettings(object):
    """
    Clase que define la estructura visual del diálogo de configuración principal.
    Contiene controles para la gestión del hardware SDR y el procesamiento de señal.
    """

    def setupUi(self, QSpectrumAnalyzerSettings):
        """
        Inicializa y construye los widgets del diálogo de configuración.

        Variables utilizadas:
            - QSpectrumAnalyzerSettings: El widget contenedor (QDialog).
            - backendComboBox: Selector del software backend (driver).
            - sampleRateSpinBox, bandwidthSpinBox: Controles numéricos de RF.
            - lnbSpinBox: Offset de frecuencia para convertidores LNB.
            - waterfallHistorySizeSpinBox: Profundidad del buffer de historial.

        Funcionamiento:
            1. Configura el layout principal vertical.
            2. Inserta un FormLayout para organizar los controles de manera estructurada.
            3. Instancia y configura cada widget de entrada (ComboBox, SpinBox, LineEdit) con sus rangos y valores por defecto.
            4. Añade botones de herramientas para selección de archivos y ayuda contextual.
            5. Configura la caja de botones estándar (OK/Cancel).
            6. Establece el orden de tabulación y conecta las señales de aceptación/rechazo.
        """
        QSpectrumAnalyzerSettings.setObjectName("QSpectrumAnalyzerSettings")
        QSpectrumAnalyzerSettings.resize(600, 388)
        
        # Layout principal vertical
        self.verticalLayout = QtWidgets.QVBoxLayout(QSpectrumAnalyzerSettings)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Layout de formulario para pares Etiqueta-Control
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        
        # --- Selección de Backend ---
        self.label_3 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        
        self.backendComboBox = QtWidgets.QComboBox(QSpectrumAnalyzerSettings)
        self.backendComboBox.setObjectName("backendComboBox")
        # Se añaden 5 opciones vacías que se rellenarán en retranslateUi
        self.backendComboBox.addItem("")
        self.backendComboBox.addItem("")
        self.backendComboBox.addItem("")
        self.backendComboBox.addItem("")
        self.backendComboBox.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.backendComboBox)
        
        # --- Selección de Ejecutable ---
        self.label = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        
        # Layout horizontal anidado para el campo de texto y el botón de búsqueda
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.executableEdit = QtWidgets.QLineEdit(QSpectrumAnalyzerSettings)
        self.executableEdit.setObjectName("executableEdit")
        self.horizontalLayout.addWidget(self.executableEdit)
        self.executableButton = QtWidgets.QToolButton(QSpectrumAnalyzerSettings)
        self.executableButton.setMinimumSize(QtCore.QSize(50, 0))
        self.executableButton.setObjectName("executableButton")
        self.horizontalLayout.addWidget(self.executableButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        
        # --- Parámetros Adicionales ---
        self.label_6 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.paramsEdit = QtWidgets.QLineEdit(QSpectrumAnalyzerSettings)
        self.paramsEdit.setObjectName("paramsEdit")
        self.horizontalLayout_2.addWidget(self.paramsEdit)
        self.paramsHelpButton = QtWidgets.QToolButton(QSpectrumAnalyzerSettings)
        self.paramsHelpButton.setMinimumSize(QtCore.QSize(50, 0))
        self.paramsHelpButton.setObjectName("paramsHelpButton")
        self.horizontalLayout_2.addWidget(self.paramsHelpButton)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)

        # --- Selección de Dispositivo ---
        self.label_5 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.deviceEdit = QtWidgets.QLineEdit(QSpectrumAnalyzerSettings)
        self.deviceEdit.setObjectName("deviceEdit")
        self.horizontalLayout_3.addWidget(self.deviceEdit)
        self.deviceHelpButton = QtWidgets.QToolButton(QSpectrumAnalyzerSettings)
        self.deviceHelpButton.setMinimumSize(QtCore.QSize(50, 0))
        self.deviceHelpButton.setObjectName("deviceHelpButton")
        self.horizontalLayout_3.addWidget(self.deviceHelpButton)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        
        # --- Tasa de Muestreo (Sample Rate) ---
        self.label_4 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        
        self.sampleRateSpinBox = QtWidgets.QDoubleSpinBox(QSpectrumAnalyzerSettings)
        self.sampleRateSpinBox.setProperty("showGroupSeparator", True)
        self.sampleRateSpinBox.setDecimals(3)
        self.sampleRateSpinBox.setMinimum(0.0)
        self.sampleRateSpinBox.setMaximum(61.44) # Límite típico para hardware SDR común
        self.sampleRateSpinBox.setSingleStep(0.01)
        self.sampleRateSpinBox.setProperty("value", 61.44)
        self.sampleRateSpinBox.setObjectName("sampleRateSpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.sampleRateSpinBox)
        
        # --- Ancho de Banda (Bandwidth) ---
        self.label_7 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_7)
        
        self.bandwidthSpinBox = QtWidgets.QDoubleSpinBox(QSpectrumAnalyzerSettings)
        self.bandwidthSpinBox.setProperty("showGroupSeparator", True)
        self.bandwidthSpinBox.setDecimals(3)
        self.bandwidthSpinBox.setMinimum(0.0)
        self.bandwidthSpinBox.setMaximum(61.44)
        self.bandwidthSpinBox.setSingleStep(0.01)
        self.bandwidthSpinBox.setProperty("value", 0.0)
        self.bandwidthSpinBox.setObjectName("bandwidthSpinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.bandwidthSpinBox)
        
        # --- Oscilador Local del LNB (LNB LO) ---
        self.label_8 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_8)
        
        self.lnbSpinBox = QtWidgets.QDoubleSpinBox(QSpectrumAnalyzerSettings)
        self.lnbSpinBox.setProperty("showGroupSeparator", True)
        self.lnbSpinBox.setDecimals(3)
        self.lnbSpinBox.setMinimum(-999999.999) # Rango amplio para up/down converters
        self.lnbSpinBox.setMaximum(999999.999)
        self.lnbSpinBox.setSingleStep(0.01)
        self.lnbSpinBox.setProperty("value", 0.0)
        self.lnbSpinBox.setObjectName("lnbSpinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.lnbSpinBox)

        # --- Tamaño del Historial de Cascada ---
        self.label_2 = QtWidgets.QLabel(QSpectrumAnalyzerSettings)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_2)
        
        self.waterfallHistorySizeSpinBox = QtWidgets.QSpinBox(QSpectrumAnalyzerSettings)
        self.waterfallHistorySizeSpinBox.setMinimum(1)
        self.waterfallHistorySizeSpinBox.setMaximum(10000000)
        self.waterfallHistorySizeSpinBox.setProperty("value", 100)
        self.waterfallHistorySizeSpinBox.setObjectName("waterfallHistorySizeSpinBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.waterfallHistorySizeSpinBox)
        
        # Agregar el formulario al layout principal
        self.verticalLayout.addLayout(self.formLayout)
        
        # Espaciador vertical
        spacerItem = QtWidgets.QSpacerItem(20, 21, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # Caja de botones estándar
        self.buttonBox = QtWidgets.QDialogButtonBox(QSpectrumAnalyzerSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        
        # Configuración de Buddies (Accesibilidad)
        self.label_3.setBuddy(self.backendComboBox)
        self.label.setBuddy(self.executableEdit)
        self.label_5.setBuddy(self.deviceEdit)
        self.label_4.setBuddy(self.sampleRateSpinBox)
        self.label_2.setBuddy(self.waterfallHistorySizeSpinBox)
        self.label_7.setBuddy(self.bandwidthSpinBox)
        self.label_8.setBuddy(self.lnbSpinBox)
        self.label_6.setBuddy(self.paramsEdit)

        self.retranslateUi(QSpectrumAnalyzerSettings)
        
        # Conexión de señales de botones
        self.buttonBox.accepted.connect(QSpectrumAnalyzerSettings.accept)
        self.buttonBox.rejected.connect(QSpectrumAnalyzerSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(QSpectrumAnalyzerSettings)
        
        # Orden de tabulación
        QSpectrumAnalyzerSettings.setTabOrder(self.backendComboBox, self.executableEdit)
        QSpectrumAnalyzerSettings.setTabOrder(self.executableEdit, self.executableButton)
        QSpectrumAnalyzerSettings.setTabOrder(self.executableButton, self.paramsEdit)
        QSpectrumAnalyzerSettings.setTabOrder(self.paramsEdit, self.paramsHelpButton)
        QSpectrumAnalyzerSettings.setTabOrder(self.paramsHelpButton, self.deviceEdit)
        QSpectrumAnalyzerSettings.setTabOrder(self.deviceEdit, self.deviceHelpButton)
        QSpectrumAnalyzerSettings.setTabOrder(self.deviceHelpButton, self.sampleRateSpinBox)
        QSpectrumAnalyzerSettings.setTabOrder(self.sampleRateSpinBox, self.bandwidthSpinBox)
        QSpectrumAnalyzerSettings.setTabOrder(self.bandwidthSpinBox, self.lnbSpinBox)
        QSpectrumAnalyzerSettings.setTabOrder(self.lnbSpinBox, self.waterfallHistorySizeSpinBox)

    def retranslateUi(self, QSpectrumAnalyzerSettings):
        """
        Traduce los textos de la interfaz.
        """
        _translate = QtCore.QCoreApplication.translate
        QSpectrumAnalyzerSettings.setWindowTitle(_translate("QSpectrumAnalyzerSettings", "Settings - Analizador de espectro MEII"))
        self.label_3.setText(_translate("QSpectrumAnalyzerSettings", "&Backend:"))
        
        # Opciones de backend disponibles
        self.backendComboBox.setItemText(0, _translate("QSpectrumAnalyzerSettings", "soapy_power"))
        self.backendComboBox.setItemText(1, _translate("QSpectrumAnalyzerSettings", "rx_power"))
        self.backendComboBox.setItemText(2, _translate("QSpectrumAnalyzerSettings", "rtl_power_fftw"))
        self.backendComboBox.setItemText(3, _translate("QSpectrumAnalyzerSettings", "rtl_power"))
        self.backendComboBox.setItemText(4, _translate("QSpectrumAnalyzerSettings", "hackrf_sweep"))
        
        self.label.setText(_translate("QSpectrumAnalyzerSettings", "E&xecutable:"))
        self.executableEdit.setText(_translate("QSpectrumAnalyzerSettings", "soapy_power"))
        self.executableButton.setText(_translate("QSpectrumAnalyzerSettings", "..."))
        self.label_5.setText(_translate("QSpectrumAnalyzerSettings", "&Device:"))
        self.label_4.setText(_translate("QSpectrumAnalyzerSettings", "Sa&mple rate:"))
        self.label_2.setText(_translate("QSpectrumAnalyzerSettings", "&Waterfall history size:"))
        self.label_7.setText(_translate("QSpectrumAnalyzerSettings", "Bandwidt&h:"))
        
        self.label_8.setToolTip(_translate("QSpectrumAnalyzerSettings", "Negative frequency for upconverters, positive frequency for downconverters."))
        self.label_8.setText(_translate("QSpectrumAnalyzerSettings", "&LNB LO:"))
        self.label_6.setText(_translate("QSpectrumAnalyzerSettings", "Add&itional parameters:"))
        self.paramsHelpButton.setText(_translate("QSpectrumAnalyzerSettings", " ? "))
        self.deviceHelpButton.setText(_translate("QSpectrumAnalyzerSettings", " ? "))
        self.sampleRateSpinBox.setSuffix(_translate("QSpectrumAnalyzerSettings", " MHz"))
        self.bandwidthSpinBox.setSuffix(_translate("QSpectrumAnalyzerSettings", " MHz"))
        self.lnbSpinBox.setToolTip(_translate("QSpectrumAnalyzerSettings", "Negative frequency for upconverters, positive frequency for downconverters."))
        self.lnbSpinBox.setSuffix(_translate("QSpectrumAnalyzerSettings", " MHz"))