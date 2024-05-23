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

    def updatePosition(self, dt):
        self.x = self.x + self.Vx * dt
        self.y = self.y + self.Vy * dt

    def updateVelocity(self, w, h):
        if self.y <= self.r or self.y >= h - self.r:  # Üst/Alt duvar
            self.Vy = -self.Vy * self.eps

        if self.x >= w - self.r or self.x <= self.r:  # Sağ/Sol duvar
            self.Vx = -self.Vx * self.eps

    def control(self, keys):
        if keys[pygame.K_UP]:
            self.Vy -= 1
        if keys[pygame.K_DOWN]:
            self.Vy += 1
        if keys[pygame.K_LEFT]:
            self.Vx -= 1
        if keys[pygame.K_RIGHT]:
            self.Vx += 1

# Kutu sınıfını tanımlayın
class Kutu:
    def __init__(self, x, y, genislik, yukseklik, renk):
        self.x = x
        self.y = y
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.renk = renk
        self.olusturulma_zamani = pygame.time.get_ticks()

    def isVisible(self):
        return pygame.time.get_ticks() - self.olusturulma_zamani < 7000  # 7 saniye

# Ana fonksiyonu tanımlayın
def main():
    # Pygame'i başlatın
    pygame.init()

    # Ekranı oluşturun
    ekran = pygame.display.set_mode((ekran_genisligi, ekran_yuksekligi))
    pygame.display.set_caption("Top ve Kutular")

    # Topu ve kutuları oluşturun
    top = Top(ekran_genisligi // 2, ekran_yuksekligi // 2, 2, 2, 20, (255, 0, 0))
    kutular = []

    # Puanı ve yazı tipi ayarlayın
    puan = 0
    font = pygame.font.SysFont(None, 32)

    # Saat döngüsünü başlatın
    saat = pygame.time.Clock()
    calisma_suresi = 0

    calisiyor = True
    while calisiyor:
        # Etkinlikleri işleyin
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False

        # Zamanı güncelleyin
        dt = saat.tick(60)
        calisma_suresi += dt

        # Topun konumunu ve hızını güncelleyin
        top.updatePosition(dt / 300)
        top.updateVelocity(ekran_genisligi, ekran_yuksekligi)

        # Topu klavyeyle kontrol edin
        keys = pygame.key.get_pressed()
        top.control(keys)

        # Yeni bir kutu oluşturun
        if random.random() < 0.1:  # Her 10 frame'de bir (yaklaşık 0.16 saniyede bir)
            kutular.append(Kutu(random.randint(top.r + 10, ekran_genisligi - top.r - 10),
                   random.randint(top.r + 10, ekran_yuksekligi - top.r - 10),
                   random.randint(20, 50),
                   random.randint(20, 50),
                   (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))

        # Kutuların konumlarını ve görünürlüklerini güncelleyin
        for kutu in kutular:
            # Kutu topla çarpşıyorsa
            if abs(top.x - kutu.x) < top.r + kutu.genislik // 2 and \
               abs(top.y - kutu.y) < top.r + kutu.yukseklik // 2:
                puan += 10
                kutular.remove(kutu)

            kutu.y += 1  # Kutuyu aşağıya doğru hareket ettirin

            # Kutu ekrandan çıkarsa yok edin
            if kutu.y > ekran_yuksekligi:
                kutular.remove(kutu)

        # Ekranı temizleyin
        ekran.fill((0, 0, 0))

        # Topu ve kutuları çizin
        pygame.draw.circle(ekran, top.renk, (int(top.x), int(top.y)), top.r)
        for kutu in kutular:
            if kutu.isVisible():
                pygame.draw.rect(ekran, kutu.renk, (kutu.x, kutu.y, kutu.genislik, kutu.yukseklik))

        # Puanı gösterin
        puan_metni = font.render(f"Puan: {puan}", True, (255, 255, 255))
        ekran.blit(puan_metni, (10, 10))

        # Ekranı güncelleyin
        pygame.display.flip()

    # Pygame'i sonlandırın
    pygame.quit()

# Ana fonksiyonu çalıştırın
if __name__ == "__main__":
    main()