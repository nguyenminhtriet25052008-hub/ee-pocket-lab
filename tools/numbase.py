#!/usr/bin/env python3
"""numbase - programmer's base converter (Hex / Dec / Bin / Oct), two's complement,
and bit-position breakdown for microcontroller register debugging.

Usage:
    python numbase.py 0xA5
    python numbase.py 0b1101_0010 -w 8
    python numbase.py -42 -w 16
"""
import argparse


def parse_int(text):
    text = str(text).strip().replace("_", "")
    return int(text, 0)


def convert(val, width=8):
    mask = (1 << width) - 1
    unsigned = val & mask
    signed = unsigned - (1 << width) if (unsigned & (1 << (width - 1))) else unsigned
    nibbles = " ".join(f"{unsigned:0{width}b}"[i : i + 4] for i in range(0, width, 4))
    set_bits = [b for b in range(width - 1, -1, -1) if (unsigned >> b) & 1]
    return {
        "width": width,
        "unsigned": unsigned,
        "signed": signed,
        "hex": f"0x{unsigned:0{(width + 3) // 4}X}",
        "oct": f"0o{unsigned:o}",
        "bin_grouped": nibbles,
        "set_bits": set_bits,
    }


def main():
    ap = argparse.ArgumentParser(description="Hex/Dec/Bin/Oct & register bitfield inspector.")
    ap.add_argument("value", help="integer in dec (-42, 255), hex (0xFF), bin (0b1010), or oct (0o77)")
    ap.add_argument("-w", "--width", type=int, choices=(8, 16, 32, 64), default=16, help="bit width (default 16)")
    args = ap.parse_args()

    r = convert(parse_int(args.value), args.width)
    print(f"Width    : {r['width']}-bit")
    print(f"Unsigned : {r['unsigned']}")
    print(f"Signed   : {r['signed']} (two's complement)")
    print(f"Hex / Oct: {r['hex']}  |  {r['oct']}")
    print(f"Binary   : {r['bin_grouped']}")
    bits_str = ", ".join(f"bit {b}" for b in r["set_bits"]) if r["set_bits"] else "none"
    print(f"Set bits : {bits_str}")


if __name__ == "__main__":
    main()
