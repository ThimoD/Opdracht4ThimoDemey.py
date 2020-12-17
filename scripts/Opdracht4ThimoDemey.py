import requests
import json
import time
import urllib.parse

# Webex API acces token (12 uur geldig)
# https://developer.webex.com/docs/api/getting-started

choice = input("Do you want to use the hard-coded access token? (y/n)? ")
if choice == "n" or choice == "N":
    accessToken = input("Please enter your access token. ")
    accessToken = "Bearer " + accessToken

else:
    accessToken = "Bearer Mjk0YmQyZTItYzRlNy00YTJjLWFmNDctYjI1M2Y2Mjk2MDcwZWM0NWY3ZTMtNGJk_PF84_consumer"

r = requests.get("https://api.ciscospark.com/v1/rooms",
                 headers={"Authorization": accessToken}
                 )

if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))


# Displays a list of rooms.
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(room["title"])

while True:
    roomNameToSearch = input("Which room should be monitored for /route")
    roomIdToGetMessages = None

    for room in rooms:
        # Searches for the room "title" using the variable roomNameToSearch 
        if (room["title"].find(roomNameToSearch) != -1):
            # Displays the rooms found using the variable roomNameToSearch (additional options included)
            print("Found rooms with the word " + roomNameToSearch)
            print(room["title"])

            # Stores room id and room title into variables
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if (roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break


def schrijftextwebex(Text):
    post_data = {
        "roomId": roomIdToGetMessages,
        "text": Text
    }

    r = requests.post("https://api.ciscospark.com/v1/messages",
                      data=json.dumps(post_data),
                      headers={"Authorization": accessToken,
                               "Content-Type": "application/json"})
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    return


def leestextwebex(optie):
    invoer = -1

    GetParameters = {"roomId": roomIdToGetMessages, "max": 1}

    while invoer == -1:
        time.sleep(1)
        r = requests.get("https://api.ciscospark.com/v1/messages",
                         params=GetParameters,
                         headers={"Authorization": accessToken}
                         )

        if r.status_code == 200:
            json_data = r.json()
            if len(json_data["items"]) == 0:
                raise Exception("There are no messages in the room.")
            # store the array of messages
            messages = json_data["items"]
            # store the text of the first message in the array
            message = messages[0]["text"]
            print("received message: " + message)
            if message.find("/route") == 0:
                if optie == 0:
                    locatie = "/route"
                    schrijftextwebex('Geef uw startlocatie in met /route $locatie$')
                if optie == 1:
                    locatie = message[7:]
                    schrijftextwebex('Geef uw eindlocatie in met /route $locatie$')
                if optie == 2:
                    locatie = message[7:]
                invoer = optie

        else:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    return locatie

schrijftextwebex('Start het programma met /route.')

while True:
    if leestextwebex(0) == "/route":
        orig = leestextwebex(1)
        dest = leestextwebex(2)

        beschrijving = "------------------------------\n"
        main_api = "https://www.mapquestapi.com/directions/v2/route?"
        key = "glMBkWdaVP2Qg4n9u7oisdqlxdKyACt1"
        url: str = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest})
        json_data = requests.get(url).json()
        json_status = json_data["info"]["statuscode"]
        for each in json_data["route"]["legs"][0]["maneuvers"]:
            beschrijving += ((each["narrative"]) + " (" + str(
                "{:.2f}".format((each["distance"]) * 1.61) + " km).\n"))
        beschrijving += "------------------------------\n"
        beschrijving += "Start opnieuw door het commando /route in te voeren."
        schrijftextwebex(beschrijving)

