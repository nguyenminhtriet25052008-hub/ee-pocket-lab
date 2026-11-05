#!/usr/bin/env python3
"""rcfilter - RC / RL / LC filter cutoff calculator & ASCII Bode magnitude plot.

Usage:
    python rcfilter.py -r 1k -c 100n                   # cutoff + table
    python rcfilter.py -r 10k -c 10n --type hp --bode  # high-pass with ASCII plot
    python rcfilter.py -l 10m -c 1u                    # LC resonant frequency
"""
import argparse
import math

UNITS = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}


def parse_val(text):
    text = str(text).strip()
    for suf in ("Hz", "F", "H", "Ohm", "ohm"):
        if text.endswith(suf):
            text = text[: -len(suf)].strip()
    return float(text[:-1]) * UNITS[text[-1]] if text[-1] in UNITS else float(text)


def fmt_hz(f):
    for p, s in (("MHz", 1e6), ("kHz", 1e3), ("Hz", 1.0)):
        if f >= s or p == "Hz":
            return f"{f / s:.4g} {p}"


def rc_cutoff(r, c):
    return 1.0 / (2.0 * math.pi * r * c)


def lc_resonance(ind, cap):
    return 1.0 / (2.0 * math.pi * math.sqrt(ind * cap))


def response(freq, fc, ftype="lp"):
    """Return (gain_linear, gain_db, phase_deg) for 1st-order LP or HP filter."""
    ratio = freq / fc
    if ftype == "lp":
        mag = 1.0 / math.sqrt(1.0 + ratio ** 2)
        phase = -math.degrees(math.atan(ratio))
    else:
        mag = ratio / math.sqrt(1.0 + ratio ** 2) if ratio > 0 else 0.0
        phase = 90.0 - math.degrees(math.atan(ratio))
    db = 20.0 * math.log10(max(mag, 1e-12))
    return mag, db, phase


def main():
    ap = argparse.ArgumentParser(description="RC / LC filter calculator & ASCII Bode plot.")
    ap.add_argument("-r", help="resistance (e.g. 1k, 4.7k)")
    ap.add_argument("-c", required=True, help="capacitance (e.g. 100n, 10u)")
    ap.add_argument("-l", help="inductance for LC tank (e.g. 10m, 100u)")
    ap.add_argument("--type", choices=("lp", "hp"), default="lp", help="lp (low-pass) or hp (high-pass)")
    ap.add_argument("--bode", action="store_true", help="print ASCII Bode plot across 4 decades")
    args = ap.parse_args()

    c = parse_val(args.c)
    if args.l and not args.r:
        ind = parse_val(args.l)
        f0 = lc_resonance(ind, c)
        z0 = math.sqrt(ind / c)
        print(f"LC Tank  |  f0 = {fmt_hz(f0)}  |  Characteristic Z0 = {z0:.2f} Ohm")
        return

    if not args.r:
        ap.error("provide -r for RC filter or -l for LC resonance")
    r = parse_val(args.r)
    fc, tau = rc_cutoff(r, c), r * c
    label = "Low-Pass" if args.type == "lp" else "High-Pass"
    print(f"RC {label} Filter  |  fc (-3 dB) = {fmt_hz(fc)}  |  tau = {tau * 1e3:.4g} ms")
    if args.bode:
        print(f"\n{'Freq':>11}  {'Gain (dB)':>9}  {'Phase':>7}  Magnitude (0 dB .. -40 dB)")
        for step in range(-8, 9, 2):
            f = fc * (10 ** (step / 4))
            _, db, ph = response(f, fc, args.type)
            bars = max(0, min(30, int(round((db + 40) / 40 * 30))))
            marker = " <-- fc" if step == 0 else ""
            print(f"{fmt_hz(f):>11}  {db:>+8.2f}   {ph:>+6.1f}d  [{'#' * bars:<30}]{marker}")


if __name__ == "__main__":
    main()
