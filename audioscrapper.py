from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip

def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(r'D:\traducidos\audio.mp3')
    
    return audio


# Lo añadimos al video con los subtitulos generados por el otro código

def add_audio(video_path, audio_path, final_video_name):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    
    # Save the video in the 'D:\traducidos\' folder

    video.write_videofile(r'D:\traducidos\{}.mp4'.format(final_video_name),codec='libx264', audio_codec='aac')


# video_path = r'D:\traducidos\coach_wang_disguise_backspin_no_spin_servenoaudio.mp4'
# audio_path = r'D:\traducidos\audio.mp3'
# final_video_name = 'coach_wang_disguise'
# add_audio(video_path, audio_path, final_video_name)












