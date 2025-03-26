import os
import fitz  # PyMuPDF
import re
import json

# Definir os subtítulos desejados
subtitulos = [
    "OBJETIVO", "RESPONSABILIDADE", "GLOSSÁRIO",
    "FORMULÁRIOS", "CONDIÇÕES GERAIS", "CONDIÇÕES ESPECÍFICAS"
]

# Definir os títulos que indicam onde a captura deve parar
subtitulos_exclusao = ["ANEXOS", "CONTROLE DE REVISÕES"]

# Criar pasta de saída para os JSONs
pasta_saida = "pdfs_processados_tec_rev"
os.makedirs(pasta_saida, exist_ok=True)

def extrair_texto_completo(caminho_pdf):
    """ Extrai todo o texto do PDF. """
    texto_completo = []
    with fitz.open(caminho_pdf) as doc:
        for pagina in doc:
            texto_completo.append(pagina.get_text("text"))
    return "\n".join(texto_completo)

def extrair_conteudo_subtitulos(texto, subtitulos, subtitulos_exclusao):
    """ Extrai o conteúdo dos subtítulos, garantindo que cada um termine no próximo. """
    resultado = {sub: "" for sub in subtitulos}  # Garante todas as chaves no JSON

    # Criar um regex que captura os subtítulos e seu conteúdo até o próximo
    padrao = r"(" + "|".join(map(re.escape, subtitulos)) + r")\s*\n"
    partes = re.split(padrao, texto)  # Divide o texto nos subtítulos encontrados

    for i in range(1, len(partes), 2):  # Pula os índices dos títulos e pega o conteúdo
        titulo = partes[i].strip()
        conteudo = partes[i + 1].strip() if i + 1 < len(partes) else ""

        # Parar a captura se encontrar um subtítulo de exclusão
        for sub_exclusao in subtitulos_exclusao:
            if sub_exclusao in conteudo:
                conteudo = conteudo.split(sub_exclusao)[0].strip()

        resultado[titulo] = conteudo

    return resultado

def processar_pasta(pasta):
    """ Processa todos os PDFs da pasta, extrai os conteúdos e salva em JSON. """
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho_pdf = os.path.join(pasta, arquivo)
            texto_pdf = extrair_texto_completo(caminho_pdf)
            conteudo_extraido = extrair_conteudo_subtitulos(texto_pdf, subtitulos, subtitulos_exclusao)

            # Criar nome do JSON
            nome_json = os.path.splitext(arquivo)[0] + ".json"
            caminho_json = os.path.join(pasta_saida, nome_json)

            # Salvar JSON
            with open(caminho_json, "w", encoding="utf-8") as f:
                json.dump(conteudo_extraido, f, ensure_ascii=False, indent=4)

            print(f"✅ JSON salvo: {caminho_json}")

# Definir a pasta dos PDFs
pasta_pdfs = r"C:\Users\Rafael\Desktop\Projeto 2025\Data\BRUTO\24 - Tecelagem e Revisao"
processar_pasta(pasta_pdfs)
