#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU TASARRUFU HESAPLAYICI
Türkiye Su Sorunu Projesi - Hesaplama Araçları

Bu modül, ev ve işyerleri için su tasarrufu potansiyelini hesaplar.
Çeşitli su tasarrufu önlemlerinin etkisini analiz eder.
"""

import math
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SuTasarrufuHesaplayici:
    """Ana hesaplama sınıfı"""
    
    def __init__(self):
        self.su_fiyatlari = {
            'istanbul': 6.85,  # TL/m³
            'ankara': 5.92,
            'izmir': 6.12,
            'antalya': 7.20,
            'bursa': 5.48,
            'adana': 4.95,
            'ortalama': 6.09
        }
        
        self.yagis_verileri = {
            'istanbul': 816,  # mm/yıl
            'ankara': 415,
            'izmir': 712,
            'antalya': 1002,
            'trabzon': 1318,
            'kayseri': 392,
            'ortalama': 650
        }
        
        self.ev_ortalama_tuketim = {
            'gunluk_kisi_basi': 150,  # litre
            'yillik_hane': 120,       # m³ (4 kişilik aile)
            'bahce_sulama': 200,      # m³/yıl (100m² bahçe)
            'araba_yikama': 24        # m³/yıl (ayda 2 kez)
        }

    def yagmur_suyu_potansiyeli(self, cati_alani_m2: float, sehir: str = 'ortalama') -> Dict:
        """Yağmur suyu toplama potansiyelini hesaplar"""
        
        yagis = self.yagis_verileri.get(sehir, self.yagis_verileri['ortalama'])
        
        # Yağmur suyu toplama hesaplaması
        # Toplam potansiyel = Çatı alanı × Yağış × Verimlilik katsayısı
        verimlilik = 0.85  # %85 toplama verimi (kayıplar dahil)
        
        yillik_toplama_m3 = (cati_alani_m2 * yagis * verimlilik) / 1000
        
        # Su fiyatına göre tasarruf
        su_fiyati = self.su_fiyatlari.get(sehir, self.su_fiyatlari['ortalama'])
        yillik_tasarruf_tl = yillik_toplama_m3 * su_fiyati
        
        # Aylık dağılım (Türkiye ortalama yağış dağılımı)
        aylik_dagilim = [0.12, 0.10, 0.09, 0.08, 0.06, 0.04, 
                        0.03, 0.04, 0.06, 0.08, 0.11, 0.13]
        
        aylik_toplama = [yillik_toplama_m3 * oran for oran in aylik_dagilim]
        
        return {
            'yillik_toplama_m3': round(yillik_toplama_m3, 1),
            'yillik_tasarruf_tl': round(yillik_tasarruf_tl, 0),
            'aylik_toplama_m3': [round(x, 1) for x in aylik_toplama],
            'gunluk_ortalama_l': round(yillik_toplama_m3 * 1000 / 365, 1),
            'yagis_mm': yagis,
            'verimlilik_yuzde': int(verimlilik * 100)
        }

    def gri_su_potansiyeli(self, hane_buyuklugu: int = 4) -> Dict:
        """Gri su geri dönüşüm potansiyelini hesaplar"""
        
        kisi_basi_gunluk = self.ev_ortalama_tuketim['gunluk_kisi_basi']
        toplam_gunluk = kisi_basi_gunluk * hane_buyuklugu
        
        # Gri su kaynakları (günlük kullanım dağılımı)
        gri_su_oranlari = {
            'dus_banyo': 0.35,      # %35 duş ve banyo
            'camasir': 0.15,        # %15 çamaşır makinesi
            'bulasik': 0.10,        # %10 bulaşık
            'lavabo': 0.08          # %8 lavabo
        }
        
        toplam_gri_su_orani = sum(gri_su_oranlari.values())
        gunluk_gri_su_l = toplam_gunluk * toplam_gri_su_orani
        yillik_gri_su_m3 = gunluk_gri_su_l * 365 / 1000
        
        # Arıtma verimliliği
        aritma_verimliligi = 0.85  # %85 geri kazanım
        kullanilabilir_m3 = yillik_gri_su_m3 * aritma_verimliligi
        
        # Kullanım alanları
        kullanim_alanlari = {
            'wc_rezervuar': kullanilabilir_m3 * 0.4,    # %40 WC
            'bahce_sulama': kullanilabilir_m3 * 0.4,    # %40 bahçe
            'temizlik': kullanilabilir_m3 * 0.2         # %20 temizlik
        }
        
        # Ekonomik analiz
        su_fiyati = self.su_fiyatlari['ortalama']
        yillik_tasarruf = kullanilabilir_m3 * su_fiyati
        
        return {
            'gunluk_gri_su_l': round(gunluk_gri_su_l, 1),
            'yillik_ham_gri_su_m3': round(yillik_gri_su_m3, 1),
            'yillik_kullanilabilir_m3': round(kullanilabilir_m3, 1),
            'kullanim_alanlari': {k: round(v, 1) for k, v in kullanim_alanlari.items()},
            'yillik_tasarruf_tl': round(yillik_tasarruf, 0),
            'aritma_verimliligi': int(aritma_verimliligi * 100),
            'gri_su_oranlari': gri_su_oranlari
        }

    def su_tasarruflu_ekipman_analizi(self, hane_buyuklugu: int = 4) -> Dict:
        """Su tasarruflu ekipmanların etki analizi"""
        
        gunluk_tuketim = self.ev_ortalama_tuketim['gunluk_kisi_basi'] * hane_buyuklugu
        yillik_tuketim_m3 = gunluk_tuketim * 365 / 1000
        
        # Ekipman tasarruf oranları
        ekipman_tasarruflari = {
            'havalandirmali_musluk': {
                'tasarruf_orani': 0.40,
                'etkiledigi_kullanim_orani': 0.25,  # Toplam kullanımın %25'i musluklar
                'maliyet_tl': 300
            },
            'su_tasarruflu_dus': {
                'tasarruf_orani': 0.50,
                'etkiledigi_kullanim_orani': 0.30,  # %30 duş kullanımı
                'maliyet_tl': 250
            },
            'cift_basmali_wc': {
                'tasarruf_orani': 0.35,
                'etkiledigi_kullanim_orani': 0.25,  # %25 WC kullanımı
                'maliyet_tl': 400
            },
            'sensörlu_musluk': {
                'tasarruf_orani': 0.60,
                'etkiledigi_kullanim_orani': 0.15,  # %15 genel musluk
                'maliyet_tl': 600
            }
        }
        
        sonuclar = {}
        toplam_tasarruf_m3 = 0
        toplam_maliyet = 0
        
        su_fiyati = self.su_fiyatlari['ortalama']
        
        for ekipman, veri in ekipman_tasarruflari.items():
            # Her ekipmanın tasarruf etkisi
            etkilenen_tuketim = yillik_tuketim_m3 * veri['etkiledigi_kullanim_orani']
            tasarruf_m3 = etkilenen_tuketim * veri['tasarruf_orani']
            tasarruf_tl = tasarruf_m3 * su_fiyati
            geri_odeme_yil = veri['maliyet_tl'] / tasarruf_tl if tasarruf_tl > 0 else float('inf')
            
            sonuclar[ekipman] = {
                'yillik_tasarruf_m3': round(tasarruf_m3, 1),
                'yillik_tasarruf_tl': round(tasarruf_tl, 0),
                'maliyet_tl': veri['maliyet_tl'],
                'geri_odeme_yil': round(geri_odeme_yil, 1),
                'tasarruf_orani': int(veri['tasarruf_orani'] * 100)
            }
            
            toplam_tasarruf_m3 += tasarruf_m3
            toplam_maliyet += veri['maliyet_tl']
        
        # Toplam analiz
        toplam_tasarruf_tl = toplam_tasarruf_m3 * su_fiyati
        toplam_geri_odeme = toplam_maliyet / toplam_tasarruf_tl if toplam_tasarruf_tl > 0 else 0
        
        return {
            'ekipman_detay': sonuclar,
            'toplam_yillik_tasarruf_m3': round(toplam_tasarruf_m3, 1),
            'toplam_yillik_tasarruf_tl': round(toplam_tasarruf_tl, 0),
            'toplam_yatirim_tl': toplam_maliyet,
            'toplam_geri_odeme_yil': round(toplam_geri_odeme, 1),
            'yillik_tuketim_m3': round(yillik_tuketim_m3, 1)
        }

    def permekültur_bahce_analizi(self, bahce_alani_m2: float, sehir: str = 'ortalama') -> Dict:
        """Permekültür bahçe su tasarrufu analizi"""
        
        # Geleneksel bahçe su tüketimi
        geleneksel_tuketim_l_m2_gun = 5  # Litre/m²/gün (yaz ayları ortalama)
        yaz_gun_sayisi = 150  # Sulama gerektiren gün sayısı
        geleneksel_yillik_m3 = (bahce_alani_m2 * geleneksel_tuketim_l_m2_gun * yaz_gun_sayisi) / 1000
        
        # Permekültür bahçe tasarrufu
        permekültur_tasarruf_orani = 0.75  # %75 daha az su
        permekültur_yillik_m3 = geleneksel_yillik_m3 * (1 - permekültur_tasarruf_orani)
        
        # Yağmur suyu entegrasyonu
        yagmur_analizi = self.yagmur_suyu_potansiyeli(bahce_alani_m2 * 0.3, sehir)  # %30'u etkili toplama
        yagmur_karsilama_orani = min(1.0, yagmur_analizi['yillik_toplama_m3'] / permekültur_yillik_m3)
        
        # Ekonomik analiz
        su_fiyati = self.su_fiyatlari.get(sehir, self.su_fiyatlari['ortalama'])
        tasarruf_m3 = geleneksel_yillik_m3 - permekültur_yillik_m3
        yillik_tasarruf_tl = tasarruf_m3 * su_fiyati
        
        # Kurulum maliyeti tahmini
        m2_basina_maliyet = 50  # TL/m² (ortalama permekültür kurulum)
        kurulum_maliyeti = bahce_alani_m2 * m2_basina_maliyet
        geri_odeme_yil = kurulum_maliyeti / yillik_tasarruf_tl if yillik_tasarruf_tl > 0 else 0
        
        # Ek faydalar
        gida_uretimi_kg = bahce_alani_m2 * 3  # kg/m²/yıl ortalama
        gida_degeri_tl = gida_uretimi_kg * 8  # TL/kg ortalama
        
        return {
            'geleneksel_tuketim_m3': round(geleneksel_yillik_m3, 1),
            'permekültur_tuketim_m3': round(permekültur_yillik_m3, 1),
            'su_tasarrufu_m3': round(tasarruf_m3, 1),
            'tasarruf_orani': int(permekültur_tasarruf_orani * 100),
            'yillik_tasarruf_tl': round(yillik_tasarruf_tl, 0),
            'yagmur_karsilama_orani': round(yagmur_karsilama_orani * 100, 1),
            'kurulum_maliyeti_tl': kurulum_maliyeti,
            'geri_odeme_yil': round(geri_odeme_yil, 1),
            'yillik_gida_uretimi_kg': round(gida_uretimi_kg, 0),
            'gida_degeri_tl': round(gida_degeri_tl, 0),
            'toplam_ekonomik_fayda_tl': round(yillik_tasarruf_tl + gida_degeri_tl, 0)
        }

    def kapsamli_ev_analizi(self, hane_buyuklugu: int = 4, cati_alani: float = 100, 
                          bahce_alani: float = 100, sehir: str = 'ortalama') -> Dict:
        """Tüm sistemlerin entegre analizi"""
        
        # Bireysel analizler
        yagmur = self.yagmur_suyu_potansiyeli(cati_alani, sehir)
        gri_su = self.gri_su_potansiyeli(hane_buyuklugu)
        ekipmanlar = self.su_tasarruflu_ekipman_analizi(hane_buyuklugu)
        bahce = self.permekültur_bahce_analizi(bahce_alani, sehir)
        
        # Mevcut tüketim
        yillik_tuketim = ekipmanlar['yillik_tuketim_m3'] + bahce['geleneksel_tuketim_m3']
        
        # Toplam tasarruf potansiyeli
        toplam_tasarruf_m3 = (
            yagmur['yillik_toplama_m3'] + 
            gri_su['yillik_kullanilabilir_m3'] + 
            ekipmanlar['toplam_yillik_tasarruf_m3'] + 
            bahce['su_tasarrufu_m3']
        )
        
        # Toplam yatırım
        toplam_yatirim = (
            1500 +  # Yağmur suyu sistemi
            5000 +  # Gri su sistemi  
            ekipmanlar['toplam_yatirim_tl'] +
            bahce['kurulum_maliyeti_tl']
        )
        
        # Ekonomik analiz
        su_fiyati = self.su_fiyatlari.get(sehir, self.su_fiyatlari['ortalama'])
        toplam_tasarruf_tl = toplam_tasarruf_m3 * su_fiyati + bahce['gida_degeri_tl']
        geri_odeme_yil = toplam_yatirim / toplam_tasarruf_tl if toplam_tasarruf_tl > 0 else 0
        
        # Tasarruf oranı
        tasarruf_orani = min(100, (toplam_tasarruf_m3 / yillik_tuketim) * 100)
        
        return {
            'mevcut_yillik_tuketim_m3': round(yillik_tuketim, 1),
            'toplam_tasarruf_m3': round(toplam_tasarruf_m3, 1),
            'tasarruf_orani_yuzde': round(tasarruf_orani, 1),
            'yillik_tasarruf_tl': round(toplam_tasarruf_tl, 0),
            'toplam_yatirim_tl': toplam_yatirim,
            'geri_odeme_yil': round(geri_odeme_yil, 1),
            'detaylar': {
                'yagmur_suyu': yagmur,
                'gri_su': gri_su,
                'ekipmanlar': ekipmanlar,
                'bahce': bahce
            },
            'analiz_tarihi': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

def main():
    """Test fonksiyonu"""
    hesaplayici = SuTasarrufuHesaplayici()
    
    print("🌊 SU TASARRUFU HESAPLAYICI")
    print("=" * 50)
    
    # Örnek hesaplama
    sonuc = hesaplayici.kapsamli_ev_analizi(
        hane_buyuklugu=4,
        cati_alani=120,
        bahce_alani=150,
        sehir='istanbul'
    )
    
    print(f"Mevcut Yıllık Tüketim: {sonuc['mevcut_yillik_tuketim_m3']} m³")
    print(f"Tasarruf Potansiyeli: {sonuc['toplam_tasarruf_m3']} m³ (%{sonuc['tasarruf_orani_yuzde']})")
    print(f"Yıllık Ekonomik Fayda: {sonuc['yillik_tasarruf_tl']} TL")
    print(f"Toplam Yatırım: {sonuc['toplam_yatirim_tl']} TL")
    print(f"Geri Ödeme Süresi: {sonuc['geri_odeme_yil']} yıl")
    
    print("\n📊 DETAY ANALİZ:")
    print(f"• Yağmur Suyu: {sonuc['detaylar']['yagmur_suyu']['yillik_toplama_m3']} m³/yıl")
    print(f"• Gri Su: {sonuc['detaylar']['gri_su']['yillik_kullanilabilir_m3']} m³/yıl")
    print(f"• Ekipman Tasarrufu: {sonuc['detaylar']['ekipmanlar']['toplam_yillik_tasarruf_m3']} m³/yıl")
    print(f"• Bahçe Tasarrufu: {sonuc['detaylar']['bahce']['su_tasarrufu_m3']} m³/yıl")

if __name__ == "__main__":
    main() 