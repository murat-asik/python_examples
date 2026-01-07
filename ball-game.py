import pygame
import random

# Ekran boyutlarını ayarlayın
ekran_genisligi = 800
ekran_yuksekligi = 600

# Top sınıfını tanımlayın
class Top:
    def __init__(self, x, y, Vx, Vy, r, renk, eps=1):
        self.x = x
        self.y = y
        self.Vx = Vx
        self.Vy = Vy
        self.r = r
        self.renk = renk
        self.eps = eps
        self.max_speed = 30.0  # HIZ ARTIRILDI (10.0 -> 15.0)
        self.friction = 0.995   # SÜRTÜNME AZALTILDI (Daha kaygan, daha az hız kaybı)

    def updatePosition(self, dt):
        # Sürtünme uygula
        self.Vx *= self.friction
        self.Vy *= self.friction
        
        # Hızı sınırla
        hiz = (self.Vx**2 + self.Vy**2)**0.5
        if hiz > self.max_speed:
            katsayi = self.max_speed / hiz
            self.Vx *= katsayi
            self.Vy *= katsayi
            
        self.x = self.x + self.Vx * dt
        self.y = self.y + self.Vy * dt

    def updateVelocity(self, w, h):
        # Duvar çarpışmaları ve düzeltmeler (Sticking fix)
        if self.y <= self.r:
            self.y = self.r # İçeri it
            self.Vy = -self.Vy * self.eps
        elif self.y >= h - self.r:
            self.y = h - self.r # İçeri it
            self.Vy = -self.Vy * self.eps

        if self.x >= w - self.r:
            self.x = w - self.r # İçeri it
            self.Vx = -self.Vx * self.eps
        elif self.x <= self.r:
            self.x = self.r # İçeri it
            self.Vx = -self.Vx * self.eps

    def control(self, keys):
        # Hızlanma miktarını biraz düşürdük çünkü sürekli basınca çok hızlanıyor
        ivme = 0.6 # Biraz daha atik olması için artırdık (0.5 -> 0.6)
        if keys[pygame.K_UP]:
            self.Vy -= ivme
        if keys[pygame.K_DOWN]:
            self.Vy += ivme
        if keys[pygame.K_LEFT]:
            self.Vx -= ivme
        if keys[pygame.K_RIGHT]:
            self.Vx += ivme

# Kutu sınıfını tanımlayın
class Kutu:
    def __init__(self, x, y, genislik, yukseklik, renk, kutu_tipi=0):
        self.x = x
        self.y = y
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.kutu_tipi = kutu_tipi
        self.olusturulma_zamani = pygame.time.get_ticks()
        
        # Tipe göre renk belirle
        if self.kutu_tipi == 1: # Süre/Yeşil
            self.renk = (0, 255, 0)
        elif self.kutu_tipi == 2: # Yavaşlatma/Mavi (Tehdit)
            self.renk = (0, 0, 255)
        else: # Normal/Kırmızı
            self.renk = (255, 0, 0)


    def update(self, target_x, target_y):
        # MAVİ KUTULAR (Tip 2) HAREKETLİ VE TAKİPÇİ
        if self.kutu_tipi == 2:
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx**2 + dy**2)**0.5
            
            if dist > 0:
                # Normalize et ve küçük bir hızla hareket ettir (Tehdit)
                speed = 1.2 # Yavaş ama kararlı takip
                self.x += (dx / dist) * speed
                self.y += (dy / dist) * speed
        
        # Diğer kutular (Kırmızı/Yeşil) ARTIK SABİT (Hareket kodları kaldırıldı)

    def isVisible(self):
        return pygame.time.get_ticks() - self.olusturulma_zamani < 7000  # 7 saniye

