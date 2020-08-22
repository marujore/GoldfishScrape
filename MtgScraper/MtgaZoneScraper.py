from bs4 import BeautifulSoup


standard_url = 'https://mtgazone.com/metagame/standard'
historic_url = 'https://mtgazone.com/metagame/historic'


def grab_links(mtgazone_html: str) -> dict:
    """
    Return dict name: link (standard, historic) of ORDERED links to scrape.
    :param mtgazone_html: html page of mtgazone metagame page for all formats
    :return: dictionary {deck_name: deck_relative_link, ...} of relative format (either standard or historic)
    """
    soup = BeautifulSoup(mtgazone_html, 'lxml')
    dfs = list()
    # import pdb; pdb.set_trace()
    for el in soup.find_all('table'):  # first table is empty
        records = []
        for tr in el.findAll("tr"):
            ths = tr.findAll("th")
            if ths == []:
                trs = tr.findAll("td")
                record = []
                for each in trs:
                    if each.text == 'Decks':
                        link = each.find('a')['href']
                        # change relative links to absolute links
                        link = link if link.startswith('https://mtgazone.com') else 'https://mtgazone.com' + link
                        record.append(link)
                    record.append(each.text)      
                records.append(record)
        dfs.append(records)

    # Third elements are names, fifths are links.
    formats = list()
    for formato in dfs:
        links = {rec[3]: rec[5] for rec in formato}
        formats.append(links)
    return formats[0]


def get_main_or_side(main_or_side_soup):
    deck = dict()
    for el in main_or_side_soup.find_all('span', {'class':"wp-streamdecker-tooltip"}):
        copies = int(el.find('div', {'class': "card-qty"}).text)
        name = el.find('div', {'class': "card-name"}).text
        name = name.replace('/', ' // ')
        deck[name] = copies
    return deck


def get_mtgazone_deck(mtgazone_deck_html) -> tuple:
    soup = BeautifulSoup(mtgazone_deck_html, 'lxml')
    main = soup.find('div', {'class': "streamdecker-main-deck"})
    side = soup.find('div', {'class': "streamdecker-sideboard"})
    if main is None and side is None:
        return None, None
    if side is None:                                    # for decks without sideboard
        return get_main_or_side(main), {}
    return get_main_or_side(main), get_main_or_side(side)


if __name__ == "__main__":
    import requests

    response = requests.get(standard_url).text
    mtgazone_standard_links = grab_links(response)
    print(mtgazone_standard_links)