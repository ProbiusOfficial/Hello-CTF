list = {
    "乾": "111", "兑": "011", "离": "101", "震": "001",
    "巽": "110", "坎": "010", "艮": "100", "坤": "000"
}

def decode(encoded_text):
    binary_text = ''.join(list.get(c, "") for c in encoded_text)
    decoded_text = ''.join(chr(int(binary_text[i:i + 10], 2)) for i in range(0, len(binary_text), 10))
    return "LitCTF{" + decoded_text + "}"

decoded_text = "坤乾兑艮兑坎坤坤巽震坤巽震艮兑坎坤震兑乾坤巽坤艮兑震巽坤巽艮坤巽艮艮兑兑艮震兑乾坤乾坤坤兑艮艮坤巽坤坤巽坎坤兑离坎震艮兑坤巽坎艮兑震坤震兑乾坤乾坎坤兑坎坤震艮离坤离乾艮震艮巽震离震坤巽兑艮兑坎坤震巽艮坤离乾艮坎离坤震巽坎坤兑坤艮兑震巽震巽坎坤巽坤艮兑兑坎震巽兑"

decoded_text = decode(decoded_text)
print(decoded_text)
# LitCTF{wh1ch_ag4in_pr0duced_the_3ight_Tr1grams}