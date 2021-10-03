from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import wolframalpha, ServerKeys, vlc, argparse, pickle, socket, hashlib, sys
from cryptography.fernet import Fernet

if __name__ == "__main__":
    # Code copied from IBM-Watson: https://cloud.ibm.com/apidocs/text-to-speech?code=python
    authenticator = IAMAuthenticator(ServerKeys.watsonKey)
    text_to_speech = TextToSpeechV1(authenticator=authenticator)
    text_to_speech.set_service_url(ServerKeys.watsonURL)
    
    # Code copied from https://products.wolframalpha.com/docs/WolframAlpha-API-Reference.pdf
    wClient = wolframalpha.Client(ServerKeys.app_id)

    # Pull question from Twitter
    parser = argparse.ArgumentParser()
    parser.add_argument('-sp', type=int, required=True, help="Server Port Number", metavar="SERVER_PORT")
    parser.add_argument('-z', type=int, required=True, help="Socket Size", metavar="SOCKET_SIZE")
    args = parser.parse_args()

    # Get question from server
    SERVER_PORT = args.sp
    SOCKET_SIZE = args.z
    HOST = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ipv4 = socket.gethostbyname(socket.gethostname())
    
    print('[Server 01] - Created socket at ' + str(ipv4) + ' on port ' + str(SERVER_PORT))
    s.bind((HOST,SERVER_PORT))
    s.listen()
    
    print('[Server 02] - Listening for client connections')
    
    client, addr = s.accept()
    print('[Server 03] - Accepted client connection from ' + str(addr) + 'On port ' + str(SERVER_PORT))
    while True:
        
        payload_serialized = client.recv(SOCKET_SIZE)
        payload = pickle.loads(payload_serialized)
        print('[Server 04] - Recieved data: ' + str(payload_serialized))
        question_encrypted = payload[1]
        key = payload[0]
        encryption = Fernet(key)
        print('[Server 05] - Decrypt Key: ',end='')
        print(key)
        checksum = payload[2]
        
        #verify Checksum
        vChecksum = hashlib.md5(question_encrypted).hexdigest()
        if checksum != vChecksum:
            print('Checksum does not match')
            sys.exit(1)
        
        question = encryption.decrypt(question_encrypted).decode()
        print('[Server 06] - Plain text: ' + str(question))
        
        # Code copied from IBM-Watson: https://cloud.ibm.com/apidocs/text-to-speech?code=python
        with open('question.wav', 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(
                    question,
                    voice='en-US_AllisonV3Voice',
                    accept='audio/wav'
                ).get_result().content)
            
        player = vlc.MediaPlayer('question.wav')
        print('[Server 07] - Speaking Question: ' + str(question))
        player.play()
        
        # Get answer, code copied from https://products.wolframalpha.com/docs/WolframAlpha-API-Reference.pdf
        print('[Server 08] - Sending question to wolfram alpha')
        res = wClient.query(question)
        answer = next(res.results).text
        print('[Server 09] - Recieved answer from wolfram alpha: ', end='')
        print(answer)

        # Build answer payload
        print('[Server 10] - Encryption key: ', end='')
        print(key)

        encrypted_answer = encryption.encrypt(answer.encode())
        print('[Server 11] - Cipher text', end='')
        print(encrypted_answer)

        checksum = hashlib.md5(encrypted_answer).hexdigest()
        print('[Server 12] - Generated md5 checksum:', end='')
        print(checksum)
        payload = (encrypted_answer, checksum)
        print('[Server 13] - Answer payload: ', end='')
        print(payload)

        # Send payload to client
        pickled_payload = pickle.dumps(payload)
        print('[Server 14] - Sending answer: ', end='')
        print(answer)
        client.send(pickled_payload)
        
        
        
    


