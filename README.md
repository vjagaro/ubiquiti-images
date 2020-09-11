# ubiquiti-images

Download Ubiquiti marketing images available at https://www.ui.com/marketing/.

## Install

This program requires [Python 3.7+](https://www.python.org/downloads/) and
[Poetry](https://python-poetry.org/).

```
git clone https://github.com/awakerow/ubiquiti-images.git
cd ubiquiti-images
poetry install
```

## Usage

```sh
# See help and options
poetry run python ubiquiti-images.py --help

# Download only front images, preferring png (~1.2GB)
poetry run python ubiquiti-images.py \
    --format best --position front \
    path/to/output/directory

# Download all images (~5.3GB)
poetry run python ubiquiti-images.py \
    --format all --position all \
    path/to/output/directory
```
