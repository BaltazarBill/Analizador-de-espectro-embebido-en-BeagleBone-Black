# Analizador de espectro basado en SDR embebido en BeagleBone Black
<!--
/****************************************************************************************************************************

TÍTULO DEL PROYECTO: Analizador de Espectro Embebido

Materia / Curso: Medidas Electrónicas II - Beca de RTOS

Año: 2025

Descripción general del repositorio:

Este repositorio contiene el código fuente y la documentación para desplegar un analizador de espectro

de radiofrecuencia (RF) basado en Software Defined Radio (SDR). El sistema está diseñado para operar

tanto en estaciones de trabajo (Windows/WSL) como en sistemas embebidos dedicados (BeagleBone Black).

Funcionamiento general:

Adquisición: Utiliza un dongle RTL-SDR y el backend rtl_power para barrer el espectro.

Procesamiento: Un script en Python procesa la FFT y los datos de potencia (dBm).

Visualización: Una interfaz gráfica (Qt5) renderiza los datos en tiempo real y en modo cascada.

Interacción: Soporte para mouse y teclado en pantallas HDMI conectadas directamente al SBC.

Notas importantes:

Optimizado para renderizado sin gestor de ventanas completo (Headless/Framebuffer) en Linux.

Requiere hardware RTL-SDR compatible (RTL2832U).
****************************************************************************************************************************/
-->

QSpectrumAnalyzer – Modificación para Entorno Embebido y Salida HDMI

1. Descripción del Proyecto

Este proyecto es una bifurcación (fork) y adaptación del repositorio original xmikos/qspectrumanalyzer, reingenierizado específicamente para cumplir con los requisitos de sistemas embebidos de recursos limitados, tales como la BeagleBone Black, y entornos de desarrollo modernos como WSL (Windows Subsystem for Linux).

La aplicación integra el backend rtl_power (parte de la suite librtlsdr) para la adquisición de datos espectrales y presenta los resultados mediante una interfaz gráfica de alto rendimiento desarrollada en PyQt5.

Optimización para Sistemas Embebidos (HDMI / Consola)

A diferencia de la versión de escritorio estándar, esta iteración ha sido optimizada para:

Renderizado directo: Ejecución sobre el Framebuffer de Linux o EGLFS, eliminando la necesidad de un entorno de escritorio pesado (GNOME/KDE).

Interacción Táctil/Mouse: Soporte nativo para entrada de puntero en pantallas HDMI.

Eficiencia: Ajustes en QT_QPA_PLATFORM para maximizar los FPS en hardware ARM.

Características Principales

Visualización en tiempo real: Gráficos de densidad espectral de potencia (PSD) y diagrama de cascada (Waterfall).

Compatibilidad Hardware: Soporte plug-and-play para dongles RTL-SDR (R820T2, etc.).

Interfaz Adaptativa: GUI basada en Qt5 optimizada para resoluciones de pantallas embebidas (ej. 800x480, 1024x600).

Configuración DSP: Control total sobre ganancia, ancho de banda, tasa de muestreo y tamaño de bins FFT.

2. Instalación y Requisitos

Siga estos pasos estrictamente para desplegar el sistema en una BeagleBone Black (Debian) o en un entorno de desarrollo WSL.

A. Clonar el Repositorio

Acceda a la terminal de su sistema y descargue el código fuente:

git clone [https://github.com/BaltazarBill/Analizador-de-espectro-embebido-en-BeagleBone-Black.git](https://github.com/BaltazarBill/Analizador-de-espectro-embebido-en-BeagleBone-Black.git)
cd Analizador-de-espectro-embebido-en-BeagleBone-Black


B. Dependencias del Sistema (Debian / Ubuntu / BBB)

Es necesario instalar las bibliotecas de manejo del SDR y los binarios de Qt5.

sudo apt update
# Instalar drivers SDR y librerías base de Qt5
sudo apt install rtl-sdr librtlsdr-dev libqt5gui5 libqt5widgets5 qt5-default


C. Configuración de Permisos USB (Solo Linux Embebido)

Para que la BeagleBone acceda al USB sin permisos de superusuario (root), debe configurar las reglas udev.

Cree el archivo de reglas:

sudo nano /etc/udev/rules.d/20-rtlsdr.rules


Pegue el siguiente contenido:

SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"


Recargue las reglas y reinicie:

sudo udevadm control --reload-rules && sudo udevadm trigger


D. Configuración del Entorno Python

Se recomienda el uso de un entorno virtual para evitar conflictos con las librerías del sistema operativo.

# 1. Instalar venv si no está presente
sudo apt install python3-venv

# 2. Crear el entorno virtual llamado 'venv'
python3 -m venv venv

# 3. Activar el entorno
source venv/bin/activate

# 4. Instalar las dependencias del proyecto
pip install -r requirements.txt


3. Uso y Ejecución

El modo de ejecución varía dependiendo de si se utiliza un entorno de escritorio completo (PC) o una salida directa a pantalla (BeagleBone).

Escenario A: Ejecución en BeagleBone Black (HDMI directo)

Para ejecutar la interfaz gráfica directamente en la pantalla conectada por HDMI (sin gestor de ventanas):

# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Definir la plataforma de Qt para embebidos (EGLFS o LinuxFB)
# Opción 1: EGLFS (Aceleración gráfica si está disponible GPU)
export QT_QPA_PLATFORM=eglfs
export QT_QPA_EGLFS_ALWAYS_SET_MODE=1

# Opción 2: LinuxFB (Framebuffer directo por CPU - Usar si EGLFS falla)
# export QT_QPA_PLATFORM=linuxfb

# Ejecutar la aplicación
python3 qspectrumanalyzer/__main__.py


Nota Técnica sobre el Mouse: El plugin eglfs normalmente detecta el mouse automáticamente a través de /dev/input/event*. Si el mouse no funciona, verifique qué evento corresponde a su mouse con ls -l /dev/input/by-id/ y fuerce la detección exportando:
export QT_QPA_EVDEV_MOUSE_PARAMETERS=/dev/input/eventX

Escenario B: Ejecución en WSL (Windows Subsystem for Linux)

Requiere un servidor X en Windows (como VcXsrv o Xming).

# 1. Iniciar VcXsrv en Windows (deshabilitar control de acceso).

# 2. Exportar la variable DISPLAY (Redirección gráfica)
export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0

# 3. Ejecutar
python3 qspectrumanalyzer/__main__.py
