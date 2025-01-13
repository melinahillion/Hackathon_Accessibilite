from playwright.sync_api import sync_playwright
import json
import time

def _scroll_infinite(page, container_selector, is_parent = False):
    previous_height = None
    scroll_attempts = 0
    max_attempts = 10  # Limiter les tentatives pour éviter une boucle infinie

    while scroll_attempts < max_attempts:
        # Obtenez la hauteur actuelle du conteneur
        if is_parent:
            current_height = page.evaluate(
                f"""
                () => {{
                    let element = document.querySelector('{container_selector}').parentNode.parentNode;
                    return element ? element.scrollHeight : null;
                }}
                """
            )
        else:
            current_height = page.evaluate(
                f"""
                () => {{
                    let element = document.querySelector('{container_selector}');
                    return element ? element.scrollHeight : null;
                }}
                """
            )

        if previous_height == current_height:
            # Si la hauteur n'a pas changé, incrémentez le compteur de tentatives
            scroll_attempts += 1
        else:
            # Réinitialisez le compteur de tentatives si de nouveaux contenus apparaissent
            scroll_attempts = 0

        # Scrollez jusqu'en bas du conteneur
        if is_parent:
            page.evaluate(
                f"""
                document.querySelector('{container_selector}').parentNode.parentNode.scrollTo(0, document.querySelector('{container_selector}').parentNode.parentNode.scrollHeight)
                """
            )
        else:
            page.evaluate(
                f"""
                document.querySelector('{container_selector}').scrollTo(0, document.querySelector('{container_selector}').scrollHeight)
                """
            )
        print(f'scrolled, height in pixels : {current_height}px')

        previous_height = current_height
        print('loop')
        time.sleep(1)  # Ajoutez un délai pour laisser le temps au contenu de se charger

    print("Défilement infini terminé ou contenu complet chargé. Scraping de tout le contenu de la page ...")
    page.screenshot(path="screenshot.png", full_page=True)


def scrape_google_reviews(query, output_file):
    with sync_playwright() as p:
        print('loading chrome')
        browser = p.chromium.launch(
            ignore_default_args = ["--headless"],
            args = [
                "--headless=new", 
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-gpu"
            ])

        context = browser.new_context()
        page = context.new_page()
        print('chrome loaded')

        # Open Google Maps
        page.goto("https://www.google.fr/maps")
        print('navigated')

        page.locator('button[aria-label="Tout accepter"]').first.click()
        print('clicked on cookies validation')
        # with open('page_source.html', 'w', encoding='utf-8') as file:
        #    file.write(page.content())

        # Search for the category in the city
        page.locator("#searchboxinput").fill(query)
        print('located')
        page.keyboard.press("Enter")
        print('entered')

        time.sleep(5)  # Wait for search results to load
        print('done waiting')

        results = []

        # Extract list of places with infinite scroll
        container_selector = 'div[aria-label*="Résultats pour"]'
        _scroll_infinite(page, container_selector)

        # Extrait les hébergements
        container = page.locator(container_selector).first
        places = container.locator('div[jsaction*="mouseover:pane"]').all()
        for place in places:
            name_selector = place.locator(".fontHeadlineSmall")
            if name_selector.count() > 0:
                name = name_selector.first.inner_text()
            else:
                continue

            link_to_place_selector = place.locator('a[jslog]')
            if link_to_place_selector.count() > 0:
                link_to_place = link_to_place_selector.first.get_attribute('href')
            else:
                continue

            rating_selector = place.locator('span[role="img"][aria-label*="étoile"]')
            if rating_selector.count() > 0:
                rating = rating_selector.first.inner_text()
            else:
                rating = None

            details = {
                "name": name,
                "rating": rating,
                "href": link_to_place,
                "comments": []
            }
            results.append(details)

        for idx, place in enumerate(results):
            try:
                # Navigate to place
                link_i = place['href']
                print(f'Processing {idx + 1} / {len(results)} : {link_i} ')
                page.goto(link_i)
                
                tab_avis_selector = page.locator('div.fontTitleSmall:has-text("Avis")')
                if (tab_avis_selector.count() == 0): 
                    print("No comments")
                    continue

                container_selector = 'div[data-review-id]'

                tab_avis_selector.first.click()
                element = page.wait_for_selector(container_selector, timeout=30000, state="visible")

                # Scroll
                _scroll_infinite(page, container_selector , True)
                #page.screenshot(path="screenshot.png", full_page=True)
                #with open('page_source.html', 'w', encoding='utf-8') as file:
                #    file.write(page.content())

                # Click sur les PLUS !
                for plus in container.locator('div[data-review-id] button[aria-label="Voir plus"]').all():
                    plus.click()
                print('Click on all PLUS')

                # Scrap comments
                results[idx]['comments'] = [el.inner_text() for el in page.locator('.MyEned').all()]
                print(f'Scraped {len(results[idx]['comments'])} comments !')
            except Exception as e:
                print(f'Error during scrap !! : ' + str(e))

        
        print('Storing ...')
        # Save results to a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print(f"Scraping complete. Data saved to {output_file}. I have scraped {len(results)} results !")

        # Close the browser
        browser.close()

# Usage
scrape_google_reviews(query="hébergement Blois", output_file="blois_accommodations_reviews.json")
