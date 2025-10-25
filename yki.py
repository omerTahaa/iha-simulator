import cv2
import socket
import threading
import json
import os
import time
import numpy as np

TELEMETRY_HOST = '127.0.0.1'
TELEMETRY_PORT = 9998

VIDEO_HOST = '127.0.0.1'
VIDEO_PORT = 9999

class YerKontrolIstasyonu:
    def __init__(self, host, telemetry_port, video_port):
        self.host = host
        self.telemetry_port = telemetry_port
        self.video_port = video_port
        
        self.telemetry_data = {}
        self.current_frame = None
        
        self.telemetry_lock = threading.Lock()
        self.frame_lock = threading.Lock()
        
        self.telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.stop_event = threading.Event()

    def _receive_telemetry(self):
        try:
            print("İHA'ya bağlanılıyor")
            self.telemetry_socket.connect((self.host, self.telemetry_port))
            print("İHA'ya bağlandı.")
            
            while not self.stop_event.is_set():
                data = self.telemetry_socket.recv(1024)
                if not data:
                    print("İHA bağlantısı koptu.")
                    break
                    
                parsed_data = json.loads(data.decode('utf-8'))
                
                with self.telemetry_lock:
                    self.telemetry_data = parsed_data
                    
        except socket.error as e:
            print(f"Bağlantı hatası oluştu {e}")
        finally:
            print("Thread durduruldu.")
            self.stop_event.set() 

    def _receive_video(self):
        try:
            self.video_socket.bind((self.host, self.video_port))
            print(f"Video {self.video_port} portundan dinleniyor...")
            
            while not self.stop_event.is_set():
                data, _ = self.video_socket.recvfrom(65536)
                
                np_arr = np.frombuffer(data, np.uint8)
                
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame
                        
        except socket.error as e:
            if not self.stop_event.is_set():
                print(f"Soket hatası: {e}")
        finally:
            print("[Thread durduruldu.")
            self.stop_event.set()

    def _display_cli(self):
        os.system('cls' if os.name == 'nt' else 'clear') 
        
        print("--- YER KONTROL İSTASYONU (YKİ) ---")
        print("Çıkış için 'Q' tuşuna basın (Video penceresi aktifken)")
        print("-" * 35)
        
        with self.telemetry_lock:
            data = self.telemetry_data.copy()
            
        if not data:
            print("İHA'dan telemetri verisi bekleniyor...")
            return

        print(f" Durum         : {data.get('durum', 'N/A')}")
        print(f" Batarya       : {data.get('batarya', 0.0):.2f} %")
        print("-" * 35)
        print(f" Konum (X, Y)  : {data.get('konum_x', 0.0):.2f}, {data.get('konum_y', 0.0):.2f}")
        print(f" İrtifa        : {data.get('irtifa', 0.0):.2f} m")
        print(f" Hız           : {data.get('hiz', 0.0):.2f} m/s")
        print("-" * 35)

    def start(self):
        telemetry_thread = threading.Thread(target=self._receive_telemetry, daemon=True)
        video_thread = threading.Thread(target=self._receive_video, daemon=True)
        
        telemetry_thread.start()
        video_thread.start()
        
        print("Ana arayüz başlatıldı.")
        
        try:
            while not self.stop_event.is_set():
                self._display_cli()
                
                with self.frame_lock:
                    frame = self.current_frame
                
                if frame is not None:
                    cv2.imshow("İHA Video Akışı (Çıkış için Q'ya basın)", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Çıkış Yapılıyor...")
                    break
                    
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("Ctrl+C ile kapatılıyor...")
        finally:
            self.stop()

    def stop(self):
        print("Kapatılıyor...")
        self.stop_event.set()
        self.telemetry_socket.close()
        self.video_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    gcs = YerKontrolIstasyonu(TELEMETRY_HOST, TELEMETRY_PORT, VIDEO_PORT)
    gcs.start()
    print("Program sonlandı.")