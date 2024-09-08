import requests
from tqdm import tqdm


def download_file(url, filename):
    # get file size
    r = requests.head(url)
    file_size = int(r.headers.get("Content-Length", 0))
    # download file
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for data in tqdm(
            response.iter_content(chunk_size=1024),
            total=file_size / 1024,
            unit="B",
            unit_scale=True,
        ):
            f.write(data)
