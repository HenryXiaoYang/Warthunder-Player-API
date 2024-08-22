import asyncio
import json
import logging

from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup

from CloudflareBypasser import CloudflareBypasser


class WarthunderScraping:
    def __init__(self, driver: ChromiumPage):
        self.driver = driver

        with open("scraping_config.json", "r") as f:
            self.config = json.load(f)

    async def get_player_stat(self, name: str):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._get_player_stat, name)
        return result

    def _get_player_stat(self, name: str) -> dict:
        html = self.get_warthunder_profile_html(name)
        data = self.parse_data_from_html(html)
        return data

    def get_warthunder_profile_html(self, name: str) -> str:
        url = f"https://warthunder.com/en/community/userinfo/?nick={name}"
        tab = None
        try:
            tab = self.bypass_cloudflare(url, 20, name=name)
            html = tab.html
            tab.close()
        except Exception as error:
            logging.error(f"{name} : Failed to request {url} : {error}")
            tab.close()
            raise error
        return html

    def bypass_cloudflare(self, url: str, retries: int, name: str = ""):
        driver = self.driver
        try:
            logging.info(f"{name} : Requesting {url}")
            tab = driver.new_tab(url, new_window=False)
            bypasser = CloudflareBypasser(tab, retries)
            bypasser.bypass(name)
            return tab
        except Exception as error:
            raise error

    @staticmethod
    def format_single_data(single_data: str) -> (None, int, str):
        if single_data == "N/A":
            return None

        single_data = single_data.replace(',', '').replace(' ', '')
        if single_data.isdigit():
            return int(single_data)
        else:
            return single_data

    def parse_data_from_html(self, html: str) -> dict:
        data = {}

        soup = BeautifulSoup(html, "html.parser")

        # Check if the player exist
        player_not_found_selector = self.config.get("player_not_found_selector")
        player_not_found = soup.select(player_not_found_selector)
        if player_not_found:  # Return if the player not found
            data["code"] = 404
            data["message"] = "Player not found"
            data["tip"] = "The nickname is case sensitive. Please check the nickname and try again."
            return data

        data = self.config.get("init_data", {})

        # Get the player's nickname
        nickname_selector = self.config.get("nickname_selector")
        nickname = soup.select(nickname_selector)
        if len(nickname) >= 1:
            nickname = nickname[0].get_text(strip=True)
            data["nickname"] = nickname

        # Get the player's clan info
        clan_selector = self.config.get("clan_selector")
        clan = soup.select(clan_selector)
        if len(clan) >= 1:
            clan_name = clan[0].get_text(strip=True)
            clan_url = f"https://warthunder.com{clan[0].get('href', default='')}"
            data["clan_name"] = clan_name
            data["clan_url"] = clan_url

        # Get the player's title
        player_title_selector = self.config.get("player_title_selector")
        player_title = soup.select(player_title_selector)
        if (len(player_title) >= 1) and ("Level" not in player_title[0].get_text(strip=True)):
            player_title = player_title[0].get_text(strip=True)
            data["player_title"] = player_title
        else:
            player_title = None

        # Get the player's level
        if player_title:  # Some player do not have player title, need a check here
            player_level_selector = self.config.get("player_level_selector_1")
        else:
            player_level_selector = self.config.get("player_level_selector_2")
        player_level = soup.select(player_level_selector)
        if len(player_level) >= 1:
            player_level = int(player_level[0].get_text(strip=True)[6:])
            data["player_level"] = player_level

        # Get the player's register date
        register_date_selector = self.config.get("register_date_selector")
        register_date = soup.select(register_date_selector)
        if len(register_date) >= 1:
            register_date = register_date[0].get_text(strip=True)[18:]
            data["register_date"] = register_date

        # Get the player's avatar
        avatar_selector = self.config.get("avatar_selector")
        avatar = soup.select(avatar_selector)
        if len(avatar) >= 1:
            avatar = avatar[0].get("src", default="")
            data["avatar"] = avatar

        # general statistics
        general_statistics_selectors = self.config.get("general_statistics_selectors")
        title = self.config.get("general_statistics_title")
        for game_type, selector in general_statistics_selectors:
            statistics_soup = soup.select(selector)
            if len(statistics_soup) >= 1:
                statistics_soup = statistics_soup[0].find_all('li')
                for j in range(1, len(statistics_soup)):
                    single_data = statistics_soup[j].get_text(strip=True)
                    single_data = self.format_single_data(single_data)
                    if single_data:
                        data["statistics"][game_type][title[j]] = single_data

        # Detailed statistics for aviation, ground, fleet
        aviation_title = self.config.get("aviation_statistics_title")
        ground_title = self.config.get("ground_statistics_title")
        fleet_title = self.config.get("fleet_statistics_title")

        aviation_selectors = self.config.get("aviation_selectors")
        ground_selectors = self.config.get("ground_selectors")
        fleet_selectors = self.config.get("fleet_selectors")

        aviation = (aviation_title, aviation_selectors, 'aviation')
        ground = (ground_title, ground_selectors, 'ground')
        fleet = (fleet_title, fleet_selectors, 'fleet')
        game_type = ["arcade", "realistic", "simulation"]

        for titles, selectors, army in [aviation, ground, fleet]:
            for i in range(len(game_type)):
                statistics_soup = soup.select(selectors[i])
                if len(statistics_soup) >= 1:
                    statistics_soup = statistics_soup[0].find_all('li')
                    for j in range(len(statistics_soup)):
                        single_data = statistics_soup[j].get_text(strip=True)
                        single_data = self.format_single_data(single_data)
                        if single_data:
                            data["statistics"][game_type[i]][army][titles[j]] = single_data

        # Vehicles and rewards
        countries = self.config.get("vehicles_and_rewards_countries")
        titles = self.config.get("vehicles_and_rewards_title")
        owned_vehicles_selector = self.config.get("owned_vehicles_selector")
        elite_vehicles_selector = self.config.get("elite_vehicles_selector")
        medals_selector = self.config.get("medals_selector")
        selectors = [owned_vehicles_selector, elite_vehicles_selector, medals_selector]

        for i in range(len(selectors)):
            vehicles_soup = soup.select(selectors[i])
            if len(vehicles_soup) >= 1:
                vehicles_soup = vehicles_soup[0].find_all('li')
                for j in range(1, len(vehicles_soup)):
                    single_data = vehicles_soup[j].get_text(strip=True)
                    single_data = self.format_single_data(single_data)
                    if single_data:
                        data["vehicles_and_rewards"][countries[j - 1]][titles[i]] = single_data

        data["url"] = f"https://warthunder.com/en/community/userinfo/?nick={nickname}"
        data["code"] = 200
        data["message"] = "Success"
        data["tip"] = "Thanks to Cloudflare, to request the data it may take a long time. Please be patient."

        return data
