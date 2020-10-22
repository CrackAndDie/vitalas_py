import tkinter as tk
import threading
from PIL import Image, ImageTk
import cv2
import time
import Funcad
import audio


class Window:
    def __init__(self, root_in):
        # open-cv
        (self.major_ver, minor_ver, subminor_ver) = cv2.__version__.split('.')
        self.fps = 60
        self.video_ratio = 1.5
        self.total_video_frames = 0
        self.current_frame = 0

        # other
        self.root = root_in

        self.video_thread = None
        self.video_thread_stopped = True

        self.video = None
        self.video_loaded = False
        self.video_frame_size = (800, 500)

        # tkinter objects
        self.video_frame = None
        self.video_label = None
        self.img_for_start = None
        self.start_button = None
        self.img_for_pause = None
        self.pause_button = None
        self.img_for_da_right = None
        self.da_right_button = None
        self.img_for_da_left = None
        self.da_left_button = None
        self.img_for_scis = None
        self.scis_button = None
        self.scis_button_state = False
        self.img_for_green_mark = None
        self.green_mark_button = None
        self.green_mark_button_state = False
        self.img_for_red_mark = None
        self.red_mark_button = None
        self.red_mark_button_state = False

        self.canvas = None
        self.thumb = None
        self.thumb_x = 0

        self.start_mark = None
        self.start_mark_x = 0
        self.end_mark = None
        self.end_mark_x = 0

        # funcs
        self.fc = Funcad.Funcad()
        self.audio_class = audio.AudioRecorder()
        self.init_objects()

    def init_objects(self):
        self.video_frame = tk.Frame(self.root, width=800, height=800, bg="black")
        self.video_frame.pack_propagate(0)
        self.video_frame.place(x=40, y=40)
        self.video_label = tk.Label(self.video_frame, bg="gray")
        self.video_label.pack(fill=tk.BOTH, expand=1)

        self.img_for_start = tk.PhotoImage(file=r"img\start.png")
        self.start_button = tk.Button(self.root, image=self.img_for_start, width=30, height=30,
                                      command=self.start_video)
        self.start_button.place(x=80, y=3)

        self.img_for_pause = tk.PhotoImage(file=r"img\pause.png")
        self.pause_button = tk.Button(self.root, image=self.img_for_pause, width=30, height=30,
                                      command=self.pause_video)
        self.pause_button.place(x=120, y=3)

        self.img_for_da_left = tk.PhotoImage(file=r"img\da_left.png")
        self.da_left_button = tk.Button(self.root, image=self.img_for_da_left, width=30, height=30,
                                        command=self.to_the_start)
        self.da_left_button.place(x=40, y=3)

        self.img_for_da_right = tk.PhotoImage(file=r"img\da_right.png")
        self.da_right_button = tk.Button(self.root, image=self.img_for_da_right, width=30, height=30,
                                         command=self.to_the_end)
        self.da_right_button.place(x=160, y=3)

        self.img_for_scis = tk.PhotoImage(file=r"img\scis2.png")
        self.scis_button = tk.Button(self.root, image=self.img_for_scis, width=30, height=30, bg="#cccccc",
                                     command=self.change_scis_state)
        self.scis_button.place(x=240, y=3)
        self.img_for_green_mark = tk.PhotoImage(file=r"img\green_mark.png")
        self.green_mark_button = tk.Button(self.root, image=self.img_for_green_mark, width=30, height=30, bg="#cccccc",
                                           state=tk.DISABLED, command=self.change_green_state)
        self.green_mark_button.place(x=280, y=3)
        self.img_for_red_mark = tk.PhotoImage(file=r"img\red_mark.png")
        self.red_mark_button = tk.Button(self.root, image=self.img_for_red_mark, width=30, height=30, bg="#cccccc",
                                         state=tk.DISABLED, command=self.change_red_state)
        self.red_mark_button.place(x=320, y=3)

        self.canvas = tk.Canvas(self.root, bg="black", width=600, height=60)
        self.canvas.bind('<B1-Motion>', self.move_on_canvas)
        self.canvas.place(x=40, y=400)
        self.thumb = self.canvas.create_rectangle([0, 0, 20, 60], fill='#555555', outline='#444444', width=3)
        self.start_mark = self.canvas.create_rectangle([0, 0, 6, 60], fill='green')
        self.end_mark = self.canvas.create_rectangle([0, 0, 6, 60], fill='red')
        self.canvas.itemconfigure(self.start_mark, state='hidden')
        self.canvas.itemconfigure(self.end_mark, state='hidden')

    def video_stream(self):
        _, frame = self.video.read()
        str_time = time.time()
        while frame is not None and getattr(self.video_thread, "running", True):
            self.current_frame += 1

            # resize and set image to label
            frame = cv2.resize(frame, self.video_frame_size)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
            self.video_label.config(image=imgtk)
            self.video_label.image = imgtk

            # waiting for frame rate
            while time.time() - str_time < (1 / self.fps):
                pass
            str_time = time.time()

            # reading next frame
            _, frame = self.video.read()
            # print("still in loop")
        # print("exited from loop")
        # self.video_thread = None

    def set_frame_to_label(self):
        _, frame = self.video.read()
        frame = cv2.resize(frame, self.video_frame_size)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
        self.video_label.config(image=imgtk)
        self.video_label.image = imgtk

    def start_video(self):
        if self.video is not None:
            self.video_thread_stopped = False
            try:
                if not self.video_thread.is_alive():
                    self.video_thread = threading.Thread(target=self.video_stream)
                    # self.video_thread.daemon = 1
                    # start audio
                    self.audio_class.start(self.current_frame, self.total_video_frames)
                    # start thread
                    self.video_thread.start()
            except AttributeError:
                if self.video_thread is None:
                    self.video_thread = threading.Thread(target=self.video_stream)
                    # self.video_thread.daemon = 1
                    # start audio
                    self.audio_class.start(self.current_frame, self.total_video_frames)
                    # start thread
                    self.video_thread.start()

    def pause_video(self):
        if self.video_loaded:
            self.video_thread_stopped = True
            if self.video_thread is not None:
                # stop audio
                self.audio_class.stop()
                print("audio stopped")

                # stop video
                self.video_thread.running = False
                print("video stopped")
                # print('before join')
                start_time = time.time()
                while self.video_thread.is_alive():
                    # print("waiting for none")
                    if time.time() - start_time > 1:
                        # self.video_thread = None
                        break
                self.video_thread.join()
                # print('after join')

    def to_the_start(self):
        self.pause_video()

        self.current_frame = 0
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        self.set_frame_to_label()

    def to_the_end(self):
        self.pause_video()

        self.current_frame = self.total_video_frames - 1
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        self.set_frame_to_label()

    def open_video_file(self, path: str):
        self.video = cv2.VideoCapture(path)
        self.video_loaded = True

        # getting frame rate
        if int(self.major_ver) < 3:
            self.fps = self.video.get(cv2.cv.CV_CAP_PROP_FPS)
        else:
            self.fps = self.video.get(cv2.CAP_PROP_FPS)

        # getting sides depends
        wid = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        hei = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.video_ratio = wid / hei

        # getting total frames of video
        self.total_video_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        # audio
        self.audio_class.open_file(path)

    def move_on_canvas(self, event=None):
        # move thumb
        if event is not None and self.video_thread_stopped and not self.scis_button_state:
            new_x = event.x - 10
            if self.fc.in_range_bool(new_x, 0, self.video_frame_size[0]-20):
                self.canvas.move(self.thumb, new_x - self.thumb_x, 0)
                self.thumb_x = new_x

                self.current_frame = self.fc.transfunc_coda(new_x - 1, [0, self.video_frame_size[0]-20], [0, self.total_video_frames])
                self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

                self.set_frame_to_label()

        # move green
        if event is not None and self.scis_button_state and self.green_mark_button_state:
            new_x = event.x - 3
            if self.fc.in_range_bool(new_x, 0, self.video_frame_size[0]-6):
                self.canvas.move(self.start_mark, new_x - self.start_mark_x, 0)
                self.start_mark_x = new_x

                self.current_frame = self.fc.transfunc_coda(new_x - 1, [0, self.video_frame_size[0]-6], [0, self.total_video_frames])
                self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

                self.set_frame_to_label()

        # move red
        if event is not None and self.scis_button_state and self.red_mark_button_state:
            new_x = event.x - 3
            if self.fc.in_range_bool(new_x, 0, self.video_frame_size[0] - 6):
                self.canvas.move(self.end_mark, new_x - self.end_mark_x, 0)
                self.end_mark_x = new_x

                self.current_frame = self.fc.transfunc_coda(new_x - 1,
                    [0, self.video_frame_size[0] - 6], [0, self.total_video_frames])
                self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

                self.set_frame_to_label()

    def change_scis_state(self):
        self.scis_button_state = not self.scis_button_state
        if self.scis_button_state:
            self.pause_video()
            self.canvas.itemconfigure(self.thumb, state='hidden')
            self.canvas.itemconfigure(self.start_mark, state='normal')
            self.canvas.itemconfigure(self.end_mark, state='normal')
            self.scis_button.config(bg="#444444")
            self.green_mark_button.config(state="normal")
            self.red_mark_button.config(state="normal")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.da_right_button.config(state=tk.DISABLED)
            self.da_left_button.config(state=tk.DISABLED)
        else:
            self.change_green_state(change_to=False)
            self.change_red_state(change_to=False)
            self.canvas.itemconfigure(self.thumb, state='normal')
            self.canvas.itemconfigure(self.start_mark, state='hidden')
            self.canvas.itemconfigure(self.end_mark, state='hidden')
            self.scis_button.config(bg="#cccccc")
            self.green_mark_button.config(state=tk.DISABLED)
            self.red_mark_button.config(state=tk.DISABLED)
            self.start_button.config(state="normal")
            self.pause_button.config(state="normal")
            self.da_right_button.config(state="normal")
            self.da_left_button.config(state="normal")

    def change_green_state(self, change_to=None):
        if change_to is None:
            self.green_mark_button_state = not self.green_mark_button_state
        else:
            self.green_mark_button_state = change_to
        if self.green_mark_button_state:
            self.green_mark_button.config(bg="#444444")
            self.red_mark_button.config(state=tk.DISABLED)
        else:
            self.green_mark_button.config(bg="#cccccc")
            self.red_mark_button.config(state="normal")

    def change_red_state(self, change_to=None):
        if change_to is None:
            self.red_mark_button_state = not self.red_mark_button_state
        else:
            self.red_mark_button_state = change_to
        if self.red_mark_button_state:
            self.red_mark_button.config(bg="#444444")
            self.green_mark_button.config(state=tk.DISABLED)
        else:
            self.red_mark_button.config(bg="#cccccc")
            self.green_mark_button.config(state="normal")

    def update_window(self):
        wid = self.root.winfo_width()
        hei = self.root.winfo_height()

        self.video_frame_size = (wid-200, int((wid - 200) / self.video_ratio))
        self.video_frame.config(width=self.video_frame_size[0], height=self.video_frame_size[1])

        self.canvas.config(width=self.video_frame_size[0])
        self.canvas.place(y=(self.video_frame_size[1] + 60))

        if not self.video_thread_stopped:
            new_x_pos_thumb = self.fc.transfunc_coda(self.current_frame, [0, self.total_video_frames], [0, self.video_frame_size[0]-20])
            self.canvas.move(self.thumb, new_x_pos_thumb - self.thumb_x, 0)
            self.thumb_x = new_x_pos_thumb

        root.after(100, self.update_window)

    def on_window_close(self):
        self.pause_video()
        # print("thread stopped")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk(className="Vitalas")
    root.geometry("800x500")
    root.minsize(800, 500)
    root.configure(bg="#666666")

    w = Window(root)
    root.protocol("WM_DELETE_WINDOW", w.on_window_close)
    w.open_video_file("video_1.mp4")
    # w.start_video()

    root.after(100, w.update_window)
    root.mainloop()
