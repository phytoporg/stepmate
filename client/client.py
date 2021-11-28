import requests
import argparse

def main(args):
    uri = f'http://{args.server_host}:{args.server_port}/api/songs/list'
    r = requests.get(uri)
    if r.status_code != 200:
        print('GET Request failed with code {r.status_code}')
        exit(-1)

    # TODO
    print(r.json())

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-host', type=str, required=True)
    parser.add_argument('--server-port', type=int, required=True)

    main(parser.parse_args())
