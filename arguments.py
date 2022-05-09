# Imports
import argparse


# Function declarations
def argumentsErrorHandling(phone, webcam, url):
    if phone and webcam:
        raise ValueError("You should choose between phone and webcam not booth")
    if phone and not url:
        raise ValueError("You should use url argument when you choose the phone camera")
    if webcam and url:
        raise ValueError("You should not use url argument when you use the webcam")


def getArguments():
    mode = None
    ap = argparse.ArgumentParser()

    ap.add_argument("-p", "--phone", help="uses the camera of a phone by url (url needed)", action="store_true")
    ap.add_argument("-u", "--url", help="url of the phone camera")
    ap.add_argument("-w", "--webcam", help="uses the webcam of the computer", action="store_true")

    args = vars(ap.parse_args())

    argumentsErrorHandling(args["phone"], args["webcam"], args["url"])

    if args["phone"]:
        mode = "phone"
    elif args["webcam"]:
        mode = "webcam"
    url = args["url"]

    return mode, url
