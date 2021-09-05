"""
Download all Goldfish decks in a dictionary.

main()
    grab_links()
    scrape_deck_page()
        scrape_cards()
            deck_text_to_dict()
"""
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from . import MtgBoard, MtgDeck


def deck_text_to_dict(stringa: str) -> MtgBoard:
    """
    Convert plain text to dictionary. Text must be separated by \n and number of copies must be separated by ' ' from
    card names.
    :param stringa: '1 Card\n3 OtherCard\n...'
    :return: {'Card': 1, 'OtherCard': 3...}
    """
    decklist = MtgBoard()
    for line in stringa.splitlines():
        if len(line.strip()) > 0:
            copies, card = line.split(' ', 1)
            card = card.split('[')[0].split('<')[0].strip()
            decklist[card] = decklist.get(card, 0) + int(copies)
    return decklist


def grab_links(gf_html: str, clean=True) -> Dict[str, str]:
    """
    Return ORDERED dict of links to scrape; if param clean is True, decks named only after colours combinations are
        not included.
    :param gf_html: html page of goldfish metagame page for a specific format (can be full or partial page)
                          e.g.: https://www.mtggoldfish.com/metagame/modern/full#paper
    :param clean: True or anything else: if clean is not True, decks names like R, UW, etc. are not
                  scraped
    :return: dictionary of deck_names with their links {deck_name: deck_relative_link, ...}
    """
    if clean:
        print("WATCH OUT: decks with names such as WR and WRBG will not be scraped")

    # split at View More to avoid Budget Decks if program is scraping only partial page
    non_budget = gf_html.split("View More")[0]
    soup = BeautifulSoup(non_budget, "lxml")

    names = soup.find_all('span', {'class': 'deck-price-paper'})[1:]
    names_links = dict()
    permutations = {'W', 'U', 'B', 'R', 'G', 'WU', 'WB', 'WR', 'WG', 'UW', 'UB', 'UR', 'UG', 'BW', 'BU', 'BR', 'BG',
                    'RW', 'RU', 'RB', 'RG', 'GW', 'GU', 'GB', 'GR', 'WUB', 'WUR', 'WUG', 'WBU', 'WBR', 'WBG', 'WRU',
                    'WRB', 'WRG', 'WGU', 'WGB', 'WGR', 'UWB', 'UWR', 'UWG', 'UBW', 'UBR', 'UBG', 'URW', 'URB', 'URG',
                    'UGW', 'UGB', 'UGR', 'BWU', 'BWR', 'BWG', 'BUW', 'BUR', 'BUG', 'BRW', 'BRU', 'BRG', 'BGW', 'BGU',
                    'BGR', 'RWU', 'RWB', 'RWG', 'RUW', 'RUB', 'RUG', 'RBW', 'RBU', 'RBG', 'RGW', 'RGU', 'RGB', 'GWU',
                    'GWB', 'GWR', 'GUW', 'GUB', 'GUR', 'GBW', 'GBU', 'GBR', 'GRW', 'GRU', 'GRB', 'WUBR', 'WUBG', 'WURB',
                    'WURG', 'WUGB', 'WUGR', 'WBUR', 'WBUG', 'WBRU', 'WBRG', 'WBGU', 'WBGR', 'WRUB', 'WRUG', 'WRBU',
                    'WRBG', 'WRGU', 'WRGB', 'WGUB', 'WGUR', 'WGBU', 'WGBR', 'WGRU', 'WGRB', 'UWBR', 'UWBG', 'UWRB',
                    'UWRG', 'UWGB', 'UWGR', 'UBWR', 'UBWG', 'UBRW', 'UBRG', 'UBGW', 'UBGR', 'URWB', 'URWG', 'URBW',
                    'URBG', 'URGW', 'URGB', 'UGWB', 'UGWR', 'UGBW', 'UGBR', 'UGRW', 'UGRB', 'BWUR', 'BWUG', 'BWRU',
                    'BWRG', 'BWGU', 'BWGR', 'BUWR', 'BUWG', 'BURW', 'BURG', 'BUGW', 'BUGR', 'BRWU', 'BRWG', 'BRUW',
                    'BRUG', 'BRGW', 'BRGU', 'BGWU', 'BGWR', 'BGUW', 'BGUR', 'BGRW', 'BGRU', 'RWUB', 'RWUG', 'RWBU',
                    'RWBG', 'RWGU', 'RWGB', 'RUWB', 'RUWG', 'RUBW', 'RUBG', 'RUGW', 'RUGB', 'RBWU', 'RBWG', 'RBUW',
                    'RBUG', 'RBGW', 'RBGU', 'RGWU', 'RGWB', 'RGUW', 'RGUB', 'RGBW', 'RGBU', 'GWUB', 'GWUR', 'GWBU',
                    'GWBR', 'GWRU', 'GWRB', 'GUWB', 'GUWR', 'GUBW', 'GUBR', 'GURW', 'GURB', 'GBWU', 'GBWR', 'GBUW',
                    'GBUR', 'GBRW', 'GBRU', 'GRWU', 'GRWB', 'GRUW', 'GRUB', 'GRBW', 'GRBU', 'WUBRG', 'WUBGR', 'WURBG',
                    'WURGB', 'WUGBR', 'WUGRB', 'WBURG', 'WBUGR', 'WBRUG', 'WBRGU', 'WBGUR', 'WBGRU', 'WRUBG', 'WRUGB',
                    'WRBUG', 'WRBGU', 'WRGUB', 'WRGBU', 'WGUBR', 'WGURB', 'WGBUR', 'WGBRU', 'WGRUB', 'WGRBU', 'UWBRG',
                    'UWBGR', 'UWRBG', 'UWRGB', 'UWGBR', 'UWGRB', 'UBWRG', 'UBWGR', 'UBRWG', 'UBRGW', 'UBGWR', 'UBGRW',
                    'URWBG', 'URWGB', 'URBWG', 'URBGW', 'URGWB', 'URGBW', 'UGWBR', 'UGWRB', 'UGBWR', 'UGBRW', 'UGRWB',
                    'UGRBW', 'BWURG', 'BWUGR', 'BWRUG', 'BWRGU', 'BWGUR', 'BWGRU', 'BUWRG', 'BUWGR', 'BURWG', 'BURGW',
                    'BUGWR', 'BUGRW', 'BRWUG', 'BRWGU', 'BRUWG', 'BRUGW', 'BRGWU', 'BRGUW', 'BGWUR', 'BGWRU', 'BGUWR',
                    'BGURW', 'BGRWU', 'BGRUW', 'RWUBG', 'RWUGB', 'RWBUG', 'RWBGU', 'RWGUB', 'RWGBU', 'RUWBG', 'RUWGB',
                    'RUBWG', 'RUBGW', 'RUGWB', 'RUGBW', 'RBWUG', 'RBWGU', 'RBUWG', 'RBUGW', 'RBGWU', 'RBGUW', 'RGWUB',
                    'RGWBU', 'RGUWB', 'RGUBW', 'RGBWU', 'RGBUW', 'GWUBR', 'GWURB', 'GWBUR', 'GWBRU', 'GWRUB', 'GWRBU',
                    'GUWBR', 'GUWRB', 'GUBWR', 'GUBRW', 'GURWB', 'GURBW', 'GBWUR', 'GBWRU', 'GBUWR', 'GBURW', 'GBRWU',
                    'GBRUW', 'GRWUB', 'GRWBU', 'GRUWB', 'GRUBW', 'GRBWU', 'GRBUW'}

    for elem in names:
        name = elem.text.replace('\n', '')

        if name not in names_links and name != 'Other':
            # if deck name already present do NOT insert it in result dict
            if clean and name not in permutations:  # exclude decks with bad names
                names_links[name] = "https://www.mtggoldfish.com" + elem.a["href"]

            elif not clean:
                names_links[name] = "https://www.mtggoldfish.com" + elem.a["href"]
    return names_links


