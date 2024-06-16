package com.gmail.euquemada;

import java.net.InetSocketAddress;

public class Main {

    public static void main(String[] args) {
        int port = 8765; // 8765 is the port number
        ScreenServer server = new ScreenServer(new InetSocketAddress(port));
        server.start();
        System.out.println("WebSocket server started on port: " + port);
    }
}