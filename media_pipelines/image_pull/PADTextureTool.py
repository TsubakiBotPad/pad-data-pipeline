################################################################################
#
# This script extracts texture images from the binary data of the popular
# iOS & Android game "Puzzle & Dragons".
#
# It was written by Cody Watts.
#
# The latest source code is always available on GitHub:
# https://github.com/codywatts/Puzzle-and-Dragons-Texture-Tool
#
# You can also read more about this project on my personal website:
# http://www.codywatts.com/projects/puzzle-and-dragons-texture-tool
#
################################################################################

# @formatter:off

from __future__ import (absolute_import, division, print_function)

import argparse
import io
import itertools
import os
from pathlib import Path
import re
import struct
import zipfile
import zlib

import png


# This class represents a packed pixel encoding.
class Encoding(object):
    def __init__(self, channels=None):
        super(Encoding, self).__init__()
        self.channels = channels
        if self.channels:
            self.strideInBits = sum(self.channels)
            self.hasAlpha = (len(self.channels) == 4)
            self.isGreyscale = (len(self.channels) == 1)
        else:
            self.strideInBits = None
            self.hasAlpha = None
            self.isGreyscale = None


R8G8B8A8 = Encoding([8, 8, 8, 8])
R5G6B5 = Encoding([5, 6, 5])
R4G4B4A4 = Encoding([4, 4, 4, 4])
R5G5B5A1 = Encoding([5, 5, 5, 1])
L8 = Encoding([8])
RAW = Encoding()
PVRTC4BPP = Encoding([4])
PVRTC2BPP = Encoding([2])

# This class represents an instance of a texture.


