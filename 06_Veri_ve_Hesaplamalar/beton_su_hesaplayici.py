#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BETON ENDÜSTRİSİ SU TÜKETİMİ HESAPLAYICI
Türkiye Su Sorunu Projesi - Endüstriyel Analiz Araçları

Beton üretiminin su ayak izini hesaplar ve alternatif malzemelerle karşılaştırır.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime

@dataclass
class MalzemeOzellikleri:
    """Malzeme özelliklerini saklayan veri sınıfı"""
    isim: str
    su_tuketimi_l_m3: float      # Litre su/m³ malzeme
    co2_emisyonu_kg_m3: float    # kg CO2/m³ malzeme
    enerji_tuketimi_mj_m3: float # MJ enerji/m³ malzeme
    maliyet_tl_m3: float         # TL/m³ malzeme
    dayaniklik_yil: int          # Yaşam süresi (yıl)
    geri_donusum_orani: float    # Geri dönüşüm oranı (0-1)

class BetonSuHesaplayici:
    """Beton ve alternatif malzemeler için hesaplama sınıfı"""
    
    def __init__(self):
        # Malzeme veritabanı
        self.malzemeler = {
            'beton': MalzemeOzellikleri(
                isim='Konvansiyonel Beton',
                su_tuketimi_l_m3=300,
                co2_emisyonu_kg_m3=400,
                enerji_tuketimi_mj_m3=2500,
                maliyet_tl_m3=450,
                dayaniklik_yil=50,
                geri_donusum_orani=0.10
            ),
            'hempcrete': MalzemeOzellikleri(
                isim='Kenevir Beton (Hempcrete)',
                su_tuketimi_l_m3=50,
                co2_emisyonu_kg_m3=-165,  # Negatif: CO2 emer
                enerji_tuketimi_mj_m3=300,
                maliyet_tl_m3=520,
                dayaniklik_yil=100,
                geri_donusum_orani=1.0
            ),
            'ahsap_clt': MalzemeOzellikleri(
                isim='Çapraz Katmanlı Ahşap (CLT)',
                su_tuketimi_l_m3=25,
                co2_emisyonu_kg_m3=-900,  # Karbon depolama
                enerji_tuketimi_mj_m3=800,
                maliyet_tl_m3=650,
                dayaniklik_yil=80,
                geri_donusum_orani=0.95
            ),
            'adobe': MalzemeOzellikleri(
                isim='Adobe/Kerpıç',
                su_tuketimi_l_m3=15,
                co2_emisyonu_kg_m3=20,
                enerji_tuketimi_mj_m3=100,
                maliyet_tl_m3=180,
                dayaniklik_yil=100,
                geri_donusum_orani=1.0
            ),
            'mycelium': MalzemeOzellikleri(
                isim='Mantar Miselium Beton',
                su_tuketimi_l_m3=10,
                co2_emisyonu_kg_m3=-50,
                enerji_tuketimi_mj_m3=200,
                maliyet_tl_m3=800,
                dayaniklik_yil=25,
                geri_donusum_orani=1.0
            )
        }
        
        # Türkiye beton endüstrisi verileri
        self.turkiye_beton = {
            'yillik_cimento_uretim_ton': 80_000_000,
            'cimento_beton_orani': 0.35,  # kg çimento/kg beton
            'hazir_beton_yoghunluk': 2400,  # kg/m³
            'yillik_beton_uretim_m3': 228_000_000,  # hesaplanan
            'su_tuketim_katsayisi': 1.1  # Endüstriyel işlem kayıpları
        }

    def malzeme_karsilastirma(self, hacim_m3: float, malzeme1: str = 'beton', 
                            malzeme2: str = 'hempcrete') -> Dict:
        """İki malzemeyi karşılaştırır"""
        
        if malzeme1 not in self.malzemeler or malzeme2 not in self.malzemeler:
            raise ValueError("Geçersiz malzeme adı")
        
        m1 = self.malzemeler[malzeme1]
        m2 = self.malzemeler[malzeme2]
        
        # Her malzeme için hesaplamalar
        sonuc1 = self._malzeme_hesapla(m1, hacim_m3)
        sonuc2 = self._malzeme_hesapla(m2, hacim_m3)
        
        # Karşılaştırma
        karsilastirma = {
            'su_tasarrufu_l': sonuc1['toplam_su_l'] - sonuc2['toplam_su_l'],
            'co2_azaltimi_kg': sonuc1['toplam_co2_kg'] - sonuc2['toplam_co2_kg'],
            'enerji_tasarrufu_mj': sonuc1['toplam_enerji_mj'] - sonuc2['toplam_enerji_mj'],
            'maliyet_farki_tl': sonuc2['toplam_maliyet_tl'] - sonuc1['toplam_maliyet_tl'],
            'su_tasarrufu_yuzde': ((sonuc1['toplam_su_l'] - sonuc2['toplam_su_l']) / sonuc1['toplam_su_l'] * 100) if sonuc1['toplam_su_l'] > 0 else 0
        }
        
        return {
            malzeme1: sonuc1,
            malzeme2: sonuc2,
            'karsilastirma': karsilastirma,
            'hacim_m3': hacim_m3,
            'analiz_tarihi': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

    def _malzeme_hesapla(self, malzeme: MalzemeOzellikleri, hacim_m3: float) -> Dict:
        """Tek malzeme için hesaplamalar"""
        
        # Doğrudan etki
        toplam_su_l = malzeme.su_tuketimi_l_m3 * hacim_m3
        toplam_co2_kg = malzeme.co2_emisyonu_kg_m3 * hacim_m3
        toplam_enerji_mj = malzeme.enerji_tuketimi_mj_m3 * hacim_m3
        toplam_maliyet_tl = malzeme.maliyet_tl_m3 * hacim_m3
        
        # Yaşam döngüsü hesaplamaları
        yasam_dongusu_co2 = toplam_co2_kg
        
        # Geri dönüşüm faydası
        geri_donusum_co2_tasarrufu = toplam_co2_kg * malzeme.geri_donusum_orani * 0.3  # %30 geri dönüşüm tasarrufu
        net_co2 = yasam_dongusu_co2 - geri_donusum_co2_tasarrufu
        
        return {
            'malzeme_adi': malzeme.isim,
            'toplam_su_l': round(toplam_su_l, 1),
            'toplam_co2_kg': round(net_co2, 1),
            'toplam_enerji_mj': round(toplam_enerji_mj, 1),
            'toplam_maliyet_tl': round(toplam_maliyet_tl, 0),
            'birim_su_l_m3': malzeme.su_tuketimi_l_m3,
            'birim_co2_kg_m3': malzeme.co2_emisyonu_kg_m3,
            'dayaniklik_yil': malzeme.dayaniklik_yil,
            'geri_donusum_orani_yuzde': int(malzeme.geri_donusum_orani * 100)
        }

    def turkiye_beton_etkisi(self) -> Dict:
        """Türkiye'nin toplam beton üretimi etkisi"""
        
        beton = self.malzemeler['beton']
        yillik_hacim = self.turkiye_beton['yillik_beton_uretim_m3']
        
        # Toplam etki hesaplaması
        yillik_su_tuketimi = yillik_hacim * beton.su_tuketimi_l_m3 * self.turkiye_beton['su_tuketim_katsayisi']
        yillik_co2_emisyonu = yillik_hacim * beton.co2_emisyonu_kg_m3
        yillik_enerji_tuketimi = yillik_hacim * beton.enerji_tuketimi_mj_m3
        
        # Su tüketimini m³'e çevir
        yillik_su_m3 = yillik_su_tuketimi / 1000
        
        # Referans noktalar (karşılaştırma için)
        ataturk_baraji_hacmi = 48_700_000_000  # m³
        istanbul_yillik_tuketim = 1_000_000_000  # m³
        
        return {
            'yillik_beton_uretim_m3': yillik_hacim,
            'yillik_su_tuketimi_m3': round(yillik_su_m3, 0),
            'yillik_co2_emisyonu_ton': round(yillik_co2_emisyonu / 1000, 0),
            'yillik_enerji_tuketimi_gwh': round(yillik_enerji_tuketimi / 3600, 0),
            'ataturk_baraji_kati': round(yillik_su_m3 / ataturk_baraji_hacmi, 3),
            'istanbul_tuketim_kati': round(yillik_su_m3 / istanbul_yillik_tuketim, 2),
            'gri_su_hapsolan_m3': round(yillik_hacim * 150, 0),  # 150L/m³ hapsolmuş su
            'cimento_uretimi_ton': self.turkiye_beton['yillik_cimento_uretim_ton']
        }

    def alternatif_senaryo_analizi(self, alternatif_oran: float = 0.30) -> Dict:
        """Alternatif malzemelerle ikame senaryosu"""
        
        turkiye_analiz = self.turkiye_beton_etkisi()
        yillik_hacim = turkiye_analiz['yillik_beton_uretim_m3']
        
        # Alternatif malzeme dağılımı
        alternatif_dagilim = {
            'hempcrete': 0.40,    # %40 kenevir beton
            'ahsap_clt': 0.35,    # %35 ahşap
            'adobe': 0.15,        # %15 kerpıç
            'mycelium': 0.10      # %10 mantar
        }
        
        # İkame edilen miktar
        ikame_hacim = yillik_hacim * alternatif_oran
        kalan_beton_hacim = yillik_hacim * (1 - alternatif_oran)
        
        # Kalan beton etkisi
        beton = self.malzemeler['beton']
        kalan_su = kalan_beton_hacim * beton.su_tuketimi_l_m3 / 1000  # m³
        kalan_co2 = kalan_beton_hacim * beton.co2_emisyonu_kg_m3 / 1000  # ton
        
        # Alternatif malzemeler etkisi
        toplam_alt_su = 0
        toplam_alt_co2 = 0
        alternatif_detay = {}
        
        for malzeme_ad, oran in alternatif_dagilim.items():
            malzeme = self.malzemeler[malzeme_ad]
            malzeme_hacim = ikame_hacim * oran
            
            malzeme_su = malzeme_hacim * malzeme.su_tuketimi_l_m3 / 1000  # m³
            malzeme_co2 = malzeme_hacim * malzeme.co2_emisyonu_kg_m3 / 1000  # ton
            
            toplam_alt_su += malzeme_su
            toplam_alt_co2 += malzeme_co2
            
            alternatif_detay[malzeme_ad] = {
                'hacim_m3': round(malzeme_hacim, 0),
                'su_tuketimi_m3': round(malzeme_su, 0),
                'co2_emisyonu_ton': round(malzeme_co2, 0)
            }
        
        # Toplam tasarruf
        mevcut_toplam_su = turkiye_analiz['yillik_su_tuketimi_m3']
        mevcut_toplam_co2 = turkiye_analiz['yillik_co2_emisyonu_ton']
        
        yeni_toplam_su = kalan_su + toplam_alt_su
        yeni_toplam_co2 = kalan_co2 + toplam_alt_co2
        
        su_tasarrufu = mevcut_toplam_su - yeni_toplam_su
        co2_azaltimi = mevcut_toplam_co2 - yeni_toplam_co2
        
        return {
            'senaryo_adi': f'%{int(alternatif_oran*100)} Alternatif Malzeme İkamesi',
            'ikame_orani_yuzde': int(alternatif_oran * 100),
            'ikame_edilen_hacim_m3': round(ikame_hacim, 0),
            'kalan_beton_hacim_m3': round(kalan_beton_hacim, 0),
            'alternatif_dagilim': alternatif_detay,
            'mevcut_su_tuketimi_m3': round(mevcut_toplam_su, 0),
            'yeni_su_tuketimi_m3': round(yeni_toplam_su, 0),
            'su_tasarrufu_m3': round(su_tasarrufu, 0),
            'su_tasarrufu_yuzde': round((su_tasarrufu / mevcut_toplam_su) * 100, 1),
            'mevcut_co2_emisyonu_ton': round(mevcut_toplam_co2, 0),
            'yeni_co2_emisyonu_ton': round(yeni_toplam_co2, 0),
            'co2_azaltimi_ton': round(co2_azaltimi, 0),
            'co2_azaltimi_yuzde': round((co2_azaltimi / mevcut_toplam_co2) * 100, 1)
        }

    def proje_hesaplayici(self, proje_tipi: str, metrekare: float, kat_sayisi: int = 1) -> Dict:
        """Belirli proje için malzeme karşılaştırması"""
        
        # Proje tipine göre hacim hesaplama
        proje_katsayilari = {
            'konut': 0.25,      # m³ beton/m² alan
            'ofis': 0.35,       # Daha fazla yapısal eleman
            'fabrika': 0.40,    # Ağır yapı
            'okul': 0.30,       # Orta seviye
            'hastane': 0.45,    # Yoğun altyapı
            'villa': 0.20       # Hafif yapı
        }
        
        katsayi = proje_katsayilari.get(proje_tipi, 0.30)
        toplam_hacim = metrekare * kat_sayisi * katsayi
        
        # Malzeme karşılaştırmaları
        sonuclar = {}
        
        karsilastirmalar = [
            ('beton', 'hempcrete'),
            ('beton', 'ahsap_clt'),
            ('beton', 'adobe')
        ]
        
        for malzeme1, malzeme2 in karsilastirmalar:
            analiz = self.malzeme_karsilastirma(toplam_hacim, malzeme1, malzeme2)
            sonuclar[f'{malzeme1}_vs_{malzeme2}'] = analiz
        
        # Özet bilgi
        ozet = {
            'proje_tipi': proje_tipi,
            'toplam_alan_m2': metrekare,
            'kat_sayisi': kat_sayisi,
            'yapisal_hacim_m3': round(toplam_hacim, 1),
            'hacim_katsayisi': katsayi,
            'karsilastirmalar': sonuclar
        }
        
        return ozet

def main():
    """Test fonksiyonu"""
    hesaplayici = BetonSuHesaplayici()
    
    print("🏗️ BETON ENDÜSTRİSİ SU TÜKETİMİ ANALİZİ")
    print("=" * 60)
    
    # Türkiye geneli analiz
    turkiye = hesaplayici.turkiye_beton_etkisi()
    print(f"🇹🇷 TÜRKİYE YILLIK BETON ÜRETİMİ:")
    print(f"   Beton Üretimi: {turkiye['yillik_beton_uretim_m3']:,} m³")
    print(f"   Su Tüketimi: {turkiye['yillik_su_tuketimi_m3']:,} m³")
    print(f"   CO2 Emisyonu: {turkiye['yillik_co2_emisyonu_ton']:,} ton")
    print(f"   Atatürk Barajı'nın {turkiye['ataturk_baraji_kati']:.3f} katı su")
    
    print("\n" + "=" * 60)
    
    # Alternatif senaryo
    senaryo = hesaplayici.alternatif_senaryo_analizi(0.30)
    print(f"📊 {senaryo['senaryo_adi']} SENARYOSU:")
    print(f"   Su Tasarrufu: {senaryo['su_tasarrufu_m3']:,} m³ (%{senaryo['su_tasarrufu_yuzde']})")
    print(f"   CO2 Azaltımı: {senaryo['co2_azaltimi_ton']:,} ton (%{senaryo['co2_azaltimi_yuzde']})")
    
    print("\n" + "=" * 60)
    
    # Örnek proje analizi
    proje = hesaplayici.proje_hesaplayici('konut', 1000, 5)  # 1000m² 5 katlı konut
    print(f"🏠 ÖRNEK PROJE ANALİZİ:")
    print(f"   Proje: {proje['proje_tipi'].title()}")
    print(f"   Alan: {proje['toplam_alan_m2']} m² × {proje['kat_sayisi']} kat")
    print(f"   Yapısal Hacim: {proje['yapisal_hacim_m3']} m³")
    
    # Beton vs Hempcrete karşılaştırması
    beton_hempcrete = proje['karsilastirmalar']['beton_vs_hempcrete']
    karsilastirma = beton_hempcrete['karsilastirma']
    print(f"\n   🌿 BETON vs HEMPcrete:")
    print(f"      Su Tasarrufu: {karsilastirma['su_tasarrufu_l']:,.0f} L (%{karsilastirma['su_tasarrufu_yuzde']:.0f})")
    print(f"      CO2 Azaltımı: {karsilastirma['co2_azaltimi_kg']:,.0f} kg")
    print(f"      Maliyet Farkı: {karsilastirma['maliyet_farki_tl']:,.0f} TL")

if __name__ == "__main__":
    main() 