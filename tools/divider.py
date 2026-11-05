#!/usr/bin/env python3
"""divider - voltage divider calculator & E12/E24 standard resistor pair finder.

Usage:
    python divider.py --vin 12 --r1 10k --r2 4.7k
    python divider.py --vin 5 --vout 3.3               # find best E24 pairs
    python divider.py --vin 12 --vout 3.3 --series E12
"""
import argparse

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
PREFIX = {"": 1.0, "k": 1e3, "K": 1e3, "M": 1e6, "m": 1e-3}


def parse_r(text):
    text = str(text).strip().replace("Ohm", "").replace("ohm", "")
    return float(text[:-1]) * PREFIX[text[-1]] if text[-1] in PREFIX else float(text)


def fmt_r(val):
    if val >= 1e6:
        return f"{val / 1e6:.3g}M"
    if val >= 1e3:
        return f"{val / 1e3:.3g}k"
    return f"{val:.3g}"


def calc_vout(vin, r1, r2, rload=None):
    r_bot = (r2 * rload) / (r2 + rload) if rload else r2
    vout = vin * r_bot / (r1 + r_bot)
    i_mA = (vin / (r1 + r_bot)) * 1e3
    return vout, i_mA


def best_pairs(vin, vout, series="E24", top=5):
    if not (0 < vout < vin):
        raise ValueError("vout must be strictly between 0 and vin")
    base = E24 if series.upper() == "E24" else E12
    values = [b * (10 ** d) for d in (2, 3, 4, 5) for b in base]  # 100 Ohm .. 910 kOhm
    results = []
    for r1 in values:
        for r2 in values:
            if 1e3 <= r1 + r2 <= 5e5:  # practical quiescent current range
                vo = vin * r2 / (r1 + r2)
                err_pct = (vo - vout) / vout * 100
                results.append((abs(err_pct), r1, r2, vo, err_pct))
    results.sort(key=lambda x: (round(x[0], 4), abs(x[1] + x[2] - 20e3)))
    return [(r1, r2, vo, err) for _, r1, r2, vo, err in results[:top]]


def main():
    ap = argparse.ArgumentParser(description="Voltage divider calculator & E12/E24 finder.")
    ap.add_argument("--vin", type=float, required=True, help="input voltage (V)")
    ap.add_argument("--vout", type=float, help="target output voltage (V) to search R1, R2")
    ap.add_argument("--r1", help="top resistor (e.g. 10k)")
    ap.add_argument("--r2", help="bottom resistor (e.g. 4.7k)")
    ap.add_argument("--rload", help="optional parallel load resistor on Vout")
    ap.add_argument("--series", choices=("E12", "E24"), default="E24")
    args = ap.parse_args()

    if args.r1 and args.r2:
        r1, r2 = parse_r(args.r1), parse_r(args.r2)
        rl = parse_r(args.rload) if args.rload else None
        vout, i_ma = calc_vout(args.vin, r1, r2, rl)
        print(f"Vin = {args.vin:g} V  |  R1 = {fmt_r(r1)}Ohm, R2 = {fmt_r(r2)}Ohm")
        print(f"Vout = {vout:.4f} V  (ratio {vout / args.vin:.4f}, I_div = {i_ma:.3f} mA)")
    elif args.vout is not None:
        print(f"Best {args.series} pairs for {args.vin:g} V -> {args.vout:g} V:\n")
        print(f"{'R1':>8}  {'R2':>8}  {'Vout':>9}  {'Error':>8}  {'I_quiescent':>12}")
        for r1, r2, vo, err in best_pairs(args.vin, args.vout, args.series):
            i_ua = args.vin / (r1 + r2) * 1e6
            print(f"{fmt_r(r1):>7}Ohm  {fmt_r(r2):>7}Ohm  {vo:>8.4f}V  {err:>+7.2f}%  {i_ua:>9.1f} uA")
    else:
        ap.error("provide either (--r1 and --r2) or --vout")


if __name__ == "__main__":
    main()
