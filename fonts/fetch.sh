#!/bin/sh
# Fetch the open-licensed comparison faces from google/fonts.
# System faces (Verdana, Georgia, Arial, Times, SF Pro, Helvetica Neue, Charter)
# ship with macOS and are found at their standard paths. Bear Sans is bundled
# inside Bear.app; if you own Bear, the driver will pick it up automatically.
# Non-open fonts are never redistributed by this repository.
set -e
cd "$(dirname "$0")"
G="https://github.com/google/fonts/raw/main/ofl"
curl -sL -o figtree.ttf        "$G/figtree/Figtree%5Bwght%5D.ttf"
curl -sL -o atkinson.ttf       "$G/atkinsonhyperlegible/AtkinsonHyperlegible-Regular.ttf"
curl -sL -o atkinsonnext.ttf   "$G/atkinsonhyperlegiblenext/AtkinsonHyperlegibleNext%5Bwght%5D.ttf"
curl -sL -o roboto.ttf         "$G/roboto/Roboto%5Bwdth,wght%5D.ttf"
curl -sL -o instrumentserif.ttf "$G/instrumentserif/InstrumentSerif-Regular.ttf"
curl -sL -o inter.ttf          "$G/inter/Inter%5Bopsz,wght%5D.ttf"
curl -sL -o fraunces.ttf       "$G/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf"
echo "fetched. Kept's own fonts: download kept-type.zip from kept.do/type"
