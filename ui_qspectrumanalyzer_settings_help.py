/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este módulo contiene la definición de la interfaz gráfica (UI) para la ventana de Ayuda y Documentación
 * del sistema. Proporciona un visor de texto plano para mostrar manuales, descripciones de parámetros
 * o información de depuración al usuario final.
 *
 * Funcionamiento general:
 * - La clase `Ui_QSpectrumAnalyzerSettingsHelp` define un cuadro de diálogo simple.
 * - Implementa un `QPlainTextEdit` configurado en modo de solo lectura para visualizar texto extenso.
 * - Incluye un botón estándar de cierre para descartar la ventana.
 * - La disposición de los elementos se gestiona mediante un `QVBoxLayout` (diseño vertical).
 *
 * Notas importantes:
 * - Este código es agnóstico a la lógica de negocio; solo define la vista.
 * - Se utiliza el flag `TextSelectableByKeyboard|TextSelectableByMouse` para permitir copiar el texto
 * sin permitir su modificación, ideal para logs o manuales técnicos.
 ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

from Qt import QtCore, QtGui, QtWidgets

# //===================================================================================================
# //=========================== CLASE DE INTERFAZ DE AYUDA (HELP UI) ==================================
# //===================================================================================================

class Ui_QSpectrumAnalyzerSettingsHelp(object):
    """
    Clase que define la estructura visual del diálogo de Ayuda.
    Muestra información textual estática o dinámica sobre la configuración del analizador.
    """

    # //===================================================================================================
    # //===================================== IMPLEMENTACIÓN DE FUNCIONES =================================
    # //===================================================================================================

    def setupUi(self, QSpectrumAnalyzerSettingsHelp):
        """
        Inicializa y construye los componentes gráficos del diálogo de ayuda.

        Variables utilizadas:
            - QSpectrumAnalyzerSettingsHelp: El widget contenedor principal (QDialog).
            - verticalLayout: Organizador vertical para el área de texto y los botones.
            - helpTextEdit: Widget de edición de texto plano (usado aquí como visor).
            - buttonBox: Contenedor estándar para botones de diálogo (Cerrar/OK).

        Funcionamiento:
            1. Configura las dimensiones y el nombre del objeto principal.
            2. Crea un layout vertical para maximizar el uso del espacio.
            3. Instancia el visor de texto y deshabilita la edición (Undo/Redo).
            4. Configura las banderas de interacción para que sea "Solo Lectura" pero seleccionable.
            5. Añade el botón estándar de cierre.
            6. Conecta las señales (eventos) de los botones a los slots correspondientes.
        """
        # Configuración inicial del objeto ventana
        QSpectrumAnalyzerSettingsHelp.setObjectName("QSpectrumAnalyzerSettingsHelp")
        QSpectrumAnalyzerSettingsHelp.resize(1200, 700)

        # Creación del Layout Vertical
        # Permite que el cuadro de texto se expanda al redimensionar la ventana
        self.verticalLayout = QtWidgets.QVBoxLayout(QSpectrumAnalyzerSettingsHelp)
        self.verticalLayout.setObjectName("verticalLayout")

        # Configuración del Visor de Texto (QPlainTextEdit)
        # Se prefiere PlainTextEdit sobre TextEdit para mejor rendimiento con textos largos sin formato rico.
        self.helpTextEdit = QtWidgets.QPlainTextEdit(QSpectrumAnalyzerSettingsHelp)
        
        # Deshabilitar la pila de Deshacer/Rehacer ahorra memoria ya que no se editará texto
        self.helpTextEdit.setUndoRedoEnabled(False)
        
        # Configuración de Banderas de Interacción:
        # Permite seleccionar texto con mouse y teclado, pero NO editarlo.
        self.helpTextEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.helpTextEdit.setObjectName("helpTextEdit")
        
        # Agregar el visor al layout principal
        self.verticalLayout.addWidget(self.helpTextEdit)

        # Configuración de la Caja de Botones (ButtonBox)
        # Proporciona una interfaz nativa para los botones de diálogo (en este caso, solo "Cerrar")
        self.buttonBox = QtWidgets.QDialogButtonBox(QSpectrumAnalyzerSettingsHelp)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        
        # Agregar los botones al final del layout vertical
        self.verticalLayout.addWidget(self.buttonBox)

        # Llamada a la traducción de la interfaz (i18n)
        self.retranslateUi(QSpectrumAnalyzerSettingsHelp)

        # Conexión de Señales y Slots:
        # accepted -> accept() (Generalmente OK/Yes)
        # rejected -> reject() (Generalmente Cancel/Close/Esc)
        self.buttonBox.accepted.connect(QSpectrumAnalyzerSettingsHelp.accept)
        self.buttonBox.rejected.connect(QSpectrumAnalyzerSettingsHelp.reject)
        
        # Conexión automática de slots por nombre (feature de Qt Designer)
        QtCore.QMetaObject.connectSlotsByName(QSpectrumAnalyzerSettingsHelp)

        # Establecer el orden de tabulación para navegación por teclado
        QSpectrumAnalyzerSettingsHelp.setTabOrder(self.helpTextEdit, self.buttonBox)

    def retranslateUi(self, QSpectrumAnalyzerSettingsHelp):
        """
        Establece los textos visibles de la interfaz, permitiendo la localización (traducción).
        
        Variables utilizadas:
            - QSpectrumAnalyzerSettingsHelp: El widget principal para establecer el título.
            - _translate: Función wrapper para QCoreApplication.translate.
        """
        _translate = QtCore.QCoreApplication.translate
        # Establece el título de la ventana del sistema operativo
        QSpectrumAnalyzerSettingsHelp.setWindowTitle(_translate("QSpectrumAnalyzerSettingsHelp", "Help - Analizador de Espectro MEII"))