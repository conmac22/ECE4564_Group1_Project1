import argparse
import ClientKeys
import hashlib
import pickle
import ServerKeys
import socket
import sys
import tweepy
import vlc
from cryptography.fernet import Fernet
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

if __name__ == "__main__":
    # Handle command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-sip', type=str, required=True, help="Server IP Address", metavar="SERVER_IP")
    parser.add_argument('-sp', type=int, required=True, help="Server Port Number", metavar="SERVER_PORT")
    parser.add_argument('-z', type=int, required=True, help="Socket Size", metavar="SOCKET_SIZE")
    args = parser.parse_args()

    SERVER_IP = args.sip
    SERVER_PORT = args.sp
    SOCKET_SIZE = args.z

    # Set up server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("[Client 01]-Connecting to " + str(SERVER_IP) + " on port " + str(SERVER_PORT))

    # Log-in for Twitter API access
    CONSUMER_KEY = ClientKeys.CONSUMER_KEY
    CONSUMER_SECRET = ClientKeys.CONSUMER_SECRET
    ACCESS_TOKEN = ClientKeys.ACCESS_TOKEN
    ACCESS_TOKEN_SECRET = ClientKeys.ACCESS_TOKEN_SECRET

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Extract tweet from question
    api = tweepy.API(auth)

    class StreamAndServer(tweepy.Stream):
        def on_status(self, tweet):
            print('[Client 03]-New question found: ' + tweet.text)
            self.send(tweet.text)

        def send(self, question):
            # Build question payload
            key = Fernet.generate_key()
            print('[Client 04]-Generated encryption key: ', end='')
            print(key)

            encryption = Fernet(key)
            encrypted_question = encryption.encrypt(question.encode())
            print('Client 05]-Cipher text: ', end='')
            print(encrypted_question)

            checksum = hashlib.md5(encrypted_question).hexdigest()
            payload = (key, encrypted_question, checksum)
            print('[Client 06]-Question payload: ', end='')
            print(payload)

            # Send payload to server and recieve answer
            pickled_payload = pickle.dumps(payload)
            print('[Client 07]-Sending question: ', end='')
            print(pickled_payload)
            sock.send(pickled_payload)

            server_response = sock.recv(SOCKET_SIZE)
            answer_payload = pickle.loads(server_response)
            print('[Client 08]-Received data: ', end='')
            print(answer_payload)
            answer_encrypted = answer_payload[0]
            answer_checksum_expected = answer_payload[1]

            # Verify checksum
            answer_checksum_actual = hashlib.md5(answer_encrypted).hexdigest()
            if answer_checksum_actual != answer_checksum_expected:
                print("Answer checksum is incorrect!")
                sys.exit(1)
            print('[Client 09]-Decrypt key: ', end='')
            print(key)
            answer = encryption.decrypt(answer_encrypted).decode()
            print('[Client 10]-Plain text: ', end='')
            print(answer)

            # Play answer
            # Example Code copied from https://cloud.ibm.com/apidocs/text-to-speech?code=python
            authenticator = IAMAuthenticator(ServerKeys.watsonKey)
            text_to_speech = TextToSpeechV1(authenticator=authenticator)
            text_to_speech.set_service_url(ServerKeys.watsonURL)
            with open('answer.wav', 'wb') as audio_file:
                audio_file.write(
                    text_to_speech.synthesize(
                        answer,
                        voice='en-US_AllisonV3Voice',
                        accept='audio/wav'
                    ).get_result().content)
            player = vlc.MediaPlayer('answer.wav')
            print('[Client 11]-Speaking answer: ', end='')
            print(answer)
            player.play()

    try:
        print('[Client 02]-Listening for tweets from Twitter API that contain questions')
        tweets_listener = StreamAndServer(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        tweets_listener.filter(follow=[ClientKeys.TWITTER_ID])
    except KeyboardInterrupt:
        tweets_listener.disconnect()
        print('done')
