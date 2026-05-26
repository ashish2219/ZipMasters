import heapq
import json
import struct

class HuffmanNode:
    def __init__(self, byte_val, freq):
        self.byte_val = byte_val  
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoder:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    def make_frequency_dict(self, raw_bytes):
        frequency = {}
        for byte in raw_bytes:
            if byte not in frequency:
                frequency[byte] = 0
            frequency[byte] += 1
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = HuffmanNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, root, current_code):
        if root is None:
            return

        if root.byte_val is not None:
            self.codes[root.byte_val] = current_code
            self.reverse_mapping[current_code] = root.byte_val
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        if root.byte_val is not None:
            self.codes[root.byte_val] = "0"
            self.reverse_mapping["0"] = root.byte_val
        else:
            self.make_codes_helper(root, current_code)

    def get_encoded_text(self, raw_bytes):
        encoded_text = ""
        for byte in raw_bytes:
            encoded_text += self.codes[byte]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return bytes(b)

    def compress(self, raw_bytes):
        if not raw_bytes or len(raw_bytes) == 0:
            return b"" # Returns only bytes now

        frequency = self.make_frequency_dict(raw_bytes)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()
        
        encoded_text = self.get_encoded_text(raw_bytes)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        compressed_data = self.get_byte_array(padded_encoded_text)
        
        # --- THE HEADER INJECTION ---
        # 1. Convert the mapping to a JSON string, then to raw utf-8 bytes
        mapping_json = json.dumps(self.reverse_mapping)
        mapping_bytes = mapping_json.encode('utf-8')
        
        # 2. Store the exact length of the JSON string as a 4-byte integer
        # '>I' means Big-Endian Unsigned Integer (4 bytes)
        header_length = struct.pack('>I', len(mapping_bytes))
        
        # 3. Glue it all together: [4-byte Length] + [Mapping Bytes] + [Compressed Data]
        standalone_file = header_length + mapping_bytes + compressed_data
        
        return standalone_file

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        if extra_padding > 0:
            encoded_text = padded_encoded_text[:-extra_padding]
        else:
            encoded_text = padded_encoded_text
        return encoded_text

    def decode_bytes(self, encoded_text, reverse_mapping):
        current_code = ""
        decoded_bytes = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in reverse_mapping:
                byte_val = reverse_mapping[current_code]
                decoded_bytes.append(byte_val)
                current_code = ""
                
        return bytes(decoded_bytes)

    def decompress(self, standalone_bytes): # No longer needs reverse_mapping argument
        if not standalone_bytes or len(standalone_bytes) == 0:
            return b""

        # --- THE HEADER EXTRACTION ---
        # 1. Read the first 4 bytes to find out how long the JSON header is
        header_length = struct.unpack('>I', standalone_bytes[:4])[0]
        
        # 2. Extract exactly that many bytes and convert back to a Python Dictionary
        mapping_bytes = standalone_bytes[4:4+header_length]
        reverse_mapping = json.loads(mapping_bytes.decode('utf-8'))
        
        # 3. Isolate the actual compressed file data (everything after the header)
        compressed_data = standalone_bytes[4+header_length:]

        bit_string = ""
        for byte in compressed_data:
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            
        encoded_text = self.remove_padding(bit_string)
        decompressed_bytes = self.decode_bytes(encoded_text, reverse_mapping) 
        
        return decompressed_bytes