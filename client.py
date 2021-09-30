import argparse, tweepy, hashlib, pickle, socket, ClientKeys
from cryptography.fernet import Fernet

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

            # Send payload to server
            print('[Client 07]-Sending question: ', end='')
            sock.send(pickle.dumps(payload))
            server_response = sock.recv(SOCKET_SIZE)
            answer = pickle.loads(server_response)

    try:
        print('[Client 02]-Listening for tweets from Twitter API that contain questions')
        tweets_listener = StreamAndServer(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        tweets_listener.filter(follow=[ClientKeys.TWITTER_ID])
    except KeyboardInterrupt:
        tweets_listener.disconnect()
        print('done')



    # Deconstruct answer payload (verify checksum and decrypt answer)
    # Display answer on monitor
    # Send answer to IBM Watson
    # Download answer audio from IBM Watson
    # Play answer audio
