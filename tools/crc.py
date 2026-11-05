#!/usr/bin/env python3
"""crc - embedded communication CRC calculator (CRC-8, CRC-16/MODBUS, CRC-16/CCITT, CRC-32).

Accepts either a hex byte frame (--hex "01 03 00 00 00 0A") or an ASCII string.

Usage:
    python crc.py --hex "01 03 00 00 00 0A"              # great for Modbus RTU frames
    python crc.py "123456789"                            # standard CRC test vector
"""
import argparse
import binascii


def crc8_smbus(data: bytes) -> int:
    crc = 0x00
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc


def crc32_iso(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def compute_all(data: bytes):
    m = crc16_modbus(data)
    return {
        "crc8": crc8_smbus(data),
        "crc16_modbus": m,
        "modbus_le_bytes": f"{m & 0xFF:02X} {(m >> 8) & 0xFF:02X}",
        "crc16_ccitt": crc16_ccitt(data),
        "crc32": crc32_iso(data),
    }


def main():
    ap = argparse.ArgumentParser(description="CRC-8 / CRC-16 (Modbus, CCITT) / CRC-32 calculator.")
    ap.add_argument("payload", nargs="?", help="ASCII text payload")
    ap.add_argument("--hex", help='hex byte string, e.g. "01 03 00 00 00 0A"')
    args = ap.parse_args()

    if args.hex:
        cleaned = args.hex.replace("0x", "").replace(" ", "").replace(",", "")
        data = bytes.fromhex(cleaned)
    elif args.payload is not None:
        data = args.payload.encode("utf-8")
    else:
        ap.error("provide either a text payload or --hex BYTES")

    r = compute_all(data)
    print(f"Input ({len(data)} bytes): {' '.join(f'{b:02X}' for b in data)}")
    print(f"  CRC-8/SMBus        : 0x{r['crc8']:02X}")
    print(f"  CRC-16/CCITT-FALSE : 0x{r['crc16_ccitt']:04X}")
    print(f"  CRC-16/MODBUS      : 0x{r['crc16_modbus']:04X}   (frame append Low-High: {r['modbus_le_bytes']})")
    print(f"  CRC-32/ISO-HDLC    : 0x{r['crc32']:08X}")


if __name__ == "__main__":
    main()
