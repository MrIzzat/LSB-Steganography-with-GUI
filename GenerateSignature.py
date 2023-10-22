import collections as ct


def generateSignature(message):
    signature = 0
    for letter in message:
        signature += ord(letter) ** 2

    signatureHex = hex(signature)
    signatureHex = signatureHex[2:]

    return signatureHex
