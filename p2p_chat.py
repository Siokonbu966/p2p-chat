# -*- coding: utf-8 -*-
import socket
import threading
import sys
import argparse

# P2Pチャットの基本設定
HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 1024

def start_server(port):
    """
    サーバーとして動作し、接続を待ち受けます。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        print(f"サーバーを開始しました。ポート {port} で接続を待機しています...")

        conn, addr = s.accept()
        print(f"接続しました: {addr}")
        
        # 受信メッセージを別スレッドで処理
        threading.Thread(target=receive_messages, args=(conn,)).start()

        # メッセージ送信ループ
        send_messages(conn)

def start_client(host, port):
    """
    クライアントとして動作し、指定されたホストに接続します。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"{host}:{port} に接続しました。")
            
            # 受信メッセージを別スレッドで処理
            threading.Thread(target=receive_messages, args=(s,)).start()

            # メッセージ送信ループ
            send_messages(s)
        except socket.error as e:
            print(f"接続エラーが発生しました: {e}")
            sys.exit(1)

def receive_messages(conn):
    """
    接続からメッセージを受信し、画面に表示します。
    """
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print("接続が切断されました。")
                break
            print(f"\n>> {data.decode('utf-8')}")
    except socket.error as e:
        print(f"受信エラー: {e}")
    finally:
        conn.close()

def send_messages(conn):
    """
    ユーザーの入力を受け付け、接続に送信します。
    """
    try:
        while True:
            message = input(">> ")
            if message.lower() == 'exit':
                break
            conn.sendall(message.encode('utf-8'))
    except (socket.error, KeyboardInterrupt) as e:
        print(f"送信エラーまたはユーザーによる中断: {e}")
    finally:
        conn.close()
        sys.exit(0)

def main():
    """
    コマンドライン引数を解析し、サーバーまたはクライアントを起動します。
    """
    parser = argparse.ArgumentParser(description='シンプルなP2Pテキストチャットアプリ')
    subparsers = parser.add_subparsers(dest='command', required=True, help='コマンド')
    
    # サーバーモードのパーサー
    server_parser = subparsers.add_parser('listen', help='サーバーモードで接続を待ち受けます')
    server_parser.add_argument('--port', type=int, default=PORT, help=f'待ち受けるポート番号 (デフォルト: {PORT})')
    
    # クライアントモードのパーサー
    client_parser = subparsers.add_parser('connect', help='クライアントモードで指定したホストに接続します')
    client_parser.add_argument('host', type=str, help='接続先のホスト名またはIPアドレス')
    client_parser.add_argument('--port', type=int, default=PORT, help=f'接続先のポート番号 (デフォルト: {PORT})')

    args = parser.parse_args()

    if args.command == 'listen':
        start_server(args.port)
    elif args.command == 'connect':
        start_client(args.host, args.port)

if __name__ == "__main__":
    main()
```
eof
---
