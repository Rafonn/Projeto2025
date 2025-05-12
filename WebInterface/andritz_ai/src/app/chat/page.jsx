"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import "../globals.css";

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

export default function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [isToggleActive, setIsToggleActive] = useState(false);
    const socketRef = useRef(null);
    const messagesEndRef = useRef(null);

    function generateUUID() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
            const r = (Math.random() * 16) | 0,
                v = c === "x" ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    }

    // Gera ou recupera userId do cookie
    function getOrCreateUserId() {
        let userId = getCookie("user_id");
        if (!userId) {
            userId = generateUUID();
            document.cookie = `user_id=${userId}; path=/; max-age=${60 * 60 * 24 * 365}`;
        }
        return userId;
    }

    // Scroll automático para a última mensagem
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Ao montar: busca toggle e abre WS
    useEffect(() => {
        const userId = getOrCreateUserId();

        // 1) busca estado atual do toggle
        fetch(`http://localhost:8001/logs/toggle/${userId}`)
            .then((res) => {
                if (!res.ok) throw new Error("Nenhum toggle encontrado");
                return res.json();
            })
            .then(({ button }) => {
                setIsToggleActive(Boolean(button));
            })
            .catch((err) => {
                console.warn("Toggle não inicializado:", err);
            });

        // 2) abre WebSocket para receber respostas do bot
        const ws = new WebSocket(`ws://localhost:8001?userId=${encodeURIComponent(userId)}`);
        socketRef.current = ws;

        ws.onopen = () => {
            console.log("WebSocket conectado ao servidor de logs do bot");
        };

        ws.onmessage = (event) => {
            const { botMessage, botTimeStamp, error } = JSON.parse(event.data);
            if (error) {
                console.error("Erro recebido no WS:", error);
            } else {
                setMessages((prev) => [
                    ...prev,
                    { text: botMessage, sender: "bot", time: botTimeStamp },
                ]);
            }
            setLoading(false);
        };

        ws.onclose = () => {
            console.log("WebSocket desconectado");
        };

        ws.onerror = (err) => {
            console.error("WebSocket erro:", err);
            ws.close();
        };

        // cleanup
        return () => {
            ws.close();
        };
    }, []);

    // Envia toggle para a API
    const handleToggleChange = async (e) => {
        const toggle = e.target.checked;
        setIsToggleActive(toggle);
        const userId = getOrCreateUserId();

        try {
            const res = await fetch("http://localhost:8001/logs/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ toggle, userId }),
            });
            const data = await res.json();
            console.log("Toggle salvo:", data);
        } catch (err) {
            console.error("Erro ao salvar toggle:", err);
        }
    };

    // Função de envio de mensagem
    const sendMessage = async () => {
        if (!input.trim()) return;
        const userId = getOrCreateUserId();
        setLoading(true);

        // 1) mostra no chat a bolha do usuário
        const textToSend = input;
        setMessages((prev) => [
            ...prev,
            { text: textToSend, sender: "user", time: new Date().toISOString() },
        ]);
        setInput("");

        // 2) envia log do usuário via REST
        try {
            await fetch("http://localhost:8001/logs/user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ log: textToSend, userId }),
            });
            // NÃO chamamos mais /logs/bot: a resposta do bot virá pelo WebSocket
        } catch (err) {
            console.error("Erro ao enviar log do usuário:", err);
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="relative min-h-screen min-w-screen flex items-center justify-center p-6">
            <div className="absolute inset-0 -z-10"></div>

            <div className="w-full max-w-7xl border border-[#3498db] p-6 rounded-lg shadow-lg">
                {/* Toggle */}
                <div className="flex justify-between text-center relative mb-6">
                    <label className="neo-toggle-container left-0">
                        <input
                            type="checkbox"
                            className="neo-toggle-input"
                            checked={isToggleActive ?? false}
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
                        <span className="neo-status">
                            <span className="neo-status-indicator">
                                <span className="neo-status-text">Andritz Mode</span>
                                <span className="neo-status-dot"></span>
                            </span>
                        </span>
                    </label>
                </div>

                {/* Fundo animado */}
                <div className="flex justify-center items-center relative w-full circle-container">
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                </div>

                {/* Janela de chat */}
                <Card className="h-[70vh] flex flex-col border border-[#3498db] bg-slate-900 rounded-md shadow-md relative overflow-hidden animate-border card-with-background">
                    <CardContent
                        ref={messagesEndRef}
                        className="flex-1 overflow-y-auto p-4 space-y-3"
                    >
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`p-3 rounded-md text-xs font-bold shadow-sm transition-all duration-500 break-words whitespace-pre-wrap max-w-fit ${msg.sender === "user"
                                    ? "bg-[#3498db] text-white self-end ml-auto hover:scale-102 custom-font"
                                    : "bot-reponse-bg text-gray-300 self-start hover:scale-102 custom-font"
                                    }`}
                            >
                                {msg.text}
                            </div>
                        ))}
                    </CardContent>
                </Card>

                {/* Input e botão */}
                <div className="flex items-center gap-2 mt-4 w-full">
                    <Input
                        as="textarea"
                        rows={4}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Digite sua mensagem..."
                        className="bg-slate-900 border border-[#3498db] text-white text-sm font-bold rounded-md px-4 py-2 h-10 shadow-md transition-all duration-500 focus:outline-none focus:border-[#0066ff] focus:text-[#3498db] placeholder:text-gray-400"
                    />
                    <button
                        onClick={sendMessage}
                        className="group relative bg-slate-900 h-10 w-36 border border-[#3498db] text-white text-xs font-bold rounded-md overflow-hidden transform transition-all duration-500 hover:scale-105 hover:border-[#0066ff] hover:text-[#3498db] p-1 flex items-center justify-center disabled:opacity-50"
                    >
                        {loading ? "Carregando..." : "Enviar"}
                    </button>
                </div>
            </div>
        </div>
    );
}