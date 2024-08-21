import logging
import time


class CloudflareBypasser:
    def __init__(self, tab, max_retries=-1):
        self.tab = tab
        self.max_retries = max_retries

    def search_recursively_shadow_root_with_iframe(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None

    def locate_cf_button(self):
        button = None
        eles = self.tab.eles("tag:input")
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break

        if button:
            return button
        else:
            # If the button is not found, search it recursively
            logging.warning("Basic search failed. Searching for button recursively.")
            ele = self.tab.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                button = self.search_recursively_shadow_root_with_cf_input(iframe("tag:body"))
            else:
                logging.warning("Iframe not found. Button search failed.")
            return button

    def click_verification_button(self):
        try:
            button = self.locate_cf_button()
            if button:
                logging.info("Verification button found. Attempting to click.")
                button.click()
            else:
                logging.warning("Verification button not found.")

        except Exception as e:
            logging.warning(f"Error clicking verification button: {e}")

    def is_bypassed(self):
        try:
            title = self.tab.html
            return "Verifying you are human" not in title
        except Exception as e:
            logging.warning(f"Error checking page title: {e}")
            return False

    def bypass(self, name):
        logging.info(f"{name} : Attempting to bypass CF")
        try_count = 0

        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                logging.info(f"{name} : Exceeded maximum retries. Bypass failed")
                break

            logging.info(f"{name} : Attempt {try_count + 1}")

            try_count += 1
            time.sleep(2)

        if self.is_bypassed():
            logging.info(f"{name} : Bypass successful")
        else:
            logging.info(f"{name} : Bypass failed")
