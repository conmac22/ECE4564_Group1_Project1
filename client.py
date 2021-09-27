import argparse, tweepy

if __name__ == "__main__":
    # Handle command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-sip', type=str, required=True, help="Server IP Address", metavar="SERVER_IP")
    parser.add_argument('-sp', type=int, required=True, help="Server Port Number", metavar="SERVER_PORT")
    parser.add_argument('-z', type=int, required=True, help="Socket Size", metavar="SOCKET_SIZE")
    args = parser.parse_args()

    server_ip = args.sip
    server_port = args.sp
    socket_size = args.z

    # Log-in for Twitter API access
    CONSUMER_KEY = 'z3zfmCPKex24aihq6liafKVEw'
    CONSUMER_SECRET = 'hXxj4M7OtLnT6fQEQyQcBCgiAudYiCSh4taiWjBIip6iYULFgM'
    ACCESS_TOKEN = '1440758875955732486-CGSl8dGWtKM7x81yvYWbWLKh2Cy1q8'
    ACCESS_TOKEN_SECRET = 'rAkcDimN9I4AxEUio44NCpN2Ip6ZNINM48YFlIEFSz7px'

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Extract tweet from question
    api = tweepy.API(auth)
    question = 'test'
    class StreamEcho(tweepy.Stream):
        def on_status(self, tweet):
            global question
            question = tweet.text
            tweets_listener.disconnect()

    tweets_listener = StreamEcho(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    thread = tweets_listener.filter(follow=[1440758875955732486], threaded=True)
    thread.join()
    print(question)
    # Encrypt question
    # Compute checksum of encrypted question
    # Build question payload (tuple:encrypt/decrypt key and encrypted text)
    # Send question payload to server
    # Wait for answer payload
    # Recieve answer payload
    # Deconstruct answer payload (verify checksum and decrypt answer)
    # Display answer on monitor
    # Send answer to IBM Watson
    # Download answer audio from IBM Watson
    # Play answer audio
