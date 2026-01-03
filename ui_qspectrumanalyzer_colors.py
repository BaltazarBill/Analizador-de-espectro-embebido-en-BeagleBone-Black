/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este módulo define la interfaz gráfica de usuario (GUI) para el cuadro de diálogo de configuración de colores.
 * Permite al usuario personalizar la apariencia de las diferentes curvas del analizador (traza principal,
 * promedios, retención de picos y persistencia) mediante selectores de color interactivos.
 *
 * Funcionamiento general:
 * - La clase Ui_QSpectrumAnalyzerColors construye un diálogo modal.
 * - Utiliza un diseño de formulario (QFormLayout) para organizar pares de Etiquetas y Botones de Color.
 * - Integra el widget personalizado 'ColorButton' de la librería PyQtGraph, que despliega un selector cromático
 * al ser presionado, retornando el valor RGBA seleccionado.
 *
 * Notas importantes:
 * - Código generado automáticamente por Qt Designer y comentado manualmente para docencia.
 * - Se utiliza 'Qt.py' para la abstracción de versiones de Qt (PySide/PyQt).
 * ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== IMPORTS / LIBRERÍAS =========================================
# //===================================================================================================

from Qt import QtCore, QtGui, QtWidgets

# //===================================================================================================
# //================================ CLASE DE INTERFAZ DE COLORES =====================================
# //===================================================================================================

