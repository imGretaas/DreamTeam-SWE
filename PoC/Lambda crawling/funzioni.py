from instagrapi import Client
from instagrapi.exceptions import (ClientError)

import json
import requests

import boto3

from postData import postData

ACCOUNT_USERNAME_1 = 'non possiamo metterla su una repo pubblica'
ACCOUNT_PASSWORD_1 = 'non possiamo metterla su una repo pubblica'

ACCOUNT_USERNAME_2 = 'non possiamo metterla su una repo pubblica'
ACCOUNT_PASSWORD_2 = 'non possiamo metterla su una repo pubblica'

AWS_KEY = 'non possiamo metterla su una repo pubblica'
AWS_PSW = 'non possiamo metterla su una repo pubblica'
AWS_REGION = 'eu-central-1'

# ritorna un array di stringhe contente tutti gli username dei profili pubblici seguiti dal profilo passato come parametro


def loginCrawler() -> "Client":
    try:
        print("Login in progress...")
        cl = Client()
        cl.login(ACCOUNT_USERNAME_1, ACCOUNT_PASSWORD_1)

        print("Login crawler Successful!!")
        return cl
    except (ClientError):
        print('http bad request trying to login with ' + ACCOUNT_USERNAME_1)

    return None


def getFollowingList(cl: Client, id):
    following = cl.user_following_v1(id)
    followingList = []
    for users in following:
        if not (users.is_private):
            followingList.append(users.username)
    return followingList

# ritorna una lista di oggetti di tipo postData corrispondente ai post del profilo passato come parametro


def getPostData(cl: Client, id, amount) -> 'list[postData]':
    print("Taking post...")
    medias = cl.user_medias_v1(id, amount)
    data = list()
    for media in medias:
        if media.media_type == 1: #il media è una foto
            url = media.thumbnail_url
        elif media.media_type == 8: #il media è un album
            album = media.resources
            url = album[0].thumbnail_url #per ora se è un album prendo solo la prima foto
        text = media.caption_text
        if media.location is not None:
            loc = media.location.name
            lng = media.location.lng
            lat = media.location.lat
            place = cl.fbsearch_places(loc, lat, lng)[0]
            info = cl.location_info_v1(place.pk)
            category = info.category
            web = info.website
            tel = info.phone
        else:
            loc = None
            lng = None
            lat = None
            category = None
            web = None
            tel = None
        data.append(postData(id, url, text, loc, lat, lng, category, tel, web))
    return data


def analyzePosts(print_to_file, print_to_log, posts) -> 'list[postData]':

    comprehend = boto3.client(service_name='comprehend',
                              region_name=AWS_REGION,
                              aws_access_key_id=AWS_KEY,
                              aws_secret_access_key=AWS_PSW)
    rekognition = boto3.client(service_name='rekognition',
                               region_name=AWS_REGION,
                               aws_access_key_id=AWS_KEY,
                               aws_secret_access_key=AWS_PSW)

    file_reko = None
    file_comp = None

    if(print_to_file):
        file_reko = open('result/rekognition.txt', 'w', encoding="utf-8")
        file_comp = open('result/comprehend.txt', 'w', encoding="utf-8")

    for post in posts:
        # analizzo testo con comprehend

        captionText = post.captionText
        # jsonResult = json.dumps(comprehend.detect_sentiment(
        #     Text=post.captionText, LanguageCode='it'), sort_keys=True, indent=4)

        # prendo il risultato di ritorno del json di comprehend e lo salvo nell'oggetto post
        jsonResult = comprehend.detect_sentiment(
            Text=post.captionText, LanguageCode='it')
        setattr(post, "sentiment", jsonResult["Sentiment"])

        #  stampa solo per vedere cosa fa
        if print_to_log:
            print(captionText + '\n')
            print(jsonResult)
            print('\n--------------------\n')

        # location
        if(file_comp is not None):

            file_comp.write(post.captionText + '\n')
            file_comp.write(json.dumps(jsonResult, sort_keys=True, indent=4))
            file_comp.write('\n--------------------\n')

        if print_to_log:
            print(post.locationName)
            print(post.lat)
            print(post.lng)

        # analizzo immagine con rekognition
        if post.imgURL is not None:

            if print_to_log:
                print("URL IMG: " + post.imgURL)

            source_bytes = requests.get(post.imgURL).content

            jsonImgResult = rekognition.detect_labels(
                Image={'Bytes': source_bytes}, MaxLabels=100)

            labels = list()

            persona = False
            for label in jsonImgResult["Labels"]:
                if label["Confidence"] >= 90:
                    labels.append(label["Name"])
                    if label["Name"] == 'Person':
                        persona = True
                else: break

            setattr(post, "tag_rekognition", labels)

            if persona == True:
                facial_analysis = rekognition.detect_faces(Image={'Bytes':source_bytes},Attributes=['ALL'])
                count = 1
                emozioniEmpty = True
                emotion = ''
                for y in facial_analysis["FaceDetails"]:
                    emotion += f'persona {count}:\n'
                    for x in y["Emotions"]: 
                        type = x["Type"]
                        confidence = x["Confidence"]
                        if confidence > 75:
                            emozioniEmpty = False
                            emotion += f'emozione: {type}, confidence: {confidence}\n'
                    count += 1
                if emozioniEmpty == False: 
                    setattr(post,"emotion_rekognition",emotion)
                else: setattr(post,"emotion_rekognition",None)

            jsonToPrint = json.dumps(jsonImgResult, indent=4)

            if print_to_log:
                print(jsonToPrint)

            if(file_reko is not None):
                file_reko.write("\nURL IMG: " + post.imgURL)
                file_reko.write(jsonToPrint)

        else:
            if print_to_log:
                print("\nURL IMG: None")
            if(file_reko is not None):
                file_reko.write("URL IMG: None\n")

    print("Took %d post" % len(posts))
    return posts


