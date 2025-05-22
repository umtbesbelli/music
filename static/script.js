// DOM içeriği tamamen yüklendiğinde fonksiyonları çalıştırıyoruz.
document.addEventListener("DOMContentLoaded", function () {  
    const listeDiv = document.querySelector(".muzik-listesi");  // Müzik listesini göstereceğimiz alan.

    // Veritabanındaki müzikleri çekip ekrana listeleyen fonksiyon.
    function listele() {
        fetch("/api/muzikler")  // API'den müzik listesini çekiyoruz.
            .then(res => res.json())  // Gelen cevabı JSON formatına çeviriyoruz.
            .then(sarkilar => {
                listeDiv.innerHTML = "";  // Önce listeyi temizleyelim ki tekrar eklenmesin.
                
                sarkilar.forEach(sarki => {  // Her bir şarkıyı ekrana ayrı bir kart olarak ekliyoruz.
                    const card = document.createElement("div");
                    card.className = "player-card";  // Kartın CSS sınıfını belirtiyoruz.

                    // Şarkı bilgilerini ve kontrol butonlarını oluşturuyoruz.
                    card.innerHTML = `
                        <div class="track-info">
                            <h2>${sarki.adi}</h2>
                            <p>${sarki.sanatci}</p>
                        </div>
                        <div class="controls">
                            <audio src="/api/oynat/${sarki.id}" preload="none" controls></audio>
                            <div class="buttons">
                                <button class="play-btn">Oynat</button>
                                <button class="delete-btn" data-id="${sarki.id}">Sil</button>
                            </div>
                        </div>`;
                    
                    listeDiv.appendChild(card);  // Kartı sayfaya ekliyoruz.
                });

                butonlariBagla();  // Butonların işlevlerini tanımlıyoruz.
            });
    }

    // Butonlara tıklanınca gerçekleşecek olayları tanımlayan fonksiyon.
    function butonlariBagla() {
        // "Oynat" butonlarına olay dinleyici ekliyoruz.
        document.querySelectorAll(".play-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const audio = this.closest(".player-card").querySelector("audio");  // Şarkıya erişiyoruz.

                // Eğer başka bir şarkı çalıyorsa önce onu durduruyoruz.
                document.querySelectorAll("audio").forEach(a => {
                    if (a !== audio) {
                        a.pause();  
                        a.currentTime = 0;  
                        const b = a.closest(".player-card").querySelector(".play-btn");  
                        if (b) b.textContent = "Oynat";  
                    }
                });

                // Şarkı oynuyorsa duraklat, duraklatılmışsa oynat.
                if (audio.paused) {
                    audio.play();
                    this.textContent = "Duraklat";  // Butonun metnini değiştiriyoruz.
                } else {
                    audio.pause();
                    this.textContent = "Oynat";
                }
            });
        });

        // "Sil" butonlarına olay dinleyici ekliyoruz.
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const id = this.getAttribute("data-id");  // Hangi şarkının silineceğini belirliyoruz.
                fetch(`/api/muzik/${id}`, { method: "DELETE" })  // API'ye DELETE isteği gönderiyoruz.
                    .then(() => listele());  // Silindikten sonra listeyi güncelliyoruz.
            });
        });
    }

    // Müzik ekleme formunun işleyişi.
    const form = document.querySelector("form");
    form.addEventListener("submit", function (e) {
        e.preventDefault();  // Formun varsayılan gönderme işlemini durduruyoruz.
        const formData = new FormData(form);  // Formdaki verileri alıyoruz.

        // Yeni müziği API'ye eklemek için POST isteği gönderiyoruz.
        fetch("/api/muzik", {
            method: "POST",
            body: formData
        })
        .then(() => {
            form.reset();  // Formu temizliyoruz.
            listele();  // Listeyi güncelliyoruz.
        });
    });

    listele();  // Sayfa açıldığında müzikleri listeleyelim.
});