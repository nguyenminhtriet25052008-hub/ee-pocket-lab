#!/usr/bin/env python3
"""opamp - operational amplifier gain calculator & standard E24 resistor pair finder.

Supports non-inverting (Av = 1 + Rf/Rin) and inverting (Av = -Rf/Rin) topologies.

Usage:
    python opamp.py noninv --rf 10k --rin 1k
    python opamp.py noninv --gain 11                  # find best E24 pairs
    python opamp.py inv --gain -4.7
"""
import argparse
import math

E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
PREFIX = {"": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}


def parse_r(text):
    text = str(text).strip().replace("Ohm", "").replace("ohm", "")
    return float(text[:-1]) * PREFIX[text[-1]] if text[-1] in PREFIX else float(text)


def fmt_r(val):
    if val >= 1e6:
        return f"{val / 1e6:.3g}M"
    if val >= 1e3:
        return f"{val / 1e3:.3g}k"
    return f"{val:.3g}"


def calc_gain(mode, rf, rin):
    av = (1.0 + rf / rin) if mode == "noninv" else (-rf / rin)
    db = 20.0 * math.log10(abs(av)) if av != 0 else float("-inf")
    return av, db


def find_pairs(mode, target_gain, top=5):
    target_mag = abs(target_gain)
    if mode == "noninv" and target_mag < 1.0:
        raise ValueError("Non-inverting gain magnitude must be >= 1.0")
    values = [b * (10 ** d) for d in (3, 4, 5) for b in E24]  # 1 kOhm .. 910 kOhm
    candidates = []
    for rin in values:
        for rf in values:
            av, db = calc_gain(mode, rf, rin)
            err_pct = (abs(av) - target_mag) / target_mag * 100.0
            candidates.append((abs(err_pct), rf, rin, av, db, err_pct))
    candidates.sort(key=lambda x: (round(x[0], 4), abs(x[1] + x[2] - 30e3)))
    return [(rf, rin, av, db, err) for _, rf, rin, av, db, err in candidates[:top]]


def main():
    ap = argparse.ArgumentParser(description="Op-Amp gain calculator & E24 resistor finder.")
    ap.add_argument("mode", choices=("noninv", "inv"), help="noninv (1 + Rf/Rin) or inv (-Rf/Rin)")
    ap.add_argument("--rf", help="feedback resistor (e.g. 10k)")
    ap.add_argument("--rin", help="input resistor (e.g. 1k)")
    ap.add_argument("--gain", type=float, help="target voltage gain Av (V/V)")
    args = ap.parse_args()

    if args.rf and args.rin:
        rf, rin = parse_r(args.rf), parse_r(args.rin)
        av, db = calc_gain(args.mode, rf, rin)
        print(f"Op-Amp ({args.mode})  |  Rf = {fmt_r(rf)}Ohm, Rin = {fmt_r(rin)}Ohm")
        print(f"Voltage Gain Av = {av:+.4f} V/V  ({db:+.2f} dB)")
    elif args.gain is not None:
        print(f"Best E24 pairs for {args.mode} Op-Amp with target gain Av = {args.gain:g} V/V:\n")
        print(f"{'Rf':>9}  {'Rin':>9}  {'Av (V/V)':>10}  {'Gain (dB)':>10}  {'Error':>8}")
        for rf, rin, av, db, err in find_pairs(args.mode, args.gain):
            print(f"{fmt_r(rf):>6}Ohm  {fmt_r(rin):>6}Ohm  {av:>+10.4f}  {db:>+9.2f}dB  {err:>+7.2f}%")
    else:
        ap.error("provide either (--rf and --rin) or --gain")


if __name__ == "__main__":
    main()
