###############################################################
# This program:
# 1. Asks the user to enter an access token or use the hard coded access token
# 2. Lists the users in Webex Teams rooms
# 3. Asks the user which Webex Teams room to monitor for "/location" requests (e.g. /San Jose)
# 4. Periodically monitors the selected Webex Team room for "/location" messages
# 5. Discovers GPS coordinates for the "location" using MapQuest API
# 6. Discovers the date and time of the next ISS flyover over the "location" using the ISS location API
# 7. Sends the results back to the Webex Team room
#
# The student will:
# 1. Enter the Webex Teams room API endpoint (URL)
# 2. Provide the code to prompt the user for their access token else
#    use the hard coded access token
# 3. Provide the MapQuest API Key
# 4. Extracts the longitude from the MapQuest API response using the specific key
# 5. Convers Unix Epoch timestamp to a human readable format
# 6. Enter the Webex Teams messages API endpoint (URL)
###############################################################

# Libraries

import requests
import json
import time
import urllib.parse

#######################################################################################
#     Ask the user to use either the hard-coded token (access token within the code)
#     or for the user to input their access token.
#     Assign the hard-coded or user-entered access token to the variable accessToken.
#######################################################################################

# Student Step #2
#    Following this comment and using the accessToken variable below, modify the code to
#    ask the user to use either hard-coded or user entered access token.

choice = input("Do you want to use the hard-coded access token? (y/n)? ")
if choice == "n" or choice == "N":
    accessToken = input("Please enter your access token. ")
    accessToken = "Bearer " + accessToken

else:
    accessToken = "Bearer NmU0YjlhMDUtZmE3MC00MTJhLWFkM2YtMGU4OTIyNGQzN2VjMDE2ZTg3MDEtYWZk_PF84_consumer"

#######################################################################################
#     Using the requests library, create a new HTTP GET Request against the Webex Teams API Endpoint for Webex Teams Rooms:
#     the local object "r" will hold the returned data.
#######################################################################################

#  Student Step #3
#     Modify the code below to use the Webex Teams room API endpoint (URL)


r = requests.get("https://api.ciscospark.com/v1/rooms",
                 headers={"Authorization": accessToken}
                 )

#######################################################################################
# Check if the response from the API call was OK (r. code 200)
#######################################################################################
if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

#######################################################################################
# Displays a list of rooms.
#
# If you want to see additional key/value pairs such as roomID:
#	print ("Room name: '" + room["title"] + "' room ID: " + room["id"])
#######################################################################################
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(room["title"])

#######################################################################################
# Searches for name of the room and displays the room
#######################################################################################

while True:
    # Input the name of the room to be searched 
    roomNameToSearch = input("Which room should be monitored for /route")

    # Defines a variable that will hold the roomId 
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




while True:

    time.sleep(1)

    GetParameters = {
        "roomId": roomIdToGetMessages,
        "max": 1
    }
    r = requests.get("https://api.ciscospark.com/v1/messages",
                     params=GetParameters,
                     headers={"Authorization": accessToken}
                     )
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

    json_data = r.json()
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")
    # store the array of messages
    messages = json_data["items"]
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # Checking for /route #
    gevondenmessage = message.find("/route")


    if gevondenmessage == 0:
        schrijftextwebex('Geef uw startlocatie in met /route $locatie$')

        while True:
            # always add 1 second of delay to the loop to not go over a rate limit of API calls
            time.sleep(1)

            # the Webex Teams GET parameters
            #  "roomId" is is ID of the selected room
            #  "max": 1  limits to get only the very last message in the room
            GetParameters = {
                "roomId": roomIdToGetMessages,
                "max": 1
            }

            # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
            r = requests.get("https://api.ciscospark.com/v1/messages",
                             params=GetParameters,
                             headers={"Authorization": accessToken}
                             )
            # verify if the retuned HTTP status code is 200/OK
            if not r.status_code == 200:
                raise Exception(
                    "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

            # get the JSON formatted returned data
            json_data = r.json()
            # check if there are any messages in the "items" array
            if len(json_data["items"]) == 0:
                raise Exception("There are no messages in the room.")

            # store the array of messages
            messages = json_data["items"]
            # store the text of the first message in the array
            message = messages[0]["text"]
            print("Received message: " + message)

            # Checking for /route #
            gevondenmessage = message.find("/route")
            if gevondenmessage == 0:
                orig = message[7:]
                schrijftextwebex('Geef uw eindlocatie in met /route $locatie$')

                while True:
                    # always add 1 second of delay to the loop to not go over a rate limit of API calls
                    time.sleep(1)


                    GetParameters = {
                        "roomId": roomIdToGetMessages,
                        "max": 1
                    }


                    r = requests.get("https://api.ciscospark.com/v1/messages",
                                     params=GetParameters,
                                     headers={"Authorization": accessToken}
                                     )
                    # verify if the retuned HTTP status code is 200/OK
                    if not r.status_code == 200:
                        raise Exception(
                            "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code,
                                                                                                     r.text))

                    # get the JSON formatted returned data
                    json_data = r.json()
                    # check if there are any messages in the "items" array
                    if len(json_data["items"]) == 0:
                        raise Exception("There are no messages in the room.")

                    # store the array of messages
                    messages = json_data["items"]
                    # store the text of the first message in the array
                    message = messages[0]["text"]
                    print("Received message: " + message)

                    # Checking for /route #
                    gevondenmessage = message.find("/route")
                    if gevondenmessage == 0:
                        dest = message[7:]


# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
