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
