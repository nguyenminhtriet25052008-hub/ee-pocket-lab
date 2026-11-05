#!/usr/bin/env python3
"""ne555 - NE555 timer calculator for Astable (oscillator) and Monostable (one-shot) modes.

Usage:
    python ne555.py astable -r1 1k -r2 10k -c 100n
    python ne555.py monostable -r 100k -c 10u
"""
import argparse
import math

LN2 = math.log(2.0)  # ~0.693147
UNITS = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}


def parse_val(text):
    text = str(text).strip()
    return float(text[:-1]) * UNITS[text[-1]] if text[-1] in UNITS else float(text)


def fmt_time(sec):
    for unit, scale in (("s", 1.0), ("ms", 1e-3), ("us", 1e-6), ("ns", 1e-9)):
        if sec >= scale or unit == "ns":
            return f"{sec / scale:.4g} {unit}"


def astable(r1, r2, c):
    t_high = LN2 * (r1 + r2) * c
    t_low = LN2 * r2 * c
    period = t_high + t_low
    freq = 1.0 / period
    duty = (t_high / period) * 100.0
    return {"freq": freq, "period": period, "t_high": t_high, "t_low": t_low, "duty": duty}


def monostable(r, c):
    return math.log(3.0) * r * c  # t = 1.1 * R * C


def main():
    ap = argparse.ArgumentParser(description="NE555 Astable & Monostable calculator.")
    sub = ap.add_subparsers(dest="mode", required=True)

    pa = sub.add_parser("astable", help="oscillator mode (R1, R2, C)")
    pa.add_argument("-r1", required=True, help="R1 between VCC and DISCH (e.g. 1k)")
    pa.add_argument("-r2", required=True, help="R2 between DISCH and TRIG/THRES (e.g. 10k)")
    pa.add_argument("-c", required=True, help="timing capacitor (e.g. 100n)")

    pm = sub.add_parser("monostable", help="one-shot pulse mode (R, C)")
    pm.add_argument("-r", required=True, help="timing resistor (e.g. 100k)")
    pm.add_argument("-c", required=True, help="timing capacitor (e.g. 10u)")

    args = ap.parse_args()
    if args.mode == "astable":
        res = astable(parse_val(args.r1), parse_val(args.r2), parse_val(args.c))
        print(f"NE555 Astable  |  Frequency = {res['freq']:.4g} Hz  |  Duty Cycle = {res['duty']:.2f}%")
        print(f"Period = {fmt_time(res['period'])}  (T_high = {fmt_time(res['t_high'])}, T_low = {fmt_time(res['t_low'])})")
    else:
        width = monostable(parse_val(args.r), parse_val(args.c))
        print(f"NE555 Monostable  |  Output Pulse Width = {fmt_time(width)}")


if __name__ == "__main__":
    main()
