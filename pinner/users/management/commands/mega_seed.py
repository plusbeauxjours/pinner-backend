import uuid
import json
import random
from django.core.management.base import BaseCommand
from users import models as user_models
from locations import models as location_models
from notifications import models as notification_models
from django_seed import Seed
from django.db.models.expressions import RawSQL
from locations import reversePlace, locationThumbnail
from googleplaces import GooglePlaces
from django.conf import settings
from math import radians, degrees, sin, cos, asin, acos, sqrt


def createCity(cityId):
    def get_locations_nearby_coords(latitude, longitude, max_distance=3000):
        gcd_formula = "6371 * acos(cos(radians(%s)) * \
        cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)))"
        distance_raw_sql = RawSQL(
            gcd_formula,
            (latitude, longitude, latitude)
        )
        qs = location_models.City.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
            for i in qs:
                pass
            return qs

    cityLatitude, cityLongitude, cityName, countryCode = reversePlace.reverse_place(cityId)
    nearCities = get_locations_nearby_coords(cityLatitude, cityLongitude, 3000)[:20]
    if cityLatitude and cityLongitude and cityName and countryCode:
        try:
            country = location_models.Country.objects.get(country_code=countryCode)
        except location_models.Country.DoesNotExist:

            with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
                countryData = json.load(file)
                currentCountry = countryData[countryCode]
                countryName = currentCountry['name']
                countryNameNative = currentCountry['native']
                countryCapital = currentCountry['capital']
                countryCurrency = currentCountry['currency']
                countryPhone = currentCountry['phone']
                countryEmoji = currentCountry['emoji']
                continentCode = currentCountry['continent']
                latitude = currentCountry['latitude']
                longitude = currentCountry['longitude']

                try:
                    continent = location_models.Continent.objects.get(continent_code=continentCode)
                except:
                    with open('pinner/locations/continentData.json', mode='rt', encoding='utf-8') as file:
                        continentData = json.load(file)
                        continentName = continentData[continentCode]

                        try:
                            gp = locationThumbnail.get_photos(term=continentName).get_urls()
                            continentPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
                            continentThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
                        except:
                            continentPhotoURL = None
                            continentThumbnailURL = None

                        continent = location_models.Continent.objects.create(
                            continent_name=continentName,
                            continent_photo=continentPhotoURL,
                            continent_thumbnail=continentThumbnailURL,
                            continent_code=continentCode
                        )
            try:
                gp = locationThumbnail.get_photos(term=countryName).get_urls()
                countryPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
                countryThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
            except:
                countryPhotoURL = None
                countryThumbnailURL = None
            country = location_models.Country.objects.create(
                country_code=countryCode,
                country_name=countryName,
                country_name_native=countryNameNative,
                country_capital=countryCapital,
                country_currency=countryCurrency,
                country_phone=countryPhone,
                country_emoji=countryEmoji,
                country_photo=countryPhotoURL,
                country_thumbnail=countryThumbnailURL,
                continent=continent,
                latitude=latitude,
                longitude=longitude
            )

        try:
            gp = locationThumbnail.get_photos(term=cityName).get_urls()
            cityPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
            cityThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
        except:
            cityPhotoURL = None
            cityThumbnailURL = None
        city = location_models.City.objects.create(
            city_id=cityId,
            city_name=cityName,
            country=country,
            city_photo=cityPhotoURL,
            city_thumbnail=cityThumbnailURL,
            latitude=cityLatitude,
            longitude=cityLongitude
        )
        print(city.city_name)
        for i in nearCities:
            city.near_city.add(i)
            city.save()


