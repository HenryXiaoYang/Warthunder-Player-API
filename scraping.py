import logging
import traceback

import nodriver as uc
from bs4 import BeautifulSoup


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Scraping(metaclass=Singleton):

    def __init__(self):
        self._inited = False

    async def async_init(self):
        if not self._inited:
            self.browser = await uc.start(lang="en-US")
            self._inited = True

    async def get_player_stat(self, name: str):
        try:
            await self.async_init()
            window = await self.browser.get(f"https://warthunder.com/en/community/userinfo/?nick={name}",
                                            new_window=True)
            await window.wait_for(selector="#GCM-Container", timeout=30)
            content = await window.get_content()
            await window.close()
            return self.analyze_html(content)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())

    @staticmethod
    def analyze_html(html: str) -> dict:
        data = {
            "nickname": "",
            "register_date": "",
            "player_level": 0,
            "clan_name": "",
            "clan_url": "",
            "avatar": "",
            "statistics": {
                "arcade": {
                    "victories": 0,
                    "completed_missions": 0,
                    "victories_battles_ratio": "0%",
                    "deaths": 0,
                    "lions_earned": 0,
                    "play_time": "0m",
                    "air_targets_destroyed": 0,
                    "ground_targets_destroyed": 0,
                    "naval_targets_destroyed": 0,
                    "aviation": {
                        "air_battles": 0,
                        "air_battles_fighters": 0,
                        "air_battles_bombers": 0,
                        "air_battles_attackers": 0,
                        "time_played_air_battles": "0m",
                        "time_played_fighter": "0m",
                        "time_played_bomber": "0m",
                        "time_played_attackers": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "ground": {
                        "ground_battles": 0,
                        "ground_battles_tanks": 0,
                        "ground_battles_spgs": 0,
                        "ground_battles_heavy_tanks": 0,
                        "ground_battles_spaa": 0,
                        "time_played_ground_battles": "0m",
                        "tank_battle_time": "0m",
                        "tank_destroyer_battle_time": "0m",
                        "heavy_tank_battle_time": "0m",
                        "spaa_battle_time": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "fleet": {
                        "naval_battles": 0,
                        "ship_battles": 0,
                        "motor_torpedo_boat_battles": 0,
                        "motor_gun_boat_battles": 0,
                        "motor_torpedo_gun_boat_battles": 0,
                        "sub_chaser_battles": 0,
                        "destroyer_battles": 0,
                        "naval_ferry_barge_battles": 0,
                        "time_played_naval": "0m",
                        "time_played_on_ship": "0m",
                        "time_played_on_motor_torpedo_boat": "0m",
                        "time_played_on_motor_gun_boat": "0m",
                        "time_played_on_motor_torpedo_gun_boat": "0m",
                        "time_played_on_sub_chaser": "0m",
                        "time_played_on_destroyer": "0m",
                        "time_played_on_naval_ferry_barge": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    }
                },
                "realistic": {
                    "victories": 0,
                    "completed_missions": 0,
                    "victories_battles_ratio": "0%",
                    "deaths": 0,
                    "lions_earned": 0,
                    "play_time": "0m",
                    "air_targets_destroyed": 0,
                    "ground_targets_destroyed": 0,
                    "naval_targets_destroyed": 0,
                    "aviation": {
                        "air_battles": 0,
                        "air_battles_fighters": 0,
                        "air_battles_bombers": 0,
                        "air_battles_attackers": 0,
                        "time_played_air_battles": "0m",
                        "time_played_fighter": "0m",
                        "time_played_bomber": "0m",
                        "time_played_attackers": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "ground": {
                        "ground_battles": 0,
                        "ground_battles_tanks": 0,
                        "ground_battles_spgs": 0,
                        "ground_battles_heavy_tanks": 0,
                        "ground_battles_spaa": 0,
                        "time_played_ground_battles": "0m",
                        "tank_battle_time": "0m",
                        "tank_destroyer_battle_time": "0m",
                        "heavy_tank_battle_time": "0m",
                        "spaa_battle_time": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "fleet": {
                        "naval_battles": 0,
                        "ship_battles": 0,
                        "motor_torpedo_boat_battles": 0,
                        "motor_gun_boat_battles": 0,
                        "motor_torpedo_gun_boat_battles": 0,
                        "sub_chaser_battles": 0,
                        "destroyer_battles": 0,
                        "naval_ferry_barge_battles": 0,
                        "time_played_naval": "0m",
                        "time_played_on_ship": "0m",
                        "time_played_on_motor_torpedo_boat": "0m",
                        "time_played_on_motor_gun_boat": "0m",
                        "time_played_on_motor_torpedo_gun_boat": "0m",
                        "time_played_on_sub_chaser": "0m",
                        "time_played_on_destroyer": "0m",
                        "time_played_on_naval_ferry_barge": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    }
                },
                "simulation": {
                    "victories": 0,
                    "completed_missions": 0,
                    "victories_battles_ratio": "0%",
                    "deaths": 0,
                    "lions_earned": 0,
                    "play_time": "0m",
                    "air_targets_destroyed": 0,
                    "ground_targets_destroyed": 0,
                    "naval_targets_destroyed": 0,
                    "aviation": {
                        "air_battles": 0,
                        "air_battles_fighters": 0,
                        "air_battles_bombers": 0,
                        "air_battles_attackers": 0,
                        "time_played_air_battles": "0m",
                        "time_played_fighter": "0m",
                        "time_played_bomber": "0m",
                        "time_played_attackers": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "ground": {
                        "ground_battles": 0,
                        "ground_battles_tanks": 0,
                        "ground_battles_spgs": 0,
                        "ground_battles_heavy_tanks": 0,
                        "ground_battles_spaa": 0,
                        "time_played_ground_battles": "0m",
                        "tank_battle_time": "0m",
                        "tank_destroyer_battle_time": "0m",
                        "heavy_tank_battle_time": "0m",
                        "spaa_battle_time": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    },
                    "fleet": {
                        "naval_battles": 0,
                        "ship_battles": 0,
                        "motor_torpedo_boat_battles": 0,
                        "motor_gun_boat_battles": 0,
                        "motor_torpedo_gun_boat_battles": 0,
                        "sub_chaser_battles": 0,
                        "destroyer_battles": 0,
                        "naval_ferry_barge_battles": 1,
                        "time_played_naval": "0m",
                        "time_played_on_ship": "0m",
                        "time_played_on_motor_torpedo_boat": "0m",
                        "time_played_on_motor_gun_boat": "0m",
                        "time_played_on_motor_torpedo_gun_boat": "0m",
                        "time_played_on_sub_chaser": "0m",
                        "time_played_on_destroyer": "0m",
                        "time_played_on_naval_ferry_barge": "0m",
                        "total_targets_destroyed": 0,
                        "air_targets_destroyed": 0,
                        "ground_targets_destroyed": 0,
                        "naval_targets_destroyed": 0
                    }
                }
            },
            "vehicles_and_rewards": {
                "USA": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "USSR": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "GreatBritain": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "Germany": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "Japan": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "Italy": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "France": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "China": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "Sweden": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                },
                "Israel": {
                    "owned_vehicles": 0,
                    "elite_vehicles": 0,
                    "medals": 0
                }
            }
        }
        try:
            soup = BeautifulSoup(html, "html.parser")

            output = {"code": 200,
                      "message": "Success",
                      "tip": "Fk cf!",
                      "data": data}

            # Get nickname while checking if the player exists
            res = soup.select("li.user-profile__data-nick")
            if len(res) == 0:
                output["code"] = 404
                output["message"] = "Player not found"
                output["tip"] = "The nickname is case sensitive. Please check the nickname and try again."
                return output

            data["nickname"] = res[0].get_text(strip=True)

            # Get player register date, player level, clan name and clan url
            res = soup.select("div.user-profile > ul > li")
            data["register_date"] = res[-1].get_text(strip=True)[18:]
            data["player_level"] = int(res[-2].get_text(strip=True)[6:])
            if len(res) == 5:  # has clan
                data["clan_name"] = res[1].get_text(strip=True)
                data["clan_url"] = f"https://warthunder.com{res[1].a.get('href', '')}"

            # Get player avatar
            res = soup.select("div.user-profile > div > img")
            data["avatar"] = res[0].get("src", "")

            # general statistics
            modes = ["arcade", "realistic", "simulation"]
            titles = ["victories", "completed_missions", "victories_battles_ratio", "deaths", "lions_earned",
                      "play_time", "air_targets_destroyed", "ground_targets_destroyed", "naval_targets_destroyed"]

            # general statistics: arcade
            res = soup.select(
                "div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.arcadeFightTab > li")
            for i in range(1, len(res)):
                stat = res[i].get_text(strip=True).replace(",", "")
                if stat.isdigit():
                    data["statistics"]["arcade"][titles[i - 1]] = int(stat)
                elif stat != "N/A":
                    data["statistics"]["arcade"][titles[i - 1]] = stat

            # general statistics: realistic
            res = soup.select(
                "div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.historyFightTab > li")
            for i in range(1, len(res)):
                stat = res[i].get_text(strip=True).replace(",", "")
                if stat.isdigit():
                    data["statistics"]["realistic"][titles[i - 1]] = int(stat)
                elif stat != "N/A":
                    data["statistics"]["realistic"][titles[i - 1]] = stat

            # general statistics: simulation
            res = soup.select(
                "div.community__user-rate.user-rate > div.user-profile__stat.user-stat > div > ul.user-stat__list.simulationFightTab > li")
            for i in range(1, len(res)):
                stat = res[i].get_text(strip=True).replace(",", "")
                if stat.isdigit():
                    data["statistics"]["simulation"][titles[i - 1]] = int(stat)
                elif stat != "N/A":
                    data["statistics"]["simulation"][titles[i - 1]] = stat

            # specific statistics
            three_modes = soup.select("div.user-rate__fightType > div > div.user-stat__list-row")

            # specific statistics: aviation
            titles = ["air_battles", "air_battles_fighters", "air_battles_bombers", "air_battles_attackers",
                      "time_played_air_battles", "time_played_fighter", "time_played_bomber", "time_played_attackers",
                      "total_targets_destroyed", "air_targets_destroyed", "ground_targets_destroyed",
                      "naval_targets_destroyed"]

            res = three_modes[0].select("ul.user-stat__list")[1:]
            for i in range(len(res)):
                stats = res[i].select("li")
                for j in range(len(stats)):
                    stat = stats[j].get_text(strip=True).replace(",", "")
                    if stat.isdigit():
                        data["statistics"][modes[i]]["aviation"][titles[j]] = int(stat)
                    elif stat != "N/A":
                        data["statistics"][modes[i]]["aviation"][titles[j]] = stat

            # specific statistics: ground
            titles = ["ground_battles", "ground_battles_tanks", "ground_battles_spgs", "ground_battles_heavy_tanks",
                      "ground_battles_spaa", "time_played_ground_battles", "tank_battle_time",
                      "tank_destroyer_battle_time", "heavy_tank_battle_time", "spaa_battle_time",
                      "total_targets_destroyed", "air_targets_destroyed", "ground_targets_destroyed",
                      "naval_targets_destroyed"]

            res = three_modes[1].select("ul.user-stat__list")[1:]
            for i in range(len(res)):
                stats = res[i].select("li")
                for j in range(len(stats)):
                    stat = stats[j].get_text(strip=True).replace(",", "")
                    if stat.isdigit():
                        data["statistics"][modes[i]]["ground"][titles[j]] = int(stat)
                    elif stat != "N/A":
                        data["statistics"][modes[i]]["ground"][titles[j]] = stat

            # specific statistics: fleet
            titles = ["naval_battles", "ship_battles", "motor_torpedo_boat_battles", "motor_gun_boat_battles",
                      "motor_torpedo_gun_boat_battles", "sub_chaser_battles", "destroyer_battles",
                      "naval_ferry_barge_battles", "time_played_naval", "time_played_on_ship",
                      "time_played_on_motor_torpedo_boat", "time_played_on_motor_gun_boat",
                      "time_played_on_motor_torpedo_gun_boat", "time_played_on_sub_chaser", "time_played_on_destroyer",
                      "time_played_on_naval_ferry_barge", "total_targets_destroyed", "air_targets_destroyed",
                      "ground_targets_destroyed", "naval_targets_destroyed"]

            res = three_modes[2].select("ul.user-stat__list")[1:]
            for i in range(len(res)):
                stats = res[i].select("li")
                for j in range(len(stats)):
                    stat = stats[j].get_text(strip=True).replace(",", "")
                    if stat.isdigit():
                        data["statistics"][modes[i]]["fleet"][titles[j]] = int(stat)
                    elif stat != "N/A":
                        data["statistics"][modes[i]]["fleet"][titles[j]] = stat

            # vehicles and rewards
            countries = ["USA", "USSR", "GreatBritain", "Germany", "Japan", "Italy", "France", "China", "Sweden",
                         "Israel"]

            # owned vehicles
            res = soup.select("div.user-profile__score.user-score > ul:nth-child(2) > li")
            for i in range(1, len(res)):
                country = countries[i - 1]
                data["vehicles_and_rewards"][country]["owned_vehicles"] = int(
                    res[i].get_text(strip=True).replace(",", ""))

            # elite vehicles
            res = soup.select("div.user-profile__score.user-score > ul:nth-child(3) > li")
            for i in range(1, len(res)):
                country = countries[i - 1]
                data["vehicles_and_rewards"][country]["elite_vehicles"] = int(
                    res[i].get_text(strip=True).replace(",", ""))

            # medals
            res = soup.select("div.user-profile__score.user-score > ul:nth-child(4) > li")
            for i in range(1, len(res)):
                country = countries[i - 1]
                data["vehicles_and_rewards"][country]["medals"] = int(res[i].get_text(strip=True).replace(",", ""))

            output["data"] = data
            return output

        except:
            return {"code": 500, "message": "Internal Server Error", "tip": "Please try again later."}
