import cv2
import numpy as np
import time

# Variables globales para almacenar el ejercicio seleccionado y el conteo de repeticiones
selected_exercise = None
repetition_count = 0
repetition_status = ""
start_repetitions = False

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
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("repetition_stats.txt", "a", buffering=1) as file:
        file.write(f"{timestamp} - {exercise_name}: Repetition completed correctly\n")


# Función para mostrar el menú en pantalla
def draw_menu(frame, articulation_colors):
    """Dibuja un menú superpuesto que muestra los nombres de las articulaciones y sus colores correspondientes."""
    menu_x, menu_y = 10, 30  # Ajusta esta línea para mover el menú hacia abajo
    cv2.putText(frame, "Articulaciones y Colores:", (menu_x, menu_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    for i, (articulation, color) in enumerate(articulation_colors.items()):
        cv2.putText(frame, articulation, (menu_x, menu_y + 30 * (i + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Función para detectar pegatinas, dibujar líneas, calcular ángulos y mostrarlos en la consola
def detect_stickers_and_draw_lines():
    global selected_exercise, repetition_count, repetition_status, start_repetitions

    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    # Rango de colores para las pegatinas
    color_ranges = {
        'MUÑECA/RODILLA': ([90, 51, 70], [128, 255, 255]),    # Azul
        'CODO': ([129, 50, 70], [158, 255, 255]),     # Morado
        'HOMBRO': ([42, 47, 159], [50, 155, 200]),     # Verde
        'CINTURA': ([0, 163, 4], [0, 255, 255]),  # Rojo
        'TOBILLO': ([24, 145, 70], [36, 255, 255])    # Amarillo
    }

    # Colores para los centros
    articulation_colors = {
        'MUÑECA/RODILLA': (255, 0, 0),    # Azul
        'CODO': (255, 0, 255),    # Morado
        'HOMBRO': (0, 255, 0),    # Verde
        'CINTURA': (0, 0, 255),   # Rojo
        'TOBILLO': (0, 255, 255)  # Amarillo
    }

    print("\nPresiona 'q' para salir del programa.\n")
    print("Presiona 's' para empezar a contar repeticiones.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se puede leer el frame.")
            break

        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        centers = {}

        # Dibuja el menú en pantalla
        draw_menu(frame, articulation_colors)

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
           
        # Dibuja líneas y calcula ángulos para MUÑECA, CODO, HOMBRO
        angles = []
        if all(part in centers for part in ['MUÑECA/RODILLA', 'CODO', 'HOMBRO']):
            cv2.line(frame, centers['MUÑECA/RODILLA'], centers['CODO'], (255, 128, 0), 2)
            cv2.line(frame, centers['CODO'], centers['HOMBRO'], (255, 128, 0), 2)
            angle_codo = calcular_angulos(centers['MUÑECA/RODILLA'], centers['CODO'], centers['HOMBRO'])
            if angle_codo is not None:
                cv2.putText(frame, f"{int(angle_codo)}°", centers['CODO'], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                #print(f"Ángulo entre MUÑECA/RODILLA, CODO y HOMBRO: {int(angle_codo)}°")
                angles.append(angle_codo)

        # Dibuja líneas y calcula ángulos para HOMBRO, CINTURA, TOBILLO
        if all(part in centers for part in ['HOMBRO', 'CINTURA', 'TOBILLO']):
            cv2.line(frame, centers['HOMBRO'], centers['CINTURA'], (0, 255, 255), 2)
            cv2.line(frame, centers['CINTURA'], centers['TOBILLO'], (0, 255, 255), 2)
            angle_cintura = calcular_angulos(centers['HOMBRO'], centers['CINTURA'], centers['TOBILLO'])
            if angle_cintura is not None:
                cv2.putText(frame, f"{int(angle_cintura)}°", centers['CINTURA'], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
               # print(f"Ángulo entre HOMBRO, CINTURA y TOBILLO: {int(angle_cintura)}°")
                angles.append(angle_cintura)
        
        # Dibuja líneas y calcula ángulos para CODO, HOMBRO, CINTURA
        if all(part in centers for part in ['CODO', 'HOMBRO', 'CINTURA']):
            cv2.line(frame, centers['CODO'], centers['HOMBRO'], (0, 255, 255), 2)
            cv2.line(frame, centers['HOMBRO'], centers['CINTURA'], (0, 255, 255), 2)
            angle_cintura = calcular_angulos(centers['CODO'], centers['HOMBRO'], centers['CINTURA'])
            if angle_cintura is not None:
                cv2.putText(frame, f"{int(angle_cintura)}°", centers['CINTURA'], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                #print(f"Ángulo entre CODO, HOMBRO y CINTURA: {int(angle_cintura)}°")
                angles.append(angle_cintura)

        # Dibuja líneas y calcula ángulos para CINTURA, RODILLA, TOBILLO
        if all(part in centers for part in ['CINTURA', 'MUÑECA/RODILLA', 'TOBILLO']):
            cv2.line(frame, centers['CINTURA'], centers['MUÑECA/RODILLA'], (0, 255, 255), 2)
            cv2.line(frame, centers['MUÑECA/RODILLA'], centers['TOBILLO'], (0, 255, 255), 2)
            angle_rodilla = calcular_angulos(centers['CINTURA'], centers['MUÑECA/RODILLA'], centers['TOBILLO'])
            if angle_rodilla is not None:
                cv2.putText(frame, f"{int(angle_rodilla)}°", centers['MUÑECA/RODILLA'], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                #print(f"Ángulo entre CINTURA, RODILLA y TOBILLO: {int(angle_rodilla)}°")
                angles.append(angle_rodilla)

        # Llama a la función de umbrales correspondiente según el ejercicio seleccionado si se ha presionado 's'
        if start_repetitions:
            if selected_exercise == "Push-up":
                pushup_umbrales(angles)
            elif selected_exercise == "Squat":
                squat_umbrales(angles)
            elif selected_exercise == "Deadlift":
                deadlift_umbrales(angles)

            # Muestra el conteo de repeticiones y el estado
            cv2.putText(frame, f"Repeticiones: {repetition_count}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(frame, f"Estado: {repetition_status}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        else:
            cv2.putText(frame, "Presiona 's' para empezar", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Muestra el frame
        cv2.imshow("Frame", frame)

        # Verifica si se presionan teclas
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            print("\nSaliendo del programa...\n")
            break
        elif key == ord('s'):
            start_repetitions = True

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

#----------------------LOgica de Umbrales --------------------------------------
# Funciones de umbrales para diferentes ejercicios
def pushup_umbrales(angulos):
    global repetition_count, repetition_status
    goi_puntu = [170.0, 60.0, 170.0]
    behe_puntu = [40.0, 40.0, 170.0]
    goi, behe = True, False

    if len(angulos) > 2:
        while goi or behe:
            while goi:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[0] < behe_puntu[0]
                        and angulos[1] < behe_puntu[1]
                        and angulos[2] < behe_puntu[2]):
                    behe = True
                    goi = False
            while behe:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[0] > goi_puntu[0]
                        and angulos[1] > goi_puntu[1]
                        and angulos[2] > goi_puntu[2]):
                    goi = True
                    behe = False
                    repetition_count += 1
                    repetition_status = "Repetición bien hecha"
                    print("Se ha completado una repetición correctamente")
                    log_repetition("Push-up")

def squat_umbrales(angulos):
    global repetition_count, repetition_status
    goi_puntu = [175.0, 175.0]
    behe_puntu = [90.0, 90.0]
    goi, behe = True, False

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
                        and angulos[1] > goi_puntu[1]):
                    goi = True
                    behe = False
                    repetition_count += 1
                    repetition_status = "Repetición bien hecha"
                    print("Se ha completado una repetición correctamente")
                    log_repetition("Squat")

def deadlift_umbrales(angulos):
    global repetition_count, repetition_status
    goi_puntu = [175.0, 175.0, 0.0]
    behe_puntu = [130.0, 40.0, 20.0]
    goi, behe = True, False

    if len(angulos) > 2:
        while goi or behe:
            while goi:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[0] < behe_puntu[0]
                        and angulos[1] < behe_puntu[1]
                        and angulos[2] < behe_puntu[2]):
                    behe = True
                    goi = False
            while behe:
                if (angulos[0] is not None and angulos[1] is not None and angulos[2] is not None
                        and angulos[0] > goi_puntu[0]
                        and angulos[1] > goi_puntu[1]
                        and angulos[2] > goi_puntu[2]):
                    goi = True
                    behe = False
                    repetition_count += 1
                    repetition_status = "Repetición bien hecha"
                    print("Se ha completado una repetición correctamente")
                    log_repetition("Deadlift")

# Ejecuta la función
if __name__ == "__main__": 
    get_exercise_choice()
    detect_stickers_and_draw_lines()