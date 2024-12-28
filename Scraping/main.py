from playwright.sync_api import sync_playwright
import json
import time

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

        previous_height = None
        scroll_attempts = 0
        max_attempts = 10  # Limiter les tentatives pour éviter une boucle infinie

        while scroll_attempts < max_attempts:
            # Obtenez la hauteur actuelle du conteneur
            current_height = page.evaluate(
                f"""
                () => {{
                    const element = document.querySelector('{container_selector}');
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
            page.evaluate(
                f"""
                document.querySelector('{container_selector}').scrollTo(0, document.querySelector('{container_selector}').scrollHeight)
                """
            )
            print(f'srcolled, height in pixels : {current_height}px')

            previous_height = current_height
            time.sleep(1)  # Ajoutez un délai pour laisser le temps au contenu de se charger

        print("Défilement infini terminé ou contenu complet chargé. Scraping de tout le contenu de la page ...")

        # Extrait les hébergements
        container = page.locator(container_selector).first
        places = container.locator('div[jsaction*="mouseover:pane"]').all()
        for place in places:
            try:
                name = place.locator(".fontHeadlineSmall").first.inner_text()
                try:
                    rating = place.locator('span[role="img"][aria-label*="étoile"]').first.inner_text()
                except Exception:
                    rating = None

                details = {
                    "name": name,
                    "rating": rating
                }
                results.append(details)
            except Exception as e:
                print(f"Error extracting place details: {e}")
        
        print('Storing ...')
        # Save results to a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print(f"Scraping complete. Data saved to {output_file}. I have scraped {len(results)} results !")

        # Close the browser
        browser.close()

# Usage
scrape_google_reviews(query="hébergement Blois", output_file="blois_accommodations_reviews.json")
