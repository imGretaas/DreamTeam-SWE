import funzioni

print_to_file = 0
print_to_log = 0


print("Hello to Crawler!\n")


def main(event, context):

    cl = funzioni.loginCrawler()

    if cl is not None:

        # profilo da cui effettuare il crawling es:gabrielezanatt, lorenzolinguini, paolo_vizzari
        crawlingFromProfile = 'paolo_vizzari'
        print("Get user ID for " + crawlingFromProfile)
        id = cl.user_id_from_username(crawlingFromProfile)

        posts = funzioni.getPostData(cl, id, 5)

        posts = funzioni.analyzePosts(print_to_file, print_to_log, posts)

        funzioni.insertPostAurora(posts)

    else:
        print("Login Failed!")


if __name__ == "__main__":
    main('', '')
