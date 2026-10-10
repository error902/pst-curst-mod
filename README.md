# PST Curst Mod

WeiDU mod scaffold for **Planescape: Torment** (classic) and **Planescape: Torment: Enhanced Edition**, aimed at Curst content.

Community docs and tooling live primarily at [The Gibberlings Three](https://www.gibberlings3.net/).

## Status

**v0.2.0** — proof of concept: **Shimmer**, a silent ghostly apparition in the Mortuary starting room (`AR0202`, Southwest Preparation Room). Talk to her for a single descriptive line; she does not answer.

## Repository layout

```
pst_curst/                 # Extract this folder into the game directory
  pst_curst.tp2            # Installer script
  pst_curst.ini            # Project Infinity metadata
  components/              # Per-component .tph logic
  languages/english/       # TRA strings (UTF-8)
  copy/                    # Finished IE resources to COPY into override
  dialog/                  # WeiDU .d sources
  scripts/                 # .baf script sources
  readme/                  # In-game / shipped readme
```

## Tools (from the G3 ecosystem)

| Tool | Role |
|------|------|
| [WeiDU](https://github.com/WeiDUorg/WeiDU/releases) | Build and install mods |
| [Near Infinity](https://github.com/Argent77/NearInfinity/releases) | Browse/edit game files (`chitin.key`) |
| [IESDP](https://gibberlings3.github.io/iesdp/) | Infinity Engine format reference |
| [A Course in WEIDU](https://gibberlings3.github.io/Documentation/readmes/weiducourse/weiducourse_0.html) | DavidW’s tutorial (start here) |
| [WeiDU Install Tool](https://github.com/InfinityTools/WeiduInstallTool) | GUI installer |
| [Project Infinity](https://github.com/ALIENQuake/ProjectInfinity) | Mod manager (install order, metadata) |

Useful G3 forum threads:

- [New Player’s Guide to Installing and Playing Mods](https://www.gibberlings3.net/forums/topic/33164-a-new-player%E2%80%99s-guide-to-installing-and-playing-mods/)
- [Modding How-Tos and Tutorials](https://www.gibberlings3.net/forums/forum/28-modding-how-tos-and-tutorials/)
- [Tools](https://www.gibberlings3.net/forums/forum/138-tools/)

Related PST projects worth studying:

- [EE Fixpack](https://www.gibberlings3.net/mods/fixes/eefp/) (includes PST:EE) — [GitHub](https://github.com/Gibberlings3/EE_Fixpack)
- [PST Unfinished Business – Reloaded](https://github.com/Argent77/PST-UB-reloaded) (classic + EE; includes Curst restorations)
- Classic: Qwinn’s Fixpack / UB / Tweaks (Spellhold Studios)

## Develop against the game

1. Install PST or PST:EE; apply the current official patch.
2. Install a fixpack first (EE Fixpack on EE; Qwinn’s Fixpack on classic).
3. Download WeiDU; put `weidu.exe` in the game folder (next to `chitin.key`).
4. Copy or symlink this repo’s `pst_curst` folder into the game folder.
5. Copy `weidu.exe` to `setup-pst_curst.exe` and run it (or use WeiDU Install Tool / Project Infinity).
6. Edit sources in the repo; reinstall the component to test.

### Quick WeiDU patterns

```weidu
COPY "%MOD_FOLDER%/copy/foo.itm" override
COMPILE "%MOD_FOLDER%/dialog/bar.d"
COMPILE "%MOD_FOLDER%/scripts/baz.baf"
EXTEND_TOP "some.bcs" "%MOD_FOLDER%/scripts/addon.baf"
COPY_EXISTING "ar0500.are" override
  // patch bytes / structures
BUT_ONLY
```

Restrict components with:

```weidu
REQUIRE_PREDICATE GAME_IS ~pst pstee~ @2
```

## Install order (players)

1. Official patch  
2. Fixpack  
3. Content mods (UB, this mod, …)  
4. Tweaks / UI / widescreen  

`pst_curst.ini` declares a starting `After =` list for Project Infinity; update it as dependencies firm up.

## Packaging a release

Ship the `pst_curst` folder (and optionally a renamed WeiDU `setup-pst_curst` binary per OS). Do not include `weidu_external/`, `backup/`, or `.debug` files. G3’s [ModPackaging](https://github.com/Gibberlings3/ModPackaging) / [WeiduModPackager](https://github.com/InfinityTools/WeiduModPackager) can automate multi-OS packages.

## License

Not set yet — add a license before public release.
