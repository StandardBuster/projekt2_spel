# ============================================================
#  SCHACKSPEL i Python
#  Använder: funktioner, listor, tupler, dictionaries, strängar
# ============================================================

# --- KONSTANTER (tuple = oföränderlig sekvens) ---
BRÄDSTORLEK = 8
TOM = "  "   # Tomt fält

# Färger som strängar
VIT   = "V"
SVART = "S"

# Pjäsernas unicode-symboler sparade i en dictionary
PJÄSER: dict[str, str] = {
    "VK":  "♔",  # Vit kung
    "VD":  "♕",  # Vit drottning
    "VT":  "♖",  # Vit torn
    "VL":  "♗",  # Vit löpare
    "VH":  "♘",  # Vit häst
    "VB":  "♙",  # Vit bonde
    "SK":  "♚",  # Svart kung
    "SD":  "♛",  # Svart drottning
    "ST":  "♜",  # Svart torn
    "SL":  "♝",  # Svart löpare
    "SH":  "♞",  # Svart häst
    "SB":  "♟",  # Svart bonde
}

# -------------------------------------------------------
# FUNKTION: Skapa ett nytt schackbräde (lista av listor)
# Returnerar en 8x8 lista med pjäskoder (strängar)
# -------------------------------------------------------
def skapa_bräde() -> list[list[str]]:
    """Skapar startuppställning. Returnerar en 8x8 lista."""

    # Startrader som listor
    svart_rad  = ["ST", "SH", "SL", "SD", "SK", "SL", "SH", "ST"]
    svart_bond = ["SB"] * 8
    tom_rad    = [TOM]  * 8
    vit_bond   = ["VB"] * 8
    vit_rad    = ["VT", "VH", "VL", "VD", "VK", "VL", "VH", "VT"]

    bräde: list[list[str]] = [
        svart_rad[:],    # rad 0  (svart baksida)
        svart_bond[:],   # rad 1
        tom_rad[:],      # rad 2
        tom_rad[:],      # rad 3
        tom_rad[:],      # rad 4
        tom_rad[:],      # rad 5
        vit_bond[:],     # rad 6
        vit_rad[:],      # rad 7  (vit baksida)
    ]
    return bräde


# -------------------------------------------------------
# FUNKTION: Skriv ut brädet snyggt i terminalen
# -------------------------------------------------------
def skriv_bräde(bräde: list[list[str]]) -> None:
    """Skriver ut brädet med koordinater."""
    kolumn_etiketter = "    a   b   c   d   e   f   g   h"
    print("\n" + kolumn_etiketter)
    print("  +" + "---+" * 8)

    for rad_nr in range(BRÄDSTORLEK):
        rad_etikett = str(8 - rad_nr)   # rad 8 överst, rad 1 underst
        rad_str = rad_etikett + " |"

        for kol_nr in range(BRÄDSTORLEK):
            pjäs = bräde[rad_nr][kol_nr]
            if pjäs == TOM:
                symbol = " · "
            else:
                symbol = " " + PJÄSER[pjäs] + " "
            rad_str += symbol + "|"

        print(rad_str + " " + rad_etikett)
        print("  +" + "---+" * 8)

    print(kolumn_etiketter + "\n")


# -------------------------------------------------------
# FUNKTION: Omvandla koordinat (t.ex. "e2") till (rad, kol)
# Returnerar ett TUPLE med (rad, kol), eller None vid fel
# -------------------------------------------------------
def koordinat_till_index(koordinat: str) -> tuple[int, int] | None:
    """Konverterar 'e2' → (rad, kol) som ett tuple."""
    if len(koordinat) != 2:
        return None

    kolumn_tecken = koordinat[0].lower()   # 'a' – 'h'
    rad_tecken    = koordinat[1]           # '1' – '8'

    if kolumn_tecken not in "abcdefgh":
        return None
    if rad_tecken not in "12345678":
        return None

    kol = ord(kolumn_tecken) - ord('a')   # 'a'=0, 'b'=1, ...
    rad = 8 - int(rad_tecken)             # '8'=0, '1'=7

    return (rad, kol)   # tuple


# -------------------------------------------------------
# FUNKTION: Hämta färgen på en pjäs ("V" eller "S")
# Returnerar None om fältet är tomt
# -------------------------------------------------------
def pjäs_färg(pjäskod: str) -> str | None:
    """Returnerar 'V' eller 'S', eller None om tomt."""
    if pjäskod == TOM:
        return None
    return pjäskod[0]   # Första tecknet är alltid färgen


