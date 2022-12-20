import private
import requests
import random
import time
from web3 import Web3
from eth_account.messages import *

w3 = Web3(Web3.HTTPProvider("https://celo-mainnet.infura.io/v3/493939980300497a8998c48dcd98dd41"))

# testnet
base_url = "https://testnets-api.opensea.io/api/"
wethAddress = "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6"
openSeaFeeRecipient = "0x0000a26b00c1F0DF003000390027140000fAa719"
zone = "0x00000000e88fe2628ebc5da81d2b3cead633e89e"
zonehash = "0x0000000000000000000000000000000000000000000000000000000000000000"
conduitkey = "0x0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000"

collectionslug = "boredapeyachtclub-ehs3xmkzrw"
quantity = 1
pricewei = 500000000000000
creatorbasispoints = 100
creatorfeerecipient = "0xCFf0Ea7978D4b39138A693E82Ddd139c55D24810"
expirationSeconds = 901


def getofferer():
    return private.ADDRESS

def getoffer(pricewei):
    return [{
        "itemType": '1',
        "token": wethAddress,
        "identifierOrCriteria": 0,
        "startAmount": str(pricewei),
        "endAmount": str(pricewei)
    },]

def getplatformfee(pricewei):
    feebasispoints = 250
    fee = (pricewei * feebasispoints) / 10000
    return {
        "itemType": 1,
        "token": wethAddress,
        "identifierOrCriteria": 0,
        "startAmount": str(int(fee)),
        "endAmount": str(int(fee)),
        "recipient": openSeaFeeRecipient
    }

def getcreatorfee(pricewei, recipient, basispoints):
    fee = (pricewei * basispoints) / 10000

    return {
        "itemType": 1,
        "token": wethAddress,
        "identifierOrCriteria": 0,
        "startAmount": str(int(fee)),
        "endAmount": str(int(fee)),
        "recipient": recipient
    }

def gettokenconsideration(collectionslug, quantity):
    offerer = getofferer()
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    payload = {
    "offerer": offerer,
    "quantity": quantity,
    "criteria": {
       "collection": {
         "slug": collectionslug
       }
    }
}
    response = requests.post(base_url + "v2/offers/build", json=payload, headers=headers)
    response = response.json()
    response = response["partialParameters"]["consideration"][0]
    # response["identifierOrCriteria"] = 3500
    response["identifierOrCriteria"] = response["identifierOrCriteria"]
    response["startAmount"] = str(response["startAmount"])
    response["endAmount"] = str(response["endAmount"])
    return response

def getconsideration(collectionslug, quantity, pricewei, recipient, creatorbasispoints):
    return [gettokenconsideration(collectionslug, quantity), getplatformfee(pricewei), getcreatorfee(pricewei, recipient, creatorbasispoints)]

def getsalt():
    return random.randint(0, 100_000)

def buildoffer2(collectionslug, quantity, pricewei, recipient, expirationtime, creatorbasispoints):
    starttime = int(str(int(time.time())))
    endtime = int(str(int(starttime) + int(expirationtime)))
    consideration = getconsideration(collectionslug, quantity, pricewei, recipient, creatorbasispoints)
    offer = {
        "offerer": getofferer(),
        "offer": getoffer(pricewei),
        "consideration": consideration,
        "startTime": int(str(starttime)),
        "endTime": int(str(endtime)),
        "orderType": 2,
        "zone": zone,
        "zoneHash": w3.to_bytes(hexstr=zonehash),
        "salt": int(str(getsalt())),
        "conduitKey": w3.to_bytes(hexstr=conduitkey),
        "totalOriginalConsiderationItems": str(len(consideration)),
        "counter": 0,
    }
    # print("the offer:", offer)
    return offer

def sing_order(msg):
    private_key = private.WALLET_PRIVATE_KEY
    message = encode_defunct(text=str(msg))
    signed_message = w3.eth.account.sign_message(message, private_key=private_key)
    return signed_message.signature.hex()

