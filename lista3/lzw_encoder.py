import argparse
import math
from collections import Counter

import universal_coding as uc

def encode_lzw(data: bytes) -> list[int]:
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(256)}

    w = b""
    result = []

    for byte in data:
        c = bytes([byte])
        wc = w + c

        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    if w:
        result.append(dictionary[w])

    return result

def bits_to_bytes(bitstream: str) -> bytes:
    while len(bitstream) % 8 != 0:
        bitstream += "0"
    b = bytearray()
    for i in range(0, len(bitstream), 8):
        byte = bitstream[i:i+8]
        b.append(int(byte, 2))
    return bytes(b)

def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    H = -sum((count/total) * math.log2(count/total) for count in counts.values())
    return H



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file")
    parser.add_argument(
        "--method",
        choices=["omega", "gamma", "delta", "fibonacci"],
        default="omega",
        help="Universal coding method to use (default: omega)"
    )

    args = parser.parse_args()

    with open(args.path, 'rb') as f:
        text = f.read()

    if len(text) == 0:
        print("File is empty. Exiting.")
        exit()

    lzw_encoded = encode_lzw(text)

    if args.method == "gamma":
        universal_encoded = uc.encode_with_elias_gamma(lzw_encoded)
    elif args.method == "delta":
        universal_encoded = uc.encode_with_elias_delta(lzw_encoded)
    elif args.method == "fibonacci":
        universal_encoded = uc.encode_with_fibonacci(lzw_encoded)
    else:
        universal_encoded = uc.encode_with_elias_omega(lzw_encoded)

    encoded_bytes = bits_to_bytes(universal_encoded)

    print("Długość pliku wejściowego: ", len(text))
    print("Długość kodowanego pliku: ", len(encoded_bytes))
    print("Stopień kompresji: ", len(encoded_bytes) / len(text))
    print("Entropia oryginalnego pliku: ", entropy(text))
    print("Entropia zakodowanego pliku: ", entropy(encoded_bytes))


    with open("encoded_output.lzw", "wb") as f:
        f.write(encoded_bytes)


