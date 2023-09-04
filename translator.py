import cv2
import os
import io
from google.cloud import vision
from google.cloud import translate_v2 as translate
from audioscrapper import *
import re
import numpy as np



def translate_image(image,client_vision,client_translate,source_lang,target_lang):
    
    img_bytes = io.BytesIO(image)
    # Detect text in the image
    image = vision.Image(content=img_bytes.getvalue())
    response = client_vision.text_detection(image=image)
    texts = response.text_annotations

    # Extract the text and translate it
    if len(texts) > 0:
        text = texts[0].description
        translation = client_translate.translate(text, source_language=source_lang, target_language=target_lang)
        return translation['translatedText']
    else:
        return None
    
def selectframe (video_path,time_sec):
    # Open the video file
    
    cap = cv2.VideoCapture(video_path)

    # Get the video properties
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set the frame position to the desired time
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)

    # Read the frame at the desired time
    ret, frame = cap.read()
    return frame

def selectROIs(frame, time_sec):

    # Select a ROI for the Chinese text, but if the user press q close the window, time_sec += 10 and try again
    while True:
        roichino = cv2.selectROI("Select ROI for Chinese text", frame, fromCenter=False, showCrosshair=True)
        if roichino == (0,0,0,0):
            time_sec += 10
            frame = selectframe(video_path,time_sec)
            continue
        else:
            break

    # Select a ROI for the English text

    roienglish = cv2.selectROI("Select ROI for translated text", frame, fromCenter=False, showCrosshair=True)

    # Destroy the windows
    cv2.destroyAllWindows()
    return frame,roichino,roienglish


def translation(frame,roichino,roienglish):
    subschino = frame[int(roichino[1]):int(roichino[1]+roichino[3]), int(roichino[0]):int(roichino[0]+roichino[2])]
    
    frame_bytes = cv2.imencode('.jpg',  subschino)[1].tobytes()

    # cv2.imshow('frame',subschino)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    while True:
        global color
        global show_text
        if color == 'yellow':
            # Parámetros para el color amarillo
            lower_yellow = np.array([0, 100, 100])
            upper_yellow = np.array([90, 255, 255])
            yellow_mask = cv2.inRange(subschino, lower_yellow, upper_yellow)
            yellow_image = cv2.bitwise_and(subschino, subschino, mask=yellow_mask)
            if show_text:
                cv2.imshow('solo_texto', yellow_image)
                show_text = False
        else:
            # Parámetros para el color blanco
            lower_white = np.array([200, 200, 200])
            upper_white = np.array([255, 255, 255])
            white_mask = cv2.inRange(subschino, lower_white, upper_white)
            white_image = cv2.bitwise_and(subschino, subschino, mask=white_mask)
            if show_text:
                cv2.imshow('solo_texto', white_image)
                show_text = False

        key = cv2.waitKey(0)
        if key == ord('n'):
            # Cambiar el color mostrado si se presiona la tecla 'n'
            color = 'white' if color == 'yellow' else 'yellow'
        elif key == 27:  # Presionar la tecla 'Esc' para salir del bucle
            break


    # Close the window
    cv2.destroyAllWindows()            
    # Call the translate_image function to generate a translation for the frame
    translated_text = translate_image(frame_bytes,client_vision,client_translate,source_lang,target_lang)


    # Check if there is some apostrophe in the text to avoid 
    if translated_text is not None:

        reemplazos = {
            "pull": "loop",
            "hair": "serve",
            "high-profile": "high arc",
            # Agrega más palabras y sus sustituciones aquí
        }


        print_translated_text = translated_text.replace("&#39;", "'")
        palabras = print_translated_text.split()

        # Aplicamos el reemplazo de palabras según el diccionario
        palabras_reemplazadas = [reemplazos[palabra] if palabra in reemplazos else palabra for palabra in palabras]

        # Creamos una nueva lista con las palabras que no están completamente en mayúsculas
        nuevas_palabras = [palabra for palabra in palabras_reemplazadas if not (palabra.isupper() or re.search(r'\d{3}', palabra))]

        # Unimos las palabras en un nuevo string
        print_translated_text = " ".join(nuevas_palabras)

        
        
    # Resto del código que utiliza print_translated_text
    else:
        print_translated_text = ""

    return print_translated_text

