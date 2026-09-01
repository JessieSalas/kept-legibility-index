# Kept Type · v2

Three typefaces, all SIL Open Font License 1.1. TTF for apps and OS install,
WOFF2 for the web.

- **Kept Sans** (7 weights, 300-900, each with a true italic): the interface
  voice. Figtree bones, five measured legibility corrections. Figtree has no
  Thin or ExtraLight; we do not invent them.
- **Numen Title** (6 weights, Light-ExtraBold, each with a true italic): the
  headline serif. Fraunces bones, axes pinned by measurement.
- **Legibility Sans** (6 weights, Light-ExtraBold, each with a true italic):
  built only to be read. Based on Atkinson Hyperlegible Next; the only face
  in our index legible at 8 px. No ligatures, on purpose. Atkinson ExtraLight
  is dropped on italic too — we do not invent a weight the roman does not ship.

Every claim is measured by the Kept Legibility Index. The protocol ships in
this zip (PROTOCOL.md); the harness, corpus, raw results, and claims ledger:
https://github.com/JessieSalas/kept-legibility-index

The story: https://kept.do/type · https://kept.do/legibility-sans
The full table: https://kept.do/most-legible-font

U+2713 and U+2717 are native in Kept Sans and Numen Title. Kept Sans keeps
its stylistic sets from Figtree; Numen Title keeps Fraunces' own ampersand.

FontBakery googlefonts: Kept Sans and Legibility Sans have no FAILs. Numen
Title's only FAIL is the known Dutch J-acute shaping (`shape_languages`)
on every face. Regular italic files use the RIBBI names `*-Italic.ttf`.
