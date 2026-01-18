import numpy as np
from PIL import Image
import pickle
import os

class LloydMaxQuantizer:

    def __init__(self, k_bits):
        self.k = k_bits
        self.levels = 2 ** k_bits
        self.centroids = None 
        self.thresholds = None # Progi decyzyjne

    def train(self, data, max_iter=20, epsilon=1e-5):
        min_val = np.min(data)
        max_val = np.max(data)
        

        self.centroids = np.linspace(min_val, max_val, self.levels) # początkowe centroidy równomiernie rozłożone
        
        prev_distortion = float('inf')
        
        for i in range(max_iter):
            # thresholds[i] oddziela region dla centroidu i od i+1
            self.thresholds = (self.centroids[:-1] + self.centroids[1:]) / 2 # średnia artymetyczna sasiadujących centroidów
            
            indices = np.digitize(data, self.thresholds) # np.digitize zwraca indeksy binów
            
            new_centroids = np.zeros_like(self.centroids)
            total_distortion = 0
            
            for l in range(self.levels):
                points_in_bucket = data[indices == l]
                if len(points_in_bucket) > 0:
                    new_centroids[l] = np.mean(points_in_bucket)
                    total_distortion += np.sum((points_in_bucket - new_centroids[l])**2) # suma kwadratów błędów - warunek stopu
                else:
                    new_centroids[l] = self.centroids[l] # brak zmian jeśli brak punktów

            if abs(prev_distortion - total_distortion) < epsilon:
                break
                
            self.centroids = new_centroids
            prev_distortion = total_distortion

    def quantize(self, value):
        # zwraca indeks bina dla danej wartości
        return np.digitize(value, self.thresholds)

    def dequantize(self, index):
        return self.centroids[index]


class ImageCodec:
    def __init__(self, k_bits):
        self.k = k_bits
        # Potrzebujemy osobnych kwantyzatorów dla pasma L (błąd predykcji) i pasma H
        # oraz dla każdego kanału koloru (R, G, B), żeby było idealnie na 5.
        # Struktura: self.quantizers['channel_idx']['band_type']
        self.quantizers = {} 

    def _split_bands(self, vector):
        v = vector.astype(float)  # konwertujemy do float dla precyzji
        pairs = v.reshape(-1, 2) # grupujemy po 2, każdy wiersz to para (x1, x2)
        
        x1 = pairs[:, 0]
        x2 = pairs[:, 1]
        
        L = (x1 + x2) / 2.0
        H = (x1 - x2) / 2.0
        return L, H

    def _merge_bands(self, L, H):
        # odwrotna transformacja
        x1 = L + H
        x2 = L - H
        
        # sklejamy x1 i x2 z L i H z powrotem w jeden wektor
        reconstructed = np.empty((L.size * 2,), dtype=float)
        reconstructed[0::2] = x1 # zaczynając od 0 co 2
        reconstructed[1::2] = x2 # zaczynając od 1 co 2
        return reconstructed

    def encode_image(self, input_path, output_path):
        print(f"--- KODOWANIE: {input_path} (k={self.k}) ---")
        img = Image.open(input_path)
        img_arr = np.array(img)
        
        original_height, original_width, channels = img_arr.shape
        
        # do algorytmu Lloyd-Max potrzebujemy parzystej szerokości
        if original_width % 2 != 0:
            print("Nieparzysta szerokość, dodanie paddingu...")
            img_arr = np.pad(img_arr, ((0,0), (0,1), (0,0)), mode='edge') # edge powiela ostatnią kolumnę
        
        height, width, channels = img_arr.shape

        # zapisujemy oryginalne wymiary, żeby przy dekodowaniu przyciąć nadmiar
        compressed_data = {
            'width': width,  
            'orig_width': original_width,
            'height': height, 
            'channels': channels, 
            'k': self.k,
            'quantizers': {}, 
            'stream': []
        }

        encoded_channels = []
        
        for c in range(channels):
            print(f"Przetwarzanie kanału {c}...")
            flat_pixels = img_arr[:, :, c].flatten() # spłaszczamy do 1D
            
            L_orig, H_orig = self._split_bands(flat_pixels)
            
            # dane treningowe.
            # dla H: po prostu wartości H.
            # dla L: wartości różnic L[i] - L[i-1].
            
            diff_L = np.diff(L_orig, prepend=L_orig[0]) # uproszczenie do treningu
            
            q_L = LloydMaxQuantizer(self.k)
            q_H = LloydMaxQuantizer(self.k)
            
            # trening na próbce danych
            # q_L.train(diff_L[::5]) 
            # q_H.train(H_orig[::5])

            # trening na całości danych
            q_L.train(diff_L) 
            q_H.train(H_orig)
            
            compressed_data['quantizers'][c] = {'L': q_L, 'H': q_H}  # zapisujemy definicje kwantyzatorów (centroidy i progi)
            

            H_indices = q_H.quantize(H_orig) # kwantyzacja H (wprost)
            
            # pasmo L: DPCM z pętlą sprzężenia zwrotnego
            L_indices = []
            first_val = L_orig[0]
            previous_reconstructed_L = first_val

            L_indices.append(first_val) # zapisujemy pierwszy piksel bez zmian
            
            for val in L_orig[1:]:
                diff = val - previous_reconstructed_L
                
                idx = int(q_L.quantize(diff)) # kwantyzacja różnicy
                L_indices.append(idx)
                
                # rekonstrukcja (to co zobaczy dekoder)
                reconstructed_diff = q_L.dequantize(idx)
                previous_reconstructed_L += reconstructed_diff
            
            encoded_channels.append({
                'L_stream': np.array(L_indices, dtype=np.uint8),
                'H_stream': np.array(H_indices, dtype=np.uint8)
            })

        compressed_data['stream'] = encoded_channels
 
        with open(output_path, 'wb') as f:
            pickle.dump(compressed_data, f)
        print(f"Zapisano skompresowany plik: {output_path}")

    def decode_image(self, input_path, output_path):
        print(f"--- DEKODOWANIE: {input_path} ---")
        with open(input_path, 'rb') as f:
            data = pickle.load(f)
            
        width = data['width']
        height = data['height']
        channels = data['channels']
        
        reconstructed_img = np.zeros((height, width, channels), dtype=float)
        
        for c in range(channels):
            q_L = data['quantizers'][c]['L']
            q_H = data['quantizers'][c]['H']
            streams = data['stream'][c]
            
            L_indices = streams['L_stream']
            H_indices = streams['H_stream']
            
            H_recon = q_H.dequantize(H_indices) # dekodowanie H (wprost)
            
            # dekodowanie L (DPCM odwrotne)
            L_recon = np.zeros_like(H_recon)
            previous_val = L_indices[0]
            L_recon[0] = previous_val
            
            for i, idx in enumerate(L_indices[1:], start=1):
                diff = q_L.dequantize(idx)
                val = previous_val + diff
                L_recon[i] = val
                previous_val = val
            
            flat_recon = self._merge_bands(L_recon, H_recon) # scalanie pasm
            
            flat_recon = np.clip(flat_recon, 0, 255)
            
            reconstructed_img[:, :, c] = flat_recon.reshape((height, width))
            
        orig_width = data.get('orig_width', width) 
        
        if orig_width != width:
            print(f"Przycinanie obrazu do oryginalnej szerokości: {orig_width}")
            reconstructed_img = reconstructed_img[:, :orig_width, :]

        final_img = Image.fromarray(reconstructed_img.astype('uint8'))
        final_img.save(output_path)
        print(f"Zapisano odkodowany obraz: {output_path}")

