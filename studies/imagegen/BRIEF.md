# Task: generate reference images of a capital O for a typeface

Use your image generation tool. Save every image into this directory as a PNG.

## What to draw

A single capital letter **O** from a geometric sans-serif typeface, drawn so that a text
recogniser will NOT confuse it with a zero, and will NOT confuse it with a capital D.

Measured background: in a machine-vision legibility benchmark over 24 typefaces, `O`
misread as `0` is the largest single error class. Making the O squarer reduces that but
creates a new `O` misread as `D`. The O sits between two attractors.

## Required image properties (these matter more than beauty)

- Pure black glyph on a pure white background. No grey, no gradient, no texture,
  no shadow, no antialiasing halo, no background pattern.
- One single letter O filling most of the frame, centred, upright.
- Square canvas, at least 1024x1024.
- No other letters, no caption, no label, no border, no frame, no watermark,
  no drop shadow, no 3D, no perspective, no reflection.
- Flat vector-like appearance, as if it were a printed letterform specimen.
- Even stroke weight, roughly 1/8 of the letter's width.

## Produce 4 distinct versions

1. `O-asym-stress.png` — asymmetric stress: the thin points of the ring sit on a
   diagonal axis rather than at top and bottom, like a humanist serif O but sans.
2. `O-offset-counter.png` — the inner counter is displaced slightly up and left of
   centre, so the ring is thicker at lower-right than upper-left.
3. `O-flat-top.png` — the outer contour is flattened along the top and bottom but stays
   round at the sides, giving a distinctly non-circular silhouette.
4. `O-tapered.png` — the ring tapers: noticeably thicker on the left and right flanks,
   thinner top and bottom, exaggerated well beyond a normal geometric sans.

Write the four PNGs into this directory. Then write a short file `NOTES.md` describing
what you actually produced and any way the output differs from the request.
