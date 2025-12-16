def elias_omega_encode(n: int) -> str:
    if n < 1:
        raise ValueError("Elias omega koduje tylko liczby >= 1")

    code = ''
    while n > 1:
        b = bin(n)[2:]
        code = b + code
        n = len(b) - 1
    code = code + '0'
    return code


def encode_with_elias_omega(indices: list[int]) -> str:
    count = len(indices)
    header = elias_omega_encode(count + 1)
    bits = [header]
    for index in indices:
        n = index + 1
        bits.append(elias_omega_encode(n))
    result = ''.join(bits)
    return result


def decode_with_elias_omega(bitstream: str) -> list[int]:
    decoded_indices = []
    pos = 0
    length_stream = len(bitstream)

    n = 1
    while True:
        if pos >= length_stream:
            return []

        if bitstream[pos] == '0':
            pos += 1
            break

        bits_to_read = n + 1
        segment = bitstream[pos: pos + bits_to_read]

        if len(segment) < bits_to_read:
            return []

        n = int(segment, 2)
        pos += bits_to_read

    count = n - 1

    for _ in range(count):
        n = 1
        while True:
            if pos >= length_stream:
                raise ValueError("Nieoczekiwany koniec ciągu bitów.")

            if bitstream[pos] == '0':
                pos += 1
                break

            bits_to_read = n + 1
            segment = bitstream[pos: pos + bits_to_read]

            if len(segment) < bits_to_read:
                raise ValueError(f"Uszkodzony kod. Oczekiwano {bits_to_read} bitów, znaleziono {len(segment)}")

            n = int(segment, 2)
            pos += bits_to_read

        decoded_indices.append(n - 1)

    return decoded_indices


def elias_gamma_encode(n: int) -> str:
    if n < 1:
        raise ValueError("Elias gamma koduje tylko liczby >= 1")

    b = bin(n)[2:]
    L = len(b)
    prefix = '0' * (L - 1)
    return prefix + b


def encode_with_elias_gamma(indices: list[int]) -> str:
    count = len(indices)
    header = elias_gamma_encode(count + 1)
    bitstream = header
    for index in indices:
        n = index + 1
        bitstream += elias_gamma_encode(n)
    return bitstream


def decode_with_elias_gamma(bitstream: str) -> list[int]:
    indices = []
    i = 0
    length_stream = len(bitstream)

    zeros = 0
    while i < length_stream and bitstream[i] == '0':
        zeros += 1
        i += 1

    if i + zeros >= length_stream:
        return []

    L_bin = bitstream[i:i + zeros + 1]
    i += zeros + 1
    L = int(L_bin, 2)

    count = L - 1

    for _ in range(count):
        zeros = 0
        while i < length_stream and bitstream[i] == '0':
            zeros += 1
            i += 1

        if i + zeros >= length_stream:
            raise ValueError("Nieoczekiwany koniec ciągu bitów.")

        b = bitstream[i:i + zeros + 1]
        i += zeros + 1
        n = int(b, 2)
        indices.append(n - 1)

    return indices


def elias_delta_encode(n: int) -> str:
    if n < 1:
        raise ValueError("Elias delta koduje tylko liczby >= 1")

    b = bin(n)[2:]
    L = len(b)
    gamma_of_L = elias_gamma_encode(L)
    return gamma_of_L + b[1:]


def encode_with_elias_delta(indices: list[int]) -> str:
    count = len(indices)
    header = elias_delta_encode(count + 1)
    bitstream = header
    for index in indices:
        n = index + 1
        bitstream += elias_delta_encode(n)
    return bitstream


def decode_with_elias_delta(bitstream: str) -> list[int]:
    indices = []
    i = 0
    length_stream = len(bitstream)

    zeros = 0
    while i < length_stream and bitstream[i] == '0':
        zeros += 1
        i += 1

    if i + zeros >= length_stream:
        return []

    L_bin = bitstream[i:i + zeros + 1]
    i += zeros + 1
    L = int(L_bin, 2)

    if i + (L - 1) >= length_stream:
        return []

    n_bin = '1' + bitstream[i:i + (L - 1)]
    i += L - 1
    L_count = int(n_bin, 2)
    count = L_count - 1

    for _ in range(count):
        zeros = 0
        while i < length_stream and bitstream[i] == '0':
            zeros += 1
            i += 1

        if i + zeros >= length_stream:
            raise ValueError("Nieoczekiwany koniec ciągu bitów.")

        L_bin = bitstream[i:i + zeros + 1]
        i += zeros + 1
        L = int(L_bin, 2)

        if i + (L - 1) > length_stream:
            raise ValueError("Nieoczekiwany koniec ciągu bitów.")

        n_bin = '1' + bitstream[i:i + (L - 1)]
        i += L - 1
        n = int(n_bin, 2)
        indices.append(n - 1)

    return indices


def fibonacci_numbers_upto(n):
    fibs = [1, 2]
    while fibs[-1] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    if fibs[-1] > n:
        fibs.pop()
    return fibs


def fibonacci_encode(n):
    if n < 1:
        raise ValueError("Fibonacci wymaga n >= 1")

    fibs = fibonacci_numbers_upto(n)
    code = []
    for f in reversed(fibs):
        if f <= n:
            code.append('1')
            n -= f
        else:
            code.append('0')
    code.append('1')
    return ''.join(code)


def encode_with_fibonacci(indices: list[int]) -> str:
    count = len(indices)
    header = fibonacci_encode(count + 1)
    bitstream = header
    for index in indices:
        bitstream += fibonacci_encode(index + 1)
    return bitstream