# -------------------------------------------------------
# FUNKTION: Kontrollera om ett drag är giltigt (förenklat)
# Regler: kan inte flytta tom ruta, kan inte slå egna pjäser
# -------------------------------------------------------
def drag_giltigt(bräde: list[list[str]],
                 från_rc: tuple[int, int],
                 till_rc: tuple[int, int],
                 nuvarande_spelare: str) -> tuple[bool, str]:
    """
    Returnerar ett tuple (giltig: bool, meddelande: str).
    Kontrollerar grundläggande regler.
    """
    från_rad, från_kol = från_rc
    till_rad, till_kol = till_rc

    # Kontroll 1: Välj inte ett tomt fält
    pjäs = bräde[från_rad][från_kol]
    if pjäs == TOM:
        return (False, "Det finns ingen pjäs på det fältet!")

    # Kontroll 2: Rätt spelares tur
    if pjäs_färg(pjäs) != nuvarande_spelare:
        färgnamn = "Vita" if nuvarande_spelare == VIT else "Svarta"
        return (False, f"Det är {färgnamn}s tur!")

    # Kontroll 3: Kan inte flytta till eget fält
    målfält = bräde[till_rad][till_kol]
    if pjäs_färg(målfält) == nuvarande_spelare:
        return (False, "Du kan inte slå din egna pjäs!")

    return (True, "OK")


# -------------------------------------------------------
# FUNKTION: Utför ett drag på brädet
# -------------------------------------------------------
def utför_drag(bräde: list[list[str]],
               från_rc: tuple[int, int],
               till_rc: tuple[int, int]) -> str | None:
    """
    Flyttar pjäs och returnerar slagen pjäs (eller None).
    Uppdaterar brädet på plats.
    """
    fr, fk = från_rc
    tr, tk = till_rc

    slagen_pjäs = bräde[tr][tk] if bräde[tr][tk] != TOM else None
    bräde[tr][tk] = bräde[fr][fk]
    bräde[fr][fk] = TOM

    return slagen_pjäs


# -------------------------------------------------------
# FUNKTION: Byt spelare
# -------------------------------------------------------
def nästa_spelare(nuvarande: str) -> str:
    """Returnerar den andra spelaren."""
    return SVART if nuvarande == VIT else VIT


# -------------------------------------------------------
# FUNKTION: Kontrollera om kungen finns kvar
# -------------------------------------------------------
def kungen_finns(bräde: list[list[str]], färg: str) -> bool:
    """Söker igenom brädet och kontrollerar om kungen lever."""
    kung_kod = färg + "K"   # t.ex. "VK" eller "SK"
    for rad in bräde:       # rad är en lista
        if kung_kod in rad:
            return True
    return False


# -------------------------------------------------------
# FUNKTION: Visa slagna pjäser
# -------------------------------------------------------
def visa_slagna(slagna: list[str]) -> None:
    """Skriver ut alla slagna pjäser med symboler."""
    if not slagna:
        print("  (inga slagna pjäser)")
    else:
        symboler = [PJÄSER[p] for p in slagna]
        print("  Slagna: " + " ".join(symboler))


# -------------------------------------------------------
#  HUVUDPROGRAMMET  –  spelloop
# -------------------------------------------------------
def main() -> None:
    print("=" * 45)
    print("       ♙  SCHACK I PYTHON  ♟")
    print("=" * 45)
    print("Ange drag som: e2 e4  (från → till)")
    print("Skriv 'sluta' för att avsluta.\n")

    bräde          = skapa_bräde()
    nuvarande      = VIT          # Vit börjar alltid
    slagna_pjäser: list[str] = [] # Samla alla slagna pjäser i en lista
    drag_historia:  list[tuple[str, str]] = []  # Lista av tupler

    while True:
        skriv_bräde(bräde)

        # Visa slagna pjäser
        print("Slagna pjäser:")
        visa_slagna(slagna_pjäser)

        # Visa vems tur det är
        spelare_namn = "Vit ♔" if nuvarande == VIT else "Svart ♚"
        print(f"\n{spelare_namn}s tur.")

        # Läs inmatning
        inmatning = input("Ditt drag: ").strip().lower()

        if inmatning == "sluta":
            print("\nSpelet avslutat. Tack för spelet! ♟")
            break

        # Dela upp inmatning i två delar
        delar = inmatning.split()
        if len(delar) != 2:
            print("⚠  Fel format! Ange t.ex.: e2 e4\n")
            continue

        från_str, till_str = delar   # Packa upp (tuple-liknande)

        # Konvertera till index-tupler
        från_rc = koordinat_till_index(från_str)
        till_rc = koordinat_till_index(till_str)

        if från_rc is None or till_rc is None:
            print("⚠  Ogiltiga koordinater! Använd a–h och 1–8.\n")
            continue

        # Validera draget
        giltigt, meddelande = drag_giltigt(bräde, från_rc, till_rc, nuvarande)
        if not giltigt:
            print(f"⚠  {meddelande}\n")
            continue

        # Utför draget
        slagen = utför_drag(bräde, från_rc, till_rc)
        if slagen:
            slagna_pjäser.append(slagen)
            print(f"  ✔ {PJÄSER[slagen]} slagen!")

        # Spara drag i historiken (tuple)
        drag_historia.append((från_str, till_str))

        # Kontrollera om motståndaren förlorat sin kung
        nästa = nästa_spelare(nuvarande)
        if not kungen_finns(bräde, nästa):
            skriv_bräde(bräde)
            vinnare = "Vit ♔" if nuvarande == VIT else "Svart ♚"
            print(f"\n🎉  SCHACKMATT!  {vinnare} vinner!\n")
            break

        # Byt spelare
        nuvarande = nästa


# --- Starta spelet ---
if __name__ == "__main__":
    main()