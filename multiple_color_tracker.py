import cv2
import numpy as np

def detect_stickers_and_draw_lines():
    # Inicializar la captura de video
    cap = cv2.VideoCapture(0)

    # Rango HSV para los colores detectados
    color_ranges = {
        'Yellow': ([12, 145, 70], [50, 255, 255]),
        'Green': ([36, 50, 70], [89, 255, 255]),
        'Red': ([0, 166, 165], [179, 255, 255]),
        'Blue': ([90, 51, 70], [128, 255, 255])
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Redimensionar el frame para mejorar el rendimiento
        frame = cv2.resize(frame, (640, 480))

        # Convertir a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        centers = []

        # Iterar sobre cada color para detectar los stickers
        for color_name, (lower, upper) in color_ranges.items():
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

                    # Dibujar el contorno
                    cv2.drawContours(frame, [cnt], -1, (0, 255, 255), 2)

                    # Mostrar las coordenadas del centro
                    text = f"{color_name} ({cx}, {cy})"
                    cv2.putText(frame, text, (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # Guardar el centro para conectar con líneas después
                    centers.append((cx, cy))

        # Dibujar líneas entre los centros detectados
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                cv2.line(frame, centers[i], centers[j], (0, 0, 255), 2)

        # Mostrar el frame original con anotaciones
        cv2.imshow("Frame", frame)

        # Salir al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Ejecutar la función
detect_stickers_and_draw_lines()