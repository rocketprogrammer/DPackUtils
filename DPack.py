from ByteArray import ByteArray
import os, zlib, sys

class DPackItem:
    def __init__(self, itemName: str, itemData: bytes):
        self.itemName = itemName
        self.itemData = itemData

class DPack:
    def __init__(self):
        self.magicCode = 1146110283

        self.unpackDir = 'unpacked/'

        if not os.path.exists(self.unpackDir):
            os.mkdir(self.unpackDir)

    def pack(self, itemList: list):
        writer = ByteArray(b'')
        writer.writeUnsignedInt(self.magicCode)
        writer.writeShort(len(itemList))

        for item in itemList:
            writer.writeUnsignedInt(len(item.itemData))
            writer.writeUTF(item.itemName)
            writer.writeBytes(item.itemData)

        return zlib.compress(writer.toByteArray())

    def unpack(self, data: bytes):
        data = zlib.decompress(data)

        reader = ByteArray(data)

        magicCode = reader.readUnsignedInt()

        if magicCode != self.magicCode:
            raise Exception('Magic code invalid!')

        numFiles = reader.readUnsignedShort()

        lengths = []

        for _ in range(numFiles):
            length = reader.readUnsignedInt()

            lengths.append(length)

        names = []

        for _ in range(numFiles):
            lengthBytes = reader.readUnsignedShort()

            name = reader.readMultiByte(lengthBytes)

            names.append(name)

        for i in range(numFiles):
            data = reader.readBytes(lengths[i])

            with open(self.unpackDir + names[i], 'wb') as outDisk:
                print(f'Writing {names[i]} to disk!')
                outDisk.write(data)

items = []
items.append(DPackItem(sys.argv[1], open(sys.argv[1], 'rb').read()))

dPack = DPack()

# First, test packing
res = dPack.pack(items)

# Finally, write out the packed data
open(sys.argv[2], 'wb').write(res)

# Test unpacking
dPack.unpack(res)