import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import Counter
from lista1.list_one import calc_probability, calc_information, calc_entropy
import argparse
from node import Node
import heapq
from bitarray import bitarray
import pickle

def count_elements(text):
    return Counter(text)

def build_huffman_tree(codes_count, probabilities):

    heap = [Node(symbol, freq) for symbol, freq in probabilities.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent_node = Node(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, parent_node)

    return heap[0]

def create_codes(node, prefix="", codebook={}):
    if node is not None:
        if node.symbol is not None:
            codebook[node.symbol] = prefix
        create_codes(node.left, prefix + "0", codebook)
        create_codes(node.right, prefix + "1", codebook)
    return codebook

def calculate_average_code_length(codes, probabilities):
    avg_length = 0.0
    for symbol, code in codes.items():
        avg_length += probabilities[symbol] * len(code)
    return avg_length

def perform_huffman_coding(file_path):
    text = b""
    with open(file_path, 'rb') as f:
        text = f.read()
    
    if len(text) == 0:
        print("File is empty. Exiting.")
        return

    codes_counts = count_elements(text)
    probabilities = calc_probability(codes_counts)
    root = build_huffman_tree(codes_counts, probabilities)
    huffman_codes = create_codes(root)
    if len(huffman_codes) == 1:
        only_symbol = next(iter(huffman_codes))
        huffman_codes[only_symbol] = '0'
    coded_text = bitarray()

    for byte in text:
        coded_text.extend(huffman_codes[byte])

    with open("compressed_file.bin", 'wb') as f:
        pickle.dump(huffman_codes, f)
        coded_text.tofile(f)

    entropy = calc_entropy(
        probabilities,
        calc_information(probabilities)
    )

    avg_code_length = calculate_average_code_length(huffman_codes, probabilities)

    print("Entropy:", entropy)
    print("Average code length:", avg_code_length)
    print("Compression ratio:", 8 / avg_code_length)





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file")
    args = parser.parse_args()

    perform_huffman_coding(args.path)



