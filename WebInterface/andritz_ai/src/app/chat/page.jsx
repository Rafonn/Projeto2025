"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import "../globals.css";

export default function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const socketRef = useRef(null);
    const messagesEndRef = useRef(null);
    const [isToggleActive, setIsToggleActive] = useState(false);

    const handleToggleChange = async (event) => {
        const newState = event.target.checked;
        setIsToggleActive(newState);

        try {
            const response = await fetch("http://localhost:8000/logs/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ toggleState: newState }),
            });

            const data = await response.json();
            console.log("Resposta da API:", data);
        } catch (error) {
            console.error("Erro ao enviar toggle:", error);
        }
    };

    useEffect(() => {
        socketRef.current = new WebSocket("ws://localhost:8000");

        socketRef.current.onopen = () => {
            console.log("Conectado ao WebSocket do bot");
        };

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const botMessage = { text: data.log, sender: "bot" };

            const match = botMessage.text.match(/BOT:\s(.+)/);
            const resposta = {
                text: match ? match[1] : botMessage.text,
                sender: "bot"
            };

            setMessages((prev) => [...prev, resposta]);
        };

        return () => {
            socketRef.current.close();
        };
    }, []);

    const sendMessage = async () => {
        if (!input.trim()) return;

        try {
            const response = await fetch("http://localhost:8000/logs/user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ log: input }),
            });

            const data = await response.json();
            if (response.ok) console.log("Log enviado:", data.message);
            else console.error("Erro ao enviar log:", data.error);
        } catch (error) {
            console.error("Erro na requisição:", error);
        }

        setMessages((prev) => [...prev, { text: input, sender: "user" }]);
        setInput("");
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else if (e.key === "Enter" && e.shiftKey) {
            setInput(input + "\n");
        }
    };

    return (
        <div className="relative min-h-screen min-w-screen flex items-center justify-center p-6">
            <div className="absolute inset-0 -z-10"></div>

            <div className="w-full max-w-7xl border border-[#3498db] p-6 rounded-lg shadow-lg">
                <div className="flex justify-between text-center relative mb-6">
                    <div>
                        <label className="neo-toggle-container left-0">
                            <input 
                                type="checkbox" 
                                className="neo-toggle-input" 
                                checked={isToggleActive} 
                                onChange={handleToggleChange} 
                            />
                            <span className="neo-toggle">
                                <span className="neo-track">
                                    <span className="neo-background-layer"></span>
                                    <span className="neo-grid-layer"></span>
                                    <span className="neo-track-highlight"></span>
                                </span>
                                <span className="neo-thumb">
                                    <span className="neo-thumb-ring"></span>
                                    <span className="neo-thumb-core">
                                        <span className="neo-thumb-icon">
                                            <span className="neo-thumb-wave"></span>
                                        </span>
                                    </span>
                                    <span className="neo-thumb-pulse"></span>
                                </span>
                            </span>
                        </label>
                    </div>
                </div>

                {/* Círculos Animados */}
                <div className="flex justify-center items-center relative w-full circle-container">
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                </div>

                {/* Chat */}
                <Card className="h-[70vh] flex flex-col border border-[#3498db] bg-slate-900 rounded-md shadow-md relative overflow-hidden animate-border card-with-background">
                    <CardContent ref={messagesEndRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`p-3 rounded-md text-xs font-bold shadow-sm transition-all duration-500 break-words whitespace-pre-wrap max-w-fit ${
                                    msg.sender === "user"
                                        ? "bg-[#3498db] text-white self-end ml-auto hover:scale-102 custom-font"
                                        : "bot-reponse-bg text-gray-300 self-start hover:scale-102 custom-font"
                                }`}
                            >
                                {msg.text}
                            </div>
                        ))}
                    </CardContent>
                </Card>

                {/* Input e Botão de Envio */}
                <div className="flex items-center gap-2 mt-4 w-full">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Digite sua mensagem..."
                        className="bg-slate-900 border border-[#3498db] text-white text-sm font-bold rounded-md px-4 py-2 h-10 shadow-md transition-all duration-500 focus:outline-none focus:border-[#0066ff] focus:text-[#3498db] placeholder:text-gray-400"
                        rows={4}
                        as="textarea"
                    />
                    <button
                        onClick={sendMessage}
                        className="group relative bg-slate-900 h-10 w-36 border border-[#3498db] text-white text-xs font-bold rounded-md overflow-hidden transform transition-all duration-500 hover:scale-105 hover:border-[#0066ff] hover:text-[#3498db] p-1 flex items-center justify-center">
                        {loading ? 'Carregando...' : 'Enviar'}
                    </button>
                </div>
            </div>
        </div>
    );
}
