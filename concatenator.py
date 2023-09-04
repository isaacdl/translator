from moviepy.editor import VideoFileClip, concatenate_videoclips
import os


def concatenate_videos(video1_path, video2_path, video3_path):
    # Carga los videos usando la clase VideoFileClip
    video1 = VideoFileClip(video1_path)
    video2 = VideoFileClip(video2_path)
    video3 = VideoFileClip(video3_path)

    # Combina los tres videos en uno solo
    final_video = concatenate_videoclips([video1, video2, video3])

    ruta_final = r'D:\tt4you\ready'
    ruta_final = os.path.join(ruta_final, video2_path.split('\\')[-1])
    

    # Exporta el video final
    final_video.write_videofile(ruta_final)
    print("Video final exportado correctamente")


