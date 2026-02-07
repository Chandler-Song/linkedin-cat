import os.path

from colorama import Fore, Style
from linkedin_cat.core.message import LinkedinMessage
from linkedin_cat.core.base import LinkedinBase
from linkedin_cat.core.profile import extract_profile, extract_profile_thread_pool
from linkedin_cat.core.helper import save_to_json, extract_and_decode_username
from urllib.parse import urlencode,unquote
from bs4 import BeautifulSoup

# li_class = "AzUHSIcDpyaLkwSZmBtCoOlWIyexIQYxg"
# title_div_class = "HfZFuPHGtwgBtEhYPPjErraXxsQikCfmkzcE"
# location_div_class = "TIPiImOlYjdixdiCAixhFkTwgWSITjWTBPJg"
# intro_p_class = "PCdOMLNLxbkXwFMvwqcTrwfJdfvlJttYufXLs"
# link_span_class = "QwrfzQPBYvtFCKlQkDFOMFZpyRFA"

class LinkedinSearch(LinkedinMessage):
    """
    Encapsulates the functionality related to interacting with
    LinkedIn using Selenium.
    """
    def __init__(self,linkedin_cookies_json:str,headless = False,**kwargs):
        super().__init__(linkedin_cookies_json,headless,**kwargs)
        self.li_class = kwargs.get('li_class')
        self.title_div_class = kwargs.get('title_div_class')
        self.location_div_class = kwargs.get('location_div_class')
        self.intro_p_class = kwargs.get('intro_p_class')
        self.link_span_class = kwargs.get('link_span_class')

    def extract_username_from_linkedin_url(self,linkedin_url):
        """
        从 LinkedIn 个人资料 URL 中提取用户名并将其解码为汉字。

        参数:
            url (str): LinkedIn 个人资料的 URL。

        返回:
            str: 解码后的用户名。
        """
        # 去除结尾的 "/"
        linkedin_url = linkedin_url.rstrip('/')

        # 提取用户名部分
        username_encoded = linkedin_url.split('/')[-1]

        # 解码为汉字
        username = unquote(username_encoded)

        return username

    def generate_linkedin_search_url(self, keywords, company=None, title=None,school=None,
                                     first_name=None, last_name=None, origin="SWITCH_SEARCH_VERTICAL",sid=None):
        base_url = "https://www.linkedin.com/search/results/people/"
        """
        Generates a LinkedIn search URL based on the provided parameters.

        Args:
            base_url (str): The base LinkedIn search URL.
            keywords (str): Required search keywords.
            company (str, optional): Company name to filter results.
            first_name (str, optional): First name of the person to filter results.
            last_name (str, optional): Last name of the person to filter results.
            origin (str, optional): Origin of the search (e.g., 'FACETED_SEARCH').
            school (str, optional): School name or text to filter results.
            title (str, optional): Job title to filter results.
            sid (str, optional): Session ID or other identifier for the search context.

        Returns:
            str: A LinkedIn search URL with all applicable parameters.
        """
        # Ensure 'keywords' parameter is provided
        if not keywords:
            raise ValueError("The 'keywords' parameter is required.")

        # Initialize parameters with the required 'keywords'
        params = {
            'keywords': keywords
        }

        # Add optional parameters if they are provided
        if company:
            params['company'] = company
        if title:
            params['titleFreeText'] = title

        if last_name:
            params['lastName'] = last_name
        if first_name:
            params['firstName'] = first_name
        if school:
            params['schoolFreetext'] = school
        if origin:
            params['origin'] = origin
        if sid:
            params['sid'] = sid

        # Encode parameters to URL query format and append to the base URL
        search_url = f"{base_url}?{urlencode(params)}"
        return search_url


    def parse_linkedin_results(self,html_text):
        """
        Parses LinkedIn search results HTML to extract structured information from each profile.

        Parameters:
        - html_text: str, HTML content of the LinkedIn search results page.

        Returns:
        - results: list of dictionaries, each containing information of a LinkedIn profile (image, name, position, location, etc.).
        """
        soup = BeautifulSoup(html_text, 'html.parser')

        # Initialize an empty list to store all results
        results = []

        # Find all list items with class `reusable-search__result-container`
        profiles = soup.find_all('li', class_=f"{self.li_class}")

        for profile in profiles:
            try:
                # Initialize a dictionary to hold profile data
                profile_data = {}



                # Extract profile name and LinkedIn profile link
                name_tag = profile.find('span', {'aria-hidden': 'true'})
                profile_data['name'] = name_tag.get_text(strip=True) if name_tag else None

                # Extract company, location, and title information if available
                title_tag = profile.find('div', class_=f"{self.title_div_class}")
                profile_data['title'] = title_tag.get_text(strip=True) if title_tag else None

                location_tag = profile.find('div', class_=f"{self.location_div_class}")
                profile_data['location'] = location_tag.get_text(strip=True) if location_tag else None

                intro_tag = profile.find('p', class_=f"{self.intro_p_class}")
                profile_data['introduction'] = intro_tag.get_text() if intro_tag else None

                # 查找具有特定class的<span>标签
                link_tag = profile.find('span', class_=f"{self.link_span_class}").find('a')
                profile_data['linkedin_url'] = link_tag["href"] if link_tag else None

                # Extract profile image URL
                # img_tag = profile.find('img', class_='presence-entity__image')
                # profile_data['image_url'] = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

                # Add profile data to results list
                results.append(profile_data)
            except Exception as e:
                print(f"Error parsing profile: {e}")
                continue

        return results

    def open_linkedin_url(self,url,wait=True):
        try:
            # Wait for a short duration
            self.short_wait()

            # Get the URL
            print(Fore.GREEN + f"Opening Linkedin URL: {url}" + Style.RESET_ALL)
            self.driver.get(url)

            # Wait for a medium duration
            self.medium_wait()
            if wait:
                # Scroll to the middle of the page
                print(Fore.GREEN + "Scrolling to the middle of the page" + Style.RESET_ALL)
                self.scroll_to_middle()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to a random position
                print(Fore.GREEN + "Scrolling to a random position" + Style.RESET_ALL)
                self.scroll_to_random()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to the bottom of the page
                print(Fore.GREEN + "Scrolling to the bottom of the page" + Style.RESET_ALL)
                self.scroll_to_bottom()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to the top of the page
                print(Fore.GREEN + "Scrolling to the top of the page" + Style.RESET_ALL)
                self.scroll_to_top()

                # Wait for a medium duration
                self.short_wait()
        except Exception as e:
            # If an exception occurs, print an error message
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)

        finally:
            return self.driver.page_source

    def search_keywords(self,keywords,wait=True):
        try:
            # Wait for a short duration
            self.short_wait()

            url = self.generate_linkedin_search_url(keywords)

            html = self.open_linkedin_url(url,wait=wait)


            results = self.parse_linkedin_results(html)

            # Wait for a medium duration
            self.medium_wait()

            return results
        except Exception as e:
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)

    def search_linkedin_profile(self,url,save_folder='./linkedin',thread_pool=True):
        # if folder does not exist,create it
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        filename = extract_and_decode_username(url)
        if os.path.exists(os.path.join(save_folder,f"{filename}.json")):
            print(Fore.YELLOW + f"Profile {filename} already exists" + Style.RESET_ALL)
            return

        try:
            print(Fore.GREEN + f"Opening LinkedIn URL:{url}" + Style.RESET_ALL)
            profile_data =  extract_profile_thread_pool(self.driver,url) if thread_pool else extract_profile(self.driver,url)
            if not profile_data:
                print(Fore.RED + "Could not extract profile" + Style.RESET_ALL)

            else:
                print(Fore.GREEN + f"Saving profile data to JSON:{save_folder}/{profile_data['filename']}" + Style.RESET_ALL)
                file_path = os.path.join(save_folder,f"{profile_data['filename']}.json")
                save_to_json(profile_data,file_path)

        except Exception as e:
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)

    def search_linkedin_profile_list(self,url_list,save_folder='./linkedin'):
        for url in url_list:
            try:
                self.search_linkedin_profile(url,save_folder)
            except Exception as e:
                print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)


    def close_driver(self):
        self.driver.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()


