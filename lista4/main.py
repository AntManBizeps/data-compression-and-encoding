import struct
import numpy as np
import matplotlib.pyplot as plt
import argparse
import numpy as np

# X - aktualny pixel (x,y)
# A - pixel po lewej (x-1,y)
# B - pixel powyżej (x,y-1)
# C - pixel po przekątnej po lewej i powyżej (x-1,y-1)

def read_tga(filename) -> np.ndarray:
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
        
        print(f"Dimensions: {width}x{height}x{pixel_depth} bits")


        if pixel_depth != 24:
            raise ValueError("This program works only for TGA 24-bit (RGB)")

        data = f.read()
        
        image_data = np.frombuffer(data, dtype=np.uint8)
        
        expected_size = width * height * 3
        image_data = image_data[:expected_size] # obcięcie nadmiaru, jeśli istnieje
        
        image = image_data.reshape((height, width, 3))

        if not (descriptor & 0x20):  # sprawdzamy 5 bit deskryptora robiąc and z 0x20 = 00100000
            image = np.flipud(image) 
            print("Image flipped vertically")
            
        return image

def calculate_entropy(data_array):

    flat_data = data_array.flatten()

    counts, _ = np.histogram(flat_data, bins=range(257))
    
    total_samples = flat_data.size
    probs = counts[counts > 0] / total_samples

    entropy = -np.sum(probs * np.log2(probs))
    
    return entropy
    
    # estimated X = A
