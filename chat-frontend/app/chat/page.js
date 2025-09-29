"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

const conversations = [
    { id: 2, name: "John Doe" },
    { id: 3, name: "Jane Smith" },
    { id: 4, name: "Alex Johnson" },
];

export default function ChatPage() {

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [receiverId, setReceiverId] = useState(2);
    const ws = useRef(null);
    const retryCount = useRef(0);
    const router = useRouter();

    const connectWebSocket = () => {
        const token = localStorage.getItem("token");
        const userId = localStorage.getItem("user_id");

        if (!token || !userId) {
            router.push("/login");
            return;
        }

        ws.current = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

        ws.current.onopen = () => {
            console.log("✅ WebSocket connected");
            retryCount.current = 0;
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.history) {
                setMessages(data.history);
            } else {
                setMessages((prev) => [...prev, data]);
            }
        };

        ws.current.onclose = () => {
            console.log("⚠️ WebSocket disconnected");
            retryConnection();
        };

        ws.current.onerror = (err) => {
            console.error("❌ WebSocket error:", err);
            ws.current.close();
        };
    };

    const retryConnection = () => {
        const delay = Math.min(10000, 1000 * 2 ** retryCount.current);
        retryCount.current += 1;
        console.log(`🔄 Reconnecting in ${delay / 1000}s...`);

        setTimeout(() => {
            connectWebSocket();
        }, delay);
    };

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (ws.current) ws.current.close();
        };
    }, []);

    const sendMessage = () => {
        const userId = localStorage.getItem("user_id");
        if (!input || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
            alert("Connection lost. Retrying...");
            return;
        }

        const message = {
            sender_id: Number(userId),
            receiver_id: Number(receiverId),
            content: input,
        };

        ws.current.send(JSON.stringify(message));
        setInput("");
    };

    return (
        <div className="flex h-screen bg-gray-100">
            <div className="w-1/4 bg-white border-r border-gray-300 flex flex-col">
                <div className="p-4 font-bold text-xl border-b border-gray-300">Chats</div>
                <div className="flex-1 overflow-y-auto">
                    {conversations.map((conv) => (
                        <div
                            key={conv.id}
                            onClick={() => setReceiverId(conv.id)}
                            className={`p-4 cursor-pointer hover:bg-gray-100 ${receiverId === conv.id ? "bg-gray-200" : ""
                                }`}
                        >
                            <div className="font-semibold">{conv.name}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="flex-1 flex flex-col">
                <div className="p-4 font-bold border-b border-gray-300">
                    {conversations.find((c) => c.id === receiverId)?.name}
                </div>

                <div className="flex-1 p-4 overflow-y-auto space-y-2">
                    {messages
                        .filter(
                            (msg) =>
                                msg.sender_id === receiverId || msg.receiver_id === receiverId
                        )
                        .map((msg, index) => (
                            <div
                                key={index}
                                className={`flex ${msg.sender_id == localStorage.getItem("user_id")
                                        ? "justify-end"
                                        : "justify-start"
                                    }`}
                            >
                                <div
                                    className={`p-3 rounded-lg max-w-xs ${msg.sender_id == localStorage.getItem("user_id")
                                            ? "bg-blue-500 text-white"
                                            : "bg-gray-200 text-gray-800"
                                        }`}
                                >
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                </div>

                <div className="p-4 border-t border-gray-300 flex gap-2">
                    <input
                        type="text"
                        placeholder="Type a message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                    />
                    <button
                        onClick={sendMessage}
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