class Texture(object):
    def __init__(self, width, height, name, buffer, encoding):
        super(Texture, self).__init__()
        self.width = width
        self.height = height
        self.name = name
        self.buffer = buffer
        self.encoding = encoding
        self.packedPixels = None

        if self.encoding.strideInBits:
            if self.encoding.strideInBits == 32:
                self.packedPixels = struct.unpack(
                    ">{}L".format(self.width * self.height), self.buffer)
            elif self.encoding.strideInBits == 16:
                self.packedPixels = struct.unpack(
                    "<{}H".format(self.width * self.height), self.buffer)
            elif self.encoding.strideInBits == 8:
                self.packedPixels = struct.unpack(
                    "<{}B".format(self.width * self.height), self.buffer)
            elif self.encoding.strideInBits < 8:
                intermediatePackedPixels = struct.unpack("<{}B".format(
                    (self.width * self.height * self.encoding.strideInBits) // 8), self.buffer)
                self.packedPixels = []
                bitMask = ((2 ** self.encoding.strideInBits) - 1)
                pixelsPerByte = (8 // self.encoding.strideInBits)
                for byte in intermediatePackedPixels:
                    for i in range(pixelsPerByte):
                        self.packedPixels.append(
                            (byte >> (self.encoding.strideInBits * (pixelsPerByte - i - 1))) & bitMask)

# This class writes Texture objects to disk.


class TextureWriter(object):
    # Build the bit-depth conversion table
    bitDepthConversionTable = [[[0 for i in range(256)] for j in range(9)] for k in range(9)]
    for currentBitDepth in range(1, 9):
        for newBitDepth in range(currentBitDepth, 9):
            for value in range(2 ** currentBitDepth):
                bitDepthConversionTable[currentBitDepth][newBitDepth][value] = int(
                    round(value * (float((2 ** newBitDepth) - 1) / float((2 ** currentBitDepth) - 1))))

    penultimateChunk = struct.pack("<H32L", 0x0, 0x45747600, 0x6F537458, 0x61777466, 0x45006572, 0x726F7078, 0x20646574, 0x6E697375, 0x68742067, 0x75502065, 0x656C7A7A, 0x44202620, 0x6F676172, 0x5420736E, 0x75747865,
                                   0x54206572, 0x206C6F6F, 0x77777728, 0x646F632E, 0x74617779, 0x632E7374, 0x702F6D6F, 0x656A6F72, 0x2F737463, 0x7A7A7570, 0x612D656C, 0x642D646E, 0x6F676172, 0x742D736E, 0x75747865, 0x742D6572, 0x296C6F6F, 0x3391286F)

    trimmingEnabled = True
    blackeningEnabled = True

    @classmethod
    def enableTrimming(cls, trimmingEnabled):
        cls.trimmingEnabled = trimmingEnabled

    @classmethod
    def enableOptimization(cls, blackeningEnabled):
        cls.blackeningEnabled = blackeningEnabled

    @classmethod
    def trimTransparentEdges(cls, flatPixelArray, width, height, channels):
        channelsPerPixel = len(channels)

        # Isolate the image's alpha channel
        alphaChannel = flatPixelArray[(channelsPerPixel - 1)::channelsPerPixel]

        getRow = (lambda rowIndex, pixelArray,
                  rowStride: pixelArray[rowIndex * rowStride:(rowIndex + 1) * rowStride])
        getColumn = (lambda columnIndex, pixelArray, rowStride: pixelArray[columnIndex::rowStride])
        isTransparent = (lambda rowOrColumn: sum(rowOrColumn) == 0)

        def findTrimEdges(minIndex, maxIndex, getSlice):
            while (minIndex <= maxIndex) and isTransparent(getSlice(minIndex, alphaChannel, width)):
                minIndex += 1
            while (minIndex <= maxIndex) and isTransparent(getSlice(maxIndex, alphaChannel, width)):
                maxIndex -= 1
            return minIndex, maxIndex

        top, bottom = findTrimEdges(0, height - 1, getRow)
        left, right = findTrimEdges(0, width - 1, getColumn)

        trimmedWidth = (right - left) + 1
        trimmedHeight = (bottom - top) + 1

        rowEdges = (left, left + trimmedWidth)
        rowOffsets = (rowIndex * width for rowIndex in range(top, top + trimmedHeight))
        rowBoundaries = (tuple(((edge + offset) * channelsPerPixel)
                               for edge in rowEdges) for offset in rowOffsets)
        trimmedRows = (flatPixelArray[rowStart: rowEnd] for rowStart, rowEnd in rowBoundaries)
        trimmedPixels = list(itertools.chain(*trimmedRows))

        return trimmedWidth, trimmedHeight, trimmedPixels

    @classmethod
    def blackenTransparentPixels(cls, flatPixelArray, width, height, channels):
        channelsPerPixel = len(channels)

        alphaChannelIndex = (channelsPerPixel - 1)
        for pixelIndex in range(width * height):
            channelIndex = pixelIndex * channelsPerPixel
            if flatPixelArray[channelIndex + alphaChannelIndex] == 0x0:
                for i in range(channelIndex, channelIndex + channelsPerPixel - 1):
                    flatPixelArray[i] = 0

        return flatPixelArray

    @classmethod
    def unpackPixels(cls, texture, targetBitDepth):
        bitsPerChannel = texture.encoding.channels
        bitShifts = [sum(bitsPerChannel[channelIndex + 1:])
                     for channelIndex, channelBitCount in enumerate(bitsPerChannel)]
        bitMasks = [(((2 ** bitCount) - 1) << bitShift)
                    for bitCount, bitShift in zip(bitsPerChannel, bitShifts)]
        conversionTables = [cls.bitDepthConversionTable[currentBitCount]
                            [targetBitDepth] for currentBitCount in bitsPerChannel]
        zippedChannelInfo = list(zip(bitShifts, bitMasks, conversionTables))

        return [conversionTable[(packedPixelValue & bitMask) >> bitShift] for packedPixelValue in texture.packedPixels for bitShift, bitMask, conversionTable in zippedChannelInfo]

    @classmethod
    def exportToImageFile(cls, texture, outputFilePath):
        binaryFileData = bytes()
        if texture.encoding == RAW:
            binaryFileData = texture.buffer

        else:
            width, height = texture.width, texture.height
            targetBitDepth = 8
            flatPixelArray = cls.unpackPixels(texture, targetBitDepth)

            if texture.encoding.hasAlpha:
                if cls.trimmingEnabled:
                    width, height, flatPixelArray = cls.trimTransparentEdges(
                        flatPixelArray, width, height, texture.encoding.channels)
                if cls.blackeningEnabled:
                    flatPixelArray = cls.blackenTransparentPixels(
                        flatPixelArray, width, height, texture.encoding.channels)

            if any(flatPixelArray):
                # Create an in-memory stream to which we can write the png data.
                pngStream = io.BytesIO()

                # Attempt to create a palette
                channelsPerPixel = len(texture.encoding.channels)
                pixels = list(zip(*(flatPixelArray[i::channelsPerPixel]
                                    for i in range(channelsPerPixel))))
                palette = list(set(pixels))

                # Palettes cannot contain more than 256 colors. Also, using palettes for
                # greyscale images typically takes more memory, not less.
                if len(palette) <= (2 ** 8) and not texture.encoding.isGreyscale:
                    def getAlphaValue(color): return color[channelsPerPixel - 1]
                    palette.sort(key=getAlphaValue)
                    colorToIndex = dict((color, paletteIndex)
                                        for paletteIndex, color in enumerate(palette))
                    paletteIndexArray = [colorToIndex[color] for color in pixels]

                    # Remove alpha from opaque pixels
                    if texture.encoding.hasAlpha:
                        palette = [(color if getAlphaValue(color) < 0xFF else color[:-1])
                                   for color in palette]
                    elif texture.encoding.isGreyscale:
                        palette = [(color[0],) * 3 for color in palette]

                    # Write the png data to the stream.
                    pngWriter = png.Writer(width, height, palette=palette, bitdepth=targetBitDepth)
                    pngWriter.write_array(pngStream, paletteIndexArray)

                else:
                    # Write the png data to the stream.
                    pngWriter = png.Writer(width, height, alpha=texture.encoding.hasAlpha, greyscale=texture.encoding.isGreyscale,
                                           bitdepth=targetBitDepth, planes=len(texture.encoding.channels))
                    pngWriter.write_array(pngStream, flatPixelArray)

                # Add the penultimate chunk.
                finalChunkSize = 12
                pngFileByteArray = bytearray(pngStream.getvalue())
                binaryFileData = bytes(
                    pngFileByteArray[:-finalChunkSize]) + cls.penultimateChunk + bytes(pngFileByteArray[-finalChunkSize:])

        if any(binaryFileData):
            outputDirectory = os.path.dirname(outputFilePath)
            if not os.path.isdir(outputDirectory):
                os.makedirs(outputDirectory)
            with open(outputFilePath, 'wb') as outputFileHandle:
                outputFileHandle.write(binaryFileData)

# This class translates binary data into Texture objects.


class TextureReader(object):
    encryptedTextureMagicString = struct.pack("<5B", 0x49, 0x4F, 0x53, 0x43, 0x68)  # "IOSCh"
    encryptedTextureHeaderFormat = "<5sBxxxxxx"
    encryptedTextureHeaderFormatSize = struct.calcsize(encryptedTextureHeaderFormat)
    unencryptedTextureMagicString = struct.pack("<3B", 0x54, 0x45, 0x58)  # "TEX"
    textureBlockHeaderFormat = "<3sxB11x"
    textureBlockHeaderSize = struct.calcsize(textureBlockHeaderFormat)
    textureBlockHeaderAlignment = 16
    textureManifestFormat = "<IHH24s"
    textureManifestSize = struct.calcsize(textureManifestFormat)

    encodings = dict()
    # Encoding 0x0 is four bytes per pixel; one byte per red, green, blue and alpha channel.
    encodings[0x0] = R8G8B8A8
    # Encoding 0x2 is two bytes per pixel; five bits for the red channel, six
    # bits for the green channel, and five bits for the blue channel.
    encodings[0x2] = R5G6B5
    # Encoding 0x3 is two bytes per pixel; four bits per red, green, blue and alpha channel.
    encodings[0x3] = R4G4B4A4
    # Encoding 0x4 is two bytes per pixel; five bits per red, green, blue
    # channel, and then one bit for the alpha channel.
    encodings[0x4] = R5G5B5A1
    # Encodings 0x8 and 0x9 are one byte per pixel; they are greyscale images.
    encodings[0x8] = L8
    encodings[0x9] = L8
    # Encoding 0xB uses the PVR texture compression algorithm. In its
    # compressed form, it uses four bits per pixel, but it decompresses to an
    # RGBA image.
    encodings[0xB] = PVRTC4BPP
    # Encoding 0xC uses the PVR texture compression algorithm. In its
    # compressed form, it uses two bits per pixel, but it decompresses to an
    # RGBA image.
    encodings[0xC] = PVRTC2BPP
    # Encoding 0xD is used for raw file data. Typically this JPEG data, but in
    # theory it could be anything.
    encodings[0xD] = RAW

    @classmethod
    def decryptAndDecompressBinaryBlob(cls, binaryBlob):
        magicString, decryptionKey = struct.unpack_from(
            cls.encryptedTextureHeaderFormat, binaryBlob)

        if magicString != cls.encryptedTextureMagicString:
            return binaryBlob

        # XOR each byte using the decryption key
        binaryBlob = bytearray(byte ^ decryptionKey for byte in bytearray(
            binaryBlob[cls.encryptedTextureHeaderFormatSize:]))

        # Inflate
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        binaryBlob = decompress.decompress(bytes(binaryBlob))
        binaryBlob += decompress.flush()

        return binaryBlob

    @classmethod
    def extractTexturesFromBinaryBlob(cls, binaryBlob, outputDirectory):
        binaryBlob = cls.decryptAndDecompressBinaryBlob(binaryBlob)

        offset = 0x0
        while (offset + cls.textureBlockHeaderSize) < len(binaryBlob):
            magicString, numberOfTexturesInBlock = struct.unpack_from(
                cls.textureBlockHeaderFormat, binaryBlob, offset)
            if magicString == cls.unencryptedTextureMagicString:
                textureBlockHeaderStart = offset
                textureBlockHeaderEnd = textureBlockHeaderStart + cls.textureBlockHeaderSize

                for textureManifestIndex in range(0, numberOfTexturesInBlock):
                    textureManifestStart = textureBlockHeaderEnd + \
                        (cls.textureManifestSize * textureManifestIndex)
                    textureManifestEnd = textureManifestStart + cls.textureManifestSize

                    startingOffset, width, height, name = struct.unpack(
                        cls.textureManifestFormat, binaryBlob[textureManifestStart:textureManifestEnd])

                    encodingIdentifier = (width >> 12)
                    width = width & 0x0FFF
                    height = height & 0x0FFF

                    try:
                        encoding = cls.encodings[encodingIdentifier]
                    except:
                        encoding = RAW
                        if encodingIdentifier not in cls.encodings:
                            print("{name} is encoded with unrecognized encoding \"{encoding}\".".format(
                                name=name, encoding=re.sub(r'^(-?0X)', lambda x: x.group(1).lower(), hex(encodingIdentifier).upper())))

                    byteCount = 0
                    if (encoding != RAW):
                        byteCount = (width * height * encoding.strideInBits) // 8
                    else:
                        name, byteCount = struct.unpack("<20sI", name)

                    if byteCount <= 0:
                        print("{name} has no associated image data.".format(name=name))

                    name = name.rstrip(b'\0').decode(encoding='UTF-8')

                    imageDataStart = textureBlockHeaderStart + startingOffset

                    # PVR encodings are prefixed by a 52-byte header whose purpose is not yet clear.
                    if encoding == PVRTC4BPP or encoding == PVRTC2BPP:
                        imageDataStart += 52

                    imageDataEnd = imageDataStart + byteCount
                    offset = max(offset, imageDataEnd & ~(cls.textureBlockHeaderAlignment - 1))

                    # PVR encodings are followed by a 12-byte footer whose purpose is not yet clear.
                    if encoding == PVRTC4BPP or encoding == PVRTC2BPP:
                        offset += 12

                    yield Texture(width, height, name, binaryBlob[imageDataStart:imageDataEnd], encoding)

            offset += cls.textureBlockHeaderAlignment

# This class represents a group of user-configurable settings which control how the script operates.


class Settings(object):
    def __init__(self):
        super(Settings, self).__init__()
        self._inputFiles = []
        self._outputDirectory = None
        self._trimmingEnabled = True
        self._blackeningEnabled = True
        self._subtexturesEnabled = False

    @property
    def inputFiles(self):
        return self._inputFiles

    def setInputPath(self, value):
        if value:
            value = os.path.abspath(value)
            if not os.path.exists(value):
                raise argparse.ArgumentTypeError(
                    "The input path you specified (\"{}\") does not exist.".format(value))
            elif os.path.isfile(value):
                self._inputFiles = [value]
            elif os.path.isdir(value):
                self._inputFiles = [os.path.join(root, file)
                                    for root, dirs, files in os.walk(value) for file in files]

    @property
    def outputDirectory(self):
        return self._outputDirectory

    def setOutputDirectory(self, value):
        self._outputDirectory = os.path.abspath(value)

    @property
    def trimmingEnabled(self):
        return self._trimmingEnabled

    def setTrimmingEnabled(self, value):
        self._trimmingEnabled = value

    @property
    def blackeningEnabled(self):
        return self._blackeningEnabled

    def setBlackeningEnabled(self, value):
        self._blackeningEnabled = value

    @property
    def subtexturesEnabled(self):
        return self._subtexturesEnabled

    def setSubtexturesEnabled(self, value):
        self._subtexturesEnabled = value


def getSettingsFromCommandLine():
    settings = Settings()

    def call(function, parameter=None):
        class ActionWrapper(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                function(parameter or values)
        return ActionWrapper

    parser = argparse.ArgumentParser(
        description="This script extracts texture images from the binary data of the popular iOS & Android game \"Puzzle & Dragons\".", add_help=False)
    inputGroup = parser.add_argument_group("Input")
    group = inputGroup.add_mutually_exclusive_group(required=True)
    group.add_argument("inputPath", metavar="IN_FILE", nargs="?",
                       help="A path to a file containing Puzzle & Dragons texture data. Typically, these files end in \".bc\" however this script is also capable of extracting textures from a Puzzle & Dragons \".apk\" file.", action=call(settings.setInputPath))
    group.add_argument("inputFolder", metavar="IN_DIR", nargs="?",
                       help="A path to a folder containing one or more Puzzle & Dragons texture files. Each file in this folder and its sub-folders will be processed and have their textures extracted.", action=call(settings.setInputPath))

    outputGroup = parser.add_argument_group("Output")
    outputGroup.add_argument("-o", "--outdir", metavar="OUT_DIR",
                             help="A path to a folder where extracted textures should be saved. This property is optional; by default, any extracted texture files will be saved in the same directory as the file from which they were extracted.", action=call(settings.setOutputDirectory))

    featuresGroup = parser.add_argument_group("Optional Features")
    featuresGroup.add_argument("-nt", "--notrim", nargs=0, help="Puzzle & Dragons' textures are padded with empty space, which this script automatically removes before writing the texture to disk. Use this flag to disable automatic trimming.",
                               action=call(settings.setTrimmingEnabled, False))
    featuresGroup.add_argument("-nb", "--noblacken", nargs=0, help="By default, this script will \"blacken\" (i.e. set the red, green and blue channels to zero) any fully-transparent pixels of an image before exporting it. This reduces file size in a way that does not affect the quality of the image. Use this flag to disable automatic blackening.", action=call(settings.setBlackeningEnabled, False))
    featuresGroup.add_argument("--subtextures", nargs=0, help="Enables extracting monsters with multiple textures",
                               action=call(settings.setSubtexturesEnabled, True))

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help",
                           help="Displays this help message and exits.")
    args = parser.parse_args()

    return settings


def getOutputFileName(suggestedFileName):
    outputFileName = suggestedFileName
    # If the file is a "monster file" then pad the ID out with extra zeroes.
    try:
        prefix, id, suffix = getOutputFileName.monsterFileNameRegex.match(
            suggestedFileName).groups()
        outputFileName = prefix + id.zfill(5) + suffix
    except AttributeError:
        pass

    # If we've already written a file with this name then add a number to the
    # file name to prevent collisions.
    try:
        getOutputFileName.filesWritten[outputFileName] += 1
        outputFileWithoutExtension, outputFileExtension = os.path.splitext(outputFileName)
        outputFileName = "{} ({}){}".format(outputFileWithoutExtension,
                                            getOutputFileName.filesWritten[outputFileName], outputFileExtension)
    except KeyError:
        getOutputFileName.filesWritten[outputFileName] = 0

    return outputFileName


getOutputFileName.filesWritten = dict()
getOutputFileName.monsterFileNameRegex = re.compile(r'^(MONS_)(\d+)(\..+)$', flags=re.IGNORECASE)


def main():
    settings = getSettingsFromCommandLine()

    TextureWriter.enableTrimming(settings.trimmingEnabled)
    TextureWriter.enableOptimization(settings.blackeningEnabled)

    for inputFilePath in settings.inputFiles:
        outputDirectoryPath = (settings.outputDirectory or os.path.dirname(inputFilePath))

        if zipfile.is_zipfile(inputFilePath):
            with zipfile.ZipFile(inputFilePath, 'r') as apkFile:
                fileContents = apkFile.read('assets/DATA001.BIN')

        else:
            with open(inputFilePath, 'rb') as binaryFile:
                fileContents = binaryFile.read()

        print("\nReading {}... ".format(inputFilePath))
        textures = list(TextureReader.extractTexturesFromBinaryBlob(fileContents, inputFilePath))
        print("{} texture{} found.\n".format(str(len(textures)) if any(
            textures) else "No", "" if len(textures) == 1 else "s"))

        if not settings.subtexturesEnabled:
            if len(textures) > 1 or '000.PNG' in textures[0].name:
                print("Skipping; subtextures not enabled")
                inputFileWithoutExtension, _ = os.path.splitext(inputFilePath)
                # Create a tag file that marks this as being animated. This is used elsewhere
                # to determine if we need to extract a video.
                Path(inputFileWithoutExtension + '.isanimated').touch()
                exit()

        for texture in textures:
            outputFileName = getOutputFileName(texture.name)
            if len(textures) > 1:
                outputFileName = os.path.basename(inputFilePath) + '_' + outputFileName

            print("  Writing {} ({} x {})...".format(outputFileName, texture.width, texture.height))
            if texture.encoding in [PVRTC2BPP, PVRTC4BPP]:
                print("  Warning: {} is encoded using PVR texture compression. This format is not yet supported by the Puzzle & Dragons Texture Tool.".format(
                    outputFileName))
            print("")
            outputFilePath = os.path.join(outputDirectoryPath, outputFileName)
            TextureWriter.exportToImageFile(texture, outputFilePath)


if __name__ == "__main__":
    main()
