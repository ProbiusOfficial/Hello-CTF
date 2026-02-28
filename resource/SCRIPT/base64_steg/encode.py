import base64

b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def message_to_bin(message):
    return ''.join([bin(ord(c))[2:].zfill(8) for c in message])

def steganography_encrypt(input_file, message):
    bin_message = message_to_bin(message)
    bin_pointer = 0
    result = []

    with open(input_file, 'r') as f:
        for line in f.readlines():
            line = line.strip()

            # If we still have message to hide and this line of base64 contains padding
            if bin_pointer < len(bin_message) and '=' in line:
                padding_count = line.count('=')
                last_char = line[-1-padding_count]
                last_char_index = b64chars.index(last_char)

                # Use up to 2 bits of our message per line with padding
                offset = int(bin_message[bin_pointer:bin_pointer+padding_count*2], 2)
                bin_pointer += padding_count * 2

                # Modify the last character by the offset
                new_last_char = b64chars[(last_char_index + offset) % 64]
                line = line[:-1-padding_count] + new_last_char + '=' * padding_count

            result.append(line)

    return '\n'.join(result)

# Demo:
input_file = '1.txt'
message = "ILOVEYOU"
encrypted_b64 = steganography_encrypt(input_file, message)
print(encrypted_b64)
