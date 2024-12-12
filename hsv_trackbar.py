import cv2
import numpy as np

def detect_hsv_and_draw():
    # Inicializar la captura de video
    cap = cv2.VideoCapture(0)
    
    # Crear una ventana para los controles de calibración HSV
    cv2.namedWindow("HSV Calibration")

    # Función vacía para los trackbars
    def nothing(x):
        pass

    # Crear sliders para ajustar los rangos HSV
    cv2.createTrackbar("H Min", "HSV Calibration", 0, 179, nothing)
    cv2.createTrackbar("H Max", "HSV Calibration", 179, 179, nothing)
    cv2.createTrackbar("S Min", "HSV Calibration", 0, 255, nothing)
    cv2.createTrackbar("S Max", "HSV Calibration", 255, 255, nothing)
    cv2.createTrackbar("V Min", "HSV Calibration", 0, 255, nothing)
    cv2.createTrackbar("V Max", "HSV Calibration", 255, 255, nothing)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Redimensionar el frame para mejorar el rendimiento
        frame = cv2.resize(frame, (640, 480))
        
        # Convertir a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Leer los valores de los sliders
        h_min = cv2.getTrackbarPos("H Min", "HSV Calibration")
        h_max = cv2.getTrackbarPos("H Max", "HSV Calibration")
        s_min = cv2.getTrackbarPos("S Min", "HSV Calibration")
        s_max = cv2.getTrackbarPos("S Max", "HSV Calibration")
        v_min = cv2.getTrackbarPos("V Min", "HSV Calibration")
        v_max = cv2.getTrackbarPos("V Max", "HSV Calibration")
        
        # Crear el rango HSV
        lower_hsv = np.array([h_min, s_min, v_min])
        upper_hsv = np.array([h_max, s_max, v_max])
        
        # Crear una máscara con el rango HSV
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
            if cv2.contourArea(cnt) > 300:#500
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
                text = f"({cx}, {cy})"
                cv2.putText(frame, text, (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Mostrar la máscara y el frame original con anotaciones
        cv2.imshow("Mask", mask)
        cv2.imshow("Frame", frame)
        
        # Salir al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Ejecutar la función
detect_hsv_and_draw()