# from ibm_watson import TextToSpeechV1
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from playsound import playsound
# import wolframalpha
# import ServerKeys
import argparse, pickle, socket
from cryptography.fernet import Fernet

if __name__ == "__main__":
    # authenticator = IAMAuthenticator(ServerKeys.watsonKey)
    # text_to_speech = TextToSpeechV1(authenticator=authenticator)
    #
    # text_to_speech.set_service_url(ServerKeys.watsonURL)

    # Pull question from Twitter-shit
    parser = argparse.ArgumentParser()
    parser.add_argument('-sp', type=int, required=True, help="Server Port Number", metavar="SERVER_PORT")
    parser.add_argument('-z', type=int, required=True, help="Socket Size", metavar="SOCKET_SIZE")
    args = parser.parse_args()

    # Get question from server
    SERVER_PORT = args.sp
    SOCKET_SIZE = args.z
    HOST = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,SERVER_PORT))
    s.listen()
    while True:
        client, addr = s.accept()
        payload_serialized = client.recv(SOCKET_SIZE)
        payload = pickle.loads(payload_serialized)
        question_encrypted = payload[1]
        encryption = Fernet(payload[0])
        question = encryption.decrypt(question_encrypted).decode()
        print(question)
        client.close()
        # Comment out break to make server infinite 
        break;
    #
    # with open('question.wav', 'wb') as audio_file:
    #     audio_file.write(
    #         text_to_speech.synthesize(
    #             question,
    #             voice='en-US_AllisonV3Voice',
    #             accept='audio/wav'
    #         ).get_result().content)
    #
    # #playsound('hello_world.wav')
    #
    # client = wolframalpha.Client(ServerKeys.app_id)
    # res = client.query(question)
    # answer = next(res.results).text
    #
    # print(answer)
