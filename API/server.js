const express = require("express");
const fs = require("fs");
const cors = require("cors");
const app = express();
const port = 8000;

app.use(express.json());
app.use(cors());

app.post("/logs/bot", (req, res) => {
    try {
        const { log } = req.body;
        if (!log) {
            return res.status(400).json({ error: "Campo 'log' é obrigatório." });
        }

        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${log}\n`;

        fs.appendFileSync("logs_bot.txt", logMessage, "utf-8");

        res.json({ message: "Log recebido com sucesso!" });
    } catch (error) {
        res.status(500).json({ error: "Erro ao salvar o log." });
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

        res.json({ message: "Log recebido com sucesso!" });
    } catch (error) {
        res.status(500).json({ error: "Erro ao salvar o log." });
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
        res.status(500).json({ error: "Erro ao ler os logs." });
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
        res.status(500).json({ error: "Erro ao ler os logs." });
    }
});

app.get("/", (req, res) => {
    res.json({ message: "API Online!" });
});

app.listen(port, () => {
    console.log(`🚀 API rodando em http://localhost:${port}`);
});
