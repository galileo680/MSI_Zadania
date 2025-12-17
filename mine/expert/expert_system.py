"""
Prosty system ekspertowy - diagnoza chorob (reguly if-then)
"""

def diagnose(symptoms):
    if "goraczka" in symptoms and "kaszel" in symptoms and "bol_miesni" in symptoms:
        return "Grypa"
    if "katar" in symptoms and "kichanie" in symptoms and "swedzenie_oczu" in symptoms:
        return "Alergia"
    if "goraczka" in symptoms and "utrata_wechu" in symptoms:
        return "COVID-19"
    if "nudnosci" in symptoms and "wymioty" in symptoms and "biegunka" in symptoms:
        return "Zatrucie pokarmowe"
    if "bol_gardla" in symptoms and "goraczka" in symptoms:
        return "Angina"
    if "katar" in symptoms and "kaszel" in symptoms:
        return "Przeziebienie"
    return "Nieznana choroba - idz do lekarza"

# Test
print(diagnose(["goraczka", "kaszel", "bol_miesni"]))  # Grypa
print(diagnose(["katar", "kichanie", "swedzenie_oczu"]))  # Alergia
print(diagnose(["goraczka", "utrata_wechu"]))  # COVID-19
print(diagnose(["nudnosci", "wymioty", "biegunka"]))  # Zatrucie pokarmowe