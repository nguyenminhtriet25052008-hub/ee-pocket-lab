#!/usr/bin/env python3
"""ledcalc - current-limiting resistor calculator for single or series LEDs,
with nearest standard E24 value and safe power rating recommendation.

Usage:
    python ledcalc.py --vs 5 --vf 2.0 --if 20            # 5V supply, red LED 20mA
    python ledcalc.py --vs 12 --vf 3.2 --if 15 -n 3      # 3 white LEDs in series
"""
import argparse

E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
RATINGS = [(0.125, "1/8 W"), (0.25, "1/4 W"), (0.5, "1/2 W"), (1.0, "1 W"), (2.0, "2 W"), (5.0, "5 W")]


def nearest_e24_up(r_exact):
    """Return the smallest E24 standard resistor >= r_exact."""
    for dec in range(-1, 7):
        for b in E24:
            cand = round(b * (10 ** dec), 4)
            if cand >= r_exact * 0.9999:
                return cand
    return r_exact


def safe_rating(power_w):
    """Recommend standard resistor wattage with >= 2x safety derating."""
    needed = power_w * 2.0
    for watts, label in RATINGS:
        if watts >= needed:
            return label
    return f"{needed:.1f} W+"


def solve_led(vs, vf, if_ma, count=1):
    v_leds = vf * count
    if vs <= v_leds:
        raise ValueError(f"Supply ({vs}V) must exceed total LED forward voltage ({v_leds}V)")
    i_a = if_ma / 1000.0
    r_exact = (vs - v_leds) / i_a
    r_std = nearest_e24_up(r_exact)
    i_actual_ma = (vs - v_leds) / r_std * 1000.0
    p_res_w = ((vs - v_leds) ** 2) / r_std
    eff_pct = (v_leds / vs) * 100.0
    return {
        "r_exact": r_exact,
        "r_std": r_std,
        "i_actual_ma": i_actual_ma,
        "p_res_mw": p_res_w * 1000.0,
        "rating": safe_rating(p_res_w),
        "eff_pct": eff_pct,
    }


def main():
    ap = argparse.ArgumentParser(description="LED series resistor & power rating calculator.")
    ap.add_argument("--vs", type=float, required=True, help="supply voltage (V)")
    ap.add_argument("--vf", type=float, default=2.0, help="LED forward voltage (V, default 2.0)")
    ap.add_argument("--if", dest="if_ma", type=float, default=20.0, help="target LED current (mA, default 20)")
    ap.add_argument("-n", "--count", type=int, default=1, help="number of LEDs in series (default 1)")
    args = ap.parse_args()

    res = solve_led(args.vs, args.vf, args.if_ma, args.count)
    print(f"Supply: {args.vs:g} V  |  LEDs: {args.count} x {args.vf:g} V  |  Target I: {args.if_ma:g} mA")
    print(f"Exact R     : {res['r_exact']:.2f} Ohm")
    print(f"Standard E24: {res['r_std']:g} Ohm  (actual I = {res['i_actual_ma']:.2f} mA)")
    print(f"Resistor P  : {res['p_res_mw']:.1f} mW  ->  Use {res['rating']} resistor (2x derated)")
    print(f"Efficiency  : {res['eff_pct']:.1f}% of power goes to LED(s)")


if __name__ == "__main__":
    main()
