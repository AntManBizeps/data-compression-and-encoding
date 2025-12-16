import random
import argparse
import struct
import numpy as np

def lgb(pixels, k):

    epsilon = np.array([1,1,1]) * 0.1
    centroids = np.array([np.mean(pixels, axis=0)])

    for i in range(k):
        centroids_new = []
        for centroid in centroids:
            centroids_new.append(centroid + epsilon)
            centroids_new.append(centroid - epsilon)
        centroids = np.array(centroids_new)


        for j in range(10):
            assignments = get_assignments(pixels, centroids)
            centroids = compute_centroids(pixels, assignments, len(centroids))

    final_assignments = get_assignments(pixels, centroids)

    pixels_lgb = centroids[final_assignments]

    return pixels_lgb.astype(np.uint8)


def compute_centroids(pixels, assignments, n):
    centroids = []
    for i in range(n):
        assigned = np.array(pixels[assignments == i])
        if len(assigned) > 0:
            centroids.append(np.mean(assigned, axis=0))
        else:
            random_idx = random.randint(0, len(pixels) - 1)
            centroids.append(pixels[random_idx])
    return np.array(centroids)

def get_assignments(pixels, centroids):
    centroids = np.array(centroids) 
    diff = pixels[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    distances = np.sum(np.abs(diff), axis=2)
    return np.argmin(distances, axis=1)

def calculate_mse(original, quantized):
    err = np.sum((original.astype("float") - quantized.astype("float")) ** 2)
    err /= float(original.shape[0])
    return err

def calculate_snr(original, mse):
    signal_power = np.sum(original.astype("float") ** 2) / original.shape[0]
    
    if mse == 0:
        return float('inf')
    
    return 10 * np.log10(signal_power / mse)

def write_tga(filename, image_data, header):
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(image_data.tobytes())

def read_tga(filename):
    with open(filename, 'rb') as f:
        #nagłówek ma 18 bajtów
        header = f.read(18)
        
        # H - unsigned short (2 bajty)
        # B - unsigned char (1 bajt)
        # < - little-endian czyli najmniejznaczący bajt pierwszy
        width = struct.unpack_from('<H', header, 12)[0]
        height = struct.unpack_from('<H', header, 14)[0]
        pixel_depth = struct.unpack_from('<B', header, 16)[0]
        descriptor = struct.unpack_from('<B', header, 17)[0]

        if pixel_depth != 24:
            raise ValueError("This program works only for TGA 24-bit (RGB)")

        data = f.read()
        
        image_data = np.frombuffer(data, dtype=np.uint8)
        
        expected_size = width * height * 3
        image_data = image_data[:expected_size] # obcięcie nadmiaru, jeśli istnieje
        
        image = image_data.reshape((height, width, 3))
            
        return image, header


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("k", help="Number of kolors")
    args = parser.parse_args()


    try:
        image_original, header = read_tga(args.input)

        h, w, d = image_original.shape
        pixels = image_original.reshape(-1, 3)

        quantized = lgb(pixels, int(args.k))

        mse = calculate_mse(pixels, quantized)
        snr = calculate_snr(pixels, mse)

        print(f"MSE: {mse:.4f}")
        print(f"SNR: {snr:.4f} dB")

        image_out = quantized.reshape(h, w, 3)
        
        write_tga(args.output, image_out, header)
        print(f"Saved to {args.output}")
        
    except FileNotFoundError:
        print("No file!")
    except Exception as e:
        print(f"Error: {e}")