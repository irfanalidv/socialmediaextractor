[![Python version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue.svg)](https://pypi.org/project/socialmediaextractor/)
[![PyPI version](https://badge.fury.io/py/socialmediaextractor.svg)](https://pypi.org/project/socialmediaextractor/)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/socialmediaextractor.svg)](https://anaconda.org/conda-forge/socialmediaextractor)

## Usage

To use the `socialmediaextractor` library, you first need to install it using pip:

```python
pip install socialmediaextractor
```

Once the library is installed, you can extract social media links from a website using the following code:

```python
from socialmediaextractor import extract_social_media_accounts
```

```python
# Example: Extract social media accounts from a website
url = 'https://example.com'
social_media_links = extract_social_media_accounts(url)
print(social_media_links)
# Output: {'Facebook': 'https://www.facebook.com/example', 'LinkedIn': 'https://www.linkedin.com/company/example/', 'Twitter': 'https://twitter.com/example'}
```
