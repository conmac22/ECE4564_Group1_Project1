from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from playsound import playsound
import wolframalpha
import key

if __name__ == "__main__":
    authenticator = IAMAuthenticator(key.watsonKey)
    text_to_speech = TextToSpeechV1(authenticator=authenticator)

    text_to_speech.set_service_url(key.watsonURL)

    # Pull question from Twitter-shit
    question = input('Ask a question:')

    with open('question.wav', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                question,
                voice='en-US_AllisonV3Voice',
                accept='audio/wav'
            ).get_result().content)

    #playsound('hello_world.wav')

    client = wolframalpha.Client(key.app_id)
    res = client.query(question)
    answer = next(res.results).text

    print(answer)
