import tkinter as tk
from tkinter import font as tkfont

RUTA_PX   = 80                        
BRÄD_PX   = RUTA_PX * 8             
PANEL_H   = 100                       
FÖNSTER_H = BRÄD_PX + PANEL_H

LJUS_RUTA    = "#F0D9B5"
MÖRK_RUTA    = "#B58863"
MARKERAD     = "#7FC97F"
MÖJLIG_FG    = "#5BA3D9"
SLÅR_FG      = "#D95B5B"
BAKGRUND     = "#1E1E28"
TEXT_LJUS    = "#F0F0F0"
TEXT_MÖ      = "#AAAAAA"
PANEL_BG     = "#14141E"
ACCENT       = "#FFC83D"

# Spelare
VIT   = "V"
SVART = "S"
TOM   = ""

SYMBOLER: dict[str, str] = {
    "VK":  "♚",  # Vit kung
    "VD":  "♛",  # Vit drottning
    "VT":  "♜",  # Vit torn
    "VL":  "♝",  # Vit löpare
    "VH":  "♞",  # Vit häst
    "VB":  "♟",  # Vit bonde
    "SK":  "♚",  # Svart kung
    "SD":  "♛",  # Svart drottning
    "ST":  "♜",  # Svart torn
    "SL":  "♝",  # Svart löpare
    "SH":  "♞",  # Svart häst
    "SB":  "♟",  # Svart bonde
}

PJÄSNAMN: dict[str, str] = {
    "K": "Kung", "D": "Drottning", "T": "Torn",
    "L": "Löpare", "H": "Häst", "B": "Bonde",
}


# Cool grejer
def pjäs_färg(kod: str) -> str | None:
    return kod[0] if kod else None

def pjäs_typ(kod: str) -> str | None:
    return kod[1] if kod else None

def inom_brädet(r: int, k: int) -> bool:
    return 0 <= r < 8 and 0 <= k < 8

def skapa_bräde() -> list[list[str]]:
    s = ["ST","SH","SL","SD","SK","SL","SH","ST"]
    b = ["SB"] * 8
    t = [TOM]  * 8
    v = ["VB"] * 8
    h = ["VT","VH","VL","VD","VK","VL","VH","VT"]
    return [s[:], b[:], t[:], t[:], t[:], t[:], v[:], h[:]]

