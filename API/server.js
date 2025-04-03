const express = require("express");
const fs = require("fs");
const cors = require("cors");
const http = require("http");
const WebSocket = require("ws");

const app = express();
const port = 8000;

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.json());
app.use(cors());

let botClients = new Set();

wss.on("connection", (ws) => {
    console.log("Cliente conectado ao WebSocket dos logs do bot");
    botClients.add(ws);

    ws.on("close", () => {
        console.log("Cliente desconectado");
        botClients.delete(ws);
    });
});

function notifyBotClients(log) {
    const timestamp = new Date().toISOString();
    const message = JSON.stringify({ timestamp, log });

    botClients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

app.post("/logs/bot", (req, res) => {
    try {
        const { log } = req.body;
        if (!log) {
            return res.status(400).json({ error: "Campo 'log' é obrigatório." });
        }

        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${log}\n`;

        fs.appendFileSync("logs_bot.txt", logMessage, "utf-8");

        notifyBotClients(log);

        res.json({ message: "Log do bot salvo com sucesso!" });
    } catch (error) {
        res.status(500).json({ error: "Erro ao salvar o log do bot." });
    }
});

app.post("/logs/user", (req, res) => {
    try {
        const { log } = req.body;
        if (!log) {
            return res.status(400).json({ error: "Campo 'log' é obrigatório." });
        }

        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${log}\n`;

        fs.appendFileSync("logs_user.txt", logMessage, "utf-8");

        res.json({ message: "Log do usuário salvo com sucesso!" });
    } catch (error) {
        res.status(500).json({ error: "Erro ao salvar o log do usuário." });
    }
});

app.post("/logs/toggle", (req, res) => {
    try {
        const { toggleState } = req.body;

        if (toggleState === undefined) {
            return res.status(400).json({ error: "Campo 'toggleState' é obrigatório." });
        }

        const logMessage = `${toggleState ? "ATIVADO" : "DESATIVADO"}\n`;

        fs.writeFileSync("logs_toggle.txt", logMessage, "utf-8");

        res.json({ message: "Log do toggle atualizado com sucesso!" });
    } catch (error) {
        res.status(500).json({ error: "Erro ao atualizar o log do toggle." });
    }
});

app.get("/logs/bot", (req, res) => {
    try {
        if (!fs.existsSync("logs_bot.txt")) {
            return res.json({ logs: [] });
        }

        const logs = fs.readFileSync("logs_bot.txt", "utf-8").split("\n").filter(line => line);
        res.json({ logs });
    } catch (error) {
        res.status(500).json({ error: "Erro ao ler os logs do bot." });
    }
});

app.get("/logs/user", (req, res) => {
    try {
        if (!fs.existsSync("logs_user.txt")) {
            return res.json({ logs: [] });
        }

        const logs = fs.readFileSync("logs_user.txt", "utf-8").split("\n").filter(line => line);
        res.json({ logs });
    } catch (error) {
        res.status(500).json({ error: "Erro ao ler os logs do usuário." });
    }
});

app.get("/logs/toggle", (req, res) => {
    try {
        if (!fs.existsSync("logs_user.txt")) {
            return res.json({ logs: [] });
        }

        const logs = fs.readFileSync("logs_toggle.txt", "utf-8").split("\n").filter(line => line);
        res.json({ logs });
    } catch (error) {
        res.status(500).json({ error: "Erro ao ler os logs do toggle." });
    }
});

app.get("/", (req, res) => {
    res.json({ message: "API Online!" });
});

server.listen(port, () => {
    console.log(`🚀 API rodando em http://localhost:${port}`);
});
