import re
import urllib.parse

TRUCK_TERMS = {
    'trucks', 'gruzavija', 'kamioni', 'nakladni-automobily', 'lastbiler',
    'vrachtwagens', 'veoautod', 'kuorma-autot', 'camions', 'lkws',
    'teherautok', 'vorubilar', 'truk', 'kravas-auto', 'sunkvejimiai',
    'ciezarowki', 'camioane', 'gruzoviki', 'tovornjaki', 'kamyonlar',
    'vantazivki', 'camiones', 'camion', 'trak', 'lastebiler',
    'camioes', 'lastbilar', 'kamiony'
}

SPARE_PARTS_TERMS = {
    'reservedeler', 'spare-parts', 'nahradne-diely', 'varahlutir', 'ersatzteile',
    'piese-de-schimb', 'zapchastki', 'alat-ganti', 'rezervni-deli', 'zapchastini',
    'rezervni-chasti', 'nahradni-dily', 'varuosad', 'rezervni_dijelovi', 'suku-cadang',
    'pecas-sobresselentes', 'rezervni-delovi', 'yedek-parcalar', 'reserveonderdelen',
    'pezzi-di-ricambio', 'pieces-detachees', 'zapchasti', 'rezervni-dijelovi',
    'potlkatreszek', 'czesci-zamienne', 'reservdelar', 'repuestos', 'reservedele',
    'varaosat', 'atsargines-dalys', 'rezerves-dalas'
}

EXCEPTIONS = {
    'contact', 'faq', 'sale', 'info', 'delivery', 'cart', 'ale',
    'mapco', 'partner', 'original', 'page', 'track', 'kontakt'
}

REFRIGERANT_PATTERN = re.compile(r'^(gas/)?r\d+[a-z0-9]*/?$', re.IGNORECASE)

def classify_url(url, brands_set=None):
    """
    Возвращает строку типа: '1_Языковая папка', '2_Карточка товара' и т.д.
    Если ничего не подошло — '16_Неопределённый тип'.
    """

    if not url:
        return '16_Неопределённый тип'

    if ('?' in url or '#' in url) and '?ft=1' not in url:
        return '16_Неопределённый тип'

    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip('/')

    # 1. Главная
    if path == '':
        return '17_Главная страница'

    parts = [p for p in path.split('/') if p]

    # 2. Языковая папка
    if len(parts) >= 1 and re.match(r'^[a-zA-Z]{2}$', parts[0]):
        return '1_Языковая папка'

    # 3. Список товаров - новый каталог
    if '?ft=1' in url:
        return '15_Список товаров - новый каталог'

    # 4. Карточка товара
    if '/kataloog/varuosa/' in path.lower():
        return '2_Карточка товара'

    if len(parts) == 3:
        if parts[0].lower() in SPARE_PARTS_TERMS and parts[1].lower() == 'varuosa':
            return '2_Карточка товара'

    # 5. Грузовики
    if any(f'/{term}/' in path.lower() for term in TRUCK_TERMS):
        return '6_Страница грузовых автомобилей'

    # 6. Мото
    if '/moto/' in path.lower():
        return '7_Страница мотоциклов'

    # 7. Спецтехника
    if '/special/' in path.lower():
        return '8_Страница спецтехники'

    # 8. Оригинальная запчасть
    if '/original/' in path.lower():
        return '13_Оригинальная запчасть'

    # 9. Хладагент
    joined_path = '/'.join(parts)
    if REFRIGERANT_PATTERN.match(joined_path):
        return '14_Хладагент'

    # 10. Основная категория
    if len(parts) == 1:
        part_lower = parts[0].lower()
        if part_lower in EXCEPTIONS or any(exc in part_lower for exc in EXCEPTIONS):
            return '16_Неопределённый тип'
        else:
            return '12_Основная категория запчастей'

    # 11. Выбор серии
    if '/model/' in path.lower():
        return '18_Выбор серии авто'

    # Для брендов
    import re
    def process_brand(b):
        b = re.sub(r'\s*\(.*?\)', '', b)
        b = b.replace('&', '-')
        b = re.sub(r'[\s_/]+', '-', b)
        b = b.replace('.', '')
        return b.lower()

    if brands_set is None:
        brands_set = set()

    processed_parts = [re.sub(r'[\s_/]+', '-', p.lower()).replace('.', '').replace('&', '-') for p in parts]

    if (len(processed_parts) >= 2 and 
        processed_parts[0] in [t.lower() for t in SPARE_PARTS_TERMS]):

        second_part = process_brand(processed_parts[1])

        if len(processed_parts) == 2 and second_part in brands_set:
            return '10_Выбор модели'

        if len(processed_parts) == 2 and second_part not in brands_set:
            return '11_Подкатегория запчастей_страница выбора авто'

        if len(processed_parts) == 3 and second_part in brands_set:
            return '9_Супергруппа'

        if (len(processed_parts) == 3 and 
            process_brand(processed_parts[2]) in brands_set and 
            second_part not in brands_set):
            return '5_Лендинг категории марки'

        if len(processed_parts) == 5 and second_part in brands_set:
            return '3_Список товаров для модификации авто'

        if len(processed_parts) == 4 and second_part in brands_set:
            return '4_Список товаров'

    return '16_Неопределённый тип'
