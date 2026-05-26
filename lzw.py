import struct

class LZWCoder:
    def __init__(self, max_dict_size=65535):
        # 65535 is the max value for a 16-bit unsigned integer
        self.max_dict_size = max_dict_size

    def compress(self, raw_bytes):
        # SAFETY GUARD: Check for empty file
        if not raw_bytes or len(raw_bytes) == 0:
            return b"", "LZW_Dynamic"

        # 1. Initialize the dictionary with standard 8-bit ASCII (0-255)
        dictionary = {bytes([i]): i for i in range(256)}
        dict_size = 256
        
        w = bytes([raw_bytes[0]])
        compressed_codes = []

        # 2. The Sliding Window Compression Logic
        for k in raw_bytes[1:]:
            k_bytes = bytes([k])
            wk = w + k_bytes
            
            # If the sequence is already in the dictionary, keep expanding the window
            if wk in dictionary:
                w = wk
            else:
                # Sequence not found. Output the code for 'w'
                compressed_codes.append(dictionary[w])
                
                # Add the new sequence 'wk' to the dictionary
                if dict_size < self.max_dict_size:
                    dictionary[wk] = dict_size
                    dict_size += 1
                
                # Start a new sequence with 'k'
                w = k_bytes
                
        # Output the code for the last remaining sequence
        compressed_codes.append(dictionary[w])

        # 3. Pack the integer codes into a raw binary bytearray (16-bits per code)
        compressed_bytes = bytearray()
        for code in compressed_codes:
            # '>H' means Big-Endian Unsigned Short (2 bytes)
            compressed_bytes.extend(struct.pack('>H', code))
            
        # We return "LZW_Dynamic" as a flag for the server, though LZW doesn't need a map!
        return bytes(compressed_bytes), "LZW_Dynamic"


    def decompress(self, compressed_bytes, dummy_mapping=None):
        # SAFETY GUARD: Check for empty file
        if not compressed_bytes or len(compressed_bytes) == 0:
            return b""

        # 1. Unpack the raw binary back into a list of integer codes
        codes = []
        for i in range(0, len(compressed_bytes), 2):
            codes.append(struct.unpack('>H', compressed_bytes[i:i+2])[0])

        # 2. Initialize the exact same starting dictionary (0-255)
        dictionary = {i: bytes([i]) for i in range(256)}
        dict_size = 256

        # 3. The Dynamic Reconstruction Logic
        w = dictionary[codes[0]]
        decompressed_bytes = bytearray(w)

        for k in codes[1:]:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                # The classic LZW Edge Case (e.g., repeating patterns like "cScSc")
                entry = w + bytes([w[0]])
            else:
                raise ValueError("Corrupt file: Invalid LZW code sequence.")

            decompressed_bytes.extend(entry)

            # Rebuild the dictionary identically to how the compressor did it
            if dict_size < self.max_dict_size:
                dictionary[dict_size] = w + bytes([entry[0]])
                dict_size += 1

            w = entry

        return bytes(decompressed_bytes)