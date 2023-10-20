import cv2
import random
import collections as ct
from GenerateSignature import generateSignature


class DecodeImageClass:
    progress = 0
    finished = False
    success=False
    reason="Success"

    def DecodeImageMethod(self, CoverImage, OutputFile):
        # methods used

        def IntegerToBinaryString(number):
            return '{0:08b}'.format(number)

        def BinaryStringToInteger(BinaryString):
            return int(BinaryString, 2)

            # *Extract the message from the image**

        # Read image
        StegoImage = cv2.imread(CoverImage)
        StegoImage = cv2.cvtColor(StegoImage, cv2.COLOR_BGR2RGB)

        # Sequence to hide the message in generator
        random.seed(4444)

        randomRows = random.sample(range(len(StegoImage)), len(StegoImage))
        randomColumns = random.sample(range(len(StegoImage[0])), len(StegoImage[0]))

        # Extract File Name and File Size

        # First, the first 400 bits will be extracted
        # 400 bits should be enough to represent both the file name and file size

        StegoImageBinaryList = []

        i = 0
        for row in randomRows:
            BinaryRow = []
            if i > 400:  # For header
                break
            for column in randomColumns:
                BinaryColumn = []

                for color in range(len(StegoImage[row][column])):
                    BinaryColor = IntegerToBinaryString(StegoImage[row][column][color])
                    BinaryColumn.append(BinaryColor)
                    i += 1
                BinaryRow.append(BinaryColumn)
            StegoImageBinaryList.append(BinaryRow)

        self.progress = 10

        HiddenMessageInformationBinary = []

        HiddenMessageInformationLength = 400  # For header data

        i = 0
        for row in range(len(StegoImageBinaryList)):
            for column in range(len(StegoImageBinaryList[row])):
                for color in range(len(StegoImageBinaryList[row][column])):
                    if (i == HiddenMessageInformationLength):
                        break
                    HiddenMessageInformationBinary.append(StegoImageBinaryList[row][column][color][-1])
                    i += 1
            else:
                continue

        self.progress = 25

        # Convert Binary to Binary Strings
        HiddenMessageInformationBinaryList = []
        BinaryString = ""

        i = 0
        for bit in HiddenMessageInformationBinary:

            BinaryString += bit
            i += 1

            if i > 7:
                HiddenMessageInformationBinaryList.append(BinaryString)
                BinaryString = ""
                i = 0

        self.progress = 30
        # Convert BinaryLists to ascii

        HiddenMessageInformationAscii = []

        for BinaryString in HiddenMessageInformationBinaryList:
            HiddenMessageInformationAscii.append(BinaryStringToInteger(BinaryString))

        # Hidden message Information from ASCII to Characters
        HiddenMessageInformation = ""

        for letter in HiddenMessageInformationAscii:
            HiddenMessageInformation += chr(letter)

        # Store the hidden message information

        hiddenMessageInformationSplit = HiddenMessageInformation.split('|')
        if len(hiddenMessageInformationSplit)!=4:
            self.finished=True
            self.success=False
            self.reason="No Hidden Data in this image"
            self.progress=100
            return

        hiddenMessageInformationSize = (len(hiddenMessageInformationSplit[0]) + len(
            hiddenMessageInformationSplit[1]) +len(hiddenMessageInformationSplit[2])+ 3) * 8

        fileName = hiddenMessageInformationSplit[0]
        fileSize = int(hiddenMessageInformationSplit[1])
        fileSignature = hiddenMessageInformationSplit[2]

        self.progress = 40
        # Now extract the message

        StegoImageBinaryList = []

        HiddenMessageLength = fileSize * 8

        i = 0
        for row in randomRows:
            BinaryRow = []
            if i > HiddenMessageLength + hiddenMessageInformationSize:
                break
            for column in randomColumns:
                BinaryColumn = []

                for color in range(len(StegoImage[row][column])):
                    BinaryColor = IntegerToBinaryString(StegoImage[row][column][color])
                    BinaryColumn.append(BinaryColor)
                    i += 1
                BinaryRow.append(BinaryColumn)
            StegoImageBinaryList.append(BinaryRow)

        self.progress = 50
        HiddenMessageBinary = []

        HiddenMessageLength = fileSize * 8

        i = 0
        for row in range(len(StegoImageBinaryList)):
            for column in range(len(StegoImageBinaryList[row])):
                for color in range(len(StegoImageBinaryList[row][column])):
                    if i > hiddenMessageInformationSize - 1:
                        if i == HiddenMessageLength + hiddenMessageInformationSize:
                            break
                        HiddenMessageBinary.append(StegoImageBinaryList[row][column][color][-1])

                    i += 1
            else:
                continue

        HiddenMessageBinaryList = []
        BinaryString = ""

        i = 0
        for bit in HiddenMessageBinary:

            BinaryString += bit
            i += 1

            if i > 7:
                HiddenMessageBinaryList.append(BinaryString)
                BinaryString = ""
                i = 0

        self.progress = 60
        HiddenMessageAscii = []

        for BinaryString in HiddenMessageBinaryList:
            HiddenMessageAscii.append(BinaryStringToInteger(BinaryString))

        HiddenMessage = ""

        for letter in HiddenMessageAscii:
            HiddenMessage += chr(letter)

        self.progress = 80
        # Save the image in a new text file

        with open(OutputFile, 'w') as f:
            f.write(HiddenMessage)

        # Check Signatures
        self.progress = 95
        extractedSignature = generateSignature(HiddenMessage)

        if extractedSignature == fileSignature:
            self.success = True
        else:
            self.reason="Text not Extracted Correctly (Signature Error)\nCheck the file to see what was extracted"

        self.progress = 100
        self.finished = True
