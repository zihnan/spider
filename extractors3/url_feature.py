import re
import requests
from extractor import Extractor
class URLExtractor(Extractor):
    def __init__(self, url):
        self.url = url
        self.features = [getattr(self,i) for i in dir(self.__class__) if i.startswith('get') and 'get_url' not in i and 'get_domain_name' not in i]
        
    def _get_keywords(self):
        temp = []
        shift = 0
        if self.is_ip_address():
            shift = len(self.get_domain_name(self.url))
            
        parameters = self.url[self.url.find('//') + 2 +shift:]

        if parameters.find('?') > -1:
            temp_parameters = parameters.split('?')
            parameters = temp_parameters[0]
            temp_parameters = temp_parameters[1:]
            
            for i in temp_parameters:
                if i.find("&") > -1:
                    temp += i.split('&')
        
        if parameters.find('/') > -1:
            for s in parameters.split('/'):
                if s.find('.') > -1:
                    temp += s.split('.')
                elif s.find('-') > -1:
                    temp += s.split('-')
                else:
                    temp.append(s)
                    
        temp_set = set(temp)
                
        return set([i for i in temp_set if not (i.startswith('htm') or i.startswith('php') or i == 'www')])
        
    # New Hybrid Features
    def _get_without_parameter(self):
        quest_mark = self.url.find('?')
        if quest_mark > 0:
            url = self.url[:quest_mark]
        else:
            url = self.url
        return url
    
    def is_at_symbol(self):
        quest_mark = self.url.find('?')
        if quest_mark > 0:
            url = self.url[:quest_mark]
        else:
            url = self.url
        return url.find('@') > -1
    
    def is_or_symbol_in_struct(self):
        url = self._get_without_parameter()
        return url.find('|') > -1
    
    def is_dash_symbol(self):
        domain_name = self.get_domain_name(self.url)
        return domain_name.find('-') > -1
    
    def is_dash_in_dir_struct(self):
        url = self._get_without_parameter()
        return url.find('-') > -1
        
    def is_start_in_dir_struct(self):
        url = self._get_without_parameter()
        return url.find('*') > -1
        
    # F49
    def get_multiple_tld(self):
        tld_list = [".AAA", ".AARP", ".ABARTH", ".ABB", ".ABBOTT", ".ABBVIE", ".ABC", ".ABLE", ".ABOGADO", ".ABUDHABI",
                    ".AC", ".ACADEMY", ".ACCENTURE", ".ACCOUNTANT", ".ACCOUNTANTS", ".ACO", ".ACTIVE", ".ACTOR", ".AD", ".ADAC",
                    ".ADS", ".ADULT", ".AE", ".AEG", ".AERO", ".AETNA", ".AF", ".AFAMILYCOMPANY", ".AFL", ".AFRICA",
                    ".AG", ".AGAKHAN", ".AGENCY", ".AI", ".AIG", ".AIGO", ".AIRBUS", ".AIRFORCE", ".AIRTEL", ".AKDN",
                    ".AL", ".ALFAROMEO", ".ALIBABA", ".ALIPAY", ".ALLFINANZ", ".ALLSTATE", ".ALLY", ".ALSACE", ".ALSTOM", ".AM",
                    ".AMERICANEXPRESS", ".AMERICANFAMILY", ".AMEX", ".AMFAM", ".AMICA", ".AMSTERDAM", ".ANALYTICS", ".ANDROID", ".ANQUAN", ".ANZ",
                    ".AO", ".AOL", ".APARTMENTS", ".APP", ".APPLE", ".AQ", ".AQUARELLE", ".AR", ".ARAMCO", ".ARCHI",
                    ".ARMY", ".ARPA", ".ART", ".ARTE", ".AS", ".ASDA", ".ASIA", ".ASSOCIATES", ".AT", ".ATHLETA",
                    ".ATTORNEY", ".AU", ".AUCTION", ".AUDI", ".AUDIBLE", ".AUDIO", ".AUSPOST", ".AUTHOR", ".AUTO", ".AUTOS",
                    ".AVIANCA", ".AW", ".AWS", ".AX", ".AXA", ".AZ", ".AZURE", ".BA", ".BABY", ".BAIDU",
                    ".BANAMEX", ".BANANAREPUBLIC", ".BAND", ".BANK", ".BAR", ".BARCELONA", ".BARCLAYCARD", ".BARCLAYS", ".BAREFOOT", ".BARGAINS",
                    ".BASEBALL", ".BASKETBALL", ".BAUHAUS", ".BAYERN", ".BB", ".BBC", ".BBT", ".BBVA", ".BCG", ".BCN",
                    ".BD", ".BE", ".BEATS", ".BEAUTY", ".BEER", ".BENTLEY", ".BERLIN", ".BEST", ".BESTBUY", ".BET",
                    ".BF", ".BG", ".BH", ".BHARTI", ".BI", ".BIBLE", ".BID", ".BIKE", ".BING", ".BINGO",
                    ".BIO", ".BIZ", ".BJ", ".BLACK", ".BLACKFRIDAY", ".BLANCO", ".BLOCKBUSTER", ".BLOG", ".BLOOMBERG", ".BLUE",
                    ".BM", ".BMS", ".BMW", ".BN", ".BNL", ".BNPPARIBAS", ".BO", ".BOATS", ".BOEHRINGER", ".BOFA",
                    ".BOM", ".BOND", ".BOO", ".BOOK", ".BOOKING", ".BOOTS", ".BOSCH", ".BOSTIK", ".BOSTON", ".BOT",
                    ".BOUTIQUE", ".BOX", ".BR", ".BRADESCO", ".BRIDGESTONE", ".BROADWAY", ".BROKER", ".BROTHER", ".BRUSSELS", ".BS",
                    ".BT", ".BUDAPEST", ".BUGATTI", ".BUILD", ".BUILDERS", ".BUSINESS", ".BUY", ".BUZZ", ".BV", ".BW",
                    ".BY", ".BZ", ".BZH", ".CA", ".CAB", ".CAFE", ".CAL", ".CALL", ".CALVINKLEIN", ".CAM",
                    ".CAMERA", ".CAMP", ".CANCERRESEARCH", ".CANON", ".CAPETOWN", ".CAPITAL", ".CAPITALONE", ".CAR", ".CARAVAN", ".CARDS",
                    ".CARE", ".CAREER", ".CAREERS", ".CARS", ".CARTIER", ".CASA", ".CASE", ".CASEIH", ".CASH", ".CASINO",
                    ".CAT", ".CATERING", ".CATHOLIC", ".CBA", ".CBN", ".CBRE", ".CBS", ".CC", ".CD", ".CEB",
                    ".CENTER", ".CEO", ".CERN", ".CF", ".CFA", ".CFD", ".CG", ".CH", ".CHANEL", ".CHANNEL",
                    ".CHASE", ".CHAT", ".CHEAP", ".CHINTAI", ".CHLOE", ".CHRISTMAS", ".CHROME", ".CHRYSLER", ".CHURCH", ".CI",
                    ".CIPRIANI", ".CIRCLE", ".CISCO", ".CITADEL", ".CITI", ".CITIC", ".CITY", ".CITYEATS", ".CK", ".CL",
                    ".CLAIMS", ".CLEANING", ".CLICK", ".CLINIC", ".CLINIQUE", ".CLOTHING", ".CLOUD", ".CLUB", ".CLUBMED", ".CM",
                    ".CN", ".CO", ".COACH", ".CODES", ".COFFEE", ".COLLEGE", ".COLOGNE", ".COM", ".COMCAST", ".COMMBANK",
                    ".COMMUNITY", ".COMPANY", ".COMPARE", ".COMPUTER", ".COMSEC", ".CONDOS", ".CONSTRUCTION", ".CONSULTING", ".CONTACT", ".CONTRACTORS",
                    ".COOKING", ".COOKINGCHANNEL", ".COOL", ".COOP", ".CORSICA", ".COUNTRY", ".COUPON", ".COUPONS", ".COURSES", ".CR",
                    ".CREDIT", ".CREDITCARD", ".CREDITUNION", ".CRICKET", ".CROWN", ".CRS", ".CRUISE", ".CRUISES", ".CSC", ".CU",
                    ".CUISINELLA", ".CV", ".CW", ".CX", ".CY", ".CYMRU", ".CYOU", ".CZ", ".DABUR", ".DAD",
                    ".DANCE", ".DATA", ".DATE", ".DATING", ".DATSUN", ".DAY", ".DCLK", ".DDS", ".DE", ".DEAL",
                    ".DEALER", ".DEALS", ".DEGREE", ".DELIVERY", ".DELL", ".DELOITTE", ".DELTA", ".DEMOCRAT", ".DENTAL", ".DENTIST",
                    ".DESI", ".DESIGN", ".DEV", ".DHL", ".DIAMONDS", ".DIET", ".DIGITAL", ".DIRECT", ".DIRECTORY", ".DISCOUNT",
                    ".DISCOVER", ".DISH", ".DIY", ".DJ", ".DK", ".DM", ".DNP", ".DO", ".DOCS", ".DOCTOR",
                    ".DODGE", ".DOG", ".DOHA", ".DOMAINS", ".DOT", ".DOWNLOAD", ".DRIVE", ".DTV", ".DUBAI", ".DUCK",
                    ".DUNLOP", ".DUNS", ".DUPONT", ".DURBAN", ".DVAG", ".DVR", ".DZ", ".EARTH", ".EAT", ".EC",
                    ".ECO", ".EDEKA", ".EDU", ".EDUCATION", ".EE", ".EG", ".EMAIL", ".EMERCK", ".ENERGY", ".ENGINEER",
                    ".ENGINEERING", ".ENTERPRISES", ".EPOST", ".EPSON", ".EQUIPMENT", ".ER", ".ERICSSON", ".ERNI", ".ES", ".ESQ",
                    ".ESTATE", ".ESURANCE", ".ET", ".EU", ".EUROVISION", ".EUS", ".EVENTS", ".EVERBANK", ".EXCHANGE", ".EXPERT",
                    ".EXPOSED", ".EXPRESS", ".EXTRASPACE", ".FAGE", ".FAIL", ".FAIRWINDS", ".FAITH", ".FAMILY", ".FAN", ".FANS",
                    ".FARM", ".FARMERS", ".FASHION", ".FAST", ".FEDEX", ".FEEDBACK", ".FERRARI", ".FERRERO", ".FI", ".FIAT",
                    ".FIDELITY", ".FIDO", ".FILM", ".FINAL", ".FINANCE", ".FINANCIAL", ".FIRE", ".FIRESTONE", ".FIRMDALE", ".FISH",
                    ".FISHING", ".FIT", ".FITNESS", ".FJ", ".FK", ".FLICKR", ".FLIGHTS", ".FLIR", ".FLORIST", ".FLOWERS",
                    ".FLY", ".FM", ".FO", ".FOO", ".FOOD", ".FOODNETWORK", ".FOOTBALL", ".FORD", ".FOREX", ".FORSALE",
                    ".FORUM", ".FOUNDATION", ".FOX", ".FR", ".FREE", ".FRESENIUS", ".FRL", ".FROGANS", ".FRONTDOOR", ".FRONTIER",
                    ".FTR", ".FUJITSU", ".FUJIXEROX", ".FUN", ".FUND", ".FURNITURE", ".FUTBOL", ".FYI", ".GA", ".GAL",
                    ".GALLERY", ".GALLO", ".GALLUP", ".GAME", ".GAMES", ".GAP", ".GARDEN", ".GB", ".GBIZ", ".GD",
                    ".GDN", ".GE", ".GEA", ".GENT", ".GENTING", ".GEORGE", ".GF", ".GG", ".GGEE", ".GH",
                    ".GI", ".GIFT", ".GIFTS", ".GIVES", ".GIVING", ".GL", ".GLADE", ".GLASS", ".GLE", ".GLOBAL",
                    ".GLOBO", ".GM", ".GMAIL", ".GMBH", ".GMO", ".GMX", ".GN", ".GODADDY", ".GOLD", ".GOLDPOINT",
                    ".GOLF", ".GOO", ".GOODHANDS", ".GOODYEAR", ".GOOG", ".GOOGLE", ".GOP", ".GOT", ".GOV", ".GP",
                    ".GQ", ".GR", ".GRAINGER", ".GRAPHICS", ".GRATIS", ".GREEN", ".GRIPE", ".GROUP", ".GS", ".GT",
                    ".GU", ".GUARDIAN", ".GUCCI", ".GUGE", ".GUIDE", ".GUITARS", ".GURU", ".GW", ".GY", ".HAIR",
                    ".HAMBURG", ".HANGOUT", ".HAUS", ".HBO", ".HDFC", ".HDFCBANK", ".HEALTH", ".HEALTHCARE", ".HELP", ".HELSINKI",
                    ".HERE", ".HERMES", ".HGTV", ".HIPHOP", ".HISAMITSU", ".HITACHI", ".HIV", ".HK", ".HKT", ".HM",
                    ".HN", ".HOCKEY", ".HOLDINGS", ".HOLIDAY", ".HOMEDEPOT", ".HOMEGOODS", ".HOMES", ".HOMESENSE", ".HONDA", ".HONEYWELL",
                    ".HORSE", ".HOSPITAL", ".HOST", ".HOSTING", ".HOT", ".HOTELES", ".HOTMAIL", ".HOUSE", ".HOW", ".HR",
                    ".HSBC", ".HT", ".HTC", ".HU", ".HUGHES", ".HYATT", ".HYUNDAI", ".IBM", ".ICBC", ".ICE",
                    ".ICU", ".ID", ".IE", ".IEEE", ".IFM", ".IKANO", ".IL", ".IM", ".IMAMAT", ".IMDB",
                    ".IMMO", ".IMMOBILIEN", ".IN", ".INDUSTRIES", ".INFINITI", ".INFO", ".ING", ".INK", ".INSTITUTE", ".INSURANCE",
                    ".INSURE", ".INT", ".INTEL", ".INTERNATIONAL", ".INTUIT", ".INVESTMENTS", ".IO", ".IPIRANGA", ".IQ", ".IR",
                    ".IRISH", ".IS", ".ISELECT", ".ISMAILI", ".IST", ".ISTANBUL", ".IT", ".ITAU", ".ITV", ".IVECO",
                    ".IWC", ".JAGUAR", ".JAVA", ".JCB", ".JCP", ".JE", ".JEEP", ".JETZT", ".JEWELRY", ".JIO",
                    ".JLC", ".JLL", ".JM", ".JMP", ".JNJ", ".JO", ".JOBS", ".JOBURG", ".JOT", ".JOY",
                    ".JP", ".JPMORGAN", ".JPRS", ".JUEGOS", ".JUNIPER", ".KAUFEN", ".KDDI", ".KE", ".KERRYHOTELS", ".KERRYLOGISTICS",
                    ".KERRYPROPERTIES", ".KFH", ".KG", ".KH", ".KI", ".KIA", ".KIM", ".KINDER", ".KINDLE", ".KITCHEN",
                    ".KIWI", ".KM", ".KN", ".KOELN", ".KOMATSU", ".KOSHER", ".KP", ".KPMG", ".KPN", ".KR",
                    ".KRD", ".KRED", ".KUOKGROUP", ".KW", ".KY", ".KYOTO", ".KZ", ".LA", ".LACAIXA", ".LADBROKES",
                    ".LAMBORGHINI", ".LAMER", ".LANCASTER", ".LANCIA", ".LANCOME", ".LAND", ".LANDROVER", ".LANXESS", ".LASALLE", ".LAT",
                    ".LATINO", ".LATROBE", ".LAW", ".LAWYER", ".LB", ".LC", ".LDS", ".LEASE", ".LECLERC", ".LEFRAK",
                    ".LEGAL", ".LEGO", ".LEXUS", ".LGBT", ".LI", ".LIAISON", ".LIDL", ".LIFE", ".LIFEINSURANCE", ".LIFESTYLE",
                    ".LIGHTING", ".LIKE", ".LILLY", ".LIMITED", ".LIMO", ".LINCOLN", ".LINDE", ".LINK", ".LIPSY", ".LIVE",
                    ".LIVING", ".LIXIL", ".LK", ".LOAN", ".LOANS", ".LOCKER", ".LOCUS", ".LOFT", ".LOL", ".LONDON",
                    ".LOTTE", ".LOTTO", ".LOVE", ".LPL", ".LPLFINANCIAL", ".LR", ".LS", ".LT", ".LTD", ".LTDA",
                    ".LU", ".LUNDBECK", ".LUPIN", ".LUXE", ".LUXURY", ".LV", ".LY", ".MA", ".MACYS", ".MADRID",
                    ".MAIF", ".MAISON", ".MAKEUP", ".MAN", ".MANAGEMENT", ".MANGO", ".MARKET", ".MARKETING", ".MARKETS", ".MARRIOTT",
                    ".MARSHALLS", ".MASERATI", ".MATTEL", ".MBA", ".MC", ".MCD", ".MCDONALDS", ".MCKINSEY", ".MD", ".ME",
                    ".MED", ".MEDIA", ".MEET", ".MELBOURNE", ".MEME", ".MEMORIAL", ".MEN", ".MENU", ".MEO", ".METLIFE",
                    ".MG", ".MH", ".MIAMI", ".MICROSOFT", ".MIL", ".MINI", ".MINT", ".MIT", ".MITSUBISHI", ".MK",
                    ".ML", ".MLB", ".MLS", ".MM", ".MMA", ".MN", ".MO", ".MOBI", ".MOBILE", ".MOBILY",
                    ".MODA", ".MOE", ".MOI", ".MOM", ".MONASH", ".MONEY", ".MONSTER", ".MONTBLANC", ".MOPAR", ".MORMON",
                    ".MORTGAGE", ".MOSCOW", ".MOTO", ".MOTORCYCLES", ".MOV", ".MOVIE", ".MOVISTAR", ".MP", ".MQ", ".MR",
                    ".MS", ".MSD", ".MT", ".MTN", ".MTPC", ".MTR", ".MU", ".MUSEUM", ".MUTUAL", ".MV",
                    ".MW", ".MX", ".MY", ".MZ", ".NA", ".NAB", ".NADEX", ".NAGOYA", ".NAME", ".NATIONWIDE",
                    ".NATURA", ".NAVY", ".NBA", ".NC", ".NE", ".NEC", ".NET", ".NETBANK", ".NETFLIX", ".NETWORK",
                    ".NEUSTAR", ".NEW", ".NEWHOLLAND", ".NEWS", ".NEXT", ".NEXTDIRECT", ".NEXUS", ".NF", ".NFL", ".NG",
                    ".NGO", ".NHK", ".NI", ".NICO", ".NIKE", ".NIKON", ".NINJA", ".NISSAN", ".NISSAY", ".NL",
                    ".NO", ".NOKIA", ".NORTHWESTERNMUTUAL", ".NORTON", ".NOW", ".NOWRUZ", ".NOWTV", ".NP", ".NR", ".NRA",
                    ".NRW", ".NTT", ".NU", ".NYC", ".NZ", ".OBI", ".OBSERVER", ".OFF", ".OFFICE", ".OKINAWA",
                    ".OLAYAN", ".OLAYANGROUP", ".OLDNAVY", ".OLLO", ".OM", ".OMEGA", ".ONE", ".ONG", ".ONL", ".ONLINE",
                    ".ONYOURSIDE", ".OOO", ".OPEN", ".ORACLE", ".ORANGE", ".ORG", ".ORGANIC", ".ORIENTEXPRESS", ".ORIGINS", ".OSAKA",
                    ".OTSUKA", ".OTT", ".OVH", ".PA", ".PAGE", ".PAMPEREDCHEF", ".PANASONIC", ".PANERAI", ".PARIS", ".PARS",
                    ".PARTNERS", ".PARTS", ".PARTY", ".PASSAGENS", ".PAY", ".PCCW", ".PE", ".PET", ".PF", ".PFIZER",
                    ".PG", ".PH", ".PHARMACY", ".PHILIPS", ".PHONE", ".PHOTO", ".PHOTOGRAPHY", ".PHOTOS", ".PHYSIO", ".PIAGET",
                    ".PICS", ".PICTET", ".PICTURES", ".PID", ".PIN", ".PING", ".PINK", ".PIONEER", ".PIZZA", ".PK",
                    ".PL", ".PLACE", ".PLAY", ".PLAYSTATION", ".PLUMBING", ".PLUS", ".PM", ".PN", ".PNC", ".POHL",
                    ".POKER", ".POLITIE", ".PORN", ".POST", ".PR", ".PRAMERICA", ".PRAXI", ".PRESS", ".PRIME", ".PRO",
                    ".PROD", ".PRODUCTIONS", ".PROF", ".PROGRESSIVE", ".PROMO", ".PROPERTIES", ".PROPERTY", ".PROTECTION", ".PRU", ".PRUDENTIAL",
                    ".PS", ".PT", ".PUB", ".PW", ".PWC", ".PY", ".QA", ".QPON", ".QUEBEC", ".QUEST",
                    ".QVC", ".RACING", ".RADIO", ".RAID", ".RE", ".READ", ".REALESTATE", ".REALTOR", ".REALTY", ".RECIPES",
                    ".RED", ".REDSTONE", ".REDUMBRELLA", ".REHAB", ".REISE", ".REISEN", ".REIT", ".RELIANCE", ".REN", ".RENT",
                    ".RENTALS", ".REPAIR", ".REPORT", ".REPUBLICAN", ".REST", ".RESTAURANT", ".REVIEW", ".REVIEWS", ".REXROTH", ".RICH",
                    ".RICHARDLI", ".RICOH", ".RIGHTATHOME", ".RIL", ".RIO", ".RIP", ".RMIT", ".RO", ".ROCHER", ".ROCKS",
                    ".RODEO", ".ROGERS", ".ROOM", ".RS", ".RSVP", ".RU", ".RUHR", ".RUN", ".RW", ".RWE",
                    ".RYUKYU", ".SA", ".SAARLAND", ".SAFE", ".SAFETY", ".SAKURA", ".SALE", ".SALON", ".SAMSCLUB", ".SAMSUNG",
                    ".SANDVIK", ".SANDVIKCOROMANT", ".SANOFI", ".SAP", ".SAPO", ".SARL", ".SAS", ".SAVE", ".SAXO", ".SB",
                    ".SBI", ".SBS", ".SC", ".SCA", ".SCB", ".SCHAEFFLER", ".SCHMIDT", ".SCHOLARSHIPS", ".SCHOOL", ".SCHULE",
                    ".SCHWARZ", ".SCIENCE", ".SCJOHNSON", ".SCOR", ".SCOT", ".SD", ".SE", ".SEAT", ".SECURE", ".SECURITY",
                    ".SEEK", ".SELECT", ".SENER", ".SERVICES", ".SES", ".SEVEN", ".SEW", ".SEX", ".SEXY", ".SFR",
                    ".SG", ".SH", ".SHANGRILA", ".SHARP", ".SHAW", ".SHELL", ".SHIA", ".SHIKSHA", ".SHOES", ".SHOP",
                    ".SHOPPING", ".SHOUJI", ".SHOW", ".SHOWTIME", ".SHRIRAM", ".SI", ".SILK", ".SINA", ".SINGLES", ".SITE",
                    ".SJ", ".SK", ".SKI", ".SKIN", ".SKY", ".SKYPE", ".SL", ".SLING", ".SM", ".SMART",
                    ".SMILE", ".SN", ".SNCF", ".SO", ".SOCCER", ".SOCIAL", ".SOFTBANK", ".SOFTWARE", ".SOHU", ".SOLAR",
                    ".SOLUTIONS", ".SONG", ".SONY", ".SOY", ".SPACE", ".SPIEGEL", ".SPOT", ".SPREADBETTING", ".SR", ".SRL",
                    ".SRT", ".ST", ".STADA", ".STAPLES", ".STAR", ".STARHUB", ".STATEBANK", ".STATEFARM", ".STATOIL", ".STC",
                    ".STCGROUP", ".STOCKHOLM", ".STORAGE", ".STORE", ".STREAM", ".STUDIO", ".STUDY", ".STYLE", ".SU", ".SUCKS",
                    ".SUPPLIES", ".SUPPLY", ".SUPPORT", ".SURF", ".SURGERY", ".SUZUKI", ".SV", ".SWATCH", ".SWIFTCOVER", ".SWISS",
                    ".SX", ".SY", ".SYDNEY", ".SYMANTEC", ".SYSTEMS", ".SZ", ".TAB", ".TAIPEI", ".TALK", ".TAOBAO",
                    ".TARGET", ".TATAMOTORS", ".TATAR", ".TATTOO", ".TAX", ".TAXI", ".TC", ".TCI", ".TD", ".TDK",
                    ".TEAM", ".TECH", ".TECHNOLOGY", ".TEL", ".TELECITY", ".TELEFONICA", ".TEMASEK", ".TENNIS", ".TEVA", ".TF",
                    ".TG", ".TH", ".THD", ".THEATER", ".THEATRE", ".TIAA", ".TICKETS", ".TIENDA", ".TIFFANY", ".TIPS",
                    ".TIRES", ".TIROL", ".TJ", ".TJMAXX", ".TJX", ".TK", ".TKMAXX", ".TL", ".TM", ".TMALL",
                    ".TN", ".TO", ".TODAY", ".TOKYO", ".TOOLS", ".TOP", ".TORAY", ".TOSHIBA", ".TOTAL", ".TOURS",
                    ".TOWN", ".TOYOTA", ".TOYS", ".TR", ".TRADE", ".TRADING", ".TRAINING", ".TRAVEL", ".TRAVELCHANNEL", ".TRAVELERS",
                    ".TRAVELERSINSURANCE", ".TRUST", ".TRV", ".TT", ".TUBE", ".TUI", ".TUNES", ".TUSHU", ".TV", ".TVS",
                    ".TW", ".TZ", ".UA", ".UBANK", ".UBS", ".UCONNECT", ".UG", ".UK", ".UNICOM", ".UNIVERSITY",
                    ".UNO", ".UOL", ".UPS", ".US", ".UY", ".UZ", ".VA", ".VACATIONS", ".VANA", ".VANGUARD",
                    ".VC", ".VE", ".VEGAS", ".VENTURES", ".VERISIGN", ".VERSICHERUNG", ".VET", ".VG", ".VI", ".VIAJES",
                    ".VIDEO", ".VIG", ".VIKING", ".VILLAS", ".VIN", ".VIP", ".VIRGIN", ".VISA", ".VISION", ".VISTA",
                    ".VISTAPRINT", ".VIVA", ".VIVO", ".VLAANDEREN", ".VN", ".VODKA", ".VOLKSWAGEN", ".VOLVO", ".VOTE", ".VOTING",
                    ".VOTO", ".VOYAGE", ".VU", ".VUELOS", ".WALES", ".WALMART", ".WALTER", ".WANG", ".WANGGOU", ".WARMAN",
                    ".WATCH", ".WATCHES", ".WEATHER", ".WEATHERCHANNEL", ".WEBCAM", ".WEBER", ".WEBSITE", ".WED", ".WEDDING", ".WEIBO",
                    ".WEIR", ".WF", ".WHOSWHO", ".WIEN", ".WIKI", ".WILLIAMHILL", ".WIN", ".WINDOWS", ".WINE", ".WINNERS",
                    ".WME", ".WOLTERSKLUWER", ".WOODSIDE", ".WORK", ".WORKS", ".WORLD", ".WOW", ".WS", ".WTC", ".WTF",
                    ".XBOX", ".XEROX", ".XFINITY", ".XIHUAN", ".XIN", ".XN--11B4C3D", ".XN--1CK2E1B", ".XN--1QQW23A", ".XN--30RR7Y", ".XN--3BST00M",
                    ".XN--3DS443G", ".XN--3E0B707E", ".XN--3OQ18VL8PN36A", ".XN--3PXU8K", ".XN--42C2D9A", ".XN--45BRJ9C", ".XN--45Q11C", ".XN--4GBRIM", ".XN--54B7FTA0CC", ".XN--55QW42G",
                    ".XN--55QX5D", ".XN--5SU34J936BGSG", ".XN--5TZM5G", ".XN--6FRZ82G", ".XN--6QQ986B3XL", ".XN--80ADXHKS", ".XN--80AO21A", ".XN--80AQECDR1A", ".XN--80ASEHDB", ".XN--80ASWG",
                    ".XN--8Y0A063A", ".XN--90A3AC", ".XN--90AE", ".XN--90AIS", ".XN--9DBQ2A", ".XN--9ET52U", ".XN--9KRT00A", ".XN--B4W605FERD", ".XN--BCK1B9A5DRE4C", ".XN--C1AVG",
                    ".XN--C2BR7G", ".XN--CCK2B3B", ".XN--CG4BKI", ".XN--CLCHC0EA0B2G2A9GCD", ".XN--CZR694B", ".XN--CZRS0T", ".XN--CZRU2D", ".XN--D1ACJ3B", ".XN--D1ALF", ".XN--E1A4C",
                    ".XN--ECKVDTC9D", ".XN--EFVY88H", ".XN--ESTV75G", ".XN--FCT429K", ".XN--FHBEI", ".XN--FIQ228C5HS", ".XN--FIQ64B", ".XN--FIQS8S", ".XN--FIQZ9S", ".XN--FJQ720A",
                    ".XN--FLW351E", ".XN--FPCRJ9C3D", ".XN--FZC2C9E2C", ".XN--FZYS8D69UVGM", ".XN--G2XX48C", ".XN--GCKR3F0F", ".XN--GECRJ9C", ".XN--GK3AT1E", ".XN--H2BRJ9C", ".XN--HXT814E",
                    ".XN--I1B6B1A6A2E", ".XN--IMR513N", ".XN--IO0A7I", ".XN--J1AEF", ".XN--J1AMH", ".XN--J6W193G", ".XN--JLQ61U9W7B", ".XN--JVR189M", ".XN--KCRX77D1X4A", ".XN--KPRW13D",
                    ".XN--KPRY57D", ".XN--KPU716F", ".XN--KPUT3I", ".XN--L1ACC", ".XN--LGBBAT1AD8J", ".XN--MGB9AWBF", ".XN--MGBA3A3EJT", ".XN--MGBA3A4F16A", ".XN--MGBA7C0BBN0A", ".XN--MGBAAM7A8H",
                    ".XN--MGBAB2BD", ".XN--MGBAI9AZGQP6J", ".XN--MGBAYH7GPA", ".XN--MGBB9FBPOB", ".XN--MGBBH1A71E", ".XN--MGBC0A9AZCG", ".XN--MGBCA7DZDO", ".XN--MGBERP4A5D4AR", ".XN--MGBI4ECEXP", ".XN--MGBPL2FH",
                    ".XN--MGBT3DHD", ".XN--MGBTX2B", ".XN--MGBX4CD0AB", ".XN--MIX891F", ".XN--MK1BU44C", ".XN--MXTQ1M", ".XN--NGBC5AZD", ".XN--NGBE9E0A", ".XN--NODE", ".XN--NQV7F",
                    ".XN--NQV7FS00EMA", ".XN--NYQY26A", ".XN--O3CW4H", ".XN--OGBPF8FL", ".XN--P1ACF", ".XN--P1AI", ".XN--PBT977C", ".XN--PGBS0DH", ".XN--PSSY2U", ".XN--Q9JYB4C",
                    ".XN--QCKA1PMC", ".XN--QXAM", ".XN--RHQV96G", ".XN--ROVU88B", ".XN--S9BRJ9C", ".XN--SES554G", ".XN--T60B56A", ".XN--TCKWE", ".XN--TIQ49XQYJ", ".XN--UNUP4Y",
                    ".XN--VERMGENSBERATER-CTB", ".XN--VERMGENSBERATUNG-PWB", ".XN--VHQUV", ".XN--VUQ861B", ".XN--W4R85EL8FHU5DNRA", ".XN--W4RS40L", ".XN--WGBH1C", ".XN--WGBL6A", ".XN--XHQ521B", ".XN--XKC2AL3HYE2A",
                    ".XN--XKC2DL3A5EE0H", ".XN--Y9A3AQ", ".XN--YFRO4I67O", ".XN--YGBI2AMMX", ".XN--ZFR164B", ".XPERIA", ".XXX", ".XYZ", ".YACHTS", ".YAHOO",
                    ".YAMAXUN", ".YANDEX", ".YE", ".YODOBASHI", ".YOGA", ".YOKOHAMA", ".YOU", ".YOUTUBE", ".YT", ".YUN",
                    ".ZA", ".ZAPPOS", ".ZARA", ".ZERO", ".ZIP", ".ZIPPO", ".ZM", ".ZONE", ".ZUERICH", ".ZW"]
        domain_name = self.get_domain_name(self.url)
        number = 0
        for i in tld_list:
            if i in domain_name:
                number += 1
        return number > 1
        
    # F50
    def get_brandname(self):
        brandname = ['dropbox','google','paypal','battle.net','yahoo','drive','alibaba','DHL','bank','hotmail','.irs.','facebook','itau','impots.gouv','amazon','amazonaws','made-in-china','twitter','gov.uk','barclays']
        domain_name = self.get_domain_name(self.url)
        for i in brandname:
            if i in domain_name:
                return 1
        return 0
        
    # F51
    def get_special_words(self):
        return self.is_at_symbol() or self.is_dash_in_dir_struct() or self.is_start_in_dir_struct() or self.is_or_symbol_in_struct()
        
    # F52
    def get_hexadecimal(self):
        domain_name = self.get_domain_name(self.url)
        return domain_name.find('%') > -1
        
    # F53
    def get_ip_address(self):
        domain_name = self.get_domain_name(self.url)
        return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_name) is not None
        
    # F54
    def get_typos(self):
        domain_name = self.get_domain_name(self.url)
        brandname = ['dropbox','google','paypal','battle.net','yahoo','drive','alibaba','DHL','bank','hotmail','.irs.','facebook','itau','impots.gouv','amazon','amazonaws','made-in-china','twitter','gov.uk','barclays']
        for i in brandname:
            typosssss = TypoGenerator().getAllTypos(i)
            for j in typosssss:
                if j in domain_name:
                    return 1
        return 0
        
    # F55
    def get_long_url(self):
        domain_name = self.get_domain_name(self.url)
        return len(domain_name) > 25
        
    # F56 not yet
    def get_misleading_subdomain(self):
        domain_name = self.get_domain_name(self.url)
        brandname = ['dropbox','google','paypal','battle.net','yahoo','drive','alibaba','DHL','bank','hotmail','.irs.','facebook','itau','impots.gouv','amazon','amazonaws','made-in-china','twitter','gov.uk','barclays']
        for i in brandname:
            if i in domain_name:
                return 1
        return 0
        
    # F57
    def get_dots(self):
        domain_name = self.get_domain_name(self.url)
        return len(domain_name.split('.')) - 1
        
    # F58
    def get_path_domain_length(self):
        p1 = self.url.find('//') + 2
        p2 = self.url.find('/', p1)
        if p2 > 0:
            p2 = p2 + 1
        else:
            p2 = len(self.url)
        return len(self.url[p2:])
        
