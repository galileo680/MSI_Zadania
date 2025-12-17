# Tablica wag IFPUG
WEIGHTS = {
    #        Low  Avg  High
    "EI":  [3,   4,   6],
    "EO":  [4,   5,   7],
    "EQ":  [3,   4,   6],
    "ILF": [7,   10,  15],
    "EIF": [5,   7,   10]
}

COMPLEXITY = {"Low": 0, "Average": 1, "High": 2}

# Unadjusted Function Points
def calculate_ufp(functions):
    ufp = 0
    for func_type, complexity, name in functions:
        weight = WEIGHTS[func_type][COMPLEXITY[complexity]]
        ufp += weight
        print(f"  {name}: {func_type} ({complexity}) = {weight} pkt")
    return ufp

# Value Adjustment Factor
def calculate_vaf(gsc):
    tdi = sum(gsc)
    vaf = 0.65 + (0.01 * tdi)
    return vaf, tdi

# Function Points
def calculate_fp(functions, gsc):
    print("\n" + "=" * 50)
    print("RAPORT PUNKTOW FUNKCYJNYCH")
    print("=" * 50)
    
    print("\n1. FUNKCJE SYSTEMU:")
    print("-" * 50)
    ufp = calculate_ufp(functions)
    
    print("-" * 50)
    print(f"   UFP (Unadjusted Function Points) = {ufp}")
    
    print("\n2. WSPOLCZYNNIKI WPLYWU (GSC):")
    print("-" * 50)
    vaf, tdi = calculate_vaf(gsc)
    print(f"   TDI (Total Degree of Influence) = {tdi}")
    print(f"   VAF = 0.65 + (0.01 x {tdi}) = {vaf:.2f}")
    
    fp = ufp * vaf
    
    print("\n3. WYNIK KONCOWY:")
    print("-" * 50)
    print(f"   FP = UFP x VAF = {ufp} x {vaf:.2f} = {fp:.1f}")
    print("=" * 50)
    
    return fp


cinema_functions = [
    # External Inputs
    ("EI", "Average", "Dodanie rezerwacji"),
    ("EI", "Low", "Rejestracja uzytkownika"),
    ("EI", "Low", "Logowanie"),
    ("EI", "Average", "Anulowanie rezerwacji"),
    
    # External Outputs
    ("EO", "Average", "Generowanie biletu PDF"),
    ("EO", "High", "Raport dzienny sprzedazy"),
    ("EO", "Low", "Potwierdzenie email"),
    
    # External Inquiries
    ("EQ", "Low", "Wyszukiwanie seansow"),
    ("EQ", "Average", "Sprawdzenie dostepnosci miejsc"),
    ("EQ", "Low", "Wyswietlenie szczegulow filmu"),
    ("EQ", "Low", "Historia rezerwacji uzytkownika"),
    
    # Internal Logical Files
    ("ILF", "Average", "Baza filmow"),
    ("ILF", "High", "Baza rezerwacji"),
    ("ILF", "Average", "Baza uzytkownikow"),
    ("ILF", "Low", "Baza sal kinowych"),
    
    # External Interface Files
    ("EIF", "Average", "System platnosci online"),
    ("EIF", "Low", "API dystrybutora filmow"),
]

# 14 wspolczynnikow wplywu systemowego (GSC) - skala 0-5
cinema_gsc = [
    3,  # 1. Komunikacja danych
    2,  # 2. Przetwarzanie rozproszone
    3,  # 3. Wydajnosc
    2,  # 4. Obciazenie sprzetu
    4,  # 5. Czestotliwosc transakcji
    5,  # 6. Wprowadzanie danych online
    4,  # 7. Latwosc obslugi
    3,  # 8. Aktualizacje online
    2,  # 9. Zlozone przetwarzanie
    2,  # 10. Reuzywalnosc
    3,  # 11. Latwosc instalacji
    2,  # 12. Latwosc obslugi operacyjnej
    1,  # 13. Wiele lokalizacji
    3,  # 14. Latwosc zmian
]

if __name__ == "__main__":
    print("\nSYSTEM REZERWACJI BILETOW DO KINA")
    fp = calculate_fp(cinema_functions, cinema_gsc)