class Ui_QSpectrumAnalyzerColors(object):
    """
    Clase que define la estructura visual del diálogo de selección de colores.
    """

    def setupUi(self, QSpectrumAnalyzerColors):
        """
        Inicializa y construye los widgets del diálogo de configuración de colores.

        Variables utilizadas:
            - QSpectrumAnalyzerColors: El widget contenedor (QDialog) donde se construye la UI.
            - formLayout: Distribución para alinear etiquetas a la izquierda y botones a la derecha.
            - ColorButton: Widget específico de pyqtgraph para selección de color.

        Funcionamiento:
            1. Configura el layout principal vertical.
            2. Inserta un FormLayout para organizar los controles.
            3. Instancia etiquetas y botones de color para cada tipo de traza (Main, Max, Min, Avg, Persistencia).
            4. Añade una caja de botones estándar (OK/Cancel).
            5. Configura la navegación por teclado (Tab Order) y señales de aceptación/rechazo.
        """
        QSpectrumAnalyzerColors.setObjectName("QSpectrumAnalyzerColors")
        QSpectrumAnalyzerColors.resize(232, 260)
        
        # Layout principal vertical para contener el formulario y los botones de acción
        self.verticalLayout = QtWidgets.QVBoxLayout(QSpectrumAnalyzerColors)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Layout de formulario para pares Label-Widget
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        
        # --- Configuración: Color de Curva Principal ---
        self.label_2 = QtWidgets.QLabel(QSpectrumAnalyzerColors)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        
        # Botón de color (pyqtgraph.ColorButton)
        self.mainColorButton = ColorButton(QSpectrumAnalyzerColors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainColorButton.sizePolicy().hasHeightForWidth())
        self.mainColorButton.setSizePolicy(sizePolicy)
        self.mainColorButton.setObjectName("mainColorButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.mainColorButton)
        
        # --- Configuración: Color de Max Hold ---
        self.label_4 = QtWidgets.QLabel(QSpectrumAnalyzerColors)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        
        self.peakHoldMaxColorButton = ColorButton(QSpectrumAnalyzerColors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peakHoldMaxColorButton.sizePolicy().hasHeightForWidth())
        self.peakHoldMaxColorButton.setSizePolicy(sizePolicy)
        self.peakHoldMaxColorButton.setObjectName("peakHoldMaxColorButton")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.peakHoldMaxColorButton)
        
        # --- Configuración: Color de Min Hold ---
        self.label_6 = QtWidgets.QLabel(QSpectrumAnalyzerColors)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        
        self.peakHoldMinColorButton = ColorButton(QSpectrumAnalyzerColors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peakHoldMinColorButton.sizePolicy().hasHeightForWidth())
        self.peakHoldMinColorButton.setSizePolicy(sizePolicy)
        self.peakHoldMinColorButton.setObjectName("peakHoldMinColorButton")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.peakHoldMinColorButton)
        
        # --- Configuración: Color de Promedio (Average) ---
        self.label_5 = QtWidgets.QLabel(QSpectrumAnalyzerColors)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        
        self.averageColorButton = ColorButton(QSpectrumAnalyzerColors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.averageColorButton.sizePolicy().hasHeightForWidth())
        self.averageColorButton.setSizePolicy(sizePolicy)
        self.averageColorButton.setObjectName("averageColorButton")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.averageColorButton)
        
        # --- Configuración: Color de Persistencia ---
        self.label_3 = QtWidgets.QLabel(QSpectrumAnalyzerColors)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        
        self.persistenceColorButton = ColorButton(QSpectrumAnalyzerColors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.persistenceColorButton.sizePolicy().hasHeightForWidth())
        self.persistenceColorButton.setSizePolicy(sizePolicy)
        self.persistenceColorButton.setObjectName("persistenceColorButton")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.persistenceColorButton)
        
        # Agregar el layout del formulario al layout vertical principal
        self.verticalLayout.addLayout(self.formLayout)
        
        # Espaciador vertical para empujar los botones hacia abajo si se redimensiona
        spacerItem = QtWidgets.QSpacerItem(20, 2, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # Caja de botones estándar (OK / Cancelar)
        self.buttonBox = QtWidgets.QDialogButtonBox(QSpectrumAnalyzerColors)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        
        # Asociación de etiquetas con sus respectivos widgets (Buddy) para accesibilidad
        self.label_2.setBuddy(self.mainColorButton)
        self.label_4.setBuddy(self.peakHoldMaxColorButton)
        self.label_6.setBuddy(self.peakHoldMinColorButton)
        self.label_5.setBuddy(self.averageColorButton)
        self.label_3.setBuddy(self.persistenceColorButton)

        self.retranslateUi(QSpectrumAnalyzerColors)
        
        # Conexión de señales de los botones estándar a slots del diálogo
        self.buttonBox.accepted.connect(QSpectrumAnalyzerColors.accept)
        self.buttonBox.rejected.connect(QSpectrumAnalyzerColors.reject)
        QtCore.QMetaObject.connectSlotsByName(QSpectrumAnalyzerColors)
        
        # Definición del orden de tabulación para navegación por teclado
        QSpectrumAnalyzerColors.setTabOrder(self.mainColorButton, self.peakHoldMaxColorButton)
        QSpectrumAnalyzerColors.setTabOrder(self.peakHoldMaxColorButton, self.peakHoldMinColorButton)
        QSpectrumAnalyzerColors.setTabOrder(self.peakHoldMinColorButton, self.averageColorButton)
        QSpectrumAnalyzerColors.setTabOrder(self.averageColorButton, self.persistenceColorButton)
        QSpectrumAnalyzerColors.setTabOrder(self.persistenceColorButton, self.buttonBox)

    def retranslateUi(self, QSpectrumAnalyzerColors):
        """
        Traduce los textos de la interfaz de usuario.
        Utiliza el sistema de traducción de Qt para soporte multi-idioma.
        """
        _translate = QtCore.QCoreApplication.translate
        QSpectrumAnalyzerColors.setWindowTitle(_translate("QSpectrumAnalyzerColors", "Colors - Analizador de Espectro MEII"))
        self.label_2.setText(_translate("QSpectrumAnalyzerColors", "Main curve color:"))
        self.mainColorButton.setText(_translate("QSpectrumAnalyzerColors", "..."))
        self.label_4.setText(_translate("QSpectrumAnalyzerColors", "Max. peak hold color:"))
        self.peakHoldMaxColorButton.setText(_translate("QSpectrumAnalyzerColors", "..."))
        self.label_6.setText(_translate("QSpectrumAnalyzerColors", "Min. peak hold color:"))
        self.peakHoldMinColorButton.setText(_translate("QSpectrumAnalyzerColors", "..."))
        self.label_5.setText(_translate("QSpectrumAnalyzerColors", "Average color:"))
        self.averageColorButton.setText(_translate("QSpectrumAnalyzerColors", "..."))
        self.label_3.setText(_translate("QSpectrumAnalyzerColors", "Persistence color:"))
        self.persistenceColorButton.setText(_translate("QSpectrumAnalyzerColors", "..."))

# //===================================================================================================
# //===================================== IMPORTACIONES TARDÍAS =======================================
# //===================================================================================================

# Importación del widget personalizado usado en el diseñador.
# Se coloca al final para evitar errores de referencia circular durante la carga.
from pyqtgraph import ColorButton