"""
    do not run this in ipython
        initial client disconnects do not function as expected,
            currently no explanation

    Kevin Corcoran 04/2018

"""
import sys, socket, select
from termcolor import colored

def prompt():
    sys.stdout.write(colored('[Me] ','blue')); sys.stdout.flush()

def chat_client():

    if(len(sys.argv) < 3):#ensure arguments are given
        print colored('Usage : python client.py hostname port','red')
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #create a socket for this client
    s.settimeout(2) #Set a timeout on blocking socket operations.

    try: #connect to the remote host

        s.connect((host, port,0,0)) #for IPv6 this is a 4 tuple, IPv4 its a pair

    except:

        print colored('Failed to connect', 'red',attrs=['reverse','bold'])
        sys.exit()

    print colored('**********CONNECTED***********\n','green')
    prompt()

    while True:
        socket_list = [sys.stdin, s]

        ready_to_read,\
        ready_to_write,\
        in_error = select.select(socket_list,\
                                    [],\
                                    [],\
                                    0) #do i need this 0?

        for sock in ready_to_read:

            if sock == s: # incoming message from remote server, s

                data = sock.recv(4096)
                if data:

                    sys.stdout.write(data.decode('ascii'),)
                    prompt()

                else:

                    print colored('\nDisconnected from chat server','red',attrs=['reverse','bold'])
                    sys.exit()

            else: # outgoing message to clients

                msg = colored(sys.stdin.readline(),'white')
                s.send(msg.encode('ascii'))
                prompt()

if __name__ == "__main__":

    sys.exit(chat_client())
