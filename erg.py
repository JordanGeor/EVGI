import os
import glob
import matplotlib.pyplot as plt
from obspy import read

def load_mseed_files(directory):
    # Αναζητούμε όλα τα αρχεία mseed στους υποφακέλους waveforms και cleaned_waveforms
    waveform_dir = os.path.join(directory, 'waveforms')
    cleaned_waveform_dir = os.path.join(directory, 'cleaned_waveforms')

    waveform_files = glob.glob(os.path.join(waveform_dir, '*.mseed'))
    cleaned_waveform_files = glob.glob(os.path.join(cleaned_waveform_dir, '*.mseed'))

    # Εμφανίζουμε τα αρχεία που βρέθηκαν για έλεγχο
    print("Αρχεία στον φάκελο 'waveforms':", waveform_files)
    print("Αρχεία στον φάκελο 'cleaned_waveforms':", cleaned_waveform_files)

    return waveform_files, cleaned_waveform_files

def plot_comparison(waveform_files, cleaned_waveform_files):
    # Αν υπάρχουν αρχεία για σύγκριση
    if len(waveform_files) == 0 or len(cleaned_waveform_files) == 0:
        print("Δεν βρέθηκαν αρχεία .mseed στους φακέλους.")
        return

    # Διασχίζουμε τα αρχεία και τα συγκρίνουμε
    for waveform_file, cleaned_file in zip(waveform_files, cleaned_waveform_files):
        try:
            # Διαβάζουμε τα αρχεία MSEED
            waveform_data = read(waveform_file)
            cleaned_data = read(cleaned_file)

            # Σχεδιάζουμε τα δεδομένα
            fig, axs = plt.subplots(2, 1, figsize=(10, 6))
            axs[0].plot(waveform_data[0].times(), waveform_data[0].data, label='Original')
            axs[0].set_title(f"Original: {os.path.basename(waveform_file)}")
            axs[0].set_xlabel('Time')
            axs[0].set_ylabel('Amplitude')
            axs[0].legend()

            axs[1].plot(cleaned_data[0].times(), cleaned_data[0].data, label='Cleaned', color='red')
            axs[1].set_title(f"Cleaned: {os.path.basename(cleaned_file)}")
            axs[1].set_xlabel('Time')
            axs[1].set_ylabel('Amplitude')
            axs[1].legend()

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Σφάλμα κατά την ανάγνωση ή εμφάνιση αρχείου: {e}")

def main():
    # Προσδιορίζουμε την τοποθεσία του φακέλου EVGI στην επιφάνεια εργασίας
    desktop_path = os.path.expanduser("~/Desktop")
    evgi_folder = os.path.join(desktop_path, 'EVGI')

    if not os.path.exists(evgi_folder):
        print("Ο φάκελος EVGI δεν βρέθηκε στην επιφάνεια εργασίας.")
        return

    waveform_files, cleaned_waveform_files = load_mseed_files(evgi_folder)
    
    plot_comparison(waveform_files, cleaned_waveform_files)

if __name__ == "__main__":
    main()
