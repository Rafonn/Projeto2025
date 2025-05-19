"use client";

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
    const socketRef = useRef(null);
    const containerRef = useRef(null);
    const lastUserMessageRef = useRef(null);
    const [setIsToggleActive] = useState(false);

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
        if (!containerRef.current || !lastUserMessageRef.current) return;

        lastUserMessageRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
        });
    }, [messages]);

    useEffect(() => {
        const userId = getOrCreateUserId();
        fetch("http://localhost:8001/logs/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ toggle: false, userId }),
        })
            .then(res => res.json())
            .then(data => console.log("Toggle reset no servidor:", data))
            .catch(err => console.error("Erro ao resetar toggle no servidor:", err));
    }, []);

    const lastUserIndex = messages
        .map(msg => msg.sender)
        .lastIndexOf('user');

    useEffect(() => {
        const userId = getOrCreateUserId();

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
        console.log("Valor do toggle:", toggle);
        const userId = getOrCreateUserId();
        await fetch("http://localhost:8001/logs/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ toggle, userId }),
        });
        if (typeof window !== "undefined") {
            localStorage.setItem("isToggleActive", JSON.stringify(toggle));
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

    const CODE_DELIM = '```';

    const parseInlineBold = (text) => {
        const parts = text.split(/(\*\*[^*]+\*\*)/g);
        return parts.map((part, i) => {
            const m = part.match(/^\*\*(.+)\*\*$/);
            return m
                ? <strong key={i}>{m[1]}</strong>
                : <React.Fragment key={i}>{part}</React.Fragment>;
        });
    };

    const renderContent = (text) => {
        const parts = text.split(CODE_DELIM);

        return parts.map((part, idx) => {
            if (idx % 2 === 1) {
                const code = part.replace(/^\w+\n/, '');
                return (
                    <pre
                        key={idx}
                        className="overflow-x-auto rounded-md p-2 bg-gray-900"
                    >
                        <code className="font-mono text-gray-200">
                            {code}
                        </code>
                    </pre>
                );
            }

            const lines = part.split(/\r?\n/);

            return (
                <React.Fragment key={idx}>
                    {lines.map((rawLine, i) => {
                        const line = rawLine.trim();
                        if (!line) {
                            return <br key={i} />;
                        }

                        if (line.startsWith('### ')) {
                            const content = line.slice(4).trim();
                            return (
                                <h3
                                    key={i}
                                    className="text-2xl font-bold mt-6 mb-2"
                                >
                                    {parseInlineBold(content)}
                                </h3>
                            );
                        }

                        if (line.startsWith('#### ')) {
                            const content = line.slice(5).trim();
                            return (
                                <h4
                                    key={i}
                                    className="text-xl font-bold mt-4 mb-1"
                                >
                                    {parseInlineBold(content)}
                                </h4>
                            );
                        }

                        if (line.startsWith('*** ')) {
                            const content = line.slice(4).trim();
                            return (
                                <p key={i} className="font-medium">
                                    <strong>{content}</strong>
                                </p>
                            );
                        }

                        if (/^[-*]\s+/.test(line)) {
                            const marker = line.slice(0, line.indexOf(' ') + 1);
                            const content = line.slice(marker.length);
                            return (
                                <p key={i} className="whitespace-pre-wrap font-medium">
                                    {marker}{parseInlineBold(content)}
                                </p>
                            );
                        }

                        return (
                            <p key={i} className="whitespace-pre-wrap font-medium">
                                {parseInlineBold(line)}
                            </p>
                        );
                    })}
                </React.Fragment>
            );
        });
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
                            defaultChecked={false}
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

                <div className="flex flex-col gap-4 flex-1">
                    <Card className="h-[75vh] w-full border border-[#3498db] bg-slate-900 rounded-md shadow-md overflow-hidden animate-border card-with-background">
                        <CardContent
                            ref={containerRef}
                            className="h-full overflow-y-auto p-4 space-y-3"
                        >
                            {messages.map((msg, i) => {
                                const isLastUser = msg.sender === 'user' && i === lastUserIndex;

                                return (
                                    <div
                                        key={i}
                                        ref={isLastUser ? lastUserMessageRef : undefined}
                                        className={`p-3 rounded-md shadow-sm break-words max-w-fit font-bold
                                        ${msg.sender === 'user'
                                                ? 'bg-[#3498db] text-white self-end ml-auto'
                                                : 'bot-reponse-bg text-gray-300 self-start'
                                            }`}
                                    >
                                        {renderContent(msg.text)}
                                    </div>
                                );
                            })}
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