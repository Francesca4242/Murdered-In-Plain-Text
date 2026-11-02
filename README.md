# Murdered In Plain Text

A Twine/SugarCube murder mystery for digital preservationists. Cluedo meets
Midsomer Murders, in an Agatha Christie and silent-movie setting.

**Play it:** https://Francesca4242.github.io/Murdered-In-Plain-Text/

Sir Regex Metadata IV is dead in his study, with an uncapped pen, a bare desk
and a confession set in a typeface he spent his life outlawing. You have three
days, twenty-one puzzles and twenty-two exhibits to work out who corrupted his final
file &mdash; and, harder, to be able to prove it afterwards.

Originally developed by the founders of the Bits and Bots study group,
following [File Format Fling](https://francesca4242.github.io/File_Format_Fling/).
This repository is a fork of [susanne404/murdered-in-plain-text](https://github.com/susanne404/murdered-in-plain-text)
with reworked visuals, harder puzzles and a tightened plot.

## The puzzles

Every location is a puzzle, and every puzzle teaches something real. All of
them are answered from the evidence on screen, two attempts each.

| Day | Location | What it asks of you |
| --- | --- | --- |
| 1 | The Library | Identify five formats from their magic bytes, including two RIFF containers that share their first four bytes |
| 1 | The Skull-ery | Run a fixity check, and tell a failed digest apart from one you simply cannot compare |
| 1 | The Graphics Room | Mark a five-step migration chain lossless or lossy, and find where faithfulness was lost |
| 1 | The Study | Authenticate a disputed document, separating real evidence of forgery from mere untidiness |
| 2 | The Nibble & Byte | Read a hex dump to the form type at offset 8, and say what the reading does and does not prove |
| 2 | The Nibble & Byte | Read a little-endian RIFF size, tell `VP8 ` from `VP8L`, and catch a certificate that predates its own format |
| 2 | The .PUB | Find every fault in a metadata record &mdash; well-formedness and validity are not the same thing |
| 2 | St. Mary of the Lossless | Decide what an SVG-to-PNG migration actually loses |
| 2 | St. Mary of the Lossless | Read web-archive capture timestamps, and spot a replay stitched together from two different days |
| 2 | The Post Office | Put the OAIS ingest-to-dissemination sequence back in order |
| 2 | The Post Office | Record dates as ISO 8601 and [EDTF](https://www.loc.gov/standards/datetime/): approximate, uncertain, unspecified, one-of-a-set |
| 2 | Loopwell's GIF Shop | Choose the significant properties of a 1996 animation, and the strategy that keeps them |
| 2 | The Village Common | Score three organisations against the [DPC Rapid Assessment Model](https://www.dpconline.org/digipres/implement-digipres/dpc-ram) |
| 3 | The Server Room | Assess a storage arrangement honestly against the 3-2-1 rule |
| 3 | The Server Room | Rebuild a dead RAID disk by hand with XOR parity, and say what RAID would never have saved you from |
| 3 | The Dark Archive | Read a payload, and judge what a self-issued signature is worth |
| 3 | The Dark Archive | Diagnose mojibake, and tell a reversible misreading from an irreversible "clean-up" |
| 3 | The Library (tidied) | Find a deleted FAT directory entry (`E5`), name the file, and decode its packed creation time |
| 3 | The Skull-ery (tidied) | Match carriers to their failure modes, and rescue a sticky-shed tape from a 230&deg;C oven |
| 3 | The Study (tidied) | Identify a crime-scene photo whose extension lies (it is a real JPEG named `.png` in this repo), and handle it as found |
| 3 | The Pixelated Passages | Describe the butler's log in PREMIS: objects, events, agents, rights, and who was the *authorizer* |

The [PRONOM registry](https://www.nationalarchives.gov.uk/PRONOM/), the DPC
RAM, EDTF, PREMIS and Memento are real, and the game links out to them. Every
exhibit you recover also writes a page in the **Preservationist's Notebook**:
what the puzzle was really teaching, and where to read more.

## Structure

Three days, gated by an evidence ledger rather than by goodwill:

- **Day 1 &mdash; the manor.** Four rooms. Whatever you record, you keep.
- **Day 2 &mdash; the village.** Six suspects, six genuine motives, one decisive identification.
- **Day 3 &mdash; what was under the pen.** Three new wings open; the four rooms
  from the first night have been tidied by the butler. Rooms you searched
  still read from your notes. But tidied is not erased: three of them still
  give up something to a preservationist who knows where to look.

The accusation needs a culprit, a weapon **and** a motive, and it only stands
if you hold all three keystone exhibits. Naming the right person without the
evidence to prove it is its own ending.

## Working on the game

The story source is `Murdered In Plain Text.twee`. `index.html` is built from
it and is what GitHub Pages serves &mdash; do not edit it by hand.

```sh
python3 build/build.py --check     # validate: broken links, dead ends, duplicates
python3 build/build.py             # rebuild index.html from the .twee
python3 -m http.server 8000        # then open http://localhost:8000
```

`build/sugarcube-2.37.3-shell.html` is the SugarCube runtime, kept as a shell
with a `{{STORYDATA}}` placeholder, so the build splices in fresh story data
without touching the engine. The `.twee` can also be imported straight into the
Twine editor if you prefer to work there; export it back over the `.twee` file
and rebuild.

Run `--check` before committing. It catches the failure modes this kind of
project actually has: links to passages that do not exist, passages nothing
links to, and duplicate names.

Earlier drafts are kept in `archive/versions/` for the record.

## Credits

Written by the Bits and Bots study group. Images and characters by the original
authors. Licensed under the terms in [LICENSE](LICENSE).