cityNames = [
    "TOKYO, Japan",
    "JAKARTA, Indonesia",
    "New York",
    "SEOUL, South Korea",
    "MANILA, Philippines",
    "Mumbai, India",
    "Sao Paulo, Brazil",
    "MEXICO CITY, Mexico",
    "Delhi, India",
    "Osaka, Japan",
    "CAIRO, Egypt",
    "Kolkata, India",
    "Los Angeles",
    "Shanghai, China",
    "MOSCOW, Russia",
    "BEIJING, China",
    "BUENOS AIRES, Argentina",
    "Istanbul, Turkey",
    "Rio de Janeiro, Brazil",
    "PARIS, France",
    "Karachi, Pakistan",
    "Nagoya, Japan",
    "Chicago",
    "Lagos, Nigeria",
    "LONDON, United Kingdom",
    "BANGKOK, Thailand",
    "KINSHASA, Dem Rep of Congo",
    "TEHRAN, Iran",
    "LIMA, Peru",
    "Dongguan, China",
    "BOGOTA, Colombia",
    "Chennai, India",
    "DHAKA, Bangladesh",
    "Essen, Germany",
    "Tianjin, China",
    "Lahore, Pakistan",
    "Bangalore, India",
    "Hyderabad, India",
    "Johannesburg, South Africa",
    "BAGHDAD, Iraq",
    "Toronto, Canada",
    "SANTIAGO, Chile",
    "KUALA LUMPUR, Malaysia",
    "San Francisco",
    "Philadelphia",
    "Wuhan, China",
    "Miami",
    "Dallas",
    "MADRID, Spain",
    "Ahmedabad, India",
    "Boston",
    "Belo Horizonte, Brazil",
    "KHARTOUM, Sudan",
    "Saint Petersburg, Russia",
    "Shenyang, China",
    "Houston",
    "Pune, India",
    "RIYADH, Saudi Arabia",
    "SINGAPORE, Singapore",
    "WASHINGTON",
    "Yangon, Myanmar",
    "Milan, Italy",
    "Atlanta",
    "Chongqing, China",
    "Alexandria, Egypt",
    "Nanjing, China",
    "Guadalajara, Mexico",
    "Barcelona, Spain",
    "Chengdu, China",
    "Detroit",
    "ANKARA, Turkey",
    "ATHENS, Greece",
    "BERLIN, Germany",
    "Sydney, Australia",
    "Monterrey, Mexico",
    "Phoenix",
    "Busan, South Korea",
    "Recife, Brazil",
    "Bandung, Indonesia",
    "Porto Alegre, Brazil",
    "Melbourne, Australia",
    "LUANDA, Angola",
    "ALGIERS, Algeria",
    "Hà Noi, Viet Nam",
    "Montréal, Canada",
    "PYONGYANG, North Korea",
    "Surat, India",
    "Fortaleza, Brazil",
    "Medellín, Colombia",
    "Durban, South Africa",
    "Kanpur, India",
    "ADDIS ABABA, Ethiopia",
    "NAIROBI, Kenya",
    "Jeddah, Saudi Arabia",
    "Naples, Italy",
    "KABUL, Afghanistan",
    "Salvador, Brazil",
    "Harbin, China",
    "Kano, Nigeria",
    "CAPE TOWN, South Africa",
    "Curitiba, Brazil",
    "Surabaya, Indonesia",
    "San Diego",
    "Seattle",
    "ROME, Italy",
    "Dar es Salaam, Tanzania",
    "Taichung, China",
    "Jaipur, India",
    "CARACAS, Venezuela",
    "DAKAR, Senegal",
    "Kaohsiung, China",
    "Minneapolis",
    "Lucknow, India",
    "AMMAN, Jordan",
    "Tel Aviv-Yafo, Israel",
    "Guayaquil, Ecuador",
    "KYIV, Ukraine",
    "Faisalabad, Pakistan",
    "Mashhad, Iran",
    "Izmir, Turkey",
    "Rawalpindi, Pakistan",
    "TASHKENT, Uzbekistan",
    "Katowice, Poland",
    "Campinas, Brazil",
    "Daegu, South Korea",
    "Changsha, China",
    "Nagpur, India",
    "San Juan, Philippines",
    "Aleppo, Syria",
    "LISBON, Portugal",
    "Frankfurt am Main, Germany",
    "Nanchang, China",
    "Birmingham, United Kingdom",
    "Tampa",
    "Medan, Indonesia",
    "TUNIS, Tunisia",
    "Manchester, United Kingdom",
    "PORT-AU-PRINCE, Haiti",
    "DAMASCUS, Syria",
    "Fukuoka, Japan",
    "SANTO DOMINGO, Dominican Republic",
    "HAVANA, Cuba",
    "Cali, Colombia",
    "Denver",
    "St. Louis, United",
    "Colombo, Brazil",
    "Dubai, United Arab Emirates",
    "Baltimore",
    "Sapporo, Japan",
    "Rotterdam, Netherlands",
    "Vancouver, Canada",
    "Preston, United Kingdom",
    "Patna, India",
    "WARSAW, Poland",
    "Bonn, Germany",
    "ACCRA, Ghana",
    "BUCHAREST, Romania",
    "Yokohama, Japan",
    "Incheon, South Korea",
    "BRASILIA, Brazil",
    "West Midlands, United Kingdom",
    "Giza, Egypt",
    "Quezon City, Philippines",
    "Chittagong, Bangladesh",
    "STOCKHOLM, Sweden",
    "Puebla de Zaragoza, Mexico",
    "BAKU, Azerbaijan",
    "Ibadan, Nigeria",
    "Brisbane, Australia",
    "MINSK, Belarus",
    "Sikasso, Mali",
    "Maracaibo, Venezuela",
    "Hamburg, Germany",
    "BUDAPEST, Hungary",
    "Manaus, Brazil",
    "Ségou, Mali",
    "VIENNA, Austria",
    "Indore, India",
    "ASUNCION, Paraguay",
    "Tianmen, China",
    "BELGRADE, Serbia",
    "Nakuru, Kenya",
    "Koulikoro, Mali",
    "Kobe, Japan",
    "Hama, Syria",
    "Esfahan, Iran",
    "TRIPOLI, Libya",
    "West Yorkshire, United Kingdom",
    "Vadodara, India",
    "QUITO, Ecuador",
    "Jinjiang, China",
    "Mopti, Mali",
    "Perth, Australia",
    "Daejeon, South Korea",
    "Kyoto, Japan",
    "Xiantao, China",
    "Tangerang, Indonesia",
    "Kharkiv, Ukraine",
    "Gwangju, South Korea",
    "Semarang, Indonesia",
    "Novosibirsk, Russia",
    "Neijiang, China",
    "MAPUTO, Mozambique",
    "Douala, Cameroon",
    "Kayes, Mali",
    "Tabriz, Iran",
    "Homs, Syria",
    "MONTEVIDEO, Uruguay",
    "Ekaterinoburg, Russia",
    "Juárez, Mexico",
    "Kawasaki, Japan",
    "Tijuana, Mexico",
    "Bursa, Turkey",
    "Al-Hasakeh, Syria",
    "Makkah, Saudi Arabia",
    "YAOUNDE, Cameroon",
    "Palembang, Indonesia",
    "Nizhny Novgorod, Russia",
    "León, Mexico",
    "Guarulhos, Brazil",
    "Heze, China",
    "Auckland, New Zealand",
    "Omdurman, Sudan",
    "Valencia, Venezuela",
    "San Antonio",
    "Almaty, Kazakhstan",
    "PHNOM PENH, Cambodia",
    "Yiyang, China",
    "Goiânia, Braz",
    "Cixi, China",
    "Karaj, Iran",
    "MOGADISHU, Somalia",
    "Varanasi, India",
    "Córdoba, Argentina",
    "KAMPALA, Uganda",
    "Shiraz, Iran",
    "Multan, Pakistan",
    "Madurai, India",
    "München, Germany",
    "Kalyan, India",
    "Quanzhou, China",
    "Adana, Turkey",
    "Bazhong, China",
    "Fès, Morocco",
    "OUAGADOUGOU, Burkina Faso",
    "Caloocan, Philippines",
    "Kalookan, Philippines",
    "Saitama, Japan",
    "PRAGUE, Czech Republic",
    "Kumasi, Ghana",
    "Meerut, India",
    "Hyderabad, Pakistan",
    "OTTAWA, Canada",
    "Yushu, China",
    "Barranquilla, Colombia",
    "Hiroshima, Japan",
    "Chifeng, China",
    "Nashik, India",
    "Makasar, Indonesia",
    "SOFIA, Bulgaria",
    "Rizhao, China",
    "Davao, Philippines",
    "Samara, Russia",
    "Omsk, Russia",
    "Gujranwala, Pakistan",
    "Adelaide, Australia",
    "La Matanza, Argentina",
    "Rosario, Argentina",
    "Jabalpur, India",
    "Kazan, Russia",
    "Jimo, China",
    "Dingzhou, China",
    "Calgary, Canada",
    "YEREVAN, Armenia",
    "Jamshedpur, India",
    "Zürich, Switzerland",
    "Pikine-Guediawaye, Senegal",
    "Anqiu, China",
    "Chelyabinsk, Russia",
    "CONAKRY, Guinea",
    "Asansol, India",
    "Ulsan, South Korea",
    "Toluca, Mexico",
    "Marrakech, Morocco",
    "Dhanbad, India",
    "TBILISI, Georgia",
    "Hanchuan, China",
    "LUSAKA, Zambia",
    "Qidong, China",
    "Faridabad, India",
    "Rostov-na-Donu, Russia",
    "Edmonton, Canada",
    "Allahabad, India",
    "Beiliu, China",
    "Dnipropetrovsk, Ukraine",
    "Gongzhuling, China",
    "Qinzhou, China",
    "Ufa, Russia",
    "Sendai, Japan",
    "Volgograd, Russia",
    "GUATEMALA CITY, Guatemala",
    "AMSTERDAM, Netherlands",
    "BRUSSELS, Belgium",
    "BAMAKO, Mali",
    "Ziyang, China",
    "ANTANANARIVO, Madagascar",
    "Amritsar, India",
    "Vijayawada, India",
    "Haora, India",
    "Donetsk, Ukraine",
    "Fuzhou, China",
    "Pimpri Chinchwad, India",
    "DUBLIN, Ireland",
    "Rajkot, India",
    "Sao Luís, Brazil",
    "Béni-Mellal, Morocco",
    "Kaduna, Nigeria",
    "Kitakyushu, Japan",
    "Perm, Russia",
    "Odessa, Ukraine",
    "Qom, Iran",
    "Yongchuan, China",
    "Peshawar, Pakistan",
    "ULAANBAATAR, Mongolia",
    "Sao Gonçalo, Brazil",
    "Ghaziabad, India",
    "Köln, Germany",
    "Ahwaz, Iran",
    "Suwon, South Korea",
    "San Luis Potosí, Mexico",
    "Gaziantep, Turkey",
    "Krasnoyarsk, Russia",
    "Chiba, Japan",
    "Voronezh, Russia",
    "Durg-Bhilai Nagar, India",
    "Maceió, Brazil",
    "Al-Madinah, Saudi Arabia",
    "Seongnam, South Korea",
    "San Jose",
    "MANAGUA, Nicaragua",
    "Safi, Morocco",
    "Soweto, South Africa",
    "Cartagena, Colombia",
    "Torino, Italy",
    "Lattakia, Syria",
    "Mérida, Mexico",
    "Göteborg, Sweden",
    "Torreón, Mexico",
    "Salé, Morocco",
    "Tyneside, United Kingdom",
    "Shubra-El-Khema, Egypt",
    "Mombasa, Kenya",
    "TEGUCIGALPA, Honduras",
    "Tiruchchirappalli, India",
    "Saratov, Russia",
    "Santiago de los Caballeros, Dominican",
    "LA PAZ, Bolivia",
    "Sakai, Japan",
    "El Alto, Bolivia",
    "Bogor, Indonesia",
    "Kermanshah, Iran",
    "Liverpool, United Kingdom",
    "Yanshi, China",
    "Guwahati, India",
    "Konya, Turkey",
    "Barquisimeto, Venezuela",
    "Valencia, Spain",
    "Guilin, China",
    "Hamamatsu, Japan",
    "Deir El-Zor, Syria",
    "BISHKEK, Kyrgyzstan",
    "BENGHAZI, Libya",
    "Zaporizhya, Ukraine",
    "Gaoyou, China",
    "Marseille, France",
    "Bandar Lampung, Indonesia",
    "Niigata, Japan",
    "Indianapolis",
    "Haiphong, Viet Nam",
    "Arequipa, Peru",
    "Jacksonville",
    "Tanger, Morocco",
    "Dandong, China",
    "KISHINEV, Moldova",
    "Krasnodar, Russia",
    "ZAGREB, Croatia",
    "Port Elizabeth, South Africa",
    "Mendoza, Argentina",
    "Khulna, Bangladesh",
    "Malang, Indonesia",
    "Padang, Indonesia",
    "Chihuahua, Mexico",
    "Campo Grande, Brazil",
    "Lódz, Poland",
    "Goyang, South Korea",
    "Benin City, Nigeria",
    "Bucheon, South Korea",
    "Kraków, Poland",
    "Lviv, Ukraine",
    "Salem, India",
    "Ad-Dammam, Saudi Arabia",
    "Samut Prakan, Thailand",
    "Nampho, North Korea",
    "Columbus",
    "Bareilly, India",
    "JERUSALEM, Israel",
    "Cuernavaca, Mexico",
    "RIGA, Latvia",
    "Québec, Canada",
    "Cebu, Philippines",
    "Aguascalientes, Mexico",
    "Tolyatti, Russia",
    "Hamilton, Canada",
    "Osasco, Brazil",
    "Nonthaburi, Thailand",
    "Blantyre City, Malawi",
    "Hamhung, North Korea",
    "Jalandhar, India",
    "Al-Rakka, Syria",
    "NIAMEY, Niger",
    "Xiangtan, China",
    "Winnipeg, Canada",
    "Oran, Algeria",
    "Kota, India",
    "Sevilla, Spain",
    "Navi Mumbai, India",
    "Port Harcourt, Nigeria",
    "Saltillo, Mexico",
    "Khartoum North, Sudan",
    "Shizuoka, Japan",
    "Yuanjiang, China",
    "Raipur, India",
    "Kryviy Rig, Ukraine",
    "Querétaro, Mexico",
    "PRETORIA, South Africa",
    "Meknès, Morocco",
    "Bulawayo, Zimbabwe",
    "Okayama, Japan",
    "Santo André, Brazil",
    "RABAT, Morocco",
    "Pakanbaru, Indonesia",
    "Memphis",
    "Joao Pessoa, Brazil",
    "KATHMANDU, Nepal",
    "Antalya, Turkey",
    "Kumamoto, Japan",
    "Palermo, Italy",
    "Nottingham, United Kingdom",
    "Mosul, Iraq",
    "Hermosillo, Mexico",
    "Morelia, Mexico",
    "Tétouan, Morocco",
    "Barnaul, Russia",
    "Jaboatao dos Guarapes, Brazil",
    "Cotonou, Benin",
    "Zaragoza, Spain",
    "Tampico, Mexico",
    "Morón, Argentina",
    "La Plata, Argentina",
    "Ciudad Guayana, Venezuela",
    "Moradabad, India",
    "Acapulco, Mexico",
    "Veracruz, Mexico",
    "Ulyanovsk, Russia",
    "Wroclaw, Poland",
    "Puente Alto, Chile",
    "Gorakhpur, India",
    "Fort Worth",
    "San Miguel de Tucumán, Argentina",
    "The Hague, Netherlands",
    "Culiacán Rosales, Mexico",
    "Maiduguri, Nigeria",
    "Genova, Italy",
    "Izhevsk, Russia",
    "Jeonju, South Korea",
    "COLOMBO, Sri Lanka",
    "Zaria, Nigeria",
    "Anlu, China",
    "Sao José dos Campos, Brazil",
    "Charlotte",
    "Malmö, Sweden",
    "Kagoshima, Japan",
    "Yaroslave, Russia",
    "Contagem, Brazil",
    "Zamboanga, Philippines",
    "Orumiyeh, Iran",
    "Kisumu, Kenya",
    "Uberlândia, Brazil",
    "El Paso",
    "Yunzhou, China",
    "Kénitra, Morocco",
    "Diyarbakir, Turkey",
    "Jurong, China",
    "Cúcuta, Colombia",
    "Dortmund, Germany",
    "Cochabamba, Bolivia",
    "Cheongju, South Korea",
    "Chongjin, North Korea",
    "Stuttgart, Germany",
    "KINGSTON, Jamaica",
    "Milwaukee",
    "Sorocaba, Brazil",
    "Glasgow, United Kingdom",
    "Khabarovsk, Russia",
    "Irkutsk, Russia",
    "Tyumen, Russia",
    "Lomas de Zamora, Argentina",
    "Funabashi, Japan",
    "Düsseldorf, Germany",
    "Içel, Turkey",
    "Maanshan, China",
    "Bandjarmasin, Indonesia",
    "Callao, Peru",
    "Poznan, Poland",
    "Kayseri, Turkey",
    "Quetta, Pakistan",
    "HELSINKI, Finland",
    "Novokuznetsk, Russia",
    "Málaga, Spain",
    "Hachioji, Japan",
    "Ribeirao Prêto,",
    "NOUAKCHOTT, Mauritania",
    "Dezhou, China",
    "Makhachkala, Russia",
    "Bristol, United Kingdom",
    "ASTANA, Kazakhstan",
    "Yizhou, China",
    "Nashville-Davidson",
    "Orenburg, Russia",
    "Cancun, Mexico",
    "OSLO, Norway",
    "Cuiabá, Brazil",
    "VILNIUS, Lithuania",
    "Bremen, Germany",
    "Feira de Santana, Brazil",
    "Portland",
    "Reynosa, Mexico",
    "Ilorin, Nigeria",
    "Oklahoma City",
    "Nakhon Ratchasima, Thailand",
    "Kerman, Iran",
    "ISLAMABAD, Pakistan",
    "DUSHANBE, Tajikistan",
    "VIENTIANE, Laos",
    "ABU DHABI, United Arab Emirates",
    "Shimkent, Kazakhstan",
    "Imbaba, Egypt",
    "SKOPLJE, Macedonia",
    "Kadhimain, Iraq",
    "Kemerovo, Russia",
    "Duisburg, Germany",
    "Rasht, Iran"
]


