import re
import requests
from bs4 import BeautifulSoup

def extract_social_media_accounts(url):
    """
    Extracts social media links from a website.

    Args:
        url (str): The URL of the website to extract social media links from.

    Returns:
        dict: A dictionary of social media platform names and their corresponding links, or None if no link is found.
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.find_all('a')

    social_media_platforms = {
        'Facebook': 'facebook.com',
        'LinkedIn': 'linkedin.com',
        'Twitter': 'twitter.com'
    }

    social_media_links = {}
    for platform, domain in social_media_platforms.items():
        for link in links:
            if domain in link.get('href', ''):
                social_media_links[platform] = link.get('href')
                break
        else:
            social_media_links[platform] = None

    return social_media_links
