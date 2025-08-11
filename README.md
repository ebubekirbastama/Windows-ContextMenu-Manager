🖱️ Windows Context Menu Manager (Sağ Tık Menüsü Düzenleyici) ⚙️

---

📌 Proje Hakkında

Windows işletim sistemlerinde sağ tık menüleri (context menu) genellikle kullanıcı deneyimini özelleştirmek için sıkça düzenlenir.  
Windows Context Menu Manager ile;

- Dosya, klasör ve masaüstü sağ tık menülerini detaylı şekilde görüntüleyebilir,  
- Menü öğeleri ekleyip güncelleyebilir,  
- Menüde kayıtlı CLSID (Component Object Model) bilgilerini ayrıntılı analiz edebilir,  
- CLSID içeriğini filtreleyebilir,  
- Komut yolunu değiştirebilir ve silebilirsiniz.

Bu araç, sistem yöneticileri, yazılım geliştiriciler ve ileri düzey Windows kullanıcıları için tasarlanmıştır.

---

🚀 Özellikler

- 💻 Dosya, Klasör ve Masaüstü sağ tık menü konumlarından öğeleri listeleme  
- 🔍 CLSID detaylı analizi ve açıklama gösterimi  
- 🧹 Menü öğesi ekleme, güncelleme ve silme  
- 🎯 CLSID filtreleme ile kolay arama  
- 🎨 Koyu tema ve modern kullanıcı arayüzü (PyQt6 ile geliştirilmiştir)  
- ⚠️ Yönetici hakları gerektirir (program otomatik yükseltme isteği yapar)

---

🛠️ Gereksinimler

- Python 3.9 veya üstü  
- Windows işletim sistemi  
- PyQt6 kütüphanesi  
- Yönetici (Admin) hakları ile çalıştırma

Gerekli Paketleri Yüklemek İçin:  
pip install PyQt6

---

📋 Kullanım

1. Programı yönetici olarak çalıştırın.  
   (Admin hakları olmadan çalışmaz, program otomatik olarak admin izni isteyecektir.)

2. Açılan arayüzde sağ tık menü konumunu seçin:  
   - Dosya  
   - Klasör  
   - Masaüstü  

3. Listelenen menü öğelerinden birini seçin.  
   - Sağ tarafta seçilen öğenin adı, komutu ve CLSID detayları görüntülenecektir.  
   - CLSID detaylarında arama yapmak için filtre alanını kullanabilirsiniz.

4. Menü öğesi eklemek veya var olanı güncellemek için:  
   - Menüde görünecek isim ve çalıştırılacak komutu girin,  
   - "Ekle / Güncelle" butonuna tıklayın.

5. Menü öğesini silmek için:  
   - Listeden öğeyi seçip "Sil" butonuna tıklayın.

---

⚠️ Önemli Notlar

- Program kayıt defteri üzerinde değişiklik yaptığı için yönetici haklarıyla çalıştırılmalıdır.  
- Kayıt defteri üzerinde yanlış işlem sistemde sorunlara yol açabilir. Lütfen dikkatli kullanın.  
- Yedek almak için sağ tık menüsü düzenlemeden önce kayıt defteri yedeği almanız önerilir.

---

💡 İleri Düzey Kullanıcılar İçin

- CLSID detaylarında Properties altındaki değerler gösterilmektedir.  
- DLL, EXE, ProgID, TypeLib gibi COM bilgileri analiz edilebilir.  
- 64-bit ve 32-bit kayıt defteri dallarında tarama yapılmaktadır.

---

🤝 Katkıda Bulunma

Proje açık kaynak! Hatalar, öneriler veya katkılar için lütfen GitHub üzerinden issue açabilir veya pull request gönderebilirsiniz.

---

📄 Lisans

MIT License

---

🙏 Teşekkürler!

Windows sağ tık menülerini kolayca yönetmek isteyen herkese faydalı olmasını dilerim!  

---

⭐ İyi çalışmalar! ⭐