def scrape_cards(html_soup: BeautifulSoup) -> Tuple[MtgBoard, Optional[MtgBoard]]:
    """
    Scrape cards in deck list page.
    :param html_soup: BeautifulSoup of html deck page OF both mainboard or sideboard
    :return: tuple of dictionaries of deck cards ({"Mox Opal": 4, ...}, {"Galvanic Blast": 2, ...})
    """
    deck_plain_text = html_soup.find('input', {'id': "deck_input_deck"})['value']
    splitted_deck = deck_plain_text.split('sideboard')
    main_text = splitted_deck[0]
    if len(splitted_deck) > 1:
        side_text = splitted_deck[1]
        return deck_text_to_dict(main_text), deck_text_to_dict(side_text)
    return deck_text_to_dict(main_text), None


def scrape_deck_page(html_deck: str) -> (str, MtgBoard, MtgBoard):
    """
    Get Tuple with Deck Name, Mainboard dict and Sideboard dict from html of deck page.

    :param: html_deck: html page of deck e.g.: https://www.mtggoldfish.com/archetype/standard-jeskai-fires#paper
    :return: tuple (deck_name: str, mainboard: dict, sideboard: dict)
    """
    soup = BeautifulSoup(html_deck, "lxml")

    # find author, then get parent node. Easiest way I could find to exclude author from deck name.
    # Structure:
    # <h1 class ="title">
    #   Four - Color Omnath
    #   <span class ="author"> by VTCLA </span>
    # </h1>
    deck_name = soup.find("span", {"class": "author"}).previousSibling.replace('\n', '').strip()
    deck_name = deck_name.replace("/", "").replace("-", " ").replace("\n\nSuggest\xa0a\xa0Better\xa0Name", "").replace(
        "\nFix Archetype", "")

    for sign in ("[", "<", "{"):
        deck_name = deck_name.split(sign)[0]

    main, side = scrape_cards(soup)
    return deck_name, main, side


