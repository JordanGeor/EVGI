import os
from obspy import read
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Εκθετική συνάρτηση
def exponential(t, a, b):
    return a * np.exp(-b * t)

folder_path = r"C:\Users\user1\Desktop\EVGI\cleaned_waveforms"

for filename in os.listdir(folder_path):
    if filename.endswith(".mseed"):
        filepath = os.path.join(folder_path, filename)
        st = read(filepath)
        tr = st.select(component="Z")[0]

        tr.detrend("demean")
        tr.filter("bandpass", freqmin=0.5, freqmax=15.0)

        # Χρόνος
        times = tr.times()
        df = tr.stats.sampling_rate

        # Max Amplitude
        max_amp = max(abs(tr.data))
        max_index = abs(tr.data).argmax()
        max_time = tr.stats.starttime + (max_index / df)

        # -------- Fit μετά το max --------
        fit_seconds = 2  # πόσα δευτερόλεπτα μετά το max
        fit_start = max_index
        fit_end = min(fit_start + int(fit_seconds * df), len(tr.data))

        x_fit = times[fit_start:fit_end] - times[fit_start]
        y_fit = abs(tr.data[fit_start:fit_end])

        # Φιλτράρουμε μηδενικά
        mask = y_fit > 0
        x_fit_valid = x_fit[mask]
        y_fit_valid = y_fit[mask]

        # Fit εκθετικής
        try:
            popt, _ = curve_fit(exponential, x_fit_valid, y_fit_valid, p0=(max_amp, 1.0))
            a_fit, b_fit = popt
            y_model = exponential(x_fit_valid, *popt)
            fit_label = f"y = {a_fit:.2f}·e^(-{b_fit:.2f}·t)"
        except:
            y_model = np.zeros_like(x_fit_valid)
            a_fit, b_fit = 0, 0
            fit_label = "Fit failed"

        # -------- Plot --------
        fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=False, gridspec_kw={"height_ratios": [3, 2, 2]})

        # 1. Waveform
        axs[0].plot(times, tr.data, 'k-', label="Waveform")
        axs[0].axvline(times[max_index], color='orange', linestyle='--', label='Max Amplitude')
        axs[0].set_title(f"{filename} - Max Amplitude: {max_amp:.4f}")
        axs[0].legend()
        axs[0].grid()

        # 2. Spectrum (FFT)
        fft = np.fft.rfft(tr.data)
        freqs = np.fft.rfftfreq(len(tr.data), d=1.0/df)
        amps = np.abs(fft)
        dom_freq = freqs[np.argmax(amps)]
        axs[1].plot(freqs, amps, color='purple')
        axs[1].set_title(f"Frequency Spectrum (Dominant: {dom_freq:.2f} Hz)")
        axs[1].set_xlabel("Frequency (Hz)")
        axs[1].set_ylabel("Amplitude")
        axs[1].grid()

        # 3. Exponential Fit
        axs[2].plot(x_fit_valid, y_fit_valid, 'gray', label="Data (post-max)")
        axs[2].plot(x_fit_valid, y_model, 'b--', label=fit_label)
        axs[2].set_title("Exponential Decay Fit")
        axs[2].set_xlabel("Time after Max (s)")
        axs[2].set_ylabel("Amplitude")
        axs[2].legend()
        axs[2].grid()

        plt.tight_layout()
        plt.show()
