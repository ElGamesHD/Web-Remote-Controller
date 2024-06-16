package com.gmail.euquemada;

import org.java_websocket.server.WebSocketServer;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

public class ScreenServer extends WebSocketServer {

    private Set<WebSocket> clients = Collections.synchronizedSet(new HashSet<>());

    public ScreenServer(InetSocketAddress address) {
        super(address);
    }

    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        System.out.println("New connection from " + conn.getRemoteSocketAddress());
        clients.add(conn);
    }

    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        System.out.println("Closed connection to " + conn.getRemoteSocketAddress());
        clients.remove(conn);
    }

    @Override
    public void onMessage(WebSocket conn, String message) {
        System.out.println("Received message from " + conn.getRemoteSocketAddress() + ": " + message);
        // Handle received message if needed
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        ex.printStackTrace();
    }

    @Override
    public void onStart() {
        System.out.println("Server started!");
        startScreenCapture();
    }

    private void startScreenCapture() {
        new Thread(() -> {
            try {
                Robot robot = new Robot();
                while (true) {
                    double startTime = System.currentTimeMillis();

                    BufferedImage screenshot = robot.createScreenCapture(new Rectangle(Toolkit.getDefaultToolkit().getScreenSize()));
                    double captureTime = System.currentTimeMillis() - startTime;

                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    ImageIO.write(screenshot, "jpg", baos);
                    double jpgTime = System.currentTimeMillis() - (captureTime + startTime);

                    byte[] imageBytes = baos.toByteArray();
                    ByteBuffer byteBuffer = ByteBuffer.wrap(imageBytes);
                    synchronized (clients) {
                        for (WebSocket client : clients) {
                            client.send(byteBuffer);
                        }
                    }

                    double sendTime = System.currentTimeMillis() - (jpgTime + captureTime + startTime);
                    System.out.println(
                            "FPS de envío: " + 1000/((System.currentTimeMillis() - startTime)) +
                                    ", CAPTURE: " + captureTime +
                                    ", JPG: " + jpgTime +
                                    ", SEND " + sendTime
                    );
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }
}