def main(formato: str, full=True) -> (Dict[str, int], Dict[str, int]):
    """
    Get dict of mains and dict of sides. 
    :formato: str (e.g.: "standard" or "modern")
    :full: bool, True for scraping all decks from /full#paper,
           False for scraping only first decks from /#paper url)
    :return:
    """
    mainboards = dict()
    sideboards = dict()

    url_start = "https://www.mtggoldfish.com/metagame/"
    url_end = "/full#paper" if full is True else "/#paper"
    url = url_start + formato + url_end
    print(f"Getting links from {url}")

    with requests.Session() as session:
        page = session.get(url)
        links = grab_links(page.text)  # .values()
        print(f"{len(links)} links grabbed!!\n")

        for link_name, link in tqdm(links.items()):
            # print(f"Getting data from:\n{link}")
            try:
                page = session.get(link).text
                name, mainb, side = scrape_deck_page(page)
                # from Nov 2020, name from grab_links is more correct than scrape_deck_page
                name = link_name
                if name in mainboards:
                    print(f"{name} is a CONFLICTING NAME and will not be saved.")
                elif len(mainb) == 0:
                    print(f"{name} has EMPTY MAINBOARD and will not be saved.")
                else:
                    mainboards[name] = mainb
                    sideboards[name] = side
            except TimeoutError:
                print("The connection FAILED due to a TimeOut Error.")
            except AttributeError as e:
                print("AttributeError", e, "at", url)
            except Exception as e:
                print(e, "\n", link, "will not be scraped")
                import pdb
                pdb.set_trace()
    return mainboards, sideboards


class MtgGoldfishScraper:
    def __init__(self, fullness=False):
        self.fullness = fullness

    def scrape_formats(self,
                       formats=(
                       'Standard', 'Modern', 'Pioneer', 'Pauper', 'Legacy', 'Vintage', 'Commander_1v1', 'Commander')
                       ):
        formats_type = type(formats)
        assert isinstance(formats, str), "formats should be an iterable but not a str"
        scraped = dict()
        scraped_sideboards = dict()

        for mtg_format in tqdm(formats):
            mainboards, sideboards = self.scrape_format(mtg_format.lower())
            scraped[mtg_format] = mainboards
            for deck_name, sideboard in sideboards.items():
                if sideboard is not None:
                    scraped_sideboards[deck_name] = sideboard

        return scraped, scraped_sideboards

    def scrape_format(self, mtg_format, fullness=None):
        if fullness is None:
            fullness = self.fullness
        return main(mtg_format, fullness)

    def scrape_page(self):
        pass


if __name__ == '__main__':
    import pdb

    example_url = "https://www.mtggoldfish.com/metagame/standard/full#paper"
    response = requests.get(example_url)
    links = grab_links(response.text)

    pdb.set_trace()
    page_html = requests.get(list(links.values())[0]).text
    decklist = scrape_deck_page(page_html)
    print(decklist)
