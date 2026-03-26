import heapq
import os

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # Define less-than for the Priority Queue (Min-Heap)
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoder:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    def make_frequency_dict(self, text):
        frequency = {}
        for char in text:
            if char not in frequency:
                frequency[char] = 0
            frequency[char] += 1
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

        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        # Pad the binary string to make its length a multiple of 8
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return bytes(b)

    def compress(self, text):
        frequency = self.make_frequency_dict(text)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()
        
        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        byte_array = self.get_byte_array(padded_encoded_text)
        
        return byte_array, self.reverse_mapping
    
    #Decompression logic
    def remove_padding(self, padded_encoded_text):
        # The first 8 bits store the padding information
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        # Remove the 8-bit info header
        padded_encoded_text = padded_encoded_text[8:]
        
        # Remove the actual padding at the end of the string
        if extra_padding > 0:
            encoded_text = padded_encoded_text[:-extra_padding]
        else:
            encoded_text = padded_encoded_text
            
        return encoded_text

    def decode_text(self, encoded_text, reverse_mapping):
        current_code = ""
        decoded_text = ""
        
        # Read bit by bit and match with the reverse mapping
        for bit in encoded_text:
            current_code += bit
            if current_code in reverse_mapping:
                character = reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
                
        return decoded_text

    def decompress(self, compressed_bytes, reverse_mapping):
        # 1. Convert the raw bytes back to a string of '0's and '1's
        bit_string = ""
        for byte in compressed_bytes:
            # bin(byte) returns '0b...' so we slice off the first two chars
            # and pad with leading zeros to ensure it's exactly 8 bits
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            
        # 2. Remove the padding
        encoded_text = self.remove_padding(bit_string)
        
        # 3. Decode using the tree mapping
        decompressed_text = self.decode_text(encoded_text, reverse_mapping)
        
        return decompressed_text