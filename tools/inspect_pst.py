#!/usr/bin/env python3
"""Minimal CHITIN.KEY / BIFF reader for PSTEE inspection."""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

RES_EXT = {
    0x3ED: "BMP",
    0x3EE: "MVE",
    0x3EF: "WAV",
    0x3F0: "WFX",
    0x3F1: "PLT",
    0x3F2: "BAM",
    0x3F3: "WED",
    0x3F4: "CHU",
    0x3F5: "TIS",
    0x3F6: "MOS",
    0x3F7: "ITM",
    0x3F8: "SPL",
    0x3F9: "BCS",
    0x3FA: "IDS",
    0x3FB: "CRE",
    0x3FC: "ARE",
    0x3FD: "DLG",
    0x3FE: "2DA",
    0x3FF: "GAM",
    0x400: "STO",
    0x401: "WMP",
    0x402: "EFF",
    0x403: "BS",
    0x404: "CHR",
    0x405: "VVC",
    0x406: "VEF",
    0x407: "PRO",
    0x408: "BIO",
    0x409: "WBM",
    0x40A: "FNT",
    0x40B: "GUI",
    0x40C: "SQL",
    0x40D: "PVRZ",
    0x40E: "GLSL",
    0x40F: "TOT",
    0x410: "TOH",
    0x411: "MENU",
    0x412: "LUA",
    0x413: "TTF",
    0x414: "PNG",
    0x415: "BAH",
    0x44C: "INI",
    0x44D: "VRT",
    0x44E: "GLC",
}


def read_cstr(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("ascii", errors="replace")


class KeyIndex:
    def __init__(self, game: Path):
        self.game = game
        key = (game / "chitin.key").read_bytes()
        sig, ver = key[0:4], key[4:8]
        assert sig == b"KEY ", sig
        bif_count, res_count, bif_off, res_off = struct.unpack_from("<IIII", key, 8)
        self.bifs: list[tuple[str, int]] = []
        for i in range(bif_count):
            off = bif_off + i * 12
            file_size, name_off, name_len, loc = struct.unpack_from("<IIHH", key, off)
            name = read_cstr(key[name_off : name_off + name_len]).replace("\\", "/")
            self.bifs.append((name, loc))
        self.resources: dict[tuple[str, int], tuple[int, int]] = {}
        for i in range(res_count):
            off = res_off + i * 14
            name = read_cstr(key[off : off + 8]).upper()
            typ, resid = struct.unpack_from("<HI", key, off + 8)
            self.resources[(name, typ)] = (resid >> 20, resid & 0xFFFFF)

    def get(self, name: str, typ: int) -> bytes:
        key = (name.upper(), typ)
        if key not in self.resources:
            raise KeyError(f"Missing {name}.{RES_EXT.get(typ, hex(typ))}")
        bif_idx, file_idx = self.resources[key]
        bif_name, _ = self.bifs[bif_idx]
        path = self.game / bif_name
        # EE may use .bif or compressed; also try data/
        if not path.exists():
            alt = self.game / "data" / Path(bif_name).name
            if alt.exists():
                path = alt
            else:
                raise FileNotFoundError(path)
        data = path.read_bytes()
        assert data[0:4] == b"BIFF", data[0:8]
        # BIFF V1
        file_count, tile_count, entry_off = struct.unpack_from("<III", data, 8)
        # locate file entry
        # V1 entries are 16 bytes starting at entry_off
        found = None
        for i in range(file_count):
            eoff = entry_off + i * 16
            resid, foff, fsize, ftype, _ = struct.unpack_from("<IIIHH", data, eoff)
            if (resid & 0xFFFFF) == file_idx or resid == file_idx:
                found = (foff, fsize)
                break
        if found is None:
            # Some EE biffs use locator differently; try index = file_idx directly
            eoff = entry_off + file_idx * 16
            resid, foff, fsize, ftype, _ = struct.unpack_from("<IIIHH", data, eoff)
            found = (foff, fsize)
        foff, fsize = found
        return data[foff : foff + fsize]


def list_matches(idx: KeyIndex, substr: str, typ: int | None = None) -> None:
    s = substr.upper()
    for (name, t), _ in sorted(idx.resources.items()):
        if s in name and (typ is None or t == typ):
            print(f"{name}.{RES_EXT.get(t, hex(t))}")


def dump_are_actors(are: bytes) -> None:
    print("ARE header", are[0:8])
    actors_off = struct.unpack_from("<I", are, 0x54)[0]
    actors_count = struct.unpack_from("<H", are, 0x58)[0]
    print(f"actors_off={actors_off:#x} count={actors_count}")
    for i in range(actors_count):
        base = actors_off + i * 0x110
        name = read_cstr(are[base : base + 32])
        x, y = struct.unpack_from("<HH", are, base + 0x20)
        cre = read_cstr(are[base + 0x80 : base + 0x88])
        print(f"  [{i:02d}] {name!r:32} ({x:4d},{y:4d}) cre={cre}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--list", default="")
    ap.add_argument("--type", type=lambda x: int(x, 0), default=None)
    ap.add_argument("--are", default="")
    ap.add_argument("--extract", nargs=2, metavar=("NAME", "TYPE"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    idx = KeyIndex(Path(args.game))
    if args.list:
        list_matches(idx, args.list, args.type)
    if args.are:
        data = idx.get(args.are, 0x3FC)
        dump_are_actors(data)
    if args.extract:
        name, typ_s = args.extract
        typ = int(typ_s, 0)
        data = idx.get(name, typ)
        out = Path(args.out) if args.out else Path(f"{name}.{RES_EXT.get(typ, 'bin')}")
        out.write_bytes(data)
        print(f"Wrote {out} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
