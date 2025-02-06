import socket
import threading

class ChatRoomClient:
    def __init__(self, host, port):
        self.host = host # 服务器主机地址
        self.port = port # 服务器端口号
        self.username = None # 创建服务器套接字
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# 创建一个TCP/IP套接字，使用IPv4地址族（socket.AF_INET）和流式套接字(socket.SOCK_STREAM)
        self.message_event = threading.Event()#创建一个线程事件对象，用于在接收到新消息时发出信号。使得菜单界面和消息接收部分在同一个线程中运行，以确保顺序执行。

    def connect(self):
        self.client_socket.connect((self.host, self.port))#连接到指定的服务器地址和端口号
        self.username = input("Enter your username: ")#输入用户名
        self.client_socket.send(self.username.encode())#客户端的用户名（self.username）转换成字节类型并通过客户端的 socket 连接发送给服务器
        welcome_message = self.client_socket.recv(1024).decode()#接收到来自服务器发送来的消息，
        # recv() 方法是用来接收从连接的另一端发送来的数据，括号中的参数是要接收的数据的最大字节数，这里设置为 1024 字节。
        print(welcome_message)
        self.start_receiving()#启动客户端接收来自服务器消息的循环或线程等处理方式，以便在客户端接收到来自服务器的任何新消息时进行处理。

    def menu(self):
        print('\n聊天室菜单：')
        print('1 私密聊天')
        print('2 创建一个新的聊天群组')
        print('3 加入一个新的聊天群组')
        print('4 离开指定的聊天群组')
        print('5 向指定的聊天群组发送消息')
        print('6 退出聊天室')

    def start_receiving(self):
        receive_thread = threading.Thread(target=self.receive_message)# 创建接收消息的线程
        receive_thread.daemon = True# 将线程设置为守护线程
        receive_thread.start()# 启动线程
        while True:
            global message# 全局变量，用于存储用户输入的消息
            self.message_event.wait(0.1)  # 等待新消息的到来，最长等待0.1秒
            self.message_event.clear()  # 清除事件状态
            self.menu()# 显示菜单选项
            option = input('请选择:\n')# 提示用户选择菜单选项
            if option == "6":
                message = "quit"    # 用户选择退出，设置消息为 "quit"
                self.client_socket.send(message.encode()) # 发送退出消息给服务器
                self.client_socket.close()# 关闭客户端套接字
                break
            elif option == '1':
                # print('请输入接收者用户名以及消息内容')
                username1=input("请输入接收者用户名: ") # 获取用户输入的接收者用户名
                message1=input("请输入给ta的消息内容: ") # 获取用户输入的消息内容
                message='private '+username1+" "+message1 # 构建私密消息格式的消息
                self.client_socket.send(message.encode())# 发送私密消息给服务器
            elif option == '2':
                message = 'create '+input('请输入要创建的聊天群组名: ')# 获取用户输入的新群组名，并构建创建群组的消息格式
                self.client_socket.send(message.encode())# 发送创建群组的消息给服务器
            elif option == '3':
                print("请输入要加入的群组名: ")
                message="join " + input()# 获取用户输入的要加入的群组名，并构建加入群组的消息格式
                self.client_socket.send(message.encode())# 发送加入群组的消息给服务器
            elif option == '4':
                message="leave "+ input("请输入要离开的群组名: ")# 获取用户输入的要离开的群组名，并构建离开群组的消息格式
                self.client_socket.send(message.encode())# 发送离开群组的消息给服务器
            elif option == '5':
                groupname=input("向哪个群组发送消息？ ")# 获取用户输入的要发送消息的群组名
                message2=input("发送的信息为: ")#  获取用户输入的要发送的消息内容
                message="group "+ groupname+" "+message2 # 构建群组消息格式的消息
                self.client_socket.send(message.encode())# 发送群组消息给服务器
            else:
                print("Invalid command.")# 无效的命令，打印错误信息

    def receive_message(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()# 接收服务器发送的消息数据
                print(data) # 打印接收到的消息
                self.message_event.set()
            except ConnectionAbortedError:
                break# 如果连接中止，跳出循环

if __name__ == "__main__":
    client = ChatRoomClient("127.0.0.1", 5000)#创建 ChatRoomClient 类的实例，并传入服务器的主机地址 "127.0.0.1" 和端口号 5000。
    client.connect()#启动客户端并与服务器建立连接。






