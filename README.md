# iha-simulator
İHA'nın canlı konum, pil, hız verilerini TCP ve UDP üzerinden yayınlayan ve görüntüleri ileten ayrıca görüntüleyebilen İHA simülatörü ve yer kontrol istasyonu
1.  **Depoyu Klonlayın:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
2.  **Sanal Ortam Oluşturun (Tavsiye Edilir):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```
3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

## Çalıştırma

Bu simülasyonun çalışması için **iki ayrı komut istemcisi (terminal)** açmanız gerekmektedir.

**1. Terminal: İHA Simülatörünü Başlatın**

(Webcam erişimine izin vermeniz istenebilir)
```bash
python simulator.py
Bu terminalde İHA'nın çalıştığını ve YKİ bağlantısı beklediğini göreceksiniz.

2. Terminal: Yer Kontrol İstasyonunu Başlatın

Bash

python yki.py
Bu terminalde, sürekli güncellenen telemetri verileri (konum, pil vb.) görünecek ve "İHA Video Akışı" adlı ayrı bir pencerede webcam görüntünüz canlı olarak yayınlanacaktır.

Çıkış Yapma
Simülasyonu durdurmak için:

YKİ tarafında, video penceresi aktifken (seçiliyken) klavyeden 'q' tuşuna basın.

Alternatif olarak, her iki terminalde de Ctrl+C tuş kombinasyonunu kullanabilirsiniz.