def write_translation_text(translated_text, roienglish, frame):
    # Draw the translated text on top of the original image
    if translated_text is not None:
        # Define el tamaño de la fuente y el espaciado entre líneas
        font_size = 1.0
        line_spacing = 30
        outline_color = (0, 0, 0) # borde negro
        text_color = (0,255,255) # texto en amarillo

        # Obtener el tamaño del texto en píxeles
        text_size, _ = cv2.getTextSize(translated_text, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness=2)
        
        # Calcular la posición del texto para que esté centrado verticalmente en el ROI
        y_center = roienglish[1] + roienglish[3] // 2
        y_start = y_center - (text_size[1] + line_spacing) // 2

        # Si el texto es demasiado largo para caber en una línea, dividirlo en dos líneas
        if text_size[0] > roienglish[2]:
            # Divide la cadena en palabras
            words = translated_text.split()
    
            # Divide las palabras en dos líneas
            line1 = ""
            line2 = ""
            for word in words:
                if cv2.getTextSize(line1 + word + " ", cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness=2)[0][0] < roienglish[2]:
                    line1 += word + " "
                else:
                    line2 += word + " "
            
            # Dibuja las dos líneas de texto
            text_size1, _ = cv2.getTextSize(line1.strip(), cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness=2)
            text_size2, _ = cv2.getTextSize(line2.strip(), cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness=2)
            
            x_start = roienglish[0] + (roienglish[2] - text_size1[0]) // 2
            x_start2 = roienglish[0] + (roienglish[2] - text_size2[0]) // 2
            y_start2 = y_start + text_size1[1] + line_spacing

            cv2.putText(frame, line1.strip(), (x_start, y_start + text_size1[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size, outline_color, 4, cv2.LINE_AA)
            cv2.putText(frame, line1.strip(), (x_start, y_start + text_size1[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)

            cv2.putText(frame, line2.strip(), (x_start2, y_start2 + text_size2[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size, outline_color, 4, cv2.LINE_AA)
            cv2.putText(frame, line2.strip(), (x_start2, y_start2 + text_size2[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
            
        else:
            # Dibuja una línea de texto centrada horizontalmente en el ROI
            x_start = roienglish[0] + (roienglish[2] - text_size[0]) // 2
            cv2.putText(frame, translated_text, (x_start, y_start + text_size[1]),cv2.FONT_HERSHEY_SIMPLEX, font_size, outline_color, 4, cv2.LINE_AA)
            cv2.putText(frame, translated_text, (x_start, y_start + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
    return frame



# Set up Google Cloud API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\Isaac\Documents\Python Scripts\translator\googlecredentials.json'


# Instantiates a client
client_vision = vision.ImageAnnotatorClient()
client_translate = translate.Client()

# Set the source and target language codes
source_lang = 'zh-CN'
target_lang = 'en'

# Set the color of the text to be detected
color = 'yellow'
show_text = True

# Set the video path and the frame we will use to select the ROI for the chinese text and the ROI for the translated text
video_name = 'weight_transfer_forehand.mp4'
video_path = r'C:\Users\Isaac\Downloads'
video_path = os.path.join(video_path,video_name)
print(video_path)

time_sec = 30
frame = selectframe(video_path,time_sec)
frame,roichino,roienglish = selectROIs(frame,time_sec)
translated_text = translation(frame,roichino,roienglish)

# Write the translated text on top of the original image

frame = write_translation_text(translated_text,roienglish, frame)

# Display the image with the translated text to a 1200x720 window

cv2.imshow('frame',frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


