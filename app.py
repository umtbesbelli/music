# Flask kütüphanesini içe aktarıyor.
from flask import Flask, jsonify, request, send_file, render_template  
import psycopg2  # PostgreSQL veritabanı bağlantısı için kullanılan kısım.
import os  # Dosya işlemleri için kullanacağız.

# Flask uygulamasını başlatma.
app = Flask(__name__)  

# Müzik dosyalarının saklanacağı klasör
UPLOAD_KLASOR = "muzik"
app.config["UPLOAD_KLASOR"] = UPLOAD_KLASOR  

# PostgreSql veritabanına bağlanıyoruz.
conn = psycopg2.connect(
    dbname="muzik_db", user="postgres", password="12345", host="localhost"
)
cursor = conn.cursor()  # SQL işlemlerini (CRUD mesela )çalıştırma işine yarıyor.

# Ana sayfa için HTML dosyamızı sunuyoruz—bu sadece arayüzü göstermek için
@app.route("/")
def index():
    return render_template("index.html")

        # Veritabanındaki müzik listesini API olarak döndüren fonksiyon.
@app.route("/api/muzikler", methods=["GET"])
def muzik_listesi():
    # En güncel şarkılar üstte olacak şekilde verileri çekiyoruz.
    cursor.execute("SELECT * FROM muzik ORDER BY id DESC")
    sarkilar = cursor.fetchall()  # Tüm sonuçları alıyoruz.
    return jsonify([
        {"id": s[0], "adi": s[1], "sanatci": s[2]} for s in sarkilar
    ])  # JSON formatında müzik bilgilerini döndürüyoruz.

                    # Kullanıcıdan gelen yeni bir müziği eklemek için API fonksiyonu.
@app.route("/api/muzik", methods=["POST"])
def muzik_ekle():
    # Formdan müzik adı ve sanatçı bilgilerini alıyoruz.
    muzik_adi = request.form["muzik_adi"]
    sanatci = request.form["sanatci"]
    dosya = request.files["dosya"]          # Kullanıcının yüklediği müzik dosyasını alıyoruz.
    
    # Dosyanın hedef konumunu belirleyip kaydediyoruz.
    dosya_yolu = os.path.join(app.config["UPLOAD_KLASOR"], dosya.filename)
    dosya.save(dosya_yolu)

    # Veritabanına bu yeni müziği ekliyoruz.
    cursor.execute(
        "INSERT INTO muzik (muzik_adi, sanatci, dosya_yolu) VALUES (%s, %s, %s)",
        (muzik_adi, sanatci, dosya_yolu)
    )
    conn.commit()  # Değişiklikleri kaydediyoruz.
    return jsonify({"durum": "ok"})  # Başarı mesajı döndürüyoruz.

# Müzik silmek için API fonksiyonu.
@app.route("/api/muzik/<int:id>", methods=["DELETE"])
def muzik_sil(id):
    # Veritabanından belirli bir müziği ID’ye göre siliyoruz.
    cursor.execute("DELETE FROM muzik WHERE id = %s", (id,))
    conn.commit()  # Değişiklikleri kaydediyoruz.
    return jsonify({"durum": "silindi"})  # Silme işleminin başarılı olduğunu belirten yanıt.

# Kullanıcı bir müzik dosyasını çalmak istediğinde çalışacak fonksiyon.
@app.route("/api/oynat/<int:id>", methods=["GET"])
def muzik_oynat(id):
    # Veritabanından müziğin dosya yolunu çekiyoruz.
    cursor.execute("SELECT dosya_yolu FROM muzik WHERE id = %s", (id,))
    sonuc = cursor.fetchone()  # Eğer şarkıyı bulursak, dosya yolunu alıyoruz.
    if sonuc:
        return send_file(sonuc[0])  # Dosyayı doğrudan kullanıcıya gönderiyoruz.
    return jsonify({"hata": "bulunamadı"}), 404  # Eğer müzik yoksa hata mesajı döndürüyoruz.

# Uygulamayı çalıştıracak ana kod.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)   # Debug modu açık, böylece hataları kolayca görebiliriz.
