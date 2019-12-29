import cssselect
import requests
from lxml import html as HTML, etree
from fake_useragent import UserAgent
from dataclasses import dataclass
from pyfiglet import Figlet
from pathlib import Path

URL = ['http://gen.lib.rus.ec/']
DEST_PATH_PREFIX = '/mnt/c/Users/Resillience/Books/'

class BookEntry:
    index: int
    author: str
    series: str
    title: str
    lang: str
    format: str
    mirrors: list
    author_link: str
    title_link: str
    book_link: str

def get_url_string(genre, search):
    search = '+'.join(search.split())
    # return f'http://gen.lib.rus.ec/search.php?req={search}&open=0&res=100'
    return URL[0] + genre + '/?q=' + '+'.join(search.split())

def get_html(url):
    try:
        print(f'\rhitting url {url}', end='\r')
        ua = UserAgent()
        header = {'User-Agent':str(ua.chrome)}
        resp = requests.get(url, headers=header)
        if resp.status_code == 200:
            return resp
        else:
            raise ValueError('html error, some probs while hitting url: ' + url)
    except Exception as e:
        print(e)
        r = input('quit?: q or \'\'\n')
        if r.strip() == 'q':
            import sys
            sys.exit(1)
        else:
            return get_html(url)

def parse_link_td(a_link):
    first, _, second, _ = a_link
    return (first.text, second.text)

def get_book_list(html):
    trs = html.xpath('//tr')
    book_list = []
    for row in trs:
        book = BookEntry()
        cols = row.xpath('.//td')
        # print(etree.tostring(row, pretty_print=True))
        author_data = list(cols[0].iterlinks())
        if len(author_data) != 0:
            a, _, l, _ = author_data[0]
            book.author = a.text.strip() if a is not None else None
            book.author_link = l
        else:
            book.author = None
            book.author_link = None
        book.series = cols[1].text
        title_data = list(cols[2].iterlinks())
        if len(title_data) != 0:
            t, _, l, _ = title_data[0]
            book.title = t.text.strip() if t is not None else None
            book.title_link = l
        else:
            book.title = None
            book.title_link = None
        book.lang = cols[3].text.strip()
        book.format = cols[4].text.strip()
        mirrors = list(cols[5].iterlinks())
        book.mirrors = {}
        for mirror in mirrors:
            name, _, link, _ = mirror
            book.mirrors[name.text.strip()] = link
        book_list.append(book)
        # print('## book is ', book.__dict__)

    return book_list

def get_table(books):
    from tabulate import tabulate
    take_columns = ['author', 'series', 'title', 'format', 'lang']
    data = []
    for index, book in enumerate(books):
        row = []
        for key in take_columns:
            row.append(book.__dict__.get(key, None))
        row = row + [', '.join([name for name in book.mirrors])]
        data.append([index] + row)
        book.index = index
    take_columns = ['index'] + take_columns + ['mirrors']
    sho = tabulate(data, headers=take_columns, tablefmt="standard")
    print('\n' + sho)
    return sho

def get_book_by_index(books, index):
    valid = [book for book in books if book.index == index]
    if len(valid) == 0:
        return None
    else:
        return valid[0]

def get_mirror_by_num(book, num):
    mirrors = book.mirrors
    return mirrors.get(f'[{num}]', None)

def from_get_page(url):
    body = get_html(url).text
    html = HTML.fromstring(body)
    links = list(html.iterlinks())
    if len(links) == 0:
        return None
    just_name = Path(url).parent.parent
    target = links[1]
    do_url = target[2]
    duh = str(just_name) + do_url
    return duh
    
def save_body(body, filename):
    filepath = DEST_PATH_PREFIX + filename
    print('saving at: ', filepath)
    with open(filepath, 'wb') as f:
        f.write(body)

def runner(books, table):
    HELP = """
    USAGE
    [index] [mirror (default=1)]

    OPTIONS
    h: help
    p: print table
    s: search with new query
    q: quit
    """
    while True:
        d = input('h: shows help\n')
        """ i get 2 3"""
        if d.strip() == 'h' or d.strip() == '?':
            print(HELP)
            continue
        if d.strip() == 'p':
            print(table)
            continue
        if d.strip() == 'q':
            import sys
            sys.exit(1)
        if d.strip() == 's':
            get_books_tables()
        if not d.strip().split()[0].isdigit():
            continue

        if len(d.split()) == 1:
            index, mirror = d, 1
        else:
            index, mirror = d.split()
        index = int(index.strip())
        book = get_book_by_index(books, index)
        if book != None:
            mirror = get_mirror_by_num(book, mirror)
            get_url = from_get_page(mirror)
            get_url = get_url.replace('http:/', 'http://')
            fileformat = str(Path(get_url).suffix)
            filename = book.title.lower().replace(' ', '_')
            filename = filename + fileformat
            body = get_html(get_url).content
            save_body(body, filename)
        # print(f' book is {book.__dict__} and mirror is {mirror}')
        
def get_books_tables():
    print(Figlet('slant').renderText('fiction libgen.ru'))
    search = input('search string? : ').strip()
    if search == '':
        search = 'east of eden'
    default_genre = 'fiction' # other page seems to have different syntax
    #genre = input(f'genre (default={default_genre})? : ').strip()
    #if genre == '':
    genre = default_genre
    url = get_url_string(genre, search)
    body = get_html(url).text
    html = HTML.fromstring(body)
    books = get_book_list(html)
    table = get_table(books)
    runner(books, table)

get_books_tables()
