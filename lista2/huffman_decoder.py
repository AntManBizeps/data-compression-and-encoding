import pickle
from bitarray import bitarray
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file")
    args = parser.parse_args()

    with open(args.path, 'rb') as f:
        huffman_codes = pickle.load(f)
        coded_text = bitarray()
        coded_text.fromfile(f)

    if len(coded_text) == 0:
        print("File is empty. Nothing to decode.")
        exit()

    inverse_codes = {v: k for k, v in huffman_codes.items()}

    decoded_bytes = bytearray()
    buffer = ""

    for bit in coded_text.to01():
        buffer += bit
        if buffer in inverse_codes:
            decoded_bytes.append(inverse_codes[buffer])
            buffer = ""

    with open("decoded_output.bin", 'wb') as f:
        f.write(decoded_bytes)
    print("Decoding completed. Output written to decoded_output.bin")