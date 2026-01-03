/****************************************************************************************************************************
 * TÍTULO DEL PROYECTO: Analizador de espectro embebido
 * Materia / Curso: Medidas Electrónicas II - Beca de RTOS
 * Año: 2025
 * Descripción general del programa:
 * Este archivo (__init__.py o version.py) cumple la función de definir la versión actual del paquete de software
 * del analizador de espectro. Es una práctica estándar en Python exponer la versión del módulo mediante
 * la variable mágica `__version__`.
 *
 * Funcionamiento general:
 * - Define una cadena de caracteres que representa la versión semántica o de desarrollo.
 * - Esta variable es importada por el script principal (main) para mostrarla en la interfaz gráfica (Ventana "Acerca de")
 * o en los registros de depuración (logs) para trazabilidad.
 *
 * Notas importantes:
 * - El formato utilizado sigue un esquema de fecha (DD.MM.YY) seguido de iniciales o variante (VF = Versión Final).
 * ****************************************************************************************************************************/

# //===================================================================================================
# //===================================== DEFINICIÓN DE CONSTANTES ====================================
# //===================================================================================================

# Definición de la versión del software.
# Esta variable es accesible globalmente cuando se importa el paquete.
# Se utiliza para el control de versiones y la identificación de la compilación en tiempo de ejecución.
# Representa la última fecha de presentación del proyecto en la materia [Medidas Electrónicas II]
__version__ = "03.10.25 VF"