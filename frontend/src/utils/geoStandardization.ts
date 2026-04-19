const COUNTRY_ALIASES: Record<string, string> = {
  'united states': 'United States of America',
  usa: 'United States of America',
  us: 'United States of America',
  'czech republic': 'Czechia',
  macedonia: 'North Macedonia',
  macedon: 'North Macedonia',
  fyr: 'North Macedonia',
  'fyr of macedonia': 'North Macedonia',
  swaziland: 'Eswatini',
  palestina: 'Palestine',
  'republic of serbia': 'Serbia',
  'timor leste': 'East Timor',
  'timor leste democratic republic': 'East Timor',
  'timor-leste': 'East Timor',
  'cape verde': 'Cabo Verde',
  "cote d ivoire": 'Ivory Coast',
  'faroe islands': 'Faeroe Islands',
  'falkland islands': 'Falkland Islands',
  'british guiana': 'Guyana',
  rhodesia: 'Zimbabwe',
  'netherlands antilles': 'Curacao',
  ussr: 'Russia',
  'soviet union': 'Russia',
  yugoslavia: 'Serbia',
  czechoslovakia: 'Czechia',
  burma: 'Myanmar',
  persia: 'Iran',
  uk: 'United Kingdom',
  'great britain': 'United Kingdom',
  'england': 'United Kingdom',
  'scotland': 'United Kingdom',
  'wales': 'United Kingdom',
  'northern ireland': 'United Kingdom',
  'u k': 'United Kingdom',
  'u.k': 'United Kingdom',
  'u.k.': 'United Kingdom',
  'united kingdom of great britain and northern ireland': 'United Kingdom',
  'zaire': 'Democratic Republic of the Congo',
  'dr congo': 'Democratic Republic of the Congo',
  'congo kinshasa': 'Democratic Republic of the Congo',
  'democratic republic of congo': 'Democratic Republic of the Congo',
  'democratic republic of the congo': 'Democratic Republic of the Congo',
  'congo brazzaville': 'Republic of the Congo',
  'republic of congo': 'Republic of the Congo',
  'the gambia': 'Gambia',
  'gambia the': 'Gambia',
  'guinea bissau': 'Guinea-Bissau',
  'sao tome and principe': 'Sao Tome and Principe',
  'libyan arab jamahiriya': 'Libya',
  'greenland denmark': 'Greenland',
  'iceland republic of': 'Iceland',
  'bolivia plurinational state of': 'Bolivia',
  'venezuela bolivarian republic of': 'Venezuela',
  brasil: 'Brazil',
  'argentine republic': 'Argentina',
  'united republic of tanzania': 'Tanzania',
  'tanzania united republic of': 'Tanzania',
  // African countries and variations
  'djibouti': 'Djibouti',
  'mauritius': 'Mauritius',
  'seychelles': 'Seychelles',
  'comoros': 'Comoros',
  'côte d ivoire': 'Ivory Coast',
  'côte divoire': 'Ivory Coast',
  'cote divoire': 'Ivory Coast',
  'ivory coast': 'Ivory Coast',
  'cabo verde': 'Cabo Verde',
  'south sudan': 'South Sudan',
  'western sahara': 'Western Sahara',
  'reunion': 'Reunion',
  'mayotte': 'Mayotte',
  'canary islands': 'Spain',
  'madeira': 'Portugal',
  'republic of cameroon': 'Cameroon',
  'republic of gabon': 'Gabon',
  'republic of equatorial guinea': 'Equatorial Guinea',
  'central african republic': 'Central African Republic',
  'republic of congo': 'Republic of the Congo',
  'republic of south sudan': 'South Sudan',
  'republic of burundi': 'Burundi',
  'republic of rwanda': 'Rwanda',
  'republic of djibouti': 'Djibouti',
  'republic of mauritius': 'Mauritius',
  'somali republic': 'Somalia',
  'united republic of tanzania': 'Tanzania',
  'united kingdom of tanzania': 'Tanzania',
  'rupublika': 'Republic of the Congo',
  'peoples democratic republic': 'Peoples Democratic Republic of Algeria',
  'falkland islands south georgia and south sandwich islands': 'Falkland Islands',
  'curacao': 'Curacao',
};


