import numpy as np  # Manipulate Arrays
import cv2
import os
from PIL import Image
import random
from GenerateSignature import generateSignature

class EncodeImageClass:
    progress = 0
    finished = False
    success=False
    reason="Working..."

    def EncodeImageMethod(self, coverImagePath, messageFilePath, outputImageDestination):

        self.progress = 0
        self.finished = False

        # methods used


        # Choose photo

        image = cv2.imread(coverImagePath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        imageSize = len(image) * len(image[0]) * len(image[0][0])

        maxMessageSize = int(imageSize / 8) -50

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
            self.finished=True
            self.progress=100
            self.reason = "The message is too big ot hide in this photo"
            self.success=False
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
        import random
        import math

        random.seed(4444)

        points = random.sample([[x, y] for x in range(len(image)) for y in range(len(image[0]))],
                               math.floor(len(messageToAsciiBinarySingleList) / 3) + 1)



        self.progress = 40

        # Encode the Message into the Cover Image *both are in binary*

        i = 0

        for point in points:
            for color in range(len(image[point[0]][point[1]])):
                if i == len(messageToAsciiBinarySingleList):
                    break

                if messageToAsciiBinarySingleList[i] == '1':
                    image[point[0]][point[1]][color] |= 1
                else:
                    image[point[0]][point[1]][color] &= ~1

                i += 1
            else:
                continue

        self.progress = 80


        # Save the image

        im = Image.fromarray(image.astype('uint8')).convert('RGB')

        im.save(outputImageDestination)

        #im.save(outputImageDestination + "/HiddenPictureTEST.png")

        self.progress = 100
        self.finished = True
        self.success = True
