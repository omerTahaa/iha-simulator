import cv2
import socket
import threading
import time
import json
import random
import numpy as np

TELEMETRY_HOST = '127.0.0.1'
TELEMETRY_PORT = 9998

VIDEO_HOST = '127.0.0.1'
VIDEO_PORT = 9999

class IHASimulator:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.irtifa = 0.0
        self.pil = 100.0
        self.hiz = 0.0
        
        self.x_degisim_faktoru = random.uniform(-0.5, 0.5)
        self.y_degisim_faktoru = random.uniform(-0.5, 0.5)
        self.konum_z_yukari = random.uniform(0.1, 0.5)
        self.konum_z_tepe = random.uniform(-0.1, 0.1)
        
        self.telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.telemetry_socket.bind((TELEMETRY_HOST, TELEMETRY_PORT))
        
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            print("Kamera açılamadı")
            raise IOError("Webcam açılamadı")
        
        self.stop_event = threading.Event()
        print(f"Yer Kontrol İstasyonu bağlantısı {TELEMETRY_PORT} portundan bekleniyor...")

    def _update_telemetry(self):
        self.x += self.x_degisim_faktoru
        self.y += self.y_degisim_faktoru
        
        if self.z <= 150:
            self.z += self.konum_z_yukari
        else:
            if self.z > 151: 
                 self.z += random.uniform(-0.1, -0.05)
            else:
                self.z += self.konum_z_tepe
        self.irtifa = self.z
        
        self.hiz = random.uniform(18.0, 22.0) 
        self.pil -= 0.05 
        if self.pil < 0:
            self.pil = 100.0 

    def _stream_telemetry(self):

        try:
            self.telemetry_socket.listen(1)
            conn, addr = self.telemetry_socket.accept()
            with conn:
                print(f"YKİ bağlandı: {addr}")
                while not self.stop_event.is_set():
                    self._update_telemetry()
                    
                    veri = {
                        'konum_x': self.x,
                        'konum_y': self.y,
                        'irtifa': self.irtifa,
                        'hiz': self.hiz,
                        'batarya': self.pil,
                        'durum': 'Ucus' if self.pil > 20 else 'Eve Donus'
                    }
                    
                    conn.sendall(json.dumps(veri).encode('utf-8'))
                    
                    time.sleep(1) 
                    
        except socket.error as e:
            if not self.stop_event.is_set():
                print(f"Bağlantı hatası: {e}")
        finally:
            print("Thread durduruldu.")
            self.telemetry_socket.close()

    def _stream_video(self):
        gcs_address = (VIDEO_HOST, VIDEO_PORT)
        print(f"Video {gcs_address} adresine başlatılıyor...")
        
        try:
            while not self.stop_event.is_set():
                ret, frame = self.video_capture.read()
                if not ret:
                    continue
                
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                if buffer.nbytes > 65507:
                    print("Hata: Frame boyutu UDP limitini aşıyor.")
                    continue
                    
                self.video_socket.sendto(buffer.tobytes(), gcs_address)
                time.sleep(0.05) 
                
        except Exception as e:
            if not self.stop_event.is_set():
                print(f"[Video Hatası: {e}")
        finally:
            print("Thread durduruldu.")
            self.video_socket.close()

    def start(self):
        telemetry_thread = threading.Thread(target=self._stream_telemetry, daemon=True)
        video_thread = threading.Thread(target=self._stream_video, daemon=True)
        
        telemetry_thread.start()
        video_thread.start()

    def stop(self):
        print("Kapatılıyor...")
        self.stop_event.set()
        self.video_capture.release()
        self.telemetry_socket.close()
        self.video_socket.close()
        print("Simülatör başarıyla kapatıldı.")

if __name__ == "__main__":
    try:
        simulator = IHASimulator()
        simulator.start()
        
        while True:
            time.sleep(1)
    except IOError as e:
        print(e)
    except KeyboardInterrupt:
        simulator.stop()
