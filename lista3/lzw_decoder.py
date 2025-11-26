import argparse
import universal_coding as uc



def decode_lzw(codes: list[int]) -> bytes:
    if not codes:
        return b""

    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    result = bytearray()
    prev_code = codes[0]
    result.extend(dictionary[prev_code])

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = dictionary[prev_code] + dictionary[prev_code][:1]
        else:
            raise ValueError(f"Niepoprawny kod LZW: {code}")

        result.extend(entry)
        dictionary[dict_size] = dictionary[prev_code] + entry[:1]
        dict_size += 1

        prev_code = code

    return bytes(result)


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

    bitstream = ''.join(f'{byte:08b}' for byte in text)

    if args.method == "gamma":
        universal_decoded = uc.decode_with_elias_gamma(bitstream)
    elif args.method == "delta":
        universal_decoded = uc.decode_with_elias_delta(bitstream)
    # elif args.method == "fibonacci":
    #     universal_decoded = uc.decode_with_fibonacci(bitstream)
    else:
        universal_decoded = uc.decode_with_elias_omega(bitstream)

    result = decode_lzw(universal_decoded)

    with open("decoded_output.bin", 'wb') as f:
        f.write(result)
