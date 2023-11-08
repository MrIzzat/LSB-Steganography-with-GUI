def generateSignature(message):

    signature = 0
    for i in range(len(message)):
        signature += (ord(message[i]) + i) ** 2  # Now signature takes the position of the letter into account

    signature+=len(message)
    signatureHex = hex(signature)
    signatureHex = signatureHex[2:]

    return signatureHex
