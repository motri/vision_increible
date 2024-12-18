# Exercise Tracker

Este proyecto es una aplicación de seguimiento de ejercicios que utiliza visión por computadora para detectar articulaciones y contar repeticiones de ejercicios como sentadillas, peso muerto y flexiones. La aplicación también proporciona retroalimentación de audio para corregir la postura.

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener instaladas las siguientes dependencias. Puedes instalarlas utilizando `pip`:

```sh
pip install -r requirements.txt
```
# Uso

## Para ejecutar la aplicación, sigue estos pasos:
1. Clona el repositorio o descarga los archivos del proyecto.
2. Asegúrate de tener una cámara conectada a tu computadora.
3. Ejecuta el archivo `app.py` para iniciar la aplicación de seguimiento de ejercicios.

---

# Navegación del Menú

### Seleccionar Ejercicio
- Al iniciar la aplicación, se mostrará un menú para seleccionar el ejercicio que deseas realizar.
- Puedes elegir entre:
  - **"Squat"**
  - **"Deadlift"**
  - **"Push-up"**

### Iniciar Seguimiento
- Después de seleccionar un ejercicio, haz clic en el botón **"Start Tracking"** para comenzar a contar las repeticiones.
- La cámara se activará y comenzará a detectar las articulaciones.

### Detener Seguimiento
- Para detener el seguimiento y volver al menú principal, haz clic en el botón **"Stop"**.

### Cerrar la Aplicación
- Para cerrar la aplicación, simplemente cierra la ventana o haz clic en el botón de cierre de la ventana.

---

# Funcionalidades

### 1. **Detección de Articulaciones**
- La aplicación detecta las articulaciones utilizando pegatinas de colores.
- Calcula los ángulos entre las articulaciones detectadas.

### 2. **Conteo de Repeticiones**
- Cuenta las repeticiones de los ejercicios seleccionados.
- Proporciona retroalimentación de audio cuando se completa una repetición correctamente.

### 3. **Corrección de Postura**
- Detecta si la postura es incorrecta.
- Reproduce un mensaje de audio para corregir la postura.

---

# Archivos Principales

- **`app.py`**:
  - Contiene la lógica principal de la aplicación y la interfaz de usuario.
- **`video_processing.py`**:
  - Maneja la captura de video y el procesamiento de los frames para detectar articulaciones y contar repeticiones.
- **`joint_detection.py`**:
  - Contiene la lógica para detectar las articulaciones basadas en los rangos de colores HSV.
- **`audio_feedback.py`**:
  - Proporciona retroalimentación de audio utilizando la biblioteca `pygame`.
- **`rep_counter.py`**:
  - Contiene la lógica para contar las repeticiones de los ejercicios.
- **`posture_checker.py`**:
  - Contiene la lógica para verificar la postura y proporcionar retroalimentación de corrección.