def calculate_jpeg_1(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 
    
    A = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    
    E = (X - A) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # extimated X = B
def calculate_jpeg_2(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    B = np.zeros_like(X) 
    
    B[1:, :, :] = X[:-1, :, :]
    
    E = (X -  B) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = C
def calculate_jpeg_3(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    C = np.zeros_like(X) 
    
    C[1:, 1:, :] = X[:-1, :-1, :]
    
    E = (X - C) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = A + B - C
def calculate_jpeg_4(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    A = np.zeros_like(X) 
    B = np.zeros_like(X) 
    C = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    B[1:, :, :] = X[:-1, :, :]
    C[1:, 1:, :] = X[:-1, :-1, :]
    
    E = (X - (A + B - C)) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = A + (B - C)/2
def calculate_jpeg_5(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    A = np.zeros_like(X) 
    B = np.zeros_like(X) 
    C = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    B[1:, :, :] = X[:-1, :, :]
    C[1:, 1:, :] = X[:-1, :-1, :]
    
    E = (X - (A + (B - C)//2)) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = B + (A - C)/2
def calculate_jpeg_6(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    A = np.zeros_like(X) 
    B = np.zeros_like(X) 
    C = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    B[1:, :, :] = X[:-1, :, :]
    C[1:, 1:, :] = X[:-1, :-1, :]
    
    E = (X - (B + (A - C)//2)) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = (A + B)/2
def calculate_jpeg_7(image: np.ndarray) -> tuple[float, float, float, float]:
    
    X = image.astype(np.int16) 

    A = np.zeros_like(X) 
    B = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    B[1:, :, :] = X[:-1, :, :]
    
    E = (X - (A + B)//2) % 256
    
    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

    # estimated X = {min(A,B) if C >= max(A,B)
    #                max(A,B) if C <= min(A,B)
    #                A + B - C indziej}
def calculate_jpeg_new(image: np.ndarray) -> tuple[float, float, float, float]:
    X = image.astype(np.int16) 

    A = np.zeros_like(X) 
    B = np.zeros_like(X) 
    C = np.zeros_like(X) 
    
    A[:, 1:, :] = X[:, :-1, :]
    B[1:, :, :] = X[:-1, :, :]
    C[1:, 1:, :] = X[:-1, :-1, :]

    E = np.zeros_like(X)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            for k in range(X.shape[2]):
                if C[i,j,k] >= max(A[i,j,k], B[i,j,k]):
                    predicted = min(A[i,j,k], B[i,j,k])
                elif C[i,j,k] <= min(A[i,j,k], B[i,j,k]):
                    predicted = max(A[i,j,k], B[i,j,k])
                else:
                    predicted = A[i,j,k] + B[i,j,k] - C[i,j,k]
                
                E[i,j,k] = (X[i,j,k] - predicted) % 256

    entropy_r = calculate_entropy(E[:, :, 0])
    entropy_g = calculate_entropy(E[:, :, 1])
    entropy_b = calculate_entropy(E[:, :, 2])
    
    entropy_total = calculate_entropy(E)
    
    return entropy_total, entropy_r, entropy_g, entropy_b

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File path")
    args = parser.parse_args()


    try:
        img_array = read_tga(args.file)
        image_entropies = {}

        image_entropy = calculate_entropy(img_array)
        r_entropy = calculate_entropy(img_array[:,:,0])
        g_entropy = calculate_entropy(img_array[:,:,1])
        b_entropy = calculate_entropy(img_array[:,:,2])

        image_entropies['image'] = [image_entropy, r_entropy, g_entropy, b_entropy]

        print("\n---------Input Image---------")
        print(f'Image entropy: {image_entropy}')
        print(f'R channel entropy: {r_entropy}')
        print(f'G channel entropy: {g_entropy}')
        print(f'B channel entropy: {b_entropy}')

        jpeg1_e, jpeg1_r, jpeg1_g, jpeg1_b = calculate_jpeg_1(img_array)
        image_entropies['jpeg1'] = [jpeg1_e, jpeg1_r, jpeg1_g, jpeg1_b]

        print("\n---------JPEG-LS Prediction 1---------")
        print(f'Image entropy: {jpeg1_e}')
        print(f'R channel entropy: {jpeg1_r}')
        print(f'G channel entropy: {jpeg1_g}')
        print(f'B channel entropy: {jpeg1_b}')

        jpeg2_e, jpeg2_r, jpeg2_g, jpeg2_b = calculate_jpeg_2(img_array)
        image_entropies['jpeg2'] = [jpeg2_e, jpeg2_r, jpeg2_g, jpeg2_b]

        print("\n---------JPEG-LS Prediction 2---------")
        print(f'Image entropy: {jpeg2_e}')
        print(f'R channel entropy: {jpeg2_r}')
        print(f'G channel entropy: {jpeg2_g}') 
        print(f'B channel entropy: {jpeg2_b}')

        jpeg3_e, jpeg3_r, jpeg3_g, jpeg3_b = calculate_jpeg_3(img_array)
        image_entropies['jpeg3'] = [jpeg3_e, jpeg3_r, jpeg3_g, jpeg3_b]

        print("\n---------JPEG-LS Prediction 3---------")
        print(f'Image entropy: {jpeg3_e}')
        print(f'R channel entropy: {jpeg3_r}')
        print(f'G channel entropy: {jpeg3_g}')
        print(f'B channel entropy: {jpeg3_b}')

        jpeg4_e, jpeg4_r, jpeg4_g, jpeg4_b = calculate_jpeg_4(img_array)
        image_entropies['jpeg4'] = [jpeg4_e, jpeg4_r, jpeg4_g, jpeg4_b]

        print("\n---------JPEG-LS Prediction 4---------")
        print(f'Image entropy: {jpeg4_e}')
        print(f'R channel entropy: {jpeg4_r}')
        print(f'G channel entropy: {jpeg4_g}')
        print(f'B channel entropy: {jpeg4_b}')

        jpeg5_e, jpeg5_r, jpeg5_g, jpeg5_b = calculate_jpeg_5(img_array)
        image_entropies['jpeg5'] = [jpeg5_e, jpeg5_r, jpeg5_g, jpeg5_b]

        print("\n---------JPEG-LS Prediction 5---------")
        print(f'Image entropy: {jpeg5_e}')
        print(f'R channel entropy: {jpeg5_r}')
        print(f'G channel entropy: {jpeg5_g}')
        print(f'B channel entropy: {jpeg5_b}')

        jpeg6_e, jpeg6_r, jpeg6_g, jpeg6_b = calculate_jpeg_6(img_array)
        image_entropies['jpeg6'] = [jpeg6_e, jpeg6_r, jpeg6_g, jpeg6_b]

        print("\n---------JPEG-LS Prediction 6---------")
        print(f'Image entropy: {jpeg6_e}')
        print(f'R channel entropy: {jpeg6_r}')
        print(f'G channel entropy: {jpeg6_g}')
        print(f'B channel entropy: {jpeg6_b}')

        jpeg7_e, jpeg7_r, jpeg7_g, jpeg7_b = calculate_jpeg_7(img_array)
        image_entropies['jpeg7'] = [jpeg7_e, jpeg7_r, jpeg7_g, jpeg7_b]

        print("\n---------JPEG-LS Prediction 7---------")
        print(f'Image entropy: {jpeg7_e}')
        print(f'R channel entropy: {jpeg7_r}') 
        print(f'G channel entropy: {jpeg7_g}')
        print(f'B channel entropy: {jpeg7_b}')

        jpegnew_e, jpegnew_r, jpegnew_g, jpegnew_b = calculate_jpeg_new(img_array)
        image_entropies['jpegnew'] = [jpegnew_e, jpegnew_r, jpegnew_g, jpegnew_b]

        print("\n---------JPEG-LS New Prediction---------")
        print(f'Image entropy: {jpegnew_e}')
        print(f'R channel entropy: {jpegnew_r}') 
        print(f'G channel entropy: {jpegnew_g}')
        print(f'B channel entropy: {jpegnew_b}')   

        best_results = {
            0: {'predictor': None, 'entropy': float('inf')},
            1: {'predictor': None, 'entropy': float('inf')},
            2: {'predictor': None, 'entropy': float('inf')},
            3: {'predictor': None, 'entropy': float('inf')}
        }

        for predictor_name, entropy_list in image_entropies.items():
            for index in range(4):
                if entropy_list[index] < best_results[index]['entropy']:
                    best_results[index]['entropy'] = entropy_list[index]
                    best_results[index]['predictor'] = predictor_name 

        print("\n---------Summary---------")
        print(f'Best overall entropy: predictor = {best_results[0]["predictor"]}, entropy = {best_results[0]["entropy"]}')
        print(f'Best entropy for channel R: predictor = {best_results[1]["predictor"]}, entropy = {best_results[1]["entropy"]}')
        print(f'Best entropy for channel G: predictor = {best_results[2]["predictor"]}, entropy = {best_results[2]["entropy"]}')
        print(f'Best entropy for channel B: predictor = {best_results[3]["predictor"]}, entropy = {best_results[3]["entropy"]}')
        
    except FileNotFoundError:
        print("No file!")
    except Exception as e:
        print(f"Error: {e}")