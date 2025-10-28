import argparse
import math

def calc_probability(codes_count):
    total = sum(codes_count.values())
    bytes_prob = {byte: count / total for byte, count in codes_count.items()}
    return bytes_prob

def calc_information(bytes_prob):
    bytes_info = {byte: -math.log2(prob) for byte, prob in bytes_prob.items()}
    return bytes_info

def calc_entropy(bytes_prob, bytes_info):
    entropy = 0.0
    for byte in bytes_prob:
        entropy += bytes_prob[byte] * bytes_info[byte]
    return entropy

def calc_conditional_entropy(codes_follow, probs):
    cond_entropy = 0.0
    for prev_byte, follow_dict in codes_follow.items():
        partial_entropy = 0.0
        total_follow = sum(follow_dict.values())
        for byte, count in follow_dict.items():
            prob_y_x = count / total_follow
            info_y_x = -math.log2(prob_y_x)
            partial_entropy += prob_y_x * info_y_x
        cond_entropy += probs.get(prev_byte, 0) * partial_entropy
    return cond_entropy


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file")
    args = parser.parse_args()

    codes_count = {}
    codes_follow = {}

    with open(args.path, 'rb') as f:
        prev = b'\x00'
        for byte in iter(lambda: f.read(1), b''):
            if byte not in codes_count:
                codes_count[byte] = 0
            codes_count[byte] += 1

            if prev not in codes_follow:
                codes_follow[prev] = {}

            if byte not in codes_follow[prev]:
                codes_follow[prev][byte] = 0
            codes_follow[prev][byte] += 1

            prev = byte

    output_file = "output.txt"


    with open(output_file, "w") as f:
        f.write("Byte Frequencies:\n")
        for byte, count in sorted(codes_count.items(), key=lambda item: item[1], reverse=True):
            f.write(f"Byte: {byte.hex()} Count: {count}\n")

        f.write("\nByte Following Frequencies:\n")
        for prev_byte, follow_dict in codes_follow.items():
            f.write(f"\nAfter byte {prev_byte.hex()}:\n")
            for byte, count in sorted(follow_dict.items(), key=lambda item: item[1], reverse=True):
                f.write(f"    Byte: {byte.hex()} Count: {count}\n")

    print(f"Analysis complete. Results written to {output_file}")

    bytes_prob = calc_probability(codes_count)
    bytes_info = calc_information(bytes_prob)
    entropy = calc_entropy(bytes_prob, bytes_info)
    cond_entropy = calc_conditional_entropy(codes_follow, bytes_prob)

    print(f"Entropy: {entropy:.4f}")
    print(f"Conditional Entropy: {cond_entropy:.4f}")