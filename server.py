from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import wolframalpha
import ServerKeys
import argparse, pickle, socket
from cryptography.fernet import Fernet

if __name__ == "__main__":
    authenticator = IAMAuthenticator(ServerKeys.watsonKey)
    text_to_speech = TextToSpeechV1(authenticator=authenticator)
    text_to_speech.set_service_url(ServerKeys.watsonURL)
    wClient = wolframalpha.Client(ServerKeys.app_id)

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
        encryption = Fernet(payload[0]
        checksum = payload[2]

        #Verify checksum
        vChecksum = hashlib.md5(question_encrypted).hexdigest()
        if checksum != vChecksum:
            print('Checksum does not match')
        
        #Get question
        question = encryption.decrypt(question_encrypted).decode()
        print(question)
        
        with open('question.wav', 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(
                    question,
                    voice='en-US_AllisonV3Voice',
                    accept='audio/wav'
                ).get_result().content)
    
        #playsound('hello_world.wav')
        
        # Get answer
        res = wClient.query(question)
        answer = next(res.results).text
        print('Answer: ', end='')
        print(answer)

        # Build answer payload
        key = Fernet.generate_key()
        print('Generated encryption key: ', end='')
        print(key)

        encryption = Fernet(key)
        encrypted_answer = encryption.encrypt(answer.encode())
        print('Cipher text', end='')
        print(encrypted_answer)

        checksum = hashlib.md5(encrypted_answer).hexdigest()
        payload = (encrypted_answer, checksum)
        print('Answer payload: ', end='')
        print(payload)

        # Send payload to client
        print('Sending answer: ', end='')
        sock.send(pickle.dumps(payload))
        
        client.close()
        # Comment out break to make server infinite 
        break;
