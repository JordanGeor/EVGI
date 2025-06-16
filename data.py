import os
import pandas as pd
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from tkinter import Tk, messagebox, simpledialog, ttk
import tkinter as tk

# Ρυθμίσεις
client = Client("NOA")
starttime = UTCDateTime("2024-01-01")
endtime = UTCDateTime("2024-02-01")
evgi_lat = 38.62
evgi_lon = 20.66
maxradius_km = 2.0

# Δημιουργία φακέλων στην επιφάνεια εργασίας (χωρίς μηνύματα)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
folder_path = os.path.join(desktop_path, "EVGI")
waveform_folder = os.path.join(folder_path, "waveforms")
os.makedirs(folder_path, exist_ok=True)
os.makedirs(waveform_folder, exist_ok=True)

# GUI λειτουργία
root = Tk()
root.withdraw()

# Αρχική ανάκτηση σεισμών για στατιστικά
try:
    all_events = client.get_events(starttime=starttime, endtime=endtime,
                                   latitude=evgi_lat, longitude=evgi_lon,
                                   maxradius=maxradius_km, minmagnitude=0)
    bins = {'0–3': 0, '3–5': 0, '5+': 0}
    for evt in all_events:
        mag = evt.magnitudes[0].mag
        if mag < 3:
            bins['0–3'] += 1
        elif mag < 5:
            bins['3–5'] += 1
        else:
            bins['5+'] += 1

    stats_msg = "\n📊 Διαθέσιμα σεισμικά γεγονότα:\n"
    for cat, val in bins.items():
        stats_msg += f" - Μέγεθος {cat}: {val} σεισμοί\n"
    messagebox.showinfo("Στατιστικά Σεισμών", stats_msg)
except Exception as e:
    messagebox.showerror("Σφάλμα", f"Αποτυχία λήψης σεισμών:\n{str(e)}")
    exit()

# Λήψη ελάχιστου μεγέθους με έλεγχο
while True:
    try:
        min_mag = float(simpledialog.askstring("Μέγεθος", "Δώσε ελάχιστο μέγεθος σεισμού (π.χ. 2.5):"))
        filtered_cat = client.get_events(starttime=starttime, endtime=endtime,
                                         latitude=evgi_lat, longitude=evgi_lon,
                                         maxradius=maxradius_km, minmagnitude=min_mag)
        total_found = len(filtered_cat)
        if total_found == 0:
            messagebox.showwarning("Χωρίς Αποτελέσματα", "Δεν βρέθηκαν σεισμοί. Προσπάθησε ξανά.")
            continue
        else:
            messagebox.showinfo("Αποτελέσματα", f"Βρέθηκαν {total_found} σεισμοί για μέγεθος ≥ {min_mag}")
            break
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Μη έγκυρη είσοδος:\n{str(e)}")

# Λήψη αριθμού γεγονότων
while True:
    try:
        requested = int(simpledialog.askstring("Πλήθος", "Δώσε πόσα σεισμικά γεγονότα να επεξεργαστώ (π.χ. 5 ή 20):"))
        if requested <= 0:
            continue

        if requested > total_found:
            choice = messagebox.askyesno("Λιγότερα διαθέσιμα", f"Οι σεισμοί είναι μόνο {total_found}. Να κατεβάσω αυτούς;")
            if choice:
                requested = total_found
                break
            else:
                continue
        else:
            break
    except:
        continue

# Επεξεργασία σεισμών
data = []
for i in range(min(requested, len(filtered_cat))):
    try:
        evt = filtered_cat[i]
        time = evt.origins[0].time
        mag = evt.magnitudes[0].mag
        lat = evt.origins[0].latitude
        lon = evt.origins[0].longitude
        time_str = time.strftime("%Y-%m-%d %H:%M")

        data.append({
            "Date and Time": time_str,
            "Magnitude": mag,
            "Latitude": lat,
            "Longitude": lon
        })

        # Προαιρετικά: Κατέβασμα waveform
        try:
            st = client.get_waveforms(network="HT", station="EVGI", location="",
                                      channel="HHZ", starttime=time - 10, endtime=time + 50)
            st.write(os.path.join(waveform_folder, f"event_{i+1}_waveform.mseed"), format="MSEED")
        except:
            pass

    except Exception as e:
        continue

# Αποθήκευση Excel
df = pd.DataFrame(data)
excel_path = os.path.join(folder_path, "evgi_earthquake_events.xlsx")
df.to_excel(excel_path, index=False)

# Εμφάνιση πίνακα σε GUI
def show_table(dataframe):
    window = tk.Tk()
    window.title("📋 Σεισμικά Γεγονότα")

    tree = ttk.Treeview(window)
    tree["columns"] = list(dataframe.columns)
    tree["show"] = "headings"

    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    for _, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(fill="both", expand=True)
    window.mainloop()

show_table(df)
