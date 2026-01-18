import sys
import random
import os

def get_bit(value, n):
    return (value >> n) & 1 # pobiera n-ty bit z wartości

def set_bit(value, n, bit_val):
    if bit_val: # ustawia n-ty bit na 1
        return value | (1 << n)
    else: # ustawia n-ty bit na 0
        return value & ~(1 << n)


def zakoduj_polbajt(dane_4bit):
    """
    koduje 4 bity danych w 8 bitów (7 bitów Hamminga + 1 bit parzystości)
    układ bitów: bity kontrolne są na pozycjach potęg 2
    pozycje (1-8): p1 p2 d1 p4 d2 d3 d4 p_calosc
    """
    # rozdzielenie bitów danych (d1 to najstarszy bit, d4 najmłodszy z czwórki)
    # przyjmujemy, że wejście to 0000(d1)(d2)(d3)(d4)
    d1 = get_bit(dane_4bit, 3)
    d2 = get_bit(dane_4bit, 2)
    d3 = get_bit(dane_4bit, 1)
    d4 = get_bit(dane_4bit, 0)

    # obliczenie bitów kontrolnych (p1, p2, p4) - parzystość odpowiednich grup
    # p1 sprawdza pozycje: 1, 3, 5, 7 (czyli p1, d1, d2, d4) -> p1 = d1 ^ d2 ^ d4
    p1 = d1 ^ d2 ^ d4
    # p2 sprawdza pozycje: 2, 3, 6, 7 (czyli p2, d1, d3, d4) -> p2 = d1 ^ d3 ^ d4
    p2 = d1 ^ d3 ^ d4
    # p4 sprawdza pozycje: 4, 5, 6, 7 (czyli p4, d2, d3, d4) -> p4 = d2 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4

    # bit: p1 p2 d1 p4 d2 d3 d4
    
    slowo_7bit = 0
    slowo_7bit = set_bit(slowo_7bit, 0, p1)
    slowo_7bit = set_bit(slowo_7bit, 1, p2)
    slowo_7bit = set_bit(slowo_7bit, 2, d1)
    slowo_7bit = set_bit(slowo_7bit, 3, p4)
    slowo_7bit = set_bit(slowo_7bit, 4, d2)
    slowo_7bit = set_bit(slowo_7bit, 5, d3)
    slowo_7bit = set_bit(slowo_7bit, 6, d4)

    # obliczenie ósmego bitu (rozszerzenie) - parzystość całego słowa 7-bitowego
    parzystosc_calosc = 0
    for i in range(7):
        parzystosc_calosc ^= get_bit(slowo_7bit, i)
    
    slowo_8bit = set_bit(slowo_7bit, 7, parzystosc_calosc)
    
    return slowo_8bit

