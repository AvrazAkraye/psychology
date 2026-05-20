# مكتبة شارين — Psychology

Small static library of seven Arabic psychology books focused on developmental psychology, childhood, and adolescence.

**Live site:** https://avrazakraye.github.io/psychology/

## What's here

- `index.html` — RTL Arabic landing page with a grid of all seven books.
- `books/` — three local PDFs (~42 MB total). Click → download / open in a new tab.
- `covers/` — book cover images. Three extracted from PDF first pages, four generated as title cards for the noor-book.com entries.
- `qr.png` — QR code that encodes the site URL.
- `tools/build.py` — regenerates the four title-card covers and the QR code.

## Regenerating assets

```bash
python3 -m venv .venv
.venv/bin/pip install 'qrcode[pil]' pillow arabic-reshaper python-bidi
.venv/bin/python tools/build.py
```

Recreates `covers/al-murahaqa-wal-inaya.jpg`, `covers/zahran-tufula-murahaqa.jpg`, `covers/usra-hal-mushkilat.jpg`, `covers/sikolojia-tifl-murahiq.jpg`, and `qr.png`. The three PDF-derived covers in `covers/` are produced separately with `pdftoppm`:

```bash
for slug in ilm-nafs-numuw ilm-nafs-numuw-v3 ilm-nafs-numuw-maryam-saleem; do
  pdftoppm -jpeg -r 120 -f 1 -l 1 "books/$slug.pdf" "covers/$slug"
  mv "covers/${slug}-001.jpg" "covers/${slug}.jpg"
done
```

## Adding a new book

1. Drop the PDF into `books/<slug>.pdf`.
2. Run the `pdftoppm` snippet above (or supply a cover JPG manually).
3. Add a new `<article class="card">` block in `index.html`, copying one of the existing local-book cards.

For an external (noor-book) entry, copy one of the `online` cards instead and replace the URL + cover.