if __name__ == "__main__":

    here = buildoffer2(collectionslug, quantity, pricewei, creatorfeerecipient, expirationSeconds, creatorbasispoints)
    here_encode = here.copy()
    here_encode['offer'][0]['itemType'] = int(here_encode['offer'][0]['itemType'])
    here_encode['offer'][0]['startAmount'] = int(here_encode['offer'][0]['startAmount'])
    here_encode['offer'][0]['endAmount'] = int(here_encode['offer'][0]['endAmount'])

    here_encode['consideration'][0]['identifierOrCriteria'] = int(here_encode['consideration'][0]['identifierOrCriteria'])
    here_encode['consideration'][0]['startAmount'] = int(here_encode['consideration'][0]['startAmount'])
    here_encode['consideration'][0]['endAmount'] = int(here_encode['consideration'][0]['endAmount'])

    here_encode['consideration'][1]['startAmount'] = int(here_encode['consideration'][1]['startAmount'])
    here_encode['consideration'][1]['endAmount'] = int(here_encode['consideration'][1]['endAmount'])

    here_encode['consideration'][2]['startAmount'] = int(here_encode['consideration'][2]['startAmount'])
    here_encode['consideration'][2]['endAmount'] = int(here_encode['consideration'][2]['endAmount'])

    print("the offer encoded:", here_encode, '\n')

    msg = {
        "types": {
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "version",
                    "type": "string"
                },
                {
                    "name": "chainId",
                    "type": "uint256"
                },
                {
                    "name": "verifyingContract",
                    "type": "address"
                }
            ],
            "OrderComponents": [
                {
                    "name": "offerer",
                    "type": "address"
                },
                {
                    "name": "zone",
                    "type": "address"
                },
                {
                    "name": "offer",
                    "type": "OfferItem[]"
                },
                {
                    "name": "consideration",
                    "type": "ConsiderationItem[]"
                },
                {
                    "name": "orderType",
                    "type": "uint8"
                },
                {
                    "name": "startTime",
                    "type": "uint256"
                },
                {
                    "name": "endTime",
                    "type": "uint256"
                },
                {
                    "name": "zoneHash",
                    "type": "bytes32"
                },
                {
                    "name": "salt",
                    "type": "uint256"
                },
                {
                    "name": "conduitKey",
                    "type": "bytes32"
                },
                {
                    "name": "counter",
                    "type": "uint256"
                }
            ],
            "OfferItem": [
                {
                    "name": "itemType",
                    "type": "uint8"
                },
                {
                    "name": "token",
                    "type": "address"
                },
                {
                    "name": "identifierOrCriteria",
                    "type": "uint256"
                },
                {
                    "name": "startAmount",
                    "type": "uint256"
                },
                {
                    "name": "endAmount",
                    "type": "uint256"
                }
            ],
            "ConsiderationItem": [
                {
                    "name": "itemType",
                    "type": "uint8"
                },
                {
                    "name": "token",
                    "type": "address"
                },
                {
                    "name": "identifierOrCriteria",
                    "type": "uint256"
                },
                {
                    "name": "startAmount",
                    "type": "uint256"
                },
                {
                    "name": "endAmount",
                    "type": "uint256"
                },
                {
                    "name": "recipient",
                    "type": "address"
                }
            ]
        },
        "primaryType": "OrderComponents",
        "domain": {
            "name": "Seaport",
            "version": "1.1",
            "chainId": 5,
            "verifyingContract": "0x00000000006c3852cbEf3e08E8dF289169EdE581"
        },
        "message": here
    }
    encoded_data = encode_structured_data(msg)
    data = w3.eth.account.sign_message(encoded_data, private_key=private.WALLET_PRIVATE_KEY)
    signature = data.signature.hex()

    print("the signature:", signature, '\n')

    time.sleep(3)

    here['startTime'] = str(here['startTime'])
    here['endTime'] = str(here['endTime'])
    here['zoneHash'] = zonehash
    here['conduitKey'] = conduitkey
    here['salt'] = str(here['salt'])
    here['totalOriginalConsiderationItems'] = str(here['totalOriginalConsiderationItems'])
    here_encode = here.copy()
    here_encode['offer'][0]['itemType'] = str(here_encode['offer'][0]['itemType'])
    here_encode['offer'][0]['startAmount'] = str(here_encode['offer'][0]['startAmount'])
    here_encode['offer'][0]['endAmount'] = str(here_encode['offer'][0]['endAmount'])

    here_encode['consideration'][0]['identifierOrCriteria'] = str(
        here_encode['consideration'][0]['identifierOrCriteria'])
    here_encode['consideration'][0]['startAmount'] = str(here_encode['consideration'][0]['startAmount'])
    here_encode['consideration'][0]['endAmount'] = str(here_encode['consideration'][0]['endAmount'])

    here_encode['consideration'][1]['startAmount'] = str(here_encode['consideration'][1]['startAmount'])
    here_encode['consideration'][1]['endAmount'] = str(here_encode['consideration'][1]['endAmount'])

    here_encode['consideration'][2]['startAmount'] = str(here_encode['consideration'][2]['startAmount'])
    here_encode['consideration'][2]['endAmount'] = str(here_encode['consideration'][2]['endAmount'])
    here = here_encode.copy()

    print("the offer decoded:", here, '\n')

    data_pay = {
        "criteria": {
            "collection": {
                "slug": collectionslug
            }
        },
        "protocol_data": {
            "parameters": here,
            "signature": str(signature)
        }
    }

    result = requests.post(base_url + "v2/offers", json=data_pay)
    print(result.json())
