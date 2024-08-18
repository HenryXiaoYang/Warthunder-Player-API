from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup

from CloudflareBypasser import CloudflareBypasser


class WarthunderScraping:
    def __init__(self):
        options = ChromiumOptions()
        options.set_paths().headless(False)
        options.auto_port()
        self.driver = ChromiumPage(addr_or_opts=options)

    async def get_player_stat(self, name: str) -> dict:
        html = await self.get_warthunder_profile_html(name)
        data = await self.parse_data_from_html(html)
        return data

    async def get_warthunder_profile_html(self, name: str) -> str:
        url = f"https://warthunder.com/en/community/userinfo/?nick={name}"
        driver = await self.bypass_cloudflare(url, 5)
        html = driver.html
        return html

    async def bypass_cloudflare(self, url: str, retries: int, log: bool = False):
        driver = self.driver
        try:
            driver.get(url)
            bypasser = CloudflareBypasser(driver, retries, log)
            await bypasser.bypass()
            return driver
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

    async def parse_data_from_html(self, html: str) -> dict:
        data = {}

        soup = BeautifulSoup(html, "html.parser")

        # Check if the player exist
        player_not_found_selector = "body > div.content > div > div > div.error-page__title.error-page__title--big"
        player_not_found = soup.select(player_not_found_selector)
        if player_not_found:  # Return if the player not found
            data["code"] = 404
            data["message"] = "Player not found"
            data["tip"] = "The nickname is case sensitive. Please check the nickname and try again."
            return data

        # Get the player's nickname
        nickname_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li.user-profile__data-nick"
        nickname = soup.select(nickname_selector)
        if len(nickname) >= 1:
            nickname = nickname[0].get_text(strip=True)
        else:
            nickname = None
        data["nickname"] = nickname

        # Get the player's clan info
        clan_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li.user-profile__data-clan > a"
        clan = soup.select(clan_selector)
        if len(clan) >= 1:
            clan_name = clan[0].get_text(strip=True)
            clan_url = f"https://warthunder.com{clan[0].get('href', default=None)}"
        else:
            clan_name = None
            clan_url = None
        data["clan_name"] = clan_name
        data["clan_url"] = clan_url

        # Get the player's title
        player_title_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li:nth-child(3)"
        player_title = soup.select(player_title_selector)
        if (len(player_title) >= 1) and ("Level" not in player_title[0].get_text(strip=True)):
            player_title = player_title[0].get_text(strip=True)
        else:
            player_title = None
        data["player_title"] = player_title

        # Get the player's level
        if player_title:  # Some player do not have player title, need a check here
            player_level_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li:nth-child(4)"
        else:
            player_level_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li:nth-child(3)"
        player_level = soup.select(player_level_selector)
        if (len(player_level) >= 1):
            player_level = int(player_level[0].get_text(strip=True)[6:])
        else:
            player_level = None
        data["player_level"] = player_level

        # Get the player's register date
        register_date_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > ul > li.user-profile__data-regdate"
        register_date = soup.select(register_date_selector)
        if (len(register_date) >= 1):
            register_date = register_date[0].get_text(strip=True)[18:]
        else:
            register_date = None
        data["register_date"] = register_date

        # Get the player's avatar
        avatar_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile > div > img"
        avatar = soup.select(avatar_selector)
        if (len(avatar) >= 1):
            avatar = avatar[0].get("src", default=None)
        else:
            avatar = None
        data["avatar"] = avatar

        # Player statistics
        statistics = {"arcade": {"aviation": {}, "ground": {}, "fleet": {}},
                      "realistic": {"aviation": {}, "ground": {}, "fleet": {}},
                      "simulation": {"aviation": {}, "ground": {}, "fleet": {}}}

        # Gernal statistics
        arcade_statistics_selector = ("arcade",
                                      "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.arcadeFightTab.is-visible")
        realistic_statistics_selector = ("realistic",
                                         "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.historyFightTab")
        simulation_selector = ("simulation",
                               "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.simulationFightTab")
        title = ["Placeholder", "Victories", "CompletedMissions", "VictoriesPerBattlesRatio", "Deaths", "LionsEarned",
                 "PlayTime", "AirTargetsDestroyed", "GroundTargetsDestroyed", "NavalTargetsDestroyed"]
        for i in [arcade_statistics_selector, realistic_statistics_selector, simulation_selector]:
            game_type = i[0]
            statistics_soup = soup.select(i[1])
            if (len(statistics_soup) >= 1):
                statistics_soup = statistics_soup[0].find_all('li')
                for j in range(1, len(statistics_soup)):
                    single_data = statistics_soup[j].get_text(strip=True)
                    statistics[game_type][title[j]] = self.format_single_data(single_data)
            else:
                for j in title:
                    statistics[game_type][j] = None

        # Detailed statistics for aviation, ground, fleet
        aviation_title = ["AirBattle", "AirBattlesInFighters", "AirBattlesInBombers", "AirBattlesInAttackers",
                          "TimePlayedInAirBattles", "TimePlayedInFighter", "TimePlayedInBomber",
                          "TimePlayedInAttackers",
                          "TotalTargetsDestroyed", "AirTargetsDestroyed", "GroundTargetsDestroyed",
                          "NavalTargetsDestroyed"]
        ground_title = ["GroundBattles", "GroundBattlesInTanks", "GroundBattlesInSPGs", "GroundBattlesInHeavyTanks",
                        "GroundBattlesInSPAA", "TimePlayedInGroundBattles", "TankBattleTime", "TankDestroyerBattleTime",
                        "HeavyTankBattleTime", "SPAABattleTime", "TotalTargetsDestroyed", "AirTargetsDestroyed",
                        "GroundTargetsDestroyed", "NavalTargetsDestroyed"]
        fleet_title = ["NavalBattles", "ShipBattles", "MotorTorpedoBoatBattles", "MotorGunBoatBattles",
                       "MotorTorpedoGunBoatBattles", "Sub-chaserBattles", "DestroyerBattles", "NavalFerryBargeBattles",
                       "TimePlayedNaval", "TimePlayedOnShip", "TimePlayedOnMotorTorpedoBoat",
                       "TimePlayedOnMotorGunBoat",
                       "TimePlayedOnMotorTorpedoGunBoat", "TimePlayedOnSub-chaser", "TimePlayedOnDestroyer",
                       "TimePlayedOnNavalFerryBarge", "TotalTargetsDestroyed", "AirTargetsDestroyed",
                       "GroundTargetsDestroyed", "NavalTargetsDestroyed"]

        aviation_selectors = [
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.arcadeFightTab.is-visible",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.historyFightTab",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.simulationFightTab"]
        ground_selectors = [
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.arcadeFightTab.is-visible",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.historyFightTab",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.simulationFightTab"]
        fleet_selectors = [
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.arcadeFightTab.is-visible",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.historyFightTab",
            "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.community__user-rate.user-rate > div.user-rate__fightType > div > div.user-stat__list-row.is-active > ul.user-stat__list.simulationFightTab"]

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
                        statistics[game_type[i]][army][titles[j]] = self.format_single_data(single_data)
                else:
                    for j in titles:
                        statistics[game_type[i]][army][j] = None

        data["statistics"] = statistics

        # Vehicles and rewards
        vehicles_and_rewards = {"USA": {}, "USSR": {}, "GreatBritain": {}, "Germany": {}, "Japan": {}, "Italy": {},
                                "France": {}, "China": {}, "Sweden": {}, "Israel": {}}
        countries = ["USA", "USSR", "GreatBritain", "Germany", "Japan", "Italy", "France", "China", "Sweden", "Israel"]
        titles = ["OwnedVehicles", "EliteVehicles", "Medals"]
        owned_vehicles_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile__score.user-score > ul:nth-child(2)"
        elite_vehicles_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile__score.user-score > ul:nth-child(3)"
        medals_selector = "#bodyRoot > div.content > div:nth-child(2) > div:nth-child(3) > div > section > div.user-info > div.user-profile__score.user-score > ul:nth-child(4)"
        selectors = [owned_vehicles_selector, elite_vehicles_selector, medals_selector]

        for i in range(len(selectors)):
            vehicles_soup = soup.select(selectors[i])
            if len(vehicles_soup) >= 1:
                vehicles_soup = vehicles_soup[0].find_all('li')
                for j in range(1, len(vehicles_soup)):
                    single_data = vehicles_soup[j].get_text(strip=True)
                    vehicles_and_rewards[countries[j - 1]][titles[i]] = self.format_single_data(single_data)
            else:
                for j in countries:
                    vehicles_and_rewards[j][titles[i]] = None

        data["vehicles_and_rewards"] = vehicles_and_rewards

        data["url"] = f"https://warthunder.com/en/community/userinfo/?nick={nickname}"
        data["code"] = 200
        data["message"] = "Success"
        data["tip"] = "Thanks to Cloudflare, to request the data it may take a long time. Please be patient."

        return data

    # get_player_stat("ABC")


warthunder_scraping = WarthunderScraping()