const PROVINCE_ALIASES: Record<string, string> = {
  'nei mongol': 'Inner Mongolia',
  xizang: 'Tibet',
  "primor ye": 'Primorskiy Kray',
  chukot: 'Chukotka',
  sakha: 'Sakha Republic',
  khabarovsk: 'Khabarovskiy Kray',
  alsace: 'Grand Est',
  'champagne ardenne': 'Grand Est',
  lorraine: 'Grand Est',
  aquitaine: 'Nouvelle-Aquitaine',
  limousin: 'Nouvelle-Aquitaine',
  'poitou charentes': 'Nouvelle-Aquitaine',
  auvergne: 'Auvergne-Rhone-Alpes',
  'rhone alpes': 'Auvergne-Rhone-Alpes',
  'basse normandie': 'Normandie',
  'haute normandie': 'Normandie',
  'franche comte': 'Bourgogne-Franche-Comte',
  bourgogne: 'Bourgogne-Franche-Comte',
  'languedoc roussillon': 'Occitanie',
  'midi pyrenees': 'Occitanie',
  'nord pas de calais': 'Hauts-de-France',
  picardie: 'Hauts-de-France',
  'chaouia ouardigha': 'Casablanca-Settat',
  'doukkala abda': 'Casablanca-Settat',
  'gharb chrarda beni hssen': 'Fes-Meknes',
  'grand casablanca': 'Casablanca-Settat',
  'guelmim es semara': 'Guelmim-Oued Noun',
  'la youne boujdour sakia el hamra': 'Laayoune-Sakia El Hamra',
  'marrakech tensift al haouz': 'Marrakech-Safi',
  'meknes tafilalet': 'Fes-Meknes',
  'rabat sale zemmour zaer': 'Rabat-Sale-Kenitra',
  'souss massa draa': 'Souss-Massa',
  'tadla azilal': 'Beni Mellal-Khenifra',
  'tanger tetouan': 'Tanger-Tetouan-Al Hoceima',
  'taza al hoceima taounate': 'Tanger-Tetouan-Al Hoceima',
  'ben arous tunis sud': 'Ben Arous',
  'nct of delhi': 'Delhi',
  'd c': 'District of Columbia',
  'county durham': 'Durham',
  michoacan: 'Michoacan',
  'al qahirah': 'Cairo',
  'al isma iliyah': 'Ismailia',
  'as suways': 'Suez',
  cataluna: 'Catalonia',
  cataluña: 'Catalonia',
  england: 'England',
  scotland: 'Scotland',
  wales: 'Wales',
  'northern ireland': 'Northern Ireland',
  'capital region': 'Hofudborgarsvaedi',
  'west region': 'Vesturland',
  'south region': 'Sudurland',
  'north region': 'Nordurland Eystra',
  'east region': 'Austurland',
  'distrito federal': 'Distrito Capital',
  'santa cruz de la sierra': 'Santa Cruz',
};

export function normalizeGeoName(value: unknown): string {
  if (typeof value !== 'string') {
    return '';
  }

  // Fix common encoding corruptions (UTF-8 mojibake from Windows-1252 → UTF-8 issues)
  let text = value;
  const encodingFixes: Record<string, string> = {
    '¨ª': 'í',   // í (from mojibake)
    '¨¢': 'á',   // á
    '¨±': 'ñ',   // ñ
    '¨©': 'é',   // é
    '¨®': 'ò',   // ò
    '¨¤': 'à',   // à
    '¨§': 'ç',   // ç
    '¨¯': 'ô',   // ô
    '¨³': 'ó',   // ó
    '¨¹': 'ù',   // ù
    '¨º': 'ú',   // ú
    '¨°': 'ö',   // ö
    '¨¨': 'è',   // è
    '¨«': 'ê',   // ê
    '¨¼': 'ü',   // ü
    '¨¶': 'æ',   // æ
    '?': '',     // Remove question mark placeholders
  };
  Object.entries(encodingFixes).forEach(([broken, fixed]) => {
    text = text.split(broken).join(fixed);
  });

  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function standardizeCountryName(value: string | undefined): string | undefined {
  if (!value) {
    return value;
  }

  const normalized = normalizeGeoName(value);
  return COUNTRY_ALIASES[normalized] ?? value.trim();
}

export function standardizeProvinceName(value: string | undefined): string | undefined {
  if (!value) {
    return value;
  }

  const normalized = normalizeGeoName(value);
  return PROVINCE_ALIASES[normalized] ?? value.trim();
}

type PointWithGeoNames = {
  country?: string;
  province?: string;
};

export function standardizePointGeoNames<T extends PointWithGeoNames>(point: T): T {
  return {
    ...point,
    country: standardizeCountryName(point.country),
    province: standardizeProvinceName(point.province),
  };
}
