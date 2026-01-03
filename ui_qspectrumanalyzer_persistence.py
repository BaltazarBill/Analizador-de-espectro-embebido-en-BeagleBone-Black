/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este archivo contiene la definición de la clase de interfaz gráfica (UI) para la configuración de la "Persistencia".
 * La persistencia es una técnica de visualización que simula el decaimiento del fósforo en pantallas CRT antiguas,
 * permitiendo ver el historial inmediato de la señal espectral.
 *
 * Funcionamiento general:
 * - La clase `Ui_QSpectrumAnalyzerPersistence` genera un cuadro de diálogo modal.
 * - Permite al usuario seleccionar la función matemática de decaimiento (Lineal o Exponencial).
 * - Permite definir la "longitud" de la persistencia (cuántos cuadros anteriores se retienen en memoria).
 * - El código define la jerarquía de widgets, layouts, propiedades iniciales y conexiones de señales básicas.
 *
 * Notas importantes:
 * - Este código es típicamente generado de forma automática por herramientas como `pyuic` o `pyside-uic` a partir de un archivo .ui.
 * - Se utiliza la abstracción `Qt` para mantener compatibilidad entre diferentes bindings (PyQt5, PySide2, etc.).
 ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

from Qt import QtCore, QtGui, QtWidgets

# //===================================================================================================
# //=========================== CLASE DE INTERFAZ DE PERSISTENCIA =====================================
# //===================================================================================================

class Ui_QSpectrumAnalyzerPersistence(object):
    """
    Clase que define la estructura visual del diálogo de configuración de Persistencia.
    Define los controles para ajustar el tipo de decaimiento visual y la profundidad del historial.
    """

    # //===================================================================================================
    # //===================================== IMPLEMENTACIÓN DE FUNCIONES =================================
    # //===================================================================================================

    def setupUi(self, QSpectrumAnalyzerPersistence):
        """
        Inicializa y construye los componentes gráficos (widgets) del diálogo.

        Variables utilizadas:
            - QSpectrumAnalyzerPersistence: El objeto QDialog contenedor principal.
            - verticalLayout: Organizador principal vertical.
            - formLayout: Organizador de formulario (Etiqueta -> Campo).
            - decayFunctionComboBox: Selector para el tipo de función matemática.
            - persistenceLengthSpinBox: Selector numérico para la cantidad de cuadros.

        Funcionamiento:
            1. Configura el objeto principal y su tamaño.
            2. Establece un layout vertical para apilar el formulario y los botones.
            3. Inserta un FormLayout para alinear etiquetas y controles de entrada.
            4. Añade los widgets específicos (ComboBox y SpinBox).
            5. Añade espaciadores y la caja de botones estándar (OK/Cancel).
            6. Configura las conexiones de señales y slots para aceptar/rechazar el diálogo.
        """
        # Configuración inicial del objeto contenedor
        QSpectrumAnalyzerPersistence.setObjectName("QSpectrumAnalyzerPersistence")
        QSpectrumAnalyzerPersistence.resize(250, 130)

        # Creación del Layout Vertical Principal
        # Este layout organizará el contenido en una columna: Formulario arriba, Botones abajo.
        self.verticalLayout = QtWidgets.QVBoxLayout(QSpectrumAnalyzerPersistence)
        self.verticalLayout.setObjectName("verticalLayout")

        # Creación del Layout de Formulario (QFormLayout)
        # Ideal para ventanas de configuración, alinea automáticamente Labels a la izquierda y Widgets a la derecha.
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")

        # --- Fila 1: Selección de Función de Decaimiento ---
        self.label_2 = QtWidgets.QLabel(QSpectrumAnalyzerPersistence)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)

        self.decayFunctionComboBox = QtWidgets.QComboBox(QSpectrumAnalyzerPersistence)
        self.decayFunctionComboBox.setObjectName("decayFunctionComboBox")
        # Se agregan dos ítems vacíos que serán rellenados con texto en retranslateUi
        self.decayFunctionComboBox.addItem("")
        self.decayFunctionComboBox.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.decayFunctionComboBox)

        # --- Fila 2: Selección de Longitud de Persistencia ---
        self.label = QtWidgets.QLabel(QSpectrumAnalyzerPersistence)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)

        self.persistenceLengthSpinBox = QtWidgets.QSpinBox(QSpectrumAnalyzerPersistence)
        self.persistenceLengthSpinBox.setProperty("value", 5) # Valor por defecto inicial
        self.persistenceLengthSpinBox.setObjectName("persistenceLengthSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.persistenceLengthSpinBox)

        # Agregar el layout de formulario al layout principal
        self.verticalLayout.addLayout(self.formLayout)

        # Agregar un espaciador vertical (Spacer)
        # Empuja los elementos hacia arriba y mantiene los botones en la parte inferior si se redimensiona.
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        # --- Caja de Botones Estándar ---
        # Provee los botones nativos del sistema operativo para Aceptar o Cancelar acciones.
        self.buttonBox = QtWidgets.QDialogButtonBox(QSpectrumAnalyzerPersistence)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        # Configuración de "Buddies" (Compañeros)
        # Permite que al usar atajos de teclado en la etiqueta (ej. Alt+D), el foco salte al widget asociado.
        self.label_2.setBuddy(self.decayFunctionComboBox)
        self.label.setBuddy(self.persistenceLengthSpinBox)

        # Llamada a la función de traducción de textos
        self.retranslateUi(QSpectrumAnalyzerPersistence)

        # Configuración de valores iniciales y conexiones
        self.decayFunctionComboBox.setCurrentIndex(1) # Selecciona "Exponencial" por defecto (índice 1)
        
        # Conexión de señales de la caja de botones a los slots del diálogo
        self.buttonBox.accepted.connect(QSpectrumAnalyzerPersistence.accept)
        self.buttonBox.rejected.connect(QSpectrumAnalyzerPersistence.reject)
        
        # Conexión automática de slots por nombre (convención de Qt)
        QtCore.QMetaObject.connectSlotsByName(QSpectrumAnalyzerPersistence)

        # Configuración del orden de tabulación (navegación con tecla Tab)
        QSpectrumAnalyzerPersistence.setTabOrder(self.decayFunctionComboBox, self.persistenceLengthSpinBox)
        QSpectrumAnalyzerPersistence.setTabOrder(self.persistenceLengthSpinBox, self.buttonBox)

    def retranslateUi(self, QSpectrumAnalyzerPersistence):
        """
        Establece los textos visibles de la interfaz gráfica.
        Esta separación permite la internacionalización (i18n) dinámica de la aplicación.

        Variables utilizadas:
            - QSpectrumAnalyzerPersistence: Objeto principal para setear el título de ventana.
            - _translate: Función auxiliar para el motor de traducción de Qt.
        """
        _translate = QtCore.QCoreApplication.translate
        # Título de la ventana
        QSpectrumAnalyzerPersistence.setWindowTitle(_translate("QSpectrumAnalyzerPersistence", "Persistence - Analizador de Espectro MEII"))
        
        # Textos para la fila de función de decaimiento
        self.label_2.setText(_translate("QSpectrumAnalyzerPersistence", "Decay function:"))
        self.decayFunctionComboBox.setItemText(0, _translate("QSpectrumAnalyzerPersistence", "linear"))
        self.decayFunctionComboBox.setItemText(1, _translate("QSpectrumAnalyzerPersistence", "exponential"))
        
        # Textos para la fila de longitud
        self.label.setText(_translate("QSpectrumAnalyzerPersistence", "Persistence length:"))