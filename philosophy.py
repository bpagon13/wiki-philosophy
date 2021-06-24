import argparse
import requests

from bs4 import BeautifulSoup

MAX_HOPS = 100

WIKIPEDIA_WIKI_START = '/wiki'
WIKIPEDIA_URL_START = 'https://en.wikipedia.org'
WIKIPEDIA_PHILOSOPHY_PAGE = 'https://en.wikipedia.org/wiki/Philosophy'

STATS_PRINT_COL_LENGTH = 35

def find_path(starting_url: str) -> tuple[tuple[str, ...], int]:
    """Find a path from the given Wikipedia page to the philosophy page.

    Args:
        starting_url (str): The Wikipedia page to start at.

    Returns:
        tuple[tuple[str, ...], int]: The path taken from the starting
            page to the philosophy page, if found, otherwise an empty
            tuple. Also, the number of URLs explored.
    """
    seen_urls = set()
    to_explore = [(starting_url,)]
    for hop_num in range(1, MAX_HOPS + 1):
        next_explore = []
        for path in to_explore:
            html_text = ''
            while len(html_text) == 0:
                try:
                    html_text = requests.get(path[-1]).text
                except Exception as e:
                    # Retry by emptying html_text
                    html_text = ''
                    # NOTE would add some logging here for HTTP retries instead
                    # of a print statement
                    print(f"Requesting URL {path[-1]} gave an error:")
                    print(e)
                    print("Retrying...")

            soup = BeautifulSoup(html_text, 'html.parser')
            for link in soup.find_all('a'):
                url = link.get('href')
                # Sometimes there's no href so need to make sure url isn't None
                if url and url.startswith(WIKIPEDIA_WIKI_START):
                    url = f"{WIKIPEDIA_URL_START}{url}"
                    if url == WIKIPEDIA_PHILOSOPHY_PAGE:
                        return path + (url,), len(seen_urls)

                    if url not in seen_urls:
                        seen_urls.add(url)
                        new_path = path + (url,)
                        next_explore.append(new_path)
        to_explore = next_explore
        print(f"Statistics for {hop_num} hop(s):")
        print(f"{'Number of URLs seen so far:':{STATS_PRINT_COL_LENGTH}} {len(seen_urls)}")
        print(f"{'Number of URLs to explore next hop:':{STATS_PRINT_COL_LENGTH}} {len(to_explore)}")
        print()
    return tuple(), len(seen_urls)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Find the Wikipedia philosophy page")
        parser.add_argument("starting_page", help="The Wikipedia page to start at")
        args = parser.parse_args()

        if args.starting_page.startswith(f"{WIKIPEDIA_URL_START}{WIKIPEDIA_WIKI_START}"):
            if args.starting_page == WIKIPEDIA_PHILOSOPHY_PAGE:
                path = (args.starting_page,)
            else:
                path, num_urls_explored = find_path(args.starting_page)
                print(f"Explored {num_urls_explored} URLs")
                print()

            if len(path) > 0:
                print("Found a path to Philosophy:")
                print("---------------------------")
                print()
                for url in path:
                    print(url)
                print(f"{len(path) - 1} hops")
            else:
                print(f"Couldn't find a path to Philosophy in {MAX_HOPS} hops")
        else:
            print(f"The site [{args.starting_page}] isn't a Wikipedia page")
    except KeyboardInterrupt:
        print()
        print("Keyboard interrupt during execution, shutting down...")
