import tmlrScraper as tScrape
from PhoenixCodeScraper import run_violation_scraper


def main():
    houses = tScrape.borrow_from_api() # tScrape.read_from_file()
    violations = run_violation_scraper(houses)
    print("Stop")
    

if __name__ == "__main__":
    main()