def möjliga_drag(bräde: list[list[str]], rad: int, kol: int) -> list[tuple[int,int]]:
    kod = bräde[rad][kol]
    if not kod: return []
    färg = pjäs_färg(kod)
    typ  = pjäs_typ(kod)
    drag: list[tuple[int,int]] = []

    def lägg(r: int, k: int) -> bool:
        if not inom_brädet(r, k): return False
        mål = bräde[r][k]
        if pjäs_färg(mål) == färg: return False
        drag.append((r, k))
        return mål == TOM

    def glidande(dirs: list[tuple[int,int]]) -> None:
        for dr, dk in dirs:
            r, k = rad+dr, kol+dk
            while inom_brädet(r, k):
                if not lägg(r, k): break
                r += dr; k += dk

    if typ == "B":
        rikt = -1 if färg == VIT else 1
        start = 6 if färg == VIT else 1
        nr = rad + rikt
        if inom_brädet(nr, kol) and bräde[nr][kol] == TOM:
            drag.append((nr, kol))
            if rad == start and bräde[nr+rikt][kol] == TOM:
                drag.append((nr+rikt, kol))
        for dk in [-1, 1]:
            nr2, nk2 = rad+rikt, kol+dk
            if inom_brädet(nr2, nk2) and bräde[nr2][nk2] and pjäs_färg(bräde[nr2][nk2]) != färg:
                drag.append((nr2, nk2))
    elif typ == "H":
        for dr,dk in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            lägg(rad+dr, kol+dk)
    elif typ == "L":
        glidande([(-1,-1),(-1,1),(1,-1),(1,1)])
    elif typ == "T":
        glidande([(-1,0),(1,0),(0,-1),(0,1)])
    elif typ == "D":
        glidande([(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])
    elif typ == "K":
        for dr in [-1,0,1]:
            for dk in [-1,0,1]:
                if dr or dk: lägg(rad+dr, kol+dk)
    return drag

def flytta_pjäs(bräde: list[list[str]],
                från_rc: tuple[int,int],
                till_rc: tuple[int,int]) -> str:
    fr,fk = från_rc; tr,tk = till_rc
    slagen = bräde[tr][tk]
    bräde[tr][tk] = bräde[fr][fk]
    bräde[fr][fk] = TOM
    return slagen

def kungen_lever(bräde: list[list[str]], färg: str) -> bool:
    kung = färg + "K"
    return any(kung in rad for rad in bräde)


# GUI
class Schackspel:
    """
    Håller hela spelets tillstånd och GUI.
    Canvas-element uppdateras på plats – fönstret återskapas ALDRIG.
    """

    def __init__(self, rot: tk.Tk):
        self.rot = rot
        rot.title("Schack – tkinter")
        rot.configure(bg=BAKGRUND)

        rot.state("zoomed")           
        rot.update()                  

        skärm_b = rot.winfo_width()
        skärm_h = rot.winfo_height()
        tillgänglig_h = skärm_h - PANEL_H

        
        global RUTA_PX, BRÄD_PX
        RUTA_PX = min(skärm_b, tillgänglig_h) // 8
        BRÄD_PX = RUTA_PX * 8

        # Status
        self.bräde:     list[list[str]]       = skapa_bräde()
        self.nuvarande: str                   = VIT
        self.vald_rc:   tuple[int,int] | None = None
        self.möjliga:   list[tuple[int,int]]  = []
        self.slagna:    list[str]             = []
        self.spel_slut: bool                  = False

        # Font och storlekar
        pjäs_storlek   = max(20, RUTA_PX // 2)
        ui_storlek     = max(12, RUTA_PX // 7)
        liten_storlek  = max(10, RUTA_PX // 8)
        etikett_storlek = max(8, RUTA_PX // 10)

        self.font_pjäs    = tkfont.Font(family="Segoe UI Emoji", size=pjäs_storlek)
        self.font_ui      = tkfont.Font(family="Arial", size=ui_storlek, weight="bold")
        self.font_liten   = tkfont.Font(family="Arial", size=liten_storlek)
        self.font_etikett = tkfont.Font(family="Arial", size=etikett_storlek)

        
        sido_marginal = (skärm_b - BRÄD_PX) // 2

        yttre_ram = tk.Frame(rot, bg=BAKGRUND)
        yttre_ram.pack(fill="both", expand=True)

        
        tk.Frame(yttre_ram, bg=BAKGRUND, width=sido_marginal).pack(side="left", fill="y")

        
        self.canvas = tk.Canvas(
            yttre_ram,
            width=BRÄD_PX, height=BRÄD_PX,
            bg=BAKGRUND, highlightthickness=0
        )
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self.vid_klick)

        
        self.panel = tk.Frame(rot, bg=PANEL_BG, height=PANEL_H)
        self.panel.pack(fill="x", side="bottom")
        self.panel.pack_propagate(False)

        self.lbl_tur = tk.Label(
            self.panel, text="", bg=PANEL_BG,
            fg=ACCENT, font=self.font_ui
        )
        self.lbl_tur.pack(pady=(10, 2))

        self.lbl_info = tk.Label(
            self.panel, text="", bg=PANEL_BG,
            fg=TEXT_LJUS, font=self.font_liten
        )
        self.lbl_info.pack()

        self.lbl_slagna = tk.Label(
            self.panel, text="", bg=PANEL_BG,
            fg=TEXT_MÖ, font=self.font_liten
        )
        self.lbl_slagna.pack()

        
        knapp_font = tkfont.Font(family="Arial", size=max(14, RUTA_PX // 5), weight="bold")
        self.knapp_ny = tk.Button(
            self.canvas,
            text="♟  NY MATCH  ♟",
            command=self.ny_match,
            bg=ACCENT, fg="#1A1A1A",
            font=knapp_font,
            relief="flat",
            padx=30, pady=14,
            cursor="hand2",
            activebackground="#FFD966",
            activeforeground="#1A1A1A",
            bd=0
        )

        
        self._rita_rutor()          
        self._uppdatera_pjäser()    
        self._uppdatera_panel()


    def _rita_rutor(self):
        """
        Ritar rutorna och koordinatetiketterna EN enda gång.
        Taggade 'rutor' – ritas aldrig om.
        """
        for rad in range(8):
            for kol in range(8):
                x1 = kol * RUTA_PX
                y1 = rad * RUTA_PX
                x2 = x1 + RUTA_PX
                y2 = y1 + RUTA_PX
                färg = LJUS_RUTA if (rad + kol) % 2 == 0 else MÖRK_RUTA
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=färg, outline="", tags="rutor"
                )

        
        for i in range(8):
            bokstav = chr(ord('a') + i)
            nummer  = str(8 - i)
            cx = i * RUTA_PX + 6
            cy = 7 * RUTA_PX + RUTA_PX - 14
            self.canvas.create_text(cx, cy, text=bokstav,
                                    font=self.font_etikett,
                                    fill="#888", tags="rutor")
            self.canvas.create_text(6, i * RUTA_PX + 10, text=nummer,
                                    font=self.font_etikett,
                                    fill="#888", tags="rutor")

    def _uppdatera_pjäser(self):
        """
        Tar bort BARA pjäs- och markeringslagret och ritar om det.
        Rutorna (bakgrunden) rörs INTE – det är den riktiga uppdateringen.
        """
        
        self.canvas.delete("markering")
        self.canvas.delete("pjäser")

        for rad in range(8):
            for kol in range(8):
                x1 = kol * RUTA_PX
                y1 = rad * RUTA_PX
                cx = x1 + RUTA_PX // 2
                cy = y1 + RUTA_PX // 2

                if self.vald_rc == (rad, kol):
                    self.canvas.create_rectangle(
                        x1, y1, x1+RUTA_PX, y1+RUTA_PX,
                        fill=MARKERAD, outline="", tags="markering"
                    )

                # Markering: möjliga drag
                elif (rad, kol) in self.möjliga:
                    kod = self.bräde[rad][kol]
                    if kod:
                        # Röd overlay = kan slå
                        self.canvas.create_rectangle(
                            x1, y1, x1+RUTA_PX, y1+RUTA_PX,
                            fill=SLÅR_FG, outline="", tags="markering"
                        )
                    else:
                        # Blå cirkel = möjlig tom ruta
                        self.canvas.create_oval(
                            cx-14, cy-14, cx+14, cy+14,
                            fill=MÖJLIG_FG, outline="", tags="markering"
                        )

                # Färg
                kod = self.bräde[rad][kol]
                if kod:
                    är_vit = pjäs_färg(kod) == VIT
                    pjäs_färg_hex  = "#FFFFFF" if är_vit else "#000000"
                    kontur_färg    = "#000000" if är_vit else "#FFFFFF"

                    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),
                                   (-2,-2),(2,-2),(-2,2),(2,2)]:
                        self.canvas.create_text(
                            cx+dx, cy+dy, text=SYMBOLER[kod],
                            font=self.font_pjäs, fill=kontur_färg,
                            tags="pjäser"
                        )

                    self.canvas.create_text(
                        cx, cy, text=SYMBOLER[kod],
                        font=self.font_pjäs, fill=pjäs_färg_hex,
                        tags="pjäser"
                    )

    def _uppdatera_panel(self):
        """Uppdaterar etiketter i infopanelen."""
        if self.spel_slut:
            return

        spelare = "Vit ♔" if self.nuvarande == VIT else "Svart ♔"
        self.lbl_tur.config(text=f"TUR: {spelare}")

        if self.vald_rc:
            r, k = self.vald_rc
            kod  = self.bräde[r][k]
            if kod:
                namn = PJÄSNAMN.get(pjäs_typ(kod), "")
                sym  = SYMBOLER[kod]
                self.lbl_info.config(
                    text=f"Vald: {sym} {namn}  →  Klicka på en markerad ruta",
                    fg="#50E890"
                )
        else:
            self.lbl_info.config(
                text="Klicka på en av dina pjäser för att välja",
                fg=TEXT_LJUS
            )

        if self.slagna:
            sym_lista = " ".join(SYMBOLER[p] for p in self.slagna)
            self.lbl_slagna.config(text=f"Slagna: {sym_lista}")


    def vid_klick(self, händelse: tk.Event):
        """
        Hanterar musklick på canvas.
        Klick 1 → välj pjäs  |  Klick 2 → flytta
        """
        if self.spel_slut:
            return

        kol = händelse.x // RUTA_PX
        rad = händelse.y // RUTA_PX

        if not inom_brädet(rad, kol):
            return

        klickad_kod = self.bräde[rad][kol]

        if self.vald_rc is None:
            if klickad_kod and pjäs_färg(klickad_kod) == self.nuvarande:
                self.vald_rc  = (rad, kol)
                self.möjliga  = möjliga_drag(self.bräde, rad, kol)
                self.lbl_info.config(
                    text=f"Vald! Klicka nu på en markerad ruta.",
                    fg="#50E890"
                )
            else:
                self.lbl_info.config(
                    text="⚠ Välj en av dina egna pjäser!",
                    fg="#FF6060"
                )

        else:
            # Byt till annan egen pjäs
            if klickad_kod and pjäs_färg(klickad_kod) == self.nuvarande:
                self.vald_rc = (rad, kol)
                self.möjliga = möjliga_drag(self.bräde, rad, kol)

            elif (rad, kol) in self.möjliga:
                slagen = flytta_pjäs(self.bräde, self.vald_rc, (rad, kol))
                if slagen:
                    self.slagna.append(slagen)

                # Schackmatt checker
                motståndare = SVART if self.nuvarande == VIT else VIT
                if not kungen_lever(self.bräde, motståndare):
                    self._uppdatera_pjäser()
                    self._visa_slutskärm(motståndare)
                    return

                self.nuvarande = motståndare
                self.vald_rc   = None
                self.möjliga   = []

            else:
                self.lbl_info.config(
                    text="⚠ Ogiltigt drag! Klicka på en markerad ruta.",
                    fg="#FF6060"
                )
                self.vald_rc = None
                self.möjliga = []

        self._uppdatera_pjäser()
        self._uppdatera_panel()


    def _visa_slutskärm(self, förlorade_färg: str):
        """Ritar ett overlay direkt på canvas."""
        self.spel_slut = True
        vinnare = "VIT ♔" if förlorade_färg == SVART else "SVART ♔"

        self.canvas.create_rectangle(
            0, 0, BRÄD_PX, BRÄD_PX,
            fill="#0A0A14", stipple="gray50", tags="overlay"
        )
        self.canvas.create_text(
            BRÄD_PX//2, BRÄD_PX//2 - 50,
            text="♔ SCHACKMATT ♔",
            font=tkfont.Font(family="Arial", size=32, weight="bold"),
            fill=ACCENT, tags="overlay"
        )
        self.canvas.create_text(
            BRÄD_PX//2, BRÄD_PX//2 + 10,
            text=f"{vinnare} vinner!",
            font=tkfont.Font(family="Arial", size=20),
            fill=TEXT_LJUS, tags="overlay"
        )

        self.lbl_tur.config(text=f"🎉 {vinnare} vinner!", fg=ACCENT)
        self.lbl_info.config(text="Klicka på knappen nedan för att spela igen", fg=TEXT_MÖ)

        self.canvas.create_window(
            BRÄD_PX // 2, BRÄD_PX // 2 + 80,
            window=self.knapp_ny,
            tags="overlay"
        )

    def ny_match(self):
        """Återställer spelet utan att stänga fönstret."""
        self.bräde     = skapa_bräde()
        self.nuvarande = VIT
        self.vald_rc   = None
        self.möjliga   = []
        self.slagna    = []
        self.spel_slut = False

        self.canvas.delete("overlay")  

        self._uppdatera_pjäser()
        self._uppdatera_panel()
        self.lbl_slagna.config(text="")



def main():
    rot = tk.Tk()
    Schackspel(rot)
    rot.mainloop()


if __name__ == "__main__":
    main()