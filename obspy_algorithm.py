import os
from obspy import read
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
import matplotlib.pyplot as plt

# Φάκελος με σεισμικά δεδομένα
folder_path = r"C:\Users\user1\Desktop\EVGI\cleaned_waveforms"

# Παράμετροι STA/LTA
sta = 0.1  # short-term window σε δευτερόλεπτα (πχ 100 ms)
lta = 2.0  # long-term window σε δευτερόλεπτα (πχ 2 sec)
trigger_on = 3.5
trigger_off = 1.0

for filename in os.listdir(folder_path):
    if filename.endswith(".mseed"):
        filepath = os.path.join(folder_path, filename)
        st = read(filepath)

        # Επιλέγουμε το κάθετο κανάλι (Z)
        tr = st.select(component="Z")[0]

        # Προεπεξεργασία σήματος
        tr.detrend("linear")  # απομάκρυνση τάσης
        tr.filter("bandpass", freqmin=1.0, freqmax=10.0)  # φίλτρο ζώνης

        df = tr.stats.sampling_rate  # συχνότητα δειγματοληψίας
        nsta = int(sta * df)
        nlta = int(lta * df)

        # Υπολογισμός recursive STA/LTA characteristic function
        cft = recursive_sta_lta(tr.data, nsta, nlta)

        # Trigger detection
        onsets = trigger_onset(cft, trigger_on, trigger_off)

        print(f"\nΑρχείο: {filename}")

        if len(onsets) >= 1:
            p_sample = onsets[0][0]
            p_time = tr.stats.starttime + p_sample / df
            print(f"P-wave: {p_time}")
        else:
            p_time = None
            print("⚠️ Δεν εντοπίστηκε P-wave")

        if len(onsets) >= 2:
            s_sample = onsets[1][0]
            s_time = tr.stats.starttime + s_sample / df
            print(f"S-wave: {s_time}")
        else:
            s_time = None
            print("⚠️ Δεν εντοπίστηκε S-wave")

        # Πλοκή waveform με γραμμές P και S
        fig, ax = plt.subplots()
        t = tr.times("matplotlib")
        ax.plot_date(t, tr.data, 'k-', label=tr.id)

        if p_time:
            ax.axvline(p_time.matplotlib_date, color='blue', label='P-wave')
        if s_time:
            ax.axvline(s_time.matplotlib_date, color='red', label='S-wave')

        ax.legend()
        ax.set_title(f"Waveform: {filename}")
        fig.autofmt_xdate()
        plt.show()
