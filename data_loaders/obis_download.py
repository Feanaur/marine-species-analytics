
import requests
import logging
import hashlib

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_data_from_file(*args, **kwargs):
    url = kwargs['FILE_URL']
    download_path = "/home/data/obis.parquet"
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0
    hasher = hashlib.sha256()  # Create a SHA-256 hasher
    
    with open(download_path, "wb") as f:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            downloaded_size += size
            hasher.update(data)  # Update the hasher with downloaded data

            if downloaded_size % (1024*1024*256) == 0:
                print(f"Downloading: {downloaded_size * 100 / total_size:.2f}%")

    print(f"SHA-256 checksum: {hasher.hexdigest()}")
    return download_path


def compute_file_crc(filename):
    hasher = hashlib.sha256()
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)  # Read in chunks of 1 MB
                if not data:
                    break
                hasher.update(data)  # Update the hasher with downloaded data

        return hasher.hexdigest()
    except IOError as e:
        print(f"Error opening or reading the file: {e}")
        return None


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """

    assert output is not None, 'The output is undefined'

    crc = compute_file_crc(output)
    print(f"SHA-256 checksum: {crc}")
    assert crc == 'b35447f1564e82fc771bd9b259316558b3734db623cae39d4c613125d89c77fd', 'The file is corrupted'
