from anticaptchaofficial.recaptchav3proxyless import *
from decouple import config

def solve_captcha(url):

    solver = recaptchaV3Proxyless()
    solver.set_verbose(1)
    solver.set_key(config('API_KEY'))
    solver.set_website_url(url)
    solver.set_website_key(config('SITE_KEY'))
    solver.set_page_action("home_page")
    solver.set_min_score(0.9)

    # Specify softId to earn 10% commission with your app.
    # Get your softId here: https://anti-captcha.com/clients/tools/devcenter
    solver.set_soft_id(0)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        print("g-response: "+g_response)
    else:
        print("task finished with error "+solver.error_code)
    