class Command(BaseCommand):

    help = "It seeds the DB with tons of stuff"

    def handle(self, *args, **options):

        # CREATE CITY

        google_places = GooglePlaces(settings.GOOGLE_MAPS_KEY)
        for i in cityNames:
            query_result = google_places.text_search(query=i, language="en",
                                                     types="(cities,)",
                                                     )
            createCity(query_result.places[0].place_id)

        # CREATE USER

        user_seeder = Seed.seeder()
        randomCountry = location_models.Country.objects.all()
        randomCity = location_models.City.objects.all()
        with open('pinner/users/adjectives.json', mode='rt', encoding='utf-8') as adjectives:
            with open('pinner/users/nouns.json', mode='rt', encoding='utf-8') as nouns:
                adjectives = json.load(adjectives)
                nouns = json.load(nouns)
                user_seeder.add_entity(
                    user_models.User,
                    300,
                    {
                        "uuid": lambda x: uuid.uuid4(),
                        "username": lambda x: random.choice(adjectives) + random.choice(nouns).capitalize(),
                        "residence": lambda x: random.choice(randomCountry),
                        "nationality": lambda x: random.choice(randomCountry),
                        "is_staff": False,
                        "is_superuser": False,
                        "current_city": lambda x: random.choice(randomCity),
                        "current_country": None,
                        "current_continent": None,
                        "is_dark_mode": True,
                        "is_hide_photos": False,
                        "is_hide_trips": False,
                        "is_hide_cities": False,
                        "is_hide_countries": False,
                        "is_hide_continents": False,
                        "is_auto_location_report": True,
                        "fbId": None,
                        "appleId": None,
                        "is_verified_phone_number": False,
                        "is_verified_email_address": False,
                        "avatar_url": None,
                        "app_avatar_url": None,
                        "push_token": None,
                        "distance": 0,
                        "website": None,
                    },
                )
                user_seeder.execute()

        # CREATE MOVENOTIFICATION

        move_otification_seeder = Seed.seeder()
        allUsers = user_models.User.objects.all()
        randomCity = location_models.City.objects.all()
        move_otification_seeder.add_entity(
            notification_models.MoveNotification,
            2000,
            {
                "actor": lambda x: random.choice(allUsers),
                "city": lambda x: random.choice(randomCity),
                "country": None,
                "continent": None,
            },
        )
        move_otification_seeder.execute()

        # UPDATE USER

        allUser = user_models.User.objects.all()
        for user in allUser:
            distance = 0
            user.current_country = user.current_city.country
            user.current_continent = user.current_city.country.continent
            trips = notification_models.MoveNotification.objects.filter(actor=user).order_by('-created_at')
            try:
                for i, trip in enumerate(trips):
                    try:
                        lon1, lat1, lon2, lat2 = map(
                            radians, [trips[i].city.longitude, trips[i].city.latitude, trips[i+1].city.longitude, trips[i+1].city.latitude])
                        dist = 6371 * (
                            acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
                        )
                        distance += dist
                    except (ZeroDivisionError, IndexError) as e:
                        print(e)
                user.distance = round(distance)
                user.save()
            except notification_models.MoveNotification.DoesNotExist:
                pass

        # UPDATE MOVENOTIFICATION

        allMoveNotification = notification_models.MoveNotification.objects.all()
        for i in allMoveNotification:
            i.country = i.city.country
            i.continent = i.city.country.continent
            i.save()

        self.stdout.write(self.style.SUCCESS(f"Everything seeded"))
