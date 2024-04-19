from setuptools import setup, find_packages

setup(
    name='socialmediaextractor',
    version='0.4',
    description='A library to extract social media links from websites',
    long_description = '''Usage
========================================
To use the socialmediaextractor library, you first need to install it using pip:

.. code-block:: bash

    pip install socialmediaextractor

Once the library is installed, you can extract social media links from a website using the following code:

.. code-block:: python

    from socialmediaextractor import extract_social_media_accounts

    # Example: Extract social media accounts from a website
    url = 'https://example.com'
    social_media_links = extract_social_media_accounts(url)
    print(social_media_links)
    # Output: {'Facebook': 'https://www.facebook.com/example', 'LinkedIn': 'https://www.linkedin.com/company/example/', 'Twitter': 'https://twitter.com/example'}

For more information and documentation, please visit the `GitHub repository <https://github.com/irfanalidv/socialmediaextractor>`_.''',
    author='Md Irfan Ali',
    author_email='irfanali29@hotmail.com',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'requests'
    ],
)
