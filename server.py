# Watson API Key: EUOrEO015oZ0rBlILjh3i8FgCq_Hhc9Woz1dn-PeTXbG
# Watson URL: https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/d1180113-b514-46c0-823c-3c542ed0425b

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

if __name__ == "__main__":

    authenticator = IAMAuthenticator('EUOrEO015oZ0rBlILjh3i8FgCq_Hhc9Woz1dn-PeTXbG')
    text_to_speech = TextToSpeechV1(authenticator=authenticator)

    text_to_speech.set_service_url('https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/d1180113-b514-46c0-823c-3c542ed0425b')

    with open('hello_world.wav', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                'Hello world',
                voice='en-US_AllisonV3Voice',
                accept='audio/wav'
            ).get_result().content)
