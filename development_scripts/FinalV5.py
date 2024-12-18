import cv2
import numpy as np
import time

# Variables globales para almacenar el ejercicio seleccionado y el conteo de repeticiones
selected_exercise = None
repetition_count = 0
repetition_status = ""

# Función para calcular ángulos
def calcular_angulos(a, b, c):
    """Calcula el ángulo formado por tres puntos a, b, c."""
    if a is None or b is None or c is None:
        return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ab, cb = a - b, c - b
    cosine = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    cosine = np.clip(cosine, -1.0, 1.0)
    angle = np.arccos(cosine)
    return np.degrees(angle)

# Función para registrar estadísticas en un archivo
def log_repetition(exercise_name):
    """Registra la repetición completada en un archivo con la fecha y hora."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("repetition_stats.txt", "a") as file:
        file.write(f"{timestamp} - {exercise_name}: Repetición completada correctamente\n")

# Función para mostrar el menú en pantalla
def draw_menu(frame, articulation_colors):
    """Dibuja un menú superpuesto que muestra los nombres de las articulaciones y sus colores correspondientes."""
    menu_x, menu_y = 10, 30  # Ajusta esta línea para mover el menú hacia abajo
    cv2.putText(frame, "Articulaciones y Colores:", (menu_x, menu_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    for i, (articulation, color) in enumerate(articulation_colors.items()):
        cv2.putText(frame, articulation, (menu_x, menu_y + 30 * (i + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Función para detectar pegatinas, dibujar líneas, calcular ángulos y mostrarlos en la consola
def detect_stickers_and_draw_lines():
    global selected_exercise, repetition_count, repetition_status

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    # Rango de colores para las pegatinas
    color_ranges = {
        'CODO/RODILLA': ([91, 87, 144], [124, 153, 250]),    # Azul
        'MUÑECA': ([112, 54, 114], [129, 177, 255]),     # Morado
        'HOMBRO': ([35, 118, 139], [45, 160, 203]),     # Verde
        'CINTURA': ([0, 141, 92], [17, 179, 255]),  # Rojo
        'TOBILLO': ([0, 193, 151], [39, 255, 199])    # Amarillo
    }

    # Colores para los centros
    articulation_colors = {
        'CODO/RODILLA': (255, 0, 0),    # Azul
        'MUÑECA': (255, 0, 255),    # Morado
        'HOMBRO': (0, 255, 0),    # Verde
        'CINTURA': (0, 0, 255),   # Rojo
        'TOBILLO': (0, 255, 255)  # Amarillo
    }

    # Configuraciones de ángulos para cada ejercicio
    exercise_angles = {
        "Push-up": [
            ['TOBILLO', 'CINTURA', 'HOMBRO'], # ángulo 1 alpha 
            ['CINTURA', 'HOMBRO', 'CODO/RODILLA'],    # ángulo 2 beta  No hace falta compribarlo
            ['HOMBRO', 'CODO/RODILLA', 'MUÑECA'] # ángulo 3 omega 
        ],
        "Squat": [
            ['TOBILLO', 'CODO/RODILLA', 'CINTURA'], # ángulo 1 alpha 
            [ 'CODO/RODILLA','CINTURA', 'HOMBRO']   # ángulo 2 Beta 
        ],
        "Deadlift": [
            ['TOBILLO', 'CODO/RODILLA', 'CINTURA'], # ángulo 1 alpha 
            [ 'CODO/RODILLA','CINTURA', 'HOMBRO']  # ángulo 2 Beta 
        ]
    }

    print("\nPresiona 'q' para salir del programa.\n")

    while True:
        # Captura un frame de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error: No se puede leer el frame.")
            break
        goi=True
        behe=False
        # Redimensiona el frame y lo convierte a HSV
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        centers = {}

        # Dibuja el menú en pantalla
        draw_menu(frame, articulation_colors)

        # Detecta las pegatinas en el frame
        for body_part, (lower, upper) in color_ranges.items():
            lower_hsv = np.array(lower)
            upper_hsv = np.array(upper)

            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > 200:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx = x + w // 2
                    cy = y + h // 2
                   
                    cv2.circle(frame, (cx, cy), 8, articulation_colors[body_part], -1)
                    centers[body_part] = (cx, cy)
                    cv2.drawContours(frame, [cnt], -1, (0, 255, 255), 2)
           
        # Calcula los ángulos según el ejercicio seleccionado
        angles_dict = {}
        if selected_exercise in exercise_angles:
            for i, angle_config in enumerate(exercise_angles[selected_exercise]):
                if all(part in centers for part in angle_config):
                    a, b, c = centers[angle_config[0]], centers[angle_config[1]], centers[angle_config[2]]
                    angle = calcular_angulos(a, b, c)
                    if angle is not None:
                        cv2.line(frame, a, b, (255, 128, 0), 2)
                        cv2.line(frame, b, c, (255, 128, 0), 2)
                        cv2.putText(frame, f"{int(angle)}°", b, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        angles_dict[i] = angle

        # Verifica si se han conseguido todos los ángulos necesarios
        if len(angles_dict) == len(exercise_angles[selected_exercise]):
            # Convierte el diccionario de ángulos en una lista ordenada
            angles = [angles_dict[i] for i in sorted(angles_dict.keys())]
            print("TODOS LOS ANGULOS DETECTADOS")
            # Llama a la función de umbrales correspondiente según el ejercicio seleccionado
            if selected_exercise == "Push-up":
                goi,behe= pushup_umbrales(angles,goi,behe)
            elif selected_exercise == "Squat":
                goi,behe=squat_umbrales(angles,goi,behe)
            elif selected_exercise == "Deadlift":
                goi,behe=deadlift_umbrales(angles,goi,behe)
        else:
            print('Esperando  todos los angulos ')

        # Muestra el conteo de repeticiones y el estado
        cv2.putText(frame, f"Repeticiones: {repetition_count}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Estado: {repetition_status}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Muestra el frame
        cv2.imshow("Frame", frame)

        # Verifica si se presionan teclas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nSaliendo del programa...\n")
            break

    cap.release()
    cv2.destroyAllWindows()

# Función para mostrar el menú en la consola y obtener la elección del usuario
def get_exercise_choice():
    global selected_exercise
    print("Selecciona el ejercicio:")
    print("1. Push-up")
    print("2. Deadlift")
    print("3. Squat")
    choice = input("Ingresa el número del ejercicio: ")
    if choice == '1':
        selected_exercise = "Push-up"
    elif choice == '2':
        selected_exercise = "Deadlift"
    elif choice == '3':
        selected_exercise = "Squat"
    else:
        print("Opción no válida. Seleccionando Push-up por defecto.")
        selected_exercise = "Push-up"

# Funciones de umbrales para diferentes ejercicios
def pushup_umbrales(angulos,goi,behe):
    global repetition_count, repetition_status
    goi_puntu = [170.0, 60.0, 140.0]
    behe_puntu = [40.0, 30.0, 70.0]
    

    if len(angulos) > 2:
        while goi or behe:
            while goi:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[1] < behe_puntu[1]
                        and angulos[2] < behe_puntu[2]):
                    behe = True
                    goi = False
            while behe:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[1] > goi_puntu[1]
                        and angulos[2] > goi_puntu[2]):
                    goi = True
                    behe = False
                    repetition_count += 1
                    repetition_status = "Repetición bien hecha"
                    print("Se ha completado una repetición correctamente")
                    log_repetition("Push-up")
    return goi, behe

def squat_umbrales(angulos,goi,behe):
    global repetition_count, repetition_status
    goi_puntu = [150.0, 150.0]
    behe_puntu = [110.0, 110.0]
    

    if len(angulos) > 1:
        if behe:
            if (angulos[0] is not None and angulos[1] is not None
                    and angulos[0] < behe_puntu[0]
                    and angulos[1] < behe_puntu[1]):
                print("Estas arriba")
                goi = True
                behe = False
        if goi:    
            if (angulos[0] is not None and angulos[1] is not None
                    and angulos[0] > goi_puntu[0]
                    and angulos[1] > goi_puntu[1]):
                repetition_count += 1
                repetition_status = "Repetición bien hecha"
                print("Se ha completado una repetición correctamente")
                log_repetition("Squat")
                goi = False
                behe = True
    
    return goi, behe

def deadlift_umbrales(angulos,goi,behe):
    global repetition_count, repetition_status
    goi_puntu = [150.0, 150.0]
    behe_puntu = [100.0, 90.0]
   

    if len(angulos) > 1:
        while goi or behe:
            while goi:
                if (angulos[0] is not None and angulos[1] is not None 
                        and angulos[0] < behe_puntu[0]
                        and angulos[1] < behe_puntu[1]):
                    behe = True
                    goi = False
            while behe:
                if (angulos[0] is not None and angulos[1] is not None 
                        and angulos[0] > goi_puntu[0]
                        and angulos[1] > goi_puntu[1] ):
                    goi = True
                    behe = False
                    repetition_count += 1
                    repetition_status = "Repetición bien hecha"
                    print("Se ha completado una repetición correctamente")
                    log_repetition("Deadlift")
    return goi, behe

# Ejecuta la función principal
if __name__ == "__main__":
    get_exercise_choice()
    detect_stickers_and_draw_lines()