def calculate_metrics(original_path, decoded_path):
    print("\n--- ANALIZA BŁĘDÓW ---")
    orig = np.array(Image.open(original_path)).astype(float)
    deco = np.array(Image.open(decoded_path)).astype(float)
    
    h, w, c = orig.shape
    total_pixels = h * w
    
    total_mse = 0
    
    print(f"{'Kanał':<10} | {'MSE':<10} | {'SNR (dB)':<10}")
    print("-" * 36)
    
    for i, color in enumerate(['R', 'G', 'B']):
        diff = orig[:,:,i] - deco[:,:,i]
        mse = np.mean(diff ** 2)
        
        signal_power = np.sum(orig[:,:,i] ** 2)
        noise_power = np.sum(diff ** 2)
        
        if noise_power == 0:
            snr = float('inf')
        else:
            snr = 10 * np.log10(signal_power / noise_power)
            
        print(f"{color:<10} | {mse:<10.4f} | {snr:<10.4f}")
        total_mse += mse
        
    avg_mse = total_mse / 3
    
    # całkowity SNR
    total_signal = np.sum(orig ** 2)
    total_noise = np.sum((orig - deco) ** 2)
    if total_noise == 0:
        total_snr = float('inf')
    else:
        total_snr = 10 * np.log10(total_signal / total_noise)
        
    print("-" * 36)
    print(f"Sredni MSE: {avg_mse:.4f}")
    print(f"Sredni SNR: {total_snr:.4f} dB")


if __name__ == "__main__":
    INPUT_FILE = "../testy4/example0.tga"
    COMPRESSED_FILE = "image.bin"
    DECODED_FILE = "decoded.tga"
    BITS_K = 3

    codec = ImageCodec(k_bits=BITS_K)
    codec.encode_image(INPUT_FILE, COMPRESSED_FILE)
    
    codec.decode_image(COMPRESSED_FILE, DECODED_FILE)
    
    calculate_metrics(INPUT_FILE, DECODED_FILE)