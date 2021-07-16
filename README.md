Checkers in Python (Tkinter)

======================

Jedná sa o hru dáma, presnejšie anglická/americká verzia
(draughts/checkers) bez povinného vybíjania figúriek.

Naprogramované v jazyku Python. Zmenením parametra "ai" objektu "game"
sa dá hrať proti hráčovi/počítaču.


Modul: tkinter

-   Pre grafické objekty a okná

Modul: tkinter.filedialog

-   Čítanie zo/zapisovanie do súborov

Modul: tkinter.messagebox

-   Vyskakovacie okná s upozorneniami, informáciami a otázkami

Modul: time.time

-   Pre získanie aktuálneho času

Modul: random.choice

-   Náhodný výber z možností.

Trieda: Piece

-   Trieda figúrky, obsahu informácie o pozícii, strane a grafike

-   \_\_init\_\_(side, pos, size, king=False)
    -   Uloží základné informácie a graficky zobrazí figúrku

-   draw(outline, fill='')
    -   Vytvorí kruh s danými vlastnosťami na svojej pozícii

-   mark()
    -   Graficky označí vybranú figúrku

-   unmark()
    -   Odznačí vybranú figúrku (grafický objekt sa odstráni)

-   delete()
    -   Odstráni všetku grafiku

-   move(x, y)
    -   Presunie figúrku na danú pozíciu

-   check\_king()
    -   Skontroluje, či sa figúrka nestala kráľom. Ak áno, vytvorí
        korunu

-   coord()
    -   Vráti súradnice potrebné na vykreslenie grafických objektov

Trieda: Board

-   Samotná hra, hlavná funkčnosť programu

-   \_\_init\_\_(size=500, ai=False)
    -   Vytvorí okná, pozadie a figúrky. Parameter 'ai' určí, či sa hrá
        proti počítaču

-   menu\_bar()
    -   Vytvorí lištu s ukladaním, načítaním, reštartovaním hry a
        vypnutí programu

-   choose\_side()
    -   Vytvorí okno pre voľbu strany hráča, po zvolení vytvorí hru

-   draw\_board()
    -   Vytvorí sa 8x8 hracia doska

-   place\_pieces()
    -   Vytvorí objekty figúrok a spustí časovač

-   timer()
    -   Udržiava počet sekúnd po spustení hry

-   click(event)
    -   Stará sa o označovanie, odznačovanie a robenie ťahov kliknutím
        ľavým tlačidlom myši

-   ai\_moves()
    -   Nájde všetky možné ťahy počítača, zhodnotí ich a vyberie
        najlepší

-   valid(selected, field)
    -   Zistí, či je pohyb zo 'selected' na 'field' validný

-   valid\_moves()
    -   Vráti slovník všetkých možných ťahov figúrky

-   field\_index(x, y)
    -   Z daných súradníc na ploche vráti figúrku / indexy polia dosky

-   threatened(piece)
    -   Vráti pole súradníc figúrok, ktoré v okolí +-1 ohrozujú 'piece'

-   check\_win()
    -   Zistí, či hra neskončila (neexistujú figúrky danej strany)