from nltk.corpus import wordnet
alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
vowels = "aeiouy"
DICTIONARY = 'brands-name'

class TypoGenerator:
    def insertedKey(self, s):
        """Produce a list of keywords using the `inserted key' method
        """
        kwds = []
        
        for i in range(0, len(s)):
            for char in alphabet:
                kwds.append(s[:i+1] + char + s[i+1:])
                
        return kwds
        
    def skipLetter(self, s):
        """Produce a list of keywords using the `skip letter' method
        """
        kwds = []
        
        for i in range(1, len(s)+1):
            kwds.append(s[:i-1] + s[i:])
            
        return kwds
        
    def doubleLetter(self, s):
        """Produce a list of keywords using the `double letter' method
        """
        kwds = []
        
        for i in range(0, len(s)+1):
            kwds.append(s[:i] + s[i-1] + s[i:])
            
        return kwds
        
    def reverseLetter(self, s):
        """Produce a list of keywords using the `reverse letter' method
        """
        kwds = []
        
        for i in range(0, len(s)):
            letters = s[i-1:i+1:1]
            if len(letters) != 2:
                continue
        
            reverse_letters = letters[1] + letters[0]
            kwds.append(s[:i-1] + reverse_letters + s[i+1:])
            
        return kwds
        
    def wrongVowel(self, s):
        """Produce a list of keywords using the `wrong vowel' method (for soundex)
        """
        kwds = []
        
        for i in range(0, len(s)):
            for letter in vowels:
                if s[i] in vowels:
                    for vowel in vowels:
                        s_list = list(s)
                        s_list[i] = vowel
                        kwd = "".join(s_list)
                        kwds.append(kwd)
                        
        return kwds
        
    def wrongKey(self, s):
        """Produce a list of keywords using the `wrong key' method
        """
        kwds = []
        
        for i in range(0, len(s)):
            for letter in alphabet:
                kwd = s[:i] + letter + s[i+1:]
                kwds.append(kwd)
                
        return kwds
        
    def _findWords(self, s):
        """Produces a list of words found in string `s'
        """
        matches = []
        
        words = file(DICTIONARY).read()
        
        for word in words.split('\n'):
            if re.match('^.*'+word+'.*$', s, re.IGNORECASE):
            #if s.find(word) != -1 and word != '' and len(word) > 1:
                matches.append(word)
                
        return matches
        
    def _getSynonyms(self, word):
        """Returns a list of synonyms for `word'
        """
        synset = []
        
        for word_type in [wordnet.ADJ, wordnet.ADV, wordnet.NOUN, wordnet.VERB]:
            synset += [lemma.name().lower().replace("_", "")
                       for lemma in sum([ss.lemmas() for ss in wordnet.synsets(word, word_type)],[])]
        return synset
        
    def synonymSubstitution(self, s):
        """Produces a list of strings with alternative synonyms from the words found in `s'
        """
        alt_strings = []
        for word in self._findWords(s):
            for synonym in self._getSynonyms(word):
                orig_s = s
                alt_strings.append( orig_s.replace(word, synonym))
                
        return list(set(alt_strings))
        
    def getAllTypos(self, s):
        """Calls all our typo generation methods on a string and return the result
        """
        kwds = []
        kwds += self.insertedKey(s)
        kwds += self.wrongKey(s)
        kwds += self.skipLetter(s)
        kwds += self.doubleLetter(s)
        kwds += self.reverseLetter(s)
        kwds += self.wrongVowel(s)
        kwds += self.synonymSubstitution(s)
        return kwds
        
        
