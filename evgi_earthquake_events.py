import os
import pandas as pd
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from math import radians, cos, sin, asin, sqrt

# Συνάρτηση για τον υπολογισμό της απόστασης μεταξύ δύο γεωγραφικών σημείων
def distance(lat1, lat2, lon1, lon2):
    lon1, lon2, lat1, lat2 = map(radians, [lon1, lon2, lat1, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Ακτίνα της γης σε χιλιόμετρα
    return c * r

# Ρυθμίσεις για τη σύνδεση με τον πελάτη FDSN
client = Client("NOA")
sts = ['EVGI']
starttime = UTCDateTime("2024-01-01")
endtime = UTCDateTime("2024-02-01")
evgi_lat = 38.62
evgi_lon = 20.66

# Λήψη σεισμικών γεγονότων
cat2 = client.get_events(starttime=starttime, endtime=endtime, latitude=evgi_lat, longitude=evgi_lon, minmagnitude=2)

# Δημιουργία μιας λίστας για αποθήκευση των δεδομένων
data = []

# Δημιουργία φακέλου στην επιφάνεια εργασίας
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
folder_name = "EVGI"  # Όνομα φακέλου
folder_path = os.path.join(desktop_path, folder_name)

# Δημιουργία φακέλου αν δεν υπάρχει
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Επεξεργασία των πρώτων 20 σεισμικών γεγονότων και αποθήκευση των δεδομένων
for i in range(min(20, len(cat2))):  # Περιορισμός στους πρώτους 20 σεισμούς
    try:
        time = cat2[i].origins[0].time
        event = client.get_events(starttime=time - 2*60, endtime=time + 3*60, minmagnitude=2)
        mag = event[0].magnitudes[0].mag
        evtlat = event[0].origins[0].latitude
        evtlon = event[0].origins[0].longitude

        # Φορμάρισμα του χρόνου
        formatted_time = time.strftime("%Y-%m-%d %H:%M")

        # Πρόσθεση δεδομένων στη λίστα
        data.append({
            "Date and Time": formatted_time,
            "Magnitude": mag,
            "Latitude": evtlat,
            "Longitude": evtlon
        })

    except Exception as e:
        print(f"Error processing event at {str(time)}: {str(e)}")
        pass

# Δημιουργία DataFrame από τη λίστα
df = pd.DataFrame(data)

# Έλεγχος αν ο φάκελος υπάρχει και είναι έτοιμος για αποθήκευση
if not os.path.exists(folder_path):
    print(f"Ο φάκελος {folder_name} δεν βρέθηκε στην επιφάνεια εργασίας. Δημιουργείται...")
    os.makedirs(folder_path)

# Ορισμός του πλήρους μονοπατιού για το αρχείο Excel
excel_path = os.path.join(folder_path, "evgi_earthquake_events.xlsx")

# Αποθήκευση στο αρχείο Excel
try:
    df.to_excel(excel_path, index=False)
    print(f"Τα δεδομένα αποθηκεύτηκαν επιτυχώς στο αρχείο '{excel_path}'.")
except Exception as e:
    print(f"Σφάλμα κατά την αποθήκευση του αρχείου Excel: {str(e)}")
