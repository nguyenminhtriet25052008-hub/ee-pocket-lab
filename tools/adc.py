#!/usr/bin/env python3
"""adc - ADC / DAC resolution, LSB step size, SNR & code <-> voltage converter.

Usage:
    python adc.py --bits 12 --vref 3.3 --vin 1.65
    python adc.py --bits 10 --vref 5.0 --code 512
"""
import argparse


def analyze_adc(bits, vref, vin=None, code=None):
    levels = (1 << bits) - 1
    lsb_v = vref / levels
    snr_db = 6.02 * bits + 1.76
    result = {"bits": bits, "levels": levels, "lsb_mv": lsb_v * 1e3, "snr_db": snr_db}
    if vin is not None:
        clamped = max(0.0, min(vref, vin))
        c = int(round((clamped / vref) * levels))
        v_recon = (c / levels) * vref
        result.update({"code": c, "hex": f"0x{c:X}", "v_recon": v_recon, "q_err_mv": (v_recon - vin) * 1e3})
    elif code is not None:
        c = max(0, min(levels, int(code)))
        result.update({"code": c, "hex": f"0x{c:X}", "v_out": (c / levels) * vref})
    return result


def main():
    ap = argparse.ArgumentParser(description="ADC / DAC code <-> voltage & LSB calculator.")
    ap.add_argument("-b", "--bits", type=int, default=12, help="ADC resolution in bits (default 12)")
    ap.add_argument("--vref", type=float, default=3.3, help="reference voltage Vref (default 3.3 V)")
    ap.add_argument("--vin", type=float, help="analog input voltage to quantize (V)")
    ap.add_argument("--code", type=int, help="digital code to convert back to voltage")
    args = ap.parse_args()

    r = analyze_adc(args.bits, args.vref, args.vin, args.code)
    print(f"{r['bits']}-bit ADC/DAC  |  Vref = {args.vref:g} V  |  Full-scale = 0..{r['levels']}")
    print(f"Step size (1 LSB) = {r['lsb_mv']:.4f} mV  |  Ideal SNR = {r['snr_db']:.2f} dB")
    if "v_recon" in r:
        print(f"Vin = {args.vin:g} V  ->  Code = {r['code']} ({r['hex']})  |  Reconstructed = {r['v_recon']:.5f} V (err {r['q_err_mv']:+.3f} mV)")
    elif "v_out" in r:
        print(f"Code = {r['code']} ({r['hex']})  ->  Vout = {r['v_out']:.5f} V ({r['v_out'] / args.vref * 100:.2f}% FS)")


if __name__ == "__main__":
    main()
