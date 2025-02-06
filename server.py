import socket
import threading

class ChatRoomServer:

    def __init__(self, host, port):
        self.host = host# 服务器主机地址
        self.port = port# 服务器监听端口
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# 创建一个 TCP 套接字
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# 设置套接字选项
        self.users = {}  # 存储所有连接到服务器的用户
        self.groups = {}  # 存储所有聊天群组的信息

    def run(self):
        self.server_socket.bind((self.host, self.port))# 绑定主机和端口号
        self.server_socket.listen(5) # 开始监听，最多允许 5 个连接
        print(f"ChatRoom server started on {self.host}:{self.port}")# 输出服务器启动信息

        while True:
            conn, addr = self.server_socket.accept()# 输出服务器启动信息
            user_thread = threading.Thread(target=self.handle_user, args=(conn, addr))# 创建新线程处理连接
            user_thread.daemon = True   # 创建新线程处理连接
            user_thread.start() # 启动线程

    def handle_user(self, conn, addr):
        username = conn.recv(1024).decode() # 接收客户端发来的用户名
        if username not in self.users: # 判断用户名是否已经存在
            self.users[username] = conn # 如果用户名不存在，将其加入到用户列表
            conn.send(b"Welcome to the ChatRoom!")# 发送欢迎消息
            print(f"New user connected: {username}")# 输出新用户连接信息
            print(f"Now have {len(self.users)} users in ChatRoom")#显示现在有多少用户在线
        else:
            conn.send(b"Username already taken. Please choose another one.")# 如果用户名已存在，发送错误消息
            conn.close() # 关闭连接
            return

        while True:# 开始循环处理用户消息
            try:
                data = conn.recv(1024).decode()# 开始循环处理用户消息
                if data == "quit":# 如果客户端发送的消息为 "quit"，则关闭连接，从 users 字典中删除该用户，并打印用户断开连接的信息
                    print(f"User disconnected: {username}")
                    conn.close()
                    del self.users[username]
                    break
                    # 如果客户端发送的消息以 "private " 开头，则将消息发送给指定的用户
                elif data.startswith("private "):
                    # 获取接收私聊消息的用户名和消息内容
                    recipient = data.split()[1]
                    message = " ".join(data.split()[2:])
                    # 如果接收私聊消息的用户在 users 字典中，则将消息发送给该用户
                    if recipient in self.users:
                        print(f"{username} send private message: '{message}' to {recipient}")
                        self.users[recipient].send(f"You have received private message from {username}: {message}".encode())
                    # 否则，向该用户发送一条错误消息
                    else:
                        conn.send(f"{recipient} is not online or not existed.".encode())
                # 如果客户端发送的消息以 "create " 开头，则创建一个新的聊天群组
                elif data.startswith("create "):
                    group_name = data.split()[1]
                    # 如果群组名称不存在于 groups 字典中，则创建新群组，并将该用户加入该群组
                    if group_name not in self.groups:
                        self.groups[group_name] = []
                        self.groups[group_name].append(username)
                        print(f"{username} created {group_name}.")
                        conn.send(f"You created {group_name} successfully.".encode())
                    # 否则，向该用户发送一条错误消息
                    else:
                        conn.send(f"{group_name} already exists.".encode())
                # 如果客户端发送的消息以 "join " 开头，则将该用户加入指定的聊天群组
                elif data.startswith("join "):
                    # 获取要加入的群组的名称
                    group_name = data.split()[1]
                    # 如果群组名称存在于 groups 字典中，则将该用户加入该群组
                    if group_name in self.groups:
                        if username in self.groups[group_name]:#如果用户已经加入的群组，则提示不要重复加入
                            conn.send(f"You have joined {group_name},please do not join repeatedly!".encode())
                        else:
                            self.groups[group_name].append(username)
                            print(f"{username} join {group_name}.")
                            conn.send(f"You joined {group_name} successfully.".encode())
                    # 否则，向该用户发送一条错误消息
                    else:
                        conn.send(f"{group_name} does not exist.".encode())
                    # 如果客户端发送的消息以 "leave " 开头，则让该用户离开指定的聊天群组
                elif data.startswith("leave "):
                    # 获取要离开的群组的名称
                    group_name = data.split()[1]
                    if group_name in self.groups:# 如果群组名称存在于 groups 字典中，则将该用户从该群组中移除
                        if username in self.groups[group_name]:
                            self.groups[group_name].remove(username)
                            print(f"{username} leave the group {group_name}.")
                            conn.send(f"You left {group_name}.".encode())
                        else:
                            conn.send(f"You have not join {group_name}.".encode())
                    else:# 否则，向该用户发送一条错误消息
                        conn.send(f"{group_name} does not exist .".encode())
                # 如果客户端发送的消息以 "group " 开头，则向指定的聊天群组发送消息
                elif data.startswith("group "):
                    # 获取群组名称和消息内容
                    group_name = data.split()[1]
                    message = " ".join(data.split()[2:])
                    # 如果群组名称存在于 groups 字典中，则向该群组中的所有成员（除发送消息的用户以外）发送群组消息
                    if group_name in self.groups:
                        if username in self.groups[group_name]:
                            print(f"{username} send message:'{message}' in {group_name}")
                            for member in self.groups[group_name]:
                                if member != username:
                                    self.users[member].send(f"group message from {username}: {message}".encode())
                        else:
                            conn.send(f"You have not joined {group_name}.".encode())
                    else: # 否则，向该用户发送一条错误消息
                        conn.send(f"{group_name} does not exist.".encode())
                else:# 如果客户端发送的消息不属于以上任何一种类型，则向该用户发送一条无效命令的消息
                    conn.send("Invalid command.".encode())
            except ConnectionResetError: # 捕获 ConnectionResetError 异常，表示用户异常断开连接，关闭连接，并将其从 users 字典中移除
                conn.close()
                del self.users[username]
                print(f"User disconnected: {username}")
                break

if __name__ == "__main__":
    server = ChatRoomServer("127.0.0.1", 5000)#定义主机地址和服务器端口
    server.run()#开始运行程序