def odkoduj_bajt(zakodowany_bajt):
    """
    odkodowuje bajt i zwraca krotkę (odkodowane_4bity, status_bledu)
    status_bledu: 0 - OK, 1 - skorygowano 1 błąd, 2 - wykryto 2 błędy (niekorygowalne)
    """
    # obliczamy ogólną parzystość otrzymanego bajtu
    parzystosc_otrzymana = 0
    for i in range(8):
        parzystosc_otrzymana ^= get_bit(zakodowany_bajt, i)
    
    # bity z odebranego słowa
    r_p1 = get_bit(zakodowany_bajt, 0)
    r_p2 = get_bit(zakodowany_bajt, 1)
    r_d1 = get_bit(zakodowany_bajt, 2)
    r_p4 = get_bit(zakodowany_bajt, 3)
    r_d2 = get_bit(zakodowany_bajt, 4)
    r_d3 = get_bit(zakodowany_bajt, 5)
    r_d4 = get_bit(zakodowany_bajt, 6)

    # jaka powinna być parzystość dla odebranych danych
    c_p1 = r_d1 ^ r_d2 ^ r_d4
    c_p2 = r_d1 ^ r_d3 ^ r_d4
    c_p4 = r_d2 ^ r_d3 ^ r_d4

    # syndrom: bit 0 to różnica p1, bit 1 to różnica p2, bit 2 to różnica p4
    s0 = r_p1 ^ c_p1
    s1 = r_p2 ^ c_p2
    s2 = r_p4 ^ c_p4
    
    syndrom = (s2 << 2) | (s1 << 1) | s0 # wartość syndromu wskazuje pozycję błędu (1-7), 0 = brak błędu

    status = 0
    skorygowany_bajt = zakodowany_bajt

    # logika Single Error Correction, Double Error Detection jest taka
    # parzystosc_otrzymana == 0 -> Liczba jedynek jest parzysta (OK lub 2 błędy)
    # parzystosc_otrzymana == 1 -> Liczba jedynek jest nieparzysta (1 błąd)

    if parzystosc_otrzymana == 1:
        # wystąpił pojedynczy błąd (lub nieparzysta liczba błędów > 1, zakładamy 1)
        if syndrom != 0:
            # błąd jest wewnątrz 7 bitów Hamminga na pozycji 'syndrom'
            # naprawiamy błąd (pozycja syndromu w pythonie to indeks syndrom-1)
            pozycja_do_naprawy = syndrom - 1
            aktualny_bit = get_bit(skorygowany_bajt, pozycja_do_naprawy)
            skorygowany_bajt = set_bit(skorygowany_bajt, pozycja_do_naprawy, not aktualny_bit)
            status = 1 # 1 błąd skorygowany
        else:
            # syndrom 0, ale parzystość zła -> błąd na ósmym bicie parzystości
            # dane są poprawne, ignorujemy błąd 8 bitu
            status = 1 # formalnie był 1 błąd, ale dane nienaruszone
            
    elif parzystosc_otrzymana == 0:
        if syndrom != 0:
            # parzystość OK (czyli parzysta liczba błędów), ale syndrom niezerowy
            status = 2 
        else:
            # parzystość OK, syndrom 0 -> brak błędów
            status = 0

    out_d1 = get_bit(skorygowany_bajt, 2)
    out_d2 = get_bit(skorygowany_bajt, 4)
    out_d3 = get_bit(skorygowany_bajt, 5)
    out_d4 = get_bit(skorygowany_bajt, 6)

    dane_wynikowe = (out_d1 << 3) | (out_d2 << 2) | (out_d3 << 1) | out_d4
    return dane_wynikowe, status

def program_koder(plik_we, plik_wy):
    """Wczytuje plik, dzieli na połówki bajtów, koduje Hammingiem(8,4) i zapisuje."""
    try:
        with open(plik_we, 'rb') as f_in, open(plik_wy, 'wb') as f_out:
            while True:
                bajt = f_in.read(1)
                if not bajt:
                    break
                wartosc = bajt[0]
                
                gorna_czworka = (wartosc >> 4) & 0x0F # najwyższe 4 bity, 0x0F to maska 00001111
                dolna_czworka = wartosc & 0x0F
                
                kod1 = zakoduj_polbajt(gorna_czworka)
                kod2 = zakoduj_polbajt(dolna_czworka)

                f_out.write(bytes([kod1, kod2]))
        print(f"Zakodowano plik '{plik_we}' do '{plik_wy}'.")
    except FileNotFoundError:
        print("Błąd: Nie znaleziono pliku wejściowego.")

def program_szum(prawdopodobienstwo_p, plik_we, plik_wy):
    try:
        p = float(prawdopodobienstwo_p)
        with open(plik_we, 'rb') as f_in, open(plik_wy, 'wb') as f_out:
            dane = bytearray(f_in.read())
            
            zmienione_bity = 0
            # iterujemy przez każdy bajt, a w nim przez każdy bit
            for i in range(len(dane)):
                original_byte = dane[i]
                new_byte = original_byte
                for bit_idx in range(8):
                    if random.random() < p:
                        new_byte ^= (1 << bit_idx)
                        zmienione_bity += 1
                dane[i] = new_byte
            
            f_out.write(dane)
        print(f"Zaszumiono plik '{plik_we}' do '{plik_wy}' (p={p}). Zmieniono {zmienione_bity} bitów.")
    except ValueError:
        print("Błąd: Prawdopodobieństwo musi być liczbą zmiennoprzecinkową.")
    except FileNotFoundError:
        print("Błąd: Nie znaleziono pliku wejściowego.")

