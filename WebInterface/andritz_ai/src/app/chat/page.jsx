"use client"

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import "../globals.css";

export default function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    // Referência para a área de mensagens
    const messagesEndRef = useRef(null);

    // Rola automaticamente para o final
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMessage = { text: input, sender: "user" };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        setTimeout(() => {
            const botMessage = {
                text: "Essa é uma resposta automática que pode ser longa e precisa quebrar a linha corretamente para manter a formatação visual adequada.",
                sender: "bot"
            };
            setMessages((prev) => [...prev, botMessage]);
        }, 1000);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else if (e.key === "Enter" && e.shiftKey) {
            // Adiciona uma nova linha ao pressionar Shift + Enter
            setInput(input + "\n");
        }
    };

    return (
        <div className="relative min-h-screen min-w-screen flex items-center justify-center p-6">
            <div className="absolute inset-0 -z-10"></div>

            <div className="w-full max-w-5xl border border-[#3498db] p-6 rounded-lg shadow-lg">
                <h1 className="text-4xl font-extrabold text-center text-[#3498db] mb-6 animate-pulse">Chatbot</h1>
                <Card className="h-[70vh] flex flex-col border border-[#3498db] bg-slate-900 rounded-md shadow-md relative overflow-hidden animate-border card-with-background">
                    <CardContent ref={messagesEndRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`p-3 rounded-md text-xs font-bold shadow-sm transition-all duration-500 break-words whitespace-pre-wrap max-w-fit ${msg.sender === "user"
                                        ? "bg-[#3498db] text-white self-end ml-auto hover:scale-103"
                                        : "bg-gray-700 text-gray-300 self-start hover:scale-103"
                                    }`}
                            >
                                {msg.text}
                            </div>
                        ))}
                    </CardContent>
                </Card>
                <div className="flex items-center gap-2 mt-4 w-full">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Digite sua mensagem..."
                        className="bg-slate-900 border border-[#3498db] text-white text-xs font-bold rounded-md px-4 py-2 h-10 shadow-md transition-all duration-500 focus:outline-none focus:border-[#0066ff] focus:text-[#3498db] placeholder:text-gray-400"
                        rows={4}
                        as="textarea"
                    />
                    <button
                        onClick={sendMessage}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") sendMessage();
                        }}
                        className="group relative bg-slate-900 h-10 w-36 border border-[#3498db] text-white text-xs font-bold rounded-md overflow-hidden transform transition-all duration-500 hover:scale-105 hover:border-[#0066ff] hover:text-[#3498db] p-1 flex items-center justify-center
                        before:absolute before:w-4 before:h-4 before:content[''] before:right-2 before:top-2 before:z-10 before:bg-indigo-500 before:rounded-full before:blur-sm before:transition-all before:duration-500 
                        after:absolute after:z-10 after:w-8 after:h-8 after:content[''] after:bg-teal-400 after:right-3 after:top-2 after:rounded-full after:blur-sm after:transition-all after:duration-500 
                        hover:before:right-6 hover:before:-bottom-2 hover:before:blur 
                        hover:after:-right-2 hover:after:scale-110">
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
}