def formatPostForDB(post: postData) -> postData:
    if getattr(post, "id") is None:
        setattr(post, "id", "null")
    if getattr(post, "imgURL") is None:
        setattr(post, "imgURL", "null")
        setattr(post, "keyS3", "null")
    else:
        source_bytes = requests.get(getattr(post, "imgURL")).content
        s3 = boto3.client(service_name='s3',
                          region_name=AWS_REGION,
                          aws_access_key_id=AWS_KEY,
                          aws_secret_access_key=AWS_PSW)
        s3.put_object(Body=source_bytes, Bucket='dream-team-instagram-images',
                      Key=getattr(post, "keyS3"),
                      ContentType='image/jpg')
    if getattr(post, "captionText") is None:
        setattr(post, "captionText", "null")
    if getattr(post, "locationName") is None:
        setattr(post, "locationName", "null")
    if getattr(post, "lat") is None:
        setattr(post, "lat", "null")
    else: setattr(post, "lat", str(post.lat))
    if getattr(post, "lng") is None:
        setattr(post, "lng", "null")
    else: setattr(post, "lng", str(post.lng))
    if getattr(post, "sentiment") is None:
        setattr(post, "sentiment", "null")
    if getattr(post, "tag_rekognition") is None:
        setattr(post, "tag_rekognition", "null")
    if getattr(post, "emotion_rekognition") is None:
        setattr(post, "emotion_rekognition", "null")
    if getattr(post, "category") is None:
        setattr(post, "category", "null")
    if getattr(post, "phone") is None or getattr(post, "phone") == '':
        setattr(post, "phone", "null")
    if getattr(post, "website") is None or getattr(post, "website") == '':
        setattr(post, "website", "null")
    return post

def insertPostAurora (posts: list[postData]):
    rdsData = boto3.client('rds-data', region_name=AWS_REGION, aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_PSW)
    cluster_arn = 'non possiamo metterla su una repo pubblica'
    secret_arn = 'non possiamo metterla su una repo pubblica'
    for post in posts:
        post = formatPostForDB(post)
        id_utente = {'name':'id_utente', 'value':{'stringValue': post.id}}
        testo_post = {'name':'testo_post', 'value':{'stringValue': post.captionText}}
        location = {'name':'location', 'value':{'stringValue': post.locationName}}
        lat = {'name':'lat', 'value':{'stringValue': post.lat}}
        lng = {'name':'lng', 'value':{'stringValue': post.lng}}
        sentiment = {'name':'sentiment', 'value':{'stringValue': post.sentiment}}
        tag_rekognition = {'name':'tag_rekognition', 'value':{'stringValue': (', '.join(getattr(post, "tag_rekognition")) if getattr(post, "tag_rekognition") is not None else "null")}}
        emotion_rekognition = {'name':'emotion_rekognition', 'value':{'stringValue': post.emotion_rekognition}}
        phone = {'name':'phone', 'value':{'stringValue': post.phone}}
        website = {'name':'website', 'value':{'stringValue': post.website}}
        image_s3 = {'name':'image_s3', 'value':{'stringValue': post.keyS3}}
        category = {'name':'category', 'value':{'stringValue': post.category}}
        paramSet = [id_utente, testo_post, location, lat, lng, sentiment, tag_rekognition, emotion_rekognition, phone, website, image_s3, category]
        response = rdsData.execute_statement(resourceArn=cluster_arn,
                                      secretArn=secret_arn,
                                      database='sweeat',
                                      sql='insert into db_poc(id_utente, testo_post, location, latitudine, longitudine, sentiment, tag_rekognition, emotion_rekognition, phone, web_site, image_s3, category) VALUES(:id_utente, :testo_post, :location, :lat, :lng, :sentiment, :tag_rekognition, :emotion_rekognition, :phone, :website, :image_s3, :category)',
                                      parameters = paramSet)
    return response
