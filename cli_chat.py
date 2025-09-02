# -*- coding: utf-8 -*-
import socket
import threading
import sys
import argparse

# P2Pチャットの基本設定
HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 1024

# 停止
stop_event = threading.Event()

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
        while not stop_event.is_set():
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print("接続が切断されました。")
                stop_event.set()
                break
            text = data.decode('utf-8').strip()
            if text in ('/exit'):
                print("\n>> 相手がチャットを終了しました。")
                stop_event.set()
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                break
            print(f"\n>> {text}")
    except socket.error as e:
        print(f"受信エラー: {e}")
    finally:
        try:
            conn.close()
        except OSError:
            pass

def send_messages(conn):
    """
    ユーザーの入力を受け付け、接続に送信します。
    """
    try:
        while not stop_event.is_set():
            message = input(">> ").strip()
            if not message:
                continue
            if message in ('/exit'):
                try:
                    conn.sendall(message.encode('utf-8'))
                except socket.error:
                    # 相手がすでに終了している可能性を無視して終了
                    pass
                stop_event.set()
                break
            try:
                conn.sendall(message.encode('utf-8'))
            except socket.error as e:
                print(f"送信エラー: {e}")
                stop_event.set()
                break
            if message.lower() == 'exit':
                break
            conn.sendall(message.encode('utf-8'))
    except (socket.error, KeyboardInterrupt) as e:
        print(f"送信エラーまたはユーザーによる中断: {e}")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass
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
