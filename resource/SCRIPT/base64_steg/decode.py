import base64

b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def decode_steganography(stegb64_list):
    bin_str = ''
    for line in stegb64_list:
        stegb64 = ''.join(line.split())
        
        # Modify for Python 3 base64 decode and encode
        decoded = base64.b64decode(stegb64)
        print(decoded).encode('utf-8').decode('utf-8')
        rowb64 = base64.b64encode(decoded).decode('utf-8')
        print(rowb64)
        rowb64 = ''.join(rowb64.split())
        
        offset = abs(b64chars.index(stegb64.replace('=', '')[-1]) - b64chars.index(rowb64.replace('=', '')[-1]))
        equalnum = stegb64.count('=')
        
        if equalnum:
            bin_str += bin(offset)[2:].zfill(equalnum * 2)

    return ''.join([chr(int(bin_str[i:i + 8], 2)) for i in range(0, len(bin_str), 8)])
# 逐行读取2.txt文件
stegb64_list = []
with open('1.txt', 'r', encoding='utf-8') as f:
    for line in f:
        stegb64_list.append(line)
decoded_message = decode_steganography(stegb64_list)
print(decoded_message)
