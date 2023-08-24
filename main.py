# written by "me"
# my email: pcbe6uy4sxbxhgpna2xyu9hscufpxk5jcb44amzqbm8ttxq6jd@mail2tor.com (real)

# if you get ban don't blame me. it's your fault
# this script only deletes your messages from a discord server of your choice

import requests
import time

def search_messages(token, guild_id, author_id=None, channel_id=None, content=None, offset=None):
    headers = {
        'Authorization': token,
    }
    
    url = f'https://discord.com/api/v10/guilds/{guild_id}/messages/search'
    
    query_params = {}
    if author_id:
        query_params['author_id'] = author_id
    if channel_id:
        query_params['channel_id'] = channel_id
    if content:
        query_params['content'] = content
    if offset:
        query_params['offset'] = offset
    
    response = rate_handling_request("get", url, headers=headers, params=query_params)
    if response == None:
        return None
    
    if response.status_code == 200:
        search_results = response.json()
        print(f"Successfully loaded {len(search_results['messages'])} messages. {search_results['total_results']} total")
        return search_results
    else:
        print(f"Search request failed. Status code: {response.status_code}")
        print(response.text)
        return None


def rate_handling_request(method, url, headers=None, params=None, data=None):
    response = None
    method = method.lower()
    
    try:
        if method == 'get':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'post':
            response = requests.post(url, headers=headers, params=params, json=data)
        elif method == 'delete':
            response = requests.delete(url, headers=headers, params=params)
    except requests.RequestException as e:
        print(f"Request exception: {e}")
        return None
    
    if response != None and response.status_code == 429:
        sleep_time = float(response.headers["retry-after"]) + 1
        print(f"Rate limit exceeded. Waiting for {sleep_time} seconds.")
        time.sleep(sleep_time)
        return rate_handling_request(method, url, headers, params, data)
    
    return response

def delete_messages(token, messages_to_delete, closed_thread_ids):
    headers = {
        'Authorization': token,
    }
    
    for message_id, channel_id in messages_to_delete:
        if channel_id in closed_thread_ids: # thread is closed and you are not able to delete message from here (not even thying to save time)
            continue

        url = f'https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}'
        response = rate_handling_request('delete', url, headers=headers)
            
        if response != None:
            if response.status_code == 204:
                print(f"Message {message_id} deleted successfully from channel {channel_id}.")
            else:
                print(f"Failed to delete message {message_id} from channel {channel_id}. Status code: {response.status_code}")
                if response.text:
                    print(response.text)
        else:
            print("Request failed or encountered an exception.")
            print(response.text)

# Replace 'YOUR_TOKEN' and 'GUILD_ID' with your token and server (guild) ID
token = "YOUR_BOT_TOKEN"
guild_id = "GUILD_ID"
# Replace 'MY_ID' with your discord id
my_id = "MY_ID"

# just checking did you forget to change values or not
assert token != "YOUR_BOT_TOKEN"
assert guild_id != "GUILD_ID"
assert my_id != "MY_ID"

# first collect your own messages
print(f"Collecting messages from server {guild_id}")
messages_to_delete = []
closed_thread_ids = []
offset = 0
while True:
    results = search_messages(token, guild_id, author_id=my_id, offset=offset)
    if results == None:
        time.sleep(1) # sleep on error
        continue # try again

    if len(results["messages"]) == 0:
        break
    
    offset += len(results["messages"])

    for thread in results.get("threads", []):
        if thread["thread_metadata"]["archived"] or thread["thread_metadata"]["locked"]:
            closed_thread_ids.append(thread["id"])

    for message in results["messages"]:
        messages_to_delete.append((message[0]["id"], message[0]["channel_id"]))

delete_messages(token, messages_to_delete, closed_thread_ids)