def program_dekoder(plik_we, plik_wy):
    """Dekoduje plik, naprawia 1 błąd, zlicza przypadki z 2 błędami."""
    licznik_2_bledow = 0
    try:
        with open(plik_we, 'rb') as f_in, open(plik_wy, 'wb') as f_out:
            # czytamy parami, bo 2 bajty kodu = 1 bajt oryginalny
            while True:
                chunk = f_in.read(2)
                if not chunk or len(chunk) < 2:
                    break
                
                bajt_kod1 = chunk[0]
                bajt_kod2 = chunk[1]
                
                dane1, status1 = odkoduj_bajt(bajt_kod1)
                dane2, status2 = odkoduj_bajt(bajt_kod2)
                
                if status1 == 2:
                    licznik_2_bledow += 1
                if status2 == 2:
                    licznik_2_bledow += 1
                
                oryginalny_bajt = (dane1 << 4) | dane2
                f_out.write(bytes([oryginalny_bajt]))
                
        print(f"Odkodowano plik '{plik_we}' do '{plik_wy}'.")
        print(f"Liczba przypadków wykrycia 2 błędów (niekorygowalnych): {licznik_2_bledow}")
        
    except FileNotFoundError:
        print("Błąd: Nie znaleziono pliku wejściowego.")

def program_sprawdz(plik1, plik2):
    try:
        with open(plik1, 'rb') as f1, open(plik2, 'rb') as f2:
            dane1 = f1.read()
            dane2 = f2.read()
            
        rozmiar1 = len(dane1)
        rozmiar2 = len(dane2)
        
        dlugosc_min = min(rozmiar1, rozmiar2)
        bledne_bajty = 0
        
        for i in range(dlugosc_min):
            if dane1[i] != dane2[i]:
                bledne_bajty += 1
        
        # jeśli pliki mają różną długość, nadmiarowe bajty też liczymy jako błąd
        roznica_dlugosci = abs(rozmiar1 - rozmiar2)
        bledne_bajty += roznica_dlugosci
        
        print(f"--- Raport porównania ---")
        print(f"Plik 1 ({plik1}): {rozmiar1} bajtów")
        print(f"Plik 2 ({plik2}): {rozmiar2} bajtów")
        
        if bledne_bajty == 0:
            print("WYNIK: Pliki są IDENTYCZNE.")
        else:
            # procent błędów względem pliku 1
            procent_bledow = (bledne_bajty / rozmiar1 * 100) if rozmiar1 > 0 else 0
            print(f"WYNIK: Pliki RÓŻNIĄ się.")
            print(f"Liczba niezgodnych bajtów: {bledne_bajty}")
            print(f"Błędy stanowią {procent_bledow:.2f}% pliku oryginalnego.")
            
            if roznica_dlugosci > 0:
                print(f"UWAGA: Pliki mają różną długość! (Różnica: {roznica_dlugosci} bajtów)")
            
    except FileNotFoundError:
        print("Błąd: Jeden z plików nie istnieje.")

if __name__ == "__main__":
    KODER_IN = "../test_kkd/pan-tadeusz-czyli-ostatni-zajazd-na-litwie.txt"
    KODER_OUT = "kodowany.bin"
    SZUM_IN = "kodowany.bin"
    SZUM_OUT = "zaszumiony.bin"
    DEKODER_IN = "zaszumiony.bin"
    DEKODER_OUT = "odkodowany.txt"
    SPRAWDZ_IN1 = "../test_kkd/pan-tadeusz-czyli-ostatni-zajazd-na-litwie.txt"
    SPRAWDZ_IN2 = "odkodowany.txt"

    program_koder(KODER_IN, KODER_OUT)
    program_szum(0.01, SZUM_IN, SZUM_OUT)  # 1% szumu
    program_dekoder(DEKODER_IN, DEKODER_OUT)
    program_sprawdz(SPRAWDZ_IN1, SPRAWDZ_IN2)

