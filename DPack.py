from ByteArray import ByteArray
from pathlib import Path
from lxml import etree
import os, zlib, sys

class DPackItem:
    def __init__(self, itemName: str, itemData: bytes):
        self.itemName = itemName
        self.itemData = itemData

class DPack:
    def __init__(self):
        self.magicCodes = [
            1146110283, # DPack
            1836597052, # XML
            1885433148 # XMC (XML)
        ]

        self.unpackDir = 'unpacked/'

        if not os.path.exists(self.unpackDir):
            os.mkdir(self.unpackDir)

    def pack(self, itemList: list) -> bytes:
        writer = ByteArray(b'')
        writer.writeUnsignedInt(self.magicCode)
        writer.writeShort(len(itemList))

        for item in itemList:
            writer.writeUnsignedInt(len(item.itemData))
            writer.writeUTF(item.itemName)
            writer.writeBytes(item.itemData)

        return zlib.compress(writer.toByteArray())

    def unpack(self, file_path: str):
        data = zlib.decompress(open(file_path, 'rb').read())

        reader = ByteArray(data)

        magicCode = reader.readUnsignedInt()

        if magicCode not in self.magicCodes:
            raise Exception(f'Magic code invalid: {magicCode}!')

        if magicCode in [self.magicCodes[1], self.magicCodes[2]]:
            # XML file
            root = etree.fromstring(reader.toByteArray())
            open(f"unpacked/{Path(file_path).stem}.xml", "wb").write((etree.tostring(root, pretty_print=True)))
            return

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

"""
items = []
items.append(DPackItem(sys.argv[1], open(sys.argv[1], 'rb').read()))

dPack = DPack()

# First, test packing
res = dPack.pack(items)

# Finally, write out the packed data
open(sys.argv[2], 'wb').write(res)

# Test unpacking
dPack.unpack(res)
"""

DPack().unpack(sys.argv[1])
