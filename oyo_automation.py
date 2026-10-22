from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time


# ============================================================
# 1. START BROWSER
# ============================================================

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

print("Opening OYO...")

driver.get("https://www.oyorooms.com/")

time.sleep(5)


# ============================================================
# 2. SELECT GOA
# ============================================================

print("Selecting Goa, India...")

try:

    location_box = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input")
        )
    )

    location_box.click()
    location_box.clear()
    location_box.send_keys("Goa, India")

    time.sleep(2)

    goa_option = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[normalize-space()='Goa, India']"
            )
        )
    )

    goa_option.click()

    print("Goa selected successfully!")

except Exception as e:

    print("ERROR selecting Goa:")
    print(e)

    input("Press Enter to close...")
    driver.quit()
    exit()


# ============================================================
# 3. DATE RANGE
# ============================================================

date_range = "10 Sep 2026 - 11 Sep 2026"

print("Date range:", date_range)


# ============================================================
# 4. CLICK SEARCH
# ============================================================

print("Clicking Search...")

try:

    search_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Search']"
            )
        )
    )

    search_button.click()

    print("Search clicked!")

except Exception as e:

    print("ERROR clicking Search:")
    print(e)

    input("Press Enter to close...")
    driver.quit()
    exit()


# ============================================================
# 5. WAIT FOR LISTING PAGE
# ============================================================

print("Waiting for hotel listing page...")

time.sleep(8)

print("Listing page loaded.")

print("Current URL:")
print(driver.current_url)


# ============================================================
# 6. COLLECT HOTELS + LISTING AVAILABILITY
# ============================================================

print("\nCollecting hotels from listing page...")

hotels = []

try:

    # Find links that look like OYO hotel detail links
    all_links = driver.find_elements(
        By.TAG_NAME,
        "a"
    )

    for link in all_links:

        href = link.get_attribute("href")
        hotel_name = link.text.strip()

        # Skip links without useful information
        if not href or not hotel_name:
            continue

        # We only want OYO hotel detail links.
        # Most OYO hotel URLs contain a numeric hotel ID.
        last_part = href.rstrip("/").split("/")[-1]

        if not last_part.isdigit():
            continue

        # ----------------------------------------------------
        # Find the hotel card containing this hotel
        # ----------------------------------------------------

        try:

            hotel_card = link.find_element(
                By.XPATH,
                "./ancestor::div[.//*[contains(normalize-space(), 'Book Now') or contains(normalize-space(), 'Sold Out')]][1]"
            )

            card_text = hotel_card.text.strip()

        except Exception:

            card_text = link.find_element(
                By.XPATH,
                "./ancestor::div[1]"
            ).text.strip()


        # ----------------------------------------------------
        # Check listing availability
        # ----------------------------------------------------

        if "Book Now" in card_text:

            listing_available = True

        elif "Sold Out" in card_text:

            listing_available = False

        else:

            listing_available = None


        # ----------------------------------------------------
        # Save hotel information
        # ----------------------------------------------------

        hotels.append(
            {
                "hotel_name": hotel_name,
                "url": href,
                "listing_available": listing_available
            }
        )


except Exception as e:

    print("ERROR collecting hotels:")
    print(e)


# ============================================================
# 7. REMOVE DUPLICATES
# ============================================================

unique_hotels = []

seen_urls = set()

for hotel in hotels:

    if hotel["url"] not in seen_urls:

        seen_urls.add(hotel["url"])

        unique_hotels.append(hotel)


hotels = unique_hotels


print("\nTotal hotels found:", len(hotels))


# ============================================================
# 8. SHOW WHAT WE FOUND
# ============================================================

print("\nHotels found on listing page:")

for hotel in hotels:

    print(
        hotel["hotel_name"],
        "→",
        hotel["listing_available"]
    )


# ============================================================
# 9. TEST ONLY FIRST 5 HOTELS
# ============================================================

hotels = hotels[:5]

print("\nTesting first", len(hotels), "hotels.")


# ============================================================
# 10. CHECK INDIVIDUAL HOTEL PAGES
# ============================================================

results = []


for index, hotel in enumerate(hotels, start=1):

    print("\n========================================")
    print("HOTEL", index)
    print("========================================")

    hotel_name = hotel["hotel_name"]

    hotel_url = hotel["url"]

    listing_available = hotel["listing_available"]


    print("Hotel:", hotel_name)

    print(
        "Listing availability:",
        listing_available
    )


    # --------------------------------------------------------
    # Open hotel page
    # --------------------------------------------------------

    print("Opening hotel page...")

    try:

        driver.get(hotel_url)

        time.sleep(5)

        # Get all visible page text
        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text


        # ----------------------------------------------------
        # Check hotel page availability
        # ----------------------------------------------------

        if "Continue to Book" in page_text:

            hotel_page_available = True

        elif "Sold Out" in page_text:

            hotel_page_available = False

        else:

            hotel_page_available = None


        print(
            "Hotel page availability:",
            hotel_page_available
        )


    except Exception as e:

        print(
            "ERROR opening hotel page:",
            e
        )

        hotel_page_available = None


    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    results.append(
        {
            "hotel_name": hotel_name,

            "date_range": date_range,

            "isAvailableOnListing": listing_available,

            "isAvailableOnHotelPage": hotel_page_available
        }
    )


# ============================================================
# 11. CREATE CSV
# ============================================================

print("\nCreating CSV...")


with open(
    "oyo_hotels.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "hotel_name",
            "date_range",
            "isAvailableOnListing",
            "isAvailableOnHotelPage"
        ]
    )

    writer.writeheader()

    writer.writerows(results)


# ============================================================
# 12. DISPLAY FINAL RESULTS
# ============================================================

print("\n\n========================================")
print("FINAL RESULTS")
print("========================================")


for result in results:

    print(
        result["hotel_name"],
        "| Listing:",
        result["isAvailableOnListing"],
        "| Hotel Page:",
        result["isAvailableOnHotelPage"]
    )


print("\nCSV created successfully!")

print(
    "File: oyo_hotels.csv"
)


input(
    "\nPress Enter to close the browser..."
)

driver.quit()