# Ana fonksiyonu tanımlayın
def main():
    # Pygame'i başlatın
    pygame.init()

    # Ekranı oluşturun
    ekran = pygame.display.set_mode((ekran_genisligi, ekran_yuksekligi))
    pygame.display.set_caption("Top ve Kutular - Gelişmiş Versiyon v4")

    font = pygame.font.SysFont(None, 32)
    buyuk_font = pygame.font.SysFont(None, 64)

    def oyunu_baslat():
        # Başlangıç hızını artırdık (4,4 -> 5,5) - Daha atik başlangıç
        return {
            "top": Top(ekran_genisligi // 2, ekran_yuksekligi // 2, 5, 5, 20, (255, 0, 0)),
            "kutular": [],
            "puan": 0,
            "calisma_suresi": 0, # ms cinsinden
            "toplam_sure": 60000, # 60 saniye
            "game_over": False,
            "baslangic_zamani": pygame.time.get_ticks(), # Oyunun başladığı gerçek zaman
            "combo_sayaci": 0,
            "son_vurus_zamani": 0
        }

    state = oyunu_baslat()
    
    # Saat döngüsünü başlatın
    saat = pygame.time.Clock()

    calisiyor = True
    while calisiyor:
        dt = saat.tick(60)
        simdiki_zaman = pygame.time.get_ticks()
        
        # Etkinlikleri işleyin
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
            if event.type == pygame.KEYDOWN:
                if state["game_over"] and event.key == pygame.K_r:
                    state = oyunu_baslat() # Oyunu sıfırla

        if not state["game_over"]:
            # Combo sıfırlama (2 saniye vuruş olmazsa)
            if simdiki_zaman - state["son_vurus_zamani"] > 2000:
                state["combo_sayaci"] = 0

            # Zamanı güncelleyin (geriye sayım)
            gecen_sure = simdiki_zaman - state["baslangic_zamani"]
            kalan_sure = max(0, state["toplam_sure"] - gecen_sure)
            if kalan_sure <= 0:
                state["game_over"] = True

            top = state["top"]
            kutular = state["kutular"]

            # Topun konumunu ve hızını güncelleyin
            top.updatePosition(dt / 300) 
            top.updateVelocity(ekran_genisligi, ekran_yuksekligi)

            # Topu klavyeyle kontrol edin
            keys = pygame.key.get_pressed()
            top.control(keys)

            # --------------------------------------------------------------------------------
            # 1. NORMAL KUTU SPAWN (Kırmızı ve Yeşil)
            # --------------------------------------------------------------------------------
            if random.random() < 0.08:  # Spawn sıklığı (Blue hariç)
                rand_val = random.random()
                k_tip = 0 # Default Kırmızı
                
                # Mavi ARTIK BURADA YOK. Sadece Kırmızı ve Yeşil.
                if rand_val < 0.20: k_tip = 1 # %20 Yeşil (Zaman)
                else: k_tip = 0 # %80 Kırmızı (Puan)

                kutular.append(Kutu(random.randint(top.r + 10, ekran_genisligi - top.r - 10),
                       random.randint(top.r + 10, ekran_yuksekligi - top.r - 10),
                       random.randint(20, 50),
                       random.randint(20, 50),
                       (0,0,0), # Renk constructor içinde atanıyor
                       kutu_tipi=k_tip))

            # --------------------------------------------------------------------------------
            # 2. MAVİ KUTU (DÜŞMAN) YÖNETİMİ
            # --------------------------------------------------------------------------------
            # Hedef Mavi Sayısı: 1 + (Her 250 puanda 1 tane)
            hedef_mavi_sayisi = 1 + (state["puan"] // 250)
            
            # Mevcut mavi sayısını bul
            mevcut_mavi_sayisi = 0
            for k in kutular:
                if k.kutu_tipi == 2:
                    mevcut_mavi_sayisi += 1
            
            # Eksik varsa tamamla
            if mevcut_mavi_sayisi < hedef_mavi_sayisi:
                # Topa çarpmayacak güvenli bir yerde doğması mantıklı olur ama şimdilik rastgele
                kutular.append(Kutu(random.randint(top.r + 10, ekran_genisligi - top.r - 10),
                       random.randint(top.r + 10, ekran_yuksekligi - top.r - 10),
                       random.randint(20, 50),
                       random.randint(20, 50),
                       (0,0,0), 
                       kutu_tipi=2)) # Tip 2 = Mavi

            # --------------------------------------------------------------------------------
            # GÜNCELLEME VE ÇARPIŞMA
            # --------------------------------------------------------------------------------
            # Listeyi kopyalayarak iterasyon yapıyoruz ki silme işlemi güvenli olsun
            for kutu in kutular[:]: 
                kutu.update(top.x, top.y) # Hedef bilgisini gönder
                
                # Süresi dolan kutuları sil
                # NOT: Mavi kutular da süreyle ölebilir, hemen yenisi spawn olur (Sürekli tehdit değişimi)
                if not kutu.isVisible():
                    kutular.remove(kutu)
                    continue

                # Kutu topla çarpşıyorsa
                if abs(top.x - kutu.x) < top.r + kutu.genislik // 2 and \
                   abs(top.y - kutu.y) < top.r + kutu.yukseklik // 2:
                    
                    # Eğer MAVİ (Tip 2) ise PUAN YOK, sadece yavaşlatma ve silme
                    if kutu.kutu_tipi == 2:
                        # Mavi kutu tehdittir. Puan vermez.
                        top.Vx *= 0.5
                        top.Vy *= 0.5
                        kutular.remove(kutu)
                        # Hemen yenisi spawn olacak loop başında
                    else:
                        # Kırmızı veya Yeşil
                        state["combo_sayaci"] += 1
                        state["son_vurus_zamani"] = simdiki_zaman
                        combo_carpan = min(5, (state["combo_sayaci"] // 5) + 1)

                        puan_artis = 10 * combo_carpan
                        
                        if kutu.kutu_tipi == 1: # Yeşil
                            state["toplam_sure"] += 5000 
                            puan_artis += 5
                        
                        state["puan"] += puan_artis
                        kutular.remove(kutu)
                        
                        # Zorluk (Top Hızı) Artışı
                        if state["puan"] % 50 == 0:
                            top.Vx *= 1.1
                            top.Vy *= 1.1

                # Kutu ekrandan çıkarsa yok edin
                if kutu.y > ekran_yuksekligi:
                    if kutu in kutular: kutular.remove(kutu)

        # Ekranı temizleyin
        ekran.fill((0, 0, 0))

        if not state["game_over"]:
            # Topu ve kutuları çizin
            pygame.draw.circle(ekran, state["top"].renk, (int(state["top"].x), int(state["top"].y)), state["top"].r)
            for kutu in state["kutular"]:
                if kutu.isVisible():
                    pygame.draw.rect(ekran, kutu.renk, (kutu.x, kutu.y, kutu.genislik, kutu.yukseklik))

            # Puanı gösterin
            puan_metni = font.render(f"Puan: {state['puan']}", True, (255, 255, 255))
            ekran.blit(puan_metni, (10, 10))
            
            # Süreyi gösterin
            sure_metni = font.render(f"Süre: {int(kalan_sure/1000)}", True, (255, 255, 255))
            ekran.blit(sure_metni, (ekran_genisligi - 120, 10))
        else:
            # Game Over Ekranı
            bitis_metni = buyuk_font.render("OYUN BİTTİ", True, (255, 0, 0))
            skor_metni = font.render(f"Toplam Puan: {state['puan']}", True, (255, 255, 255))
            bilgi_metni = font.render("Yeniden başlamak için 'R' tuşuna basın", True, (200, 200, 200))
            
            ekran.blit(bitis_metni, (ekran_genisligi//2 - bitis_metni.get_width()//2, ekran_yuksekligi//2 - 50))
            ekran.blit(skor_metni, (ekran_genisligi//2 - skor_metni.get_width()//2, ekran_yuksekligi//2 + 10))
            ekran.blit(bilgi_metni, (ekran_genisligi//2 - bilgi_metni.get_width()//2, ekran_yuksekligi//2 + 50))

        # Ekranı güncelleyin
        pygame.display.flip()

    # Pygame'i sonlandırın
    pygame.quit()

# Ana fonksiyonu çalıştırın
if __name__ == "__main__":
    main()