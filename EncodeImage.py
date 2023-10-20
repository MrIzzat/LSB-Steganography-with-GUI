import numpy as np  # Manipulate Arrays
import cv2
import os
from PIL import Image
import random
from GenerateSignature import generateSignature

class EncodeImageClass:
    progress = 0
    finished = False

    def EncodeImageMethod(self, coverImagePath, messageFilePath, outputImageDestination):

        self.progress = 0
        self.finished = False

        # methods used


        def IntegerToBinaryString(number):
            return '{0:08b}'.format(number)

        def BinaryStringToInteger(BinaryString):
            return int(BinaryString, 2)

        # Choose photo

        image = cv2.imread(coverImagePath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        imageSize = len(image) * len(image[0]) * len(image[0][0])

        maxMessageSize = int(imageSize / 8)

        print("The maximum image size: " + str(maxMessageSize))

        # Choose message to hide

        with open(messageFilePath) as f:
            messageContent = f.read()

        #Remove restricted character ( | ) from message

        messageContent = messageContent.replace('|', '')

        #Prepare content for hiding

        messageContentSize = len(messageContent)

        messageFileName = os.path.basename(f.name)
        messageSignature = generateSignature(messageContent)

        messageToHide = messageFileName + "|" + str(messageContentSize) +"|"+messageSignature+"|"+ messageContent

        self.progress=10
        # See if the image will fit inside the photo

        if len(messageToHide) > maxMessageSize - 1:
            print("The message is too big to hide in this photo.")
            return

            # Hide the message
        self.progress = 15
        # Convert message to binary ascii

        messageToAscii = []

        for letter in messageToHide:
            messageToAscii.extend(ord(num) for num in letter)

        def IntegerToBinaryString(number):
            return '{0:08b}'.format(number)

        messageToAsciiBinary = []

        for num in messageToAscii:
            messageToAsciiBinary.append(IntegerToBinaryString(num))

        messageToAsciiBinarySingleList = "".join(messageToAsciiBinary)


        #Sequence to hide the message in generator
        random.seed(4444)

        randomRows = random.sample(range(len(image)), len(image))
        randomColumns = random.sample(range(len(image[0])), len(image[0]))



        self.progress = 40
        # Convert Cover Image to Binary

        CoverImageBinary = []

        i = 0

        for row in randomRows:
            BinaryRow = []
            if (i > len(messageToAsciiBinarySingleList)):
                break
            for column in randomColumns:
                BinaryColumn = []

                for color in range(len(image[row][column])):
                    BinaryColor = IntegerToBinaryString(image[row][column][color])
                    BinaryColumn.append(BinaryColor)
                    i += 1
                BinaryRow.append(BinaryColumn)
            CoverImageBinary.append(BinaryRow)


        self.progress = 60
        # Encode the Message into the Cover Image *both are in binary*

        i = 0

        for row in range(len(CoverImageBinary)):
            for column in range(len(CoverImageBinary[row])):
                for color in range(len(CoverImageBinary[row][column])):
                    if (i == len(messageToAsciiBinarySingleList)):
                        break
                    if (CoverImageBinary[row][column][color][-1] != messageToAsciiBinarySingleList[i]):
                        # print(i)
                        CoverImageBinary[row][column][color] = CoverImageBinary[row][column][color][0:-1] + \
                                                               messageToAsciiBinarySingleList[i]
                    i += 1
            else:
                continue

        self.progress = 80
        # Convert the cover pixel values back to integer to store as a new picture

        i = 0
        CoverImageBackToInteger = []

        for row in range(len(CoverImageBinary)):
            IntegerRow = []
            if (i == len(messageToAsciiBinarySingleList)):
                break
            for column in range(len(CoverImageBinary[row])):
                IntegerColumn = []

                for color in range(len(CoverImageBinary[row][column])):
                    if (i == len(messageToAsciiBinarySingleList)):
                        break
                    IntegerColor = BinaryStringToInteger(CoverImageBinary[row][column][color])
                    IntegerColumn.append(IntegerColor)

                IntegerRow.append(IntegerColumn)
            CoverImageBackToInteger.append(IntegerRow)

        #Reorder the columns to the usual order

        coverImageWithHiddenMessageAsNumpy = np.array(CoverImageBackToInteger)

        for row in range(len(coverImageWithHiddenMessageAsNumpy)):
            for column in range(len(coverImageWithHiddenMessageAsNumpy[row])):
                image[randomRows[row]][randomColumns[column]] = coverImageWithHiddenMessageAsNumpy[row][column]

        # Save the image



        im = Image.fromarray(image.astype('uint8')).convert('RGB')

        im.save(outputImageDestination)

        #im.save(outputImageDestination + "/HiddenPictureTEST.png")

        self.progress = 100
        self.finished = True
