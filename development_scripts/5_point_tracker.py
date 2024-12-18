import cv2
import numpy as np

def detect_stickers_and_draw_lines():
    # Inicializar la captura de video
    cap = cv2.VideoCapture(0)

    # Rango HSV para los colores detectados
    color_ranges = {
        'MUÑECA': ([90, 51, 70], [128, 255, 255]),    # Azul
        'CODO': ([129, 50, 70], [158, 255, 255]),     # Morado
        'HOMBRO': ([42, 47, 159], [50, 155, 200]),     # Verde
        'CINTURA': ([0, 155, 143], [0, 199, 255]),  # Rojo
        'TOBILLO': ([24, 145, 70], [36, 255, 255])    # Amarillo
    }

    # Orden de conexión entre puntos
    connection_order = ['MUÑECA', 'CODO', 'HOMBRO', 'CINTURA', 'TOBILLO']

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Redimensionar el frame para mejorar el rendimiento
        frame = cv2.resize(frame, (640, 480))

        # Convertir a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        centers = {}

        # Iterar sobre cada color para detectar los stickers
        for body_part, (lower, upper) in color_ranges.items():
            lower_hsv = np.array(lower)
            upper_hsv = np.array(upper)

            # Crear una máscara con el rango HSV específico
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

            # Aplicar filtros para reducir el ruido
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=1)

            # Encontrar contornos en la máscara
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Dibujar contornos y calcular centros
            for cnt in contours:
                # Asegurarse de que el contorno sea suficientemente grande
                if cv2.contourArea(cnt) > 300:
                    # Calcular el rectángulo delimitador
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    # Calcular el centro del rectángulo
                    cx = x + w // 2
                    cy = y + h // 2
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                    # Mostrar el nombre del punto y las coordenadas
                    text = f"{body_part} ({cx}, {cy})"
                    cv2.putText(frame, text, (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # Guardar el centro para conectar con líneas después
                    centers[body_part] = (cx, cy)

        # Dibujar líneas siguiendo el orden especificado
        for i in range(len(connection_order) - 1):
            part1 = connection_order[i]
            part2 = connection_order[i + 1]

            if part1 in centers and part2 in centers:
                cv2.line(frame, centers[part1], centers[part2], (0, 0, 255), 2)

        # Mostrar el frame original con anotaciones
        cv2.imshow("Frame", frame)

        # Salir al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Ejecutar la función
detect_stickers_and_draw_lines()