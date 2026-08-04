#!/bin/sh
# Fetch the open-licensed comparison faces from google/fonts.
# System faces (Verdana, Georgia, Arial, Times, SF Pro, Helvetica Neue, Charter)
# ship with macOS and are found at their standard paths. Bear Sans is bundled
# inside Bear.app; if you own Bear, the driver will pick it up automatically.
# Non-open fonts are never redistributed by this repository.
set -e
cd "$(dirname "$0")"
# Pinned to a specific google/fonts commit so fetches are reproducible. This is
# the commit main pointed at when the v3.1 official results were measured, so a
# fetch today returns the same binaries the published numbers came from. Moving
# the pin invalidates comparability with results/v31 and requires a re-run.
G="https://github.com/google/fonts/raw/2796410152d4f9524b68ed46e69c1b60f8e0f7c3/ofl"
# -f so an HTTP error is a non-zero exit rather than an error page written to a
# .ttf; without it set -e never fires and the driver reads a corrupt face.
curl -fsL -o figtree.ttf        "$G/figtree/Figtree%5Bwght%5D.ttf"
curl -fsL -o atkinson.ttf       "$G/atkinsonhyperlegible/AtkinsonHyperlegible-Regular.ttf"
curl -fsL -o atkinsonnext.ttf   "$G/atkinsonhyperlegiblenext/AtkinsonHyperlegibleNext%5Bwght%5D.ttf"
curl -fsL -o roboto.ttf         "$G/roboto/Roboto%5Bwdth,wght%5D.ttf"
curl -fsL -o instrumentserif.ttf "$G/instrumentserif/InstrumentSerif-Regular.ttf"
curl -fsL -o inter.ttf          "$G/inter/Inter%5Bopsz,wght%5D.ttf"
curl -fsL -o fraunces.ttf       "$G/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf"  # Numen Title chassis
curl -fsL -o lexend.ttf         "$G/lexend/Lexend%5Bwght%5D.ttf"
curl -fsL -o andika.ttf         "$G/andika/Andika-Regular.ttf"
curl -fsL -o notosans.ttf       "$G/notosans/NotoSans%5Bwdth,wght%5D.ttf"
curl -fsL -o sourcesans3.ttf    "$G/sourcesans3/SourceSans3%5Bwght%5D.ttf"
curl -fsL -o ibmplexsans.ttf    "$G/ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf"
curl -fsL -o publicsans.ttf     "$G/publicsans/PublicSans%5Bwght%5D.ttf"

# Verify against the binaries the published v3.1 results were measured from.
# The pin above fixes the URL; this fixes the bytes. If upstream ever rewrites
# history at that sha, or a proxy or mirror substitutes a file, the panel is no
# longer the one behind results/v31 and the run must not silently proceed.
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 -c SHA256SUMS >/dev/null || {
    echo "checksum mismatch: fetched faces are NOT the ones behind results/v31" >&2
    echo "re-run 'shasum -a 256 -c SHA256SUMS' to see which." >&2
    exit 1
  }
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c SHA256SUMS >/dev/null || {
    echo "checksum mismatch: fetched faces are NOT the ones behind results/v31" >&2
    echo "re-run 'sha256sum -c SHA256SUMS' to see which." >&2
    exit 1
  }
else
  echo "warning: no shasum/sha256sum found, comparison faces unverified" >&2
fi

echo "fetched and verified. Kept's own fonts are in ../kept-type/ (or kept.do/type)"
