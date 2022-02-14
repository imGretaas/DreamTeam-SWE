import random


class postData:
    id: str #id utente
    imgURL: str  # url all'immagine del post, non funziona ancora con raccolta immagini
    captionText: str  # testo del post
    locationName: str  # nome della location del post
    lat: float  # latitudine della location del post
    lng: float  # longitudine della location del post
    sentiment: str
    tag_rekognition: list
    emotion_rekognition: str
    category: str #categoria della location
    phone: str #numero di telefono della location
    website: str #sito web della location
    keyS3: str #nome del file in s3

    def __init__(self, id, imgurl, captionText, locationName, lat, lng, category, phone, website):
        self.id = id
        self.imgURL = imgurl
        self.captionText = captionText
        self.locationName = locationName
        self.lat = lat
        self.lng = lng
        self.sentiment = ''
        self.tag_rekognition = list()
        self.emotion_rekognition = None
        self.category = category
        self.phone = phone
        self.website = website
        self.keyS3 = str(random.randint(0,10000000)) + '.jpg' 