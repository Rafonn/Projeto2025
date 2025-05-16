"use client";

import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import React, { useState, useEffect, useRef } from "react";
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

    function getOrCreateUserId() {
        let userId = getCookie("user_id");
        if (!userId) {
            userId = generateUUID();
            document.cookie = `user_id=${userId}; path=/; max-age=${60 * 60 * 24 * 365}`;
        }
        return userId;
    }

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        const userId = getOrCreateUserId();

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

        return () => {
            ws.close();
        };
    }, []);

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

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userId = getOrCreateUserId();
        setLoading(true);

        const textToSend = input;
        setMessages((prev) => [
            ...prev,
            { text: textToSend, sender: "user", time: new Date().toISOString() },
        ]);
        setInput("");

        try {
            await fetch("http://localhost:8001/logs/user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ log: textToSend, userId }),
            });
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

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const CODE_DELIM = '```';
    const LINE_BREAK_TOKEN = /<br\s*\/?>/gi;

    const renderContent = (text) => {
        const parts = text.split(CODE_DELIM);

        return parts.map((part, idx) => {
            if (idx % 2 === 1) {
                const code = part.replace(/^\w+\n/, '');
                return (
                    <pre
                        key={idx}
                        className="overflow-x-auto rounded-md p-2"
                        style={{ backgroundColor: '#2d2d2d' }}
                    >
                        <code style={{ fontFamily: 'monospace', color: '#e0e0e0' }}>
                            {code}
                        </code>
                    </pre>
                );
            }

            const lines = part.split(LINE_BREAK_TOKEN);
            return (
                <p key={idx} className="whitespace-pre-wrap font-medium">
                    {lines.map((line, i) => (
                        <React.Fragment key={i}>
                            {line}
                            {i < lines.length - 1 && <br />}
                        </React.Fragment>
                    ))}
                </p>
            );
        })
    };

    return (
        <div className="relative min-h-screen min-w-screen flex items-center justify-center p-6 w-full h-full">
            <div className="absolute inset-0 -z-10"></div>

            <div className="flex flex-col h-full w-full border border-[#3498db] p-6 rounded-lg shadow-lg overflow-auto">
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

                <div className="flex justify-center items-center relative w-full circle-container">
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                    <div className="circle"></div>
                </div>

                <div className="flex flex-col gap-4">
                    <Card className="h-[75vh] w-full border border-[#3498db] bg-slate-900 rounded-md shadow-md overflow-hidden animate-border card-with-background">
                        <CardContent
                            ref={messagesEndRef}
                            className="h-full overflow-y-auto p-4 space-y-3"
                        >
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={`p-3 rounded-md shadow-sm break-words max-w-fit font-bold
                                        ${msg.sender === 'user'
                                            ? 'bg-[#3498db] text-white self-end ml-auto'
                                            : 'bot-reponse-bg text-gray-300 self-start'
                                        }`}
                                >
                                    {renderContent(msg.text)}
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <div className="flex flex-wrap items-center gap-2 w-full">
                        <Input
                            as="textarea"
                            rows={4}
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Digite sua mensagem..."
                            className="flex-1 min-w-0 bg-slate-900 border border-[#3498db]
                            text-[#3498db] rounded-md px-4 py-2 h-12
                            focus:outline-none focus:border-[#0066ff] focus:text-white
                            placeholder:text-gray-400"
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading}
                            className="w-32 sm:w-36 bg-slate-900 h-12 border border-[#3498db]
                            rounded-md font-bold disabled:opacity-50 text-white
                            transition-transform duration-300 hover:scale-105 hover:border-[#0066ff] hover:text-[#3498db]"
                        >
                            {loading ? "Carregando..." : "Enviar"}
                        </button>
                    </div>
                </div>
            </div>

        </div>
    );
}