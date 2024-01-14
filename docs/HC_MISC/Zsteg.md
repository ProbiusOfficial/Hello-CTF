zsteg: This is a steganography 隐写术tool used for detecting steganographic content in images.
`zsteg -e b1,rgb,lsb,xy 719af25af2ca4707972c6ae57060238e.png > 1.zip`
-e: "extract." When used in the command, it specifies that the zsteg tool should be used for extracting hidden data from the image, rather than just analyzing or displaying information about the steganographic content.
b1: Extracts data hidden in the least significant bit (LSB) of the blue channel.
rgb: Extracts data hidden in the RGB channels.
lsb: Extracts data hidden in the least significant bit of each channel.
xy: Extracts data using various spatial methods.