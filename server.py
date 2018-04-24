"""
links of reference:
    -https://docs.python.org/3/howto/sockets.html
    -https://docs.python.org/2/library/socket.html#module-socket
    -http://www.delorie.com/gnu/docs/glibc/libc_352.html
    -http://pubs.opengroup.org/onlinepubs/7908799/xns/getsockopt.html
    -https://www.ibm.com/developerworks/linux/tutorials/l-pysocks/
    -https://docs.python.org/3/howto/sockets.html

    Kevin Corcoran 04/2018
"""
import sys, socket, select
from termcolor import colored

HOST = "::"              # Symbolic name meaning all available interfaces
SOCKET_LIST = []            #server's clients
RECV_BUFFER = 4096
PORT = 9009
clearline  = "\x1b[2K\r"

def chat_server():

    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        #create a socket using the given address family, socket type and protocol number.:
        #   AF_INET6 - support for Internet Protocol version 6 (IPv6) 128 bit (16 byte) address structures
        #   SOCK_STREAM - connection orientated
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #Set socket options:
        #   SOL_SOCKET - specified level, the socket itself
        #   SO_REUSEADDR - Option used to prevent this error -> [socket.error: [Errno 98] Address already in use]
        #                  This is because the previous execution has left the socket in a TIME_WAIT state, and can't be immediately reused.
        #                  This flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire.
    server_socket.bind((HOST, PORT,0,0))
        #Bind the socket to address - socket is reachable by any address the machine happens to have
    server_socket.listen(10)
        #Listen for 10 connections made to the socket
    SOCKET_LIST.append(server_socket)
        # add server socket object to the list of readable connections

    print colored("Chat server started on port " + str(PORT)\
                  +"\n*********************************",'green',attrs=['bold'])

    while True:

        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)
            # timeout as zero means it won't block
            # The select method allows you to multiplex events for several sockets
            # and for several different events. For example, you can instruct select
            # to notify you when a socket has data available, when it's possible to
            # write data through a socket, and when an error occurs on a socket
            # and you can perform these actions for many sockets at the same time

        for sock in ready_to_read:

            if sock == server_socket: # if a new connection request is recieved

                conn, addr = server_socket.accept()
                    #conn is a new socket object usable to send and receive data on the connection
                    #addr is the address bound to the socket on the other end of the connection
                SOCKET_LIST.append(conn)

                print colored("Client (%s, %s) Connected" % addr[:2],'green')
                broadcast(server_socket,\
                          conn,\
                          colored(clearline + "[%s,%s] Entered the chat\n"  % addr[:2],'green',attrs=['bold','reverse']))
                print  "No. of Current Clients: ", len(SOCKET_LIST)-1


            else: # a message from a client, not a new connection

                try: # process data recieved from client,

                    data = sock.recv(RECV_BUFFER) #Receive data from the socket of max size 4096bytes

                    if data: # data will have 0bytes if the socket has cosed or is closing

                        # there is something in the socket, a message
                        broadcast(server_socket,\
                                  sock,\
                                  colored(clearline + '[' + str(sock.getpeername()[0])+','\
                                                     + str(sock.getpeername()[1]) + '] ','yellow')\
                                               + colored(data,'white'))

                    else:# socket has zero bits so it is closed or closing

                        if sock in SOCKET_LIST:# i think to get to here it will have to of been in the socket list
                            SOCKET_LIST.remove(sock) # remove the socket that's broken


                        print colored(clearline+"Client (%s, %s) Disconnected\n" % addr[:2],'red')

                        broadcast(server_socket,\
                                  sock,\
                                  colored(clearline+"Client (%s, %s) is now offline\n" % addr[:2],'red',attrs=['bold','reverse']))

                        sock.close
                        print  "No. of Current Clients: ", len(SOCKET_LIST)-1

                except: #failed to receive any data from client. We don't remove since we can try again

                    broadcast(server_socket,\
                              sock,\
                              colored(clearline+"Client (%s, %s) is now offline\n" % addr[:2], 'red',attrs=['bold','reverse']))

                    sock.close()
                    print  "No. of Current Clients: ", len(SOCKET_LIST)-1
                    continue

    server_socket.close()

def broadcast (server_socket, sock, message): # broadcast chat messages to all connected clients

    for socket in SOCKET_LIST:
        # send the message only to peers
        if socket != server_socket and socket != sock : # dont send to the server or to the clients self
            try:

                socket.send(message.encode('ascii'))

            except:

                socket.close()

                if socket in SOCKET_LIST:

                    SOCKET_LIST.remove(socket)

if __name__ == "__main__":

   sys.exit(chat_server())
