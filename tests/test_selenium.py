import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.slow
class TestUpdateHitCount(StaticLiveServerTestCase):
    def setUp(self):
        options = Options()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox()
        self.delay = 10

    def tearDown(self):
        self.selenium.quit()

    def test_ajax_hit(self):
        url = reverse("ajax", args=[1])
        self.selenium.get("%s%s" % (self.live_server_url, url))

        wait = WebDriverWait(self.selenium, self.delay)
        response = wait.until(EC.text_to_be_present_in_element((By.ID, "hit-counted-value"), "true"))

        self.assertIs(response, True)
