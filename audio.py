import moviepy.editor as mp
from scipy.io import wavfile
import sounddevice as sd
import Funcad


class AudioRecorder:

    # Audio class based on pyAudio and Wave
    def __init__(self):
        self.fc = Funcad.Funcad()

        self.opened = False
        self.rate = 44100
        self.channels = 2
        self.all_data = [[0, 0]]
        self.all_data_count = 0
        self.curr_frame_n = 0

    # Finishes the audio recording therefore the thread too
    def stop(self):
        if self.opened:
            sd.stop()

    # Launches the audio recording function using a thread
    def start(self, curr_frame: float, all_frames: float):
        if self.opened:
            self.curr_frame_n = self.fc.transfunc_coda(curr_frame, [0, all_frames], [0, self.all_data_count])
            sd.play(self.all_data[int(self.curr_frame_n):], self.rate)

    def open_file(self, path):
        video = mp.VideoFileClip(path)  # 2.
        video.audio.write_audiofile(r"audio.wav")
        fname = r'audio.wav'
        self.rate, self.all_data = wavfile.read(fname)
        self.all_data_count = len(self.all_data)
        self.opened = True


if __name__ == "__main__":
    a = AudioRecorder()
    a.open_file("video_1.mp4")
