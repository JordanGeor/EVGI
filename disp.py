import pandas as pd
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# Βήμα 1: Φόρτωση δεδομένων και προεπεξεργασία
file_path = 'C:/Users/user1/Desktop/EVGI/evgi_earthquake_events.xlsx'  # Ενημερώστε τη διαδρομή
data = pd.read_excel(file_path)

# Μετατροπή δεδομένων αν χρειαστεί
if data['Magnitude'].dtype == 'object':
    data['Magnitude'] = data['Magnitude'].str.replace(',', '.').astype(float)

# Demean και Detrend
data['magnitude_demeaned'] = data['Magnitude'] - data['Magnitude'].mean()
data['magnitude_detrended'] = signal.detrend(data['magnitude_demeaned'])

# Βήμα 2: Αφαίρεση instrument-response (προσομοίωση)
# Χρειάζονται οι πραγματικές παράμετροι απόκρισης οργάνου (sensitivity, poles, zeros κλπ).
# Παράδειγμα χωρίς πραγματικά δεδομένα απόκρισης:
instrument_sensitivity = 1.0  # Υποθετικό
data['corrected_signal'] = data['magnitude_detrended'] / instrument_sensitivity

# Βήμα 3: Υπολογισμός μετατόπισης (Displacement)
# Από επιταχυνσιογράφημα υπολογίζουμε πρώτα την ταχύτητα και στη συνέχεια τη μετατόπιση
dt = 1 / 100.0  # Παράδειγμα συχνότητας δειγματοληψίας (100 Hz)
velocity = np.cumsum(data['corrected_signal']) * dt
displacement = np.cumsum(velocity) * dt
data['displacement'] = displacement

# Απεικόνιση αποτελεσμάτων
plt.figure(figsize=(10, 6))
plt.plot(data['Date and Time'], data['displacement'], label='Displacement (Μετατόπιση)')

# Ρύθμιση για καλύτερη εμφάνιση του γραφήματος
plt.xlabel('Ημερομηνία και Ώρα')
plt.ylabel('Μετατόπιση')
plt.title('Μετατόπιση από σεισμικά δεδομένα')

# Εισαγωγή legend και πλέγμα
plt.legend()
plt.grid()

# Ρύθμιση για καλύτερη εμφάνιση των ετικετών στον άξονα X
plt.xticks(rotation=45, ha='right')  # Περιστροφή ετικετών για καλύτερη αναγνωσιμότητα
plt.tight_layout()  # Ρύθμιση του γραφήματος για καλύτερη εμφάνιση

# Εμφάνιση διαγράμματος
plt.show()

# Αποθήκευση αποτελεσμάτων
output_file = 'C:/Users/user1/Desktop/earthquake_displacement.xlsx'
data.to_excel(output_file, index=False)
print(f"Τα αποτελέσματα αποθηκεύτηκαν στο: {output_file}")
