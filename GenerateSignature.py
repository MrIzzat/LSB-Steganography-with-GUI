import collections as ct


def generateSignature(message):
    lowerCaseLetters = "abcdefghijklmnopqrstuvwxyz"
    capitalLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    whiteSpace = " "
    puncuation = ",./;!?"
    specialCharacters = "@#$%^&*()_+-=/*<>[]{}~`"

    lowerCaseLettersCounter = sum(v for k, v in ct.Counter(message).items() if k in lowerCaseLetters)
    capitalLettersCounter = sum(v for k, v in ct.Counter(message).items() if k in capitalLetters)
    numbersCounter = sum(v for k, v in ct.Counter(message).items() if k in numbers)
    whiteSpaceCount = sum(v for k, v in ct.Counter(message).items() if k in whiteSpace)
    puncuationCount = sum(v for k, v in ct.Counter(message).items() if k in puncuation)
    specialCharactersCount = sum(v for k, v in ct.Counter(message).items() if k in specialCharacters)

    signatureInteger = lowerCaseLettersCounter + 2 * capitalLettersCounter + 3 * numbersCounter + whiteSpaceCount + 3 * puncuationCount + 4 * specialCharactersCount

    signatureHex = hex(signatureInteger)
    signatureHex = signatureHex[2:]  # remove the 0x from the begining

    return signatureHex