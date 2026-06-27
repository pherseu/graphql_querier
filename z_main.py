# https://developer.webex-cx.com/documentation/guides/getting-started-with-search-api

import requests
import json

from datetime import datetime, timezone

def converter_para_epoch(data_str):
    dt = datetime.strptime(data_str, "%Y/%m/%d %H:%M:%S")
    # Definir o fuso horário como UTC
    dt_utc = dt.replace(tzinfo=timezone.utc)
    
    # Converter para epoch time (retorna float e convertemos para inteiro)
    return int(dt_utc.timestamp()) * 1000

def get_customer(name):
    aux = {"name": name}
    if name == "Rendimento":
        aux["orgid"] = "b1d28762-9d04-465e-a1d3-fa0cbfa88503"
        return aux
    elif name == "Omint":
        aux["orgid"] = "44e1791a-132a-4a90-8123-1999444663fd"
        return aux

def graphqlQuery(orgid, token, filename, starttime, endtime):
    url = f"https://api.wxcc-us1.cisco.com/search?orgId={orgid}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }

    with open("./input/" + filename + ".txt", 'r') as file:
        query = file.read()

    variables = {
        "from": starttime,
        "to": endtime,
        "channelType": "telephony",
        # "id":"94065e9a-4c4e-447f-9a6e-42ad8940b3c4"
        # "first": 1
    }

    response = requests.post(
        url,
        json={'query': query, 'variables': variables},
        headers=headers
        )
    
    print(response)
        
    with open("./output/" + filename + ".json", "w", encoding="utf-8") as json_file:
        json.dump(response.json(), json_file, indent=4, ensure_ascii=False)


customer = get_customer("Rendimento")
token = "YmJkODY4ZDItYTM1ZS00OTg1LWEyNjktN2U1OWU5ZDljY2MxYjU3ODJhOGYtMzBh_P0A1_b1d28762-9d04-465e-a1d3-fa0cbfa88503"
starttime = converter_para_epoch("2025/12/02 00:00:00")
endtime = converter_para_epoch("2025/12/03 00:00:00")

print(customer)

# Primeira Query de painel
# filename = "painel_a"
# graphqlQuery(orgid=orgid, token=token, filename=filename, starttime=starttime, endtime=endtime)

# Segunda Query de painel
# filename = "painel_b"
# graphqlQuery(orgid=orgid, token=token, filename=filename, starttime=starttime, endtime=endtime)

# Terceira Query de painel - Rendimento Agentes
# filename = "painel_c"
# filename = "painel_c_a"
# filename = "painel_a"
# filename = "painel_canal"
# filename = "painel_d"
# filename = "painel_e"
# filename = "teste"
# filename = "introspection"
# filename = "call_by_call"
# filename = "feedback"
# filename = "query_by_id"
# filename = "call_by_call_pagination"
# filename = "call_by_call_pagination_query"
# filename = "call_by_call_pagination_subquery"

graphqlQuery(orgid=customer['orgid'], token=token, filename=filename, starttime=starttime, endtime=endtime)