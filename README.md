# Wywóz odpadów – gmina Ślesin 2026 (kod QR → kalendarz)

Statyczna strona (bez serwera i bez budowania). Użytkownik wybiera miejscowość i rodzaje odpadów,
a strona pokazuje kod QR prowadzący do pliku `.ics` z terminami wywozu.

## Publikacja w GitHub Pages
1. Utwórz repozytorium i wrzuć do niego całą zawartość tego katalogu (razem z `ics/`, `vendor/`, `data.js`, `.nojekyll`).
2. *Settings → Pages → Build and deployment → Deploy from a branch* → gałąź `main`, katalog `/ (root)`.
3. Po chwili strona będzie pod adresem `https://TWOJA-NAZWA.github.io/NAZWA-REPO/`.

Kody QR są liczone w przeglądarce z adresu, pod którym strona jest otwarta, więc nie trzeba nigdzie wpisywać domeny.
Otwarcie `index.html` z dysku pokaże stronę, ale kod QR będzie wtedy wskazywał na plik lokalny.

## Struktura
- `index.html` – cała strona
- `data.js` – miejscowości i daty (generowany)
- `ics/<zbiór>-<maska>.ics` – pliki kalendarza; zbiory: `pon`, `wto`, `sro`, `czw`, `pia`;
  maska to suma bitów: 1 niesegregowane, 2 popiół i żużel, 4 papier i plastik, 8 szkło, 16 bio (31 = wszystko)
- `generate.py` – przepisane z PDF-a daty, walidacja dni tygodnia i generator `ics/` oraz `data.js`
- `vendor/qrcode.js` – biblioteka qrcode-generator (MIT)

## Poprawianie terminów
Zmień ciągi liczb w `RAW` (lub przesunięcia świąteczne w `KNOWN_SHIFTS`) w `generate.py`
i uruchom `python3 generate.py`. Skrypt zgłosi daty, które nie wypadają w dniu tygodnia danego zbioru.
