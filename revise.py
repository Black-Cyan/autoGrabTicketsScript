from DrissionPage import ChromiumPage
from DrissionPage.common import Keys

needDown = ['longhui','beijingxi']
dp = ChromiumPage()

def need_revise(city):
    for c in needDown:
        if city == c:
            dp.ele('css:#toStationText').input(Keys.DOWN)
            break
