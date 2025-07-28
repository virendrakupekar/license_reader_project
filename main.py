from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics.texture import Texture
from kivy.clock import Clock, mainthread
from kivy.core.image import Image as CoreImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.base import EventLoop

from io import BytesIO
import cv2
import numpy as np
from threading import Thread, Lock
import atexit

from utils.detector import detect_license_plate
from utils.file_logger import log_entry, read_log_entries


class LicensePlateApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.image = Image(allow_stretch=True, keep_ratio=False)
        self.label = Label(text="No license plate detected yet.")
        self.choose_btn = Button(text="Choose Image")
        self.camera_btn = Button(text="Use Camera")
        self.capture_btn = Button(text="Capture", disabled=True)
        self.logs_btn = Button(text="Show Logs")

        self.choose_btn.bind(on_press=self.open_filechooser)
        self.camera_btn.bind(on_press=self.start_camera)
        self.capture_btn.bind(on_press=self.capture_frame)
        self.logs_btn.bind(on_press=self.show_logs)

        self.add_widget(self.image)
        self.add_widget(self.label)
        self.add_widget(self.choose_btn)
        self.add_widget(self.camera_btn)
        self.add_widget(self.capture_btn)
        self.add_widget(self.logs_btn)

        self.capture = None
        self.frame = None
        self.camera_running = False
        self.camera_thread = None
        self.lock = Lock()

        EventLoop.window.bind(on_close=self.on_app_close)
        atexit.register(self.stop_camera)

    def stop_camera(self):
        self.camera_running = False
        self.capture_btn.disabled = True
        with self.lock:
            if self.capture and self.capture.isOpened():
                self.capture.release()
                self.capture = None

    def open_filechooser(self, instance):
        self.stop_camera()
        self.clear_widgets()
        self.chooser = FileChooserIconView()
        self.chooser.bind(on_submit=self.load_image)
        self.add_widget(self.chooser)

    def load_image(self, chooser, selection, touch):
        if selection:
            image_path = selection[0]
            self.chooser.unbind(on_submit=self.load_image)
            self.restore_ui()
            Clock.schedule_once(lambda dt: self.display_and_detect(image_path), 0)

    def start_camera(self, instance):
        self.restore_ui()
        self.stop_camera()

        self.capture = cv2.VideoCapture(0)
        if not self.capture or not self.capture.isOpened():
            self.label_update("Error: Could not access camera.")
            return

        self.camera_running = True
        self.capture_btn.disabled = False
        self.camera_thread = Thread(target=self.camera_loop, daemon=True)
        self.camera_thread.start()

    def camera_loop(self):
        while self.camera_running:
            ret, frame = self.capture.read()
            if not ret:
                continue
            with self.lock:
                self.frame = frame
            Clock.schedule_once(self.prepare_texture, 0)

    @mainthread
    def prepare_texture(self, dt):
        with self.lock:
            if self.frame is None:
                return
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 480))
            flipped = cv2.flip(frame_resized, 0)
            texture = Texture.create(size=(flipped.shape[1], flipped.shape[0]), colorfmt='rgb')
            texture.blit_buffer(flipped.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture

    def capture_frame(self, instance):
        with self.lock:
            if self.frame is None:
                self.label_update("No frame to capture.")
                return
            cv2.imwrite("captured_frame.jpg", self.frame)
        Clock.schedule_once(lambda dt: self.display_and_detect("captured_frame.jpg"), 0)

    def display_and_detect(self, image_path):
        def process_image():
            try:
                plate_number, annotated_img, vehicle_type = detect_license_plate(image_path)
                log_entry(plate_number)

                if annotated_img is None:
                    raise ValueError("annotated_img is None")

                display_img = cv2.resize(annotated_img, (640, 480))
                display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                success, buffer = cv2.imencode('.png', display_img)
                if not success:
                    raise ValueError("Failed to encode image")

                data = BytesIO(buffer.tobytes())
                Clock.schedule_once(lambda dt: self.update_ui(data, plate_number, vehicle_type), 0)
            except Exception as e:
                print(f"[ERROR] Detection failed: {e}")
                Clock.schedule_once(lambda dt: self.label_update("Detection failed."), 0)

        Thread(target=process_image, daemon=True).start()

    @mainthread
    def update_ui(self, data, plate_number, vehicle_type):
        try:
            core_img = CoreImage(data, ext='png')
            self.image.texture = core_img.texture
            self.label.text = f"[{vehicle_type}] Plate: {plate_number}"
        except Exception as e:
            print(f"[ERROR] UI update failed: {e}")
        finally:
            self.restore_ui()

    def show_logs(self, instance):
        self.stop_camera()
        self.clear_widgets()
        log_entries = read_log_entries()

        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        if not log_entries:
            label = Label(text="No valid detections logged yet.", size_hint_y=None, height=40)
            layout.add_widget(label)
        else:
            for plate, timestamp in reversed(log_entries):
                label = Label(text=f"{timestamp} ➤ {plate}", size_hint_y=None, height=40)
                layout.add_widget(label)

        scroll.add_widget(layout)
        self.add_widget(scroll)

        back_btn = Button(text="Back")
        back_btn.bind(on_press=lambda x: self.restore_ui())
        self.add_widget(back_btn)

    def label_update(self, msg):
        self.label.text = msg

    def restore_ui(self):
        self.clear_widgets()
        self.add_widget(self.image)
        self.add_widget(self.label)
        self.add_widget(self.choose_btn)
        self.add_widget(self.camera_btn)
        self.add_widget(self.capture_btn)
        self.add_widget(self.logs_btn)

    def on_app_close(self, *args):
        self.stop_camera()

    def on_stop(self):
        self.stop_camera()


class LicenseApp(App):
    def build(self):
        return LicensePlateApp()

    def on_stop(self):
        if self.root:
            self.root.on_stop()


if __name__ == '__main__':
    LicenseApp().run()
