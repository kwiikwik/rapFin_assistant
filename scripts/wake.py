"""Visite l'appli Streamlit avec un vrai navigateur pour l'empêcher de dormir."""
import os
import re

from playwright.sync_api import sync_playwright

# L'URL de ton appli est passée par le workflow GitHub Actions
URL = os.environ["STREAMLIT_URL"]

with sync_playwright() as p:
    # Lance un Chromium invisible (sans fenêtre)
    browser = p.chromium.launch()
    page = browser.new_page()

    print(f"Visite de {URL} ...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(5_000)  # laisse la page se charger

    # Si l'appli dort, Streamlit affiche un bouton "Yes, get this app back up!"
    bouton = page.get_by_role("button", name=re.compile("get this app back up", re.I))

    if bouton.count() > 0:
        print("L'appli dormait : clic sur le bouton de réveil.")
        bouton.first.click()
        page.wait_for_timeout(60_000)  # laisse 1 min à l'appli pour redémarrer
        print("Réveil lancé.")
    else:
        print("L'appli est déjà éveillée : visite enregistrée.")
        page.wait_for_timeout(15_000)  # reste un peu pour que la visite compte

    browser.close()
