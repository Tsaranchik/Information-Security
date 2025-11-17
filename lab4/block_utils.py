def split_into_blocks(data: bytes, block_size: int) -> list:
	blocks = []
	for i in range(0, len(data), block_size):
		block = data[i:i + block_size]
		if len(block) < block_size:
			block += b'\x00' * (block_size - len(block))
		blocks.append(block)
	
	return blocks


def combine_blocks(blocks: list, original_length: int = None) -> bytes:
	data = b''.join(blocks)
	if original_length is not None:
		return data[:original_length]
	else:
		return data.rstrip(b'\x00')


def pad_data(data: bytes, block_size: int) -> bytes:
	padding_length = block_size - (len(data) % block_size)
	if padding_length == block_size:
		padding_length = 0
	
	return data + b'\x00' * padding_length


def unpad_data(data: bytes) -> bytes:
	return data.rstrip(b'\x00')
