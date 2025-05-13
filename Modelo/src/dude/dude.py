import requests
from datetime import datetime, timezone
from urllib.parse import urlencode

class DudeConnectionBase:
    def __init__(self):
        self.url = "https://assetessentials.dudesolutions.com/XeriumTechnologies/api"
        self.username = "PSiqueira"
        self.password = "@#Andritz001"
        self.culture = "pt-BR"
        self.token_expiry = 120

    def get_current_date(self) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%dT")

    def date_formatted(self) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%dT%H:%M:%S")

    def _get_token(self, endpoint: str) -> str:
        login_data = {
            'loginName': self.username,
            'Password': self.password,
            'cultureCode': self.culture,
            'Expires': self.token_expiry
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post(
            f"{self.url}/{endpoint}",
            data=urlencode(login_data),
            headers=headers
        )
        resp.raise_for_status()

        return resp.text

    def _search_info(self, token: str, city: str, start_date: str, end_date: str):
        search_url = f"{self.url}/workorders/searches"
        all_orders = []
        page = 1
        total_pages = 1

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Basic {token}"
        }

        while page <= total_pages:
            payload = {
                "Options": {
                    "PopulateCustomFields": True,
                    "PopulateMedium": True,
                    "PopulateSource": True,
                    "PopulateParentPaths": True,
                    "ParentPathDelimiter": "--",
                    "TotalItems": 0,
                    "TotalObjectCountOption": "TotalObjectCount"
                },
                "Page": {
                    "PageNumber": page,
                    "PageSize": 200
                },
                "City": {
                    "Filters": [{
                        "Value": city,
                        "MatchType": "Equals"
                    }]
                },
                "DateLastModified": {
                    "StartValue": start_date,
                    "EndValue": end_date
                }
            }

            resp = requests.post(search_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            all_orders.extend(data.get('Items', []))
            total_pages = data.get('TotalPages', 1)
            page += 1

        return all_orders

    def _filter(self, orders: list, status_filter: str) -> list:
        filtered = [
            {
                "IdOrdem":        o.get("WorkOrderNo", "Sem apontamento."),
                "CriadaPor":      o.get("CreatedBy", "Sem apontamento."),
                "NomeCriador":    o.get("OriginUserFullName", "Sem apontamento."),
                "Cidade":         o.get("City", "Sem apontamento."),
                "Motivo":         o.get("Name", "Sem apontamento."),
                "Problema":       o.get("ProblemName", "Sem apontamento."),
                "Categoria":      o.get("WorkCategoryName", "Sem apontamento."),
                "Setor":          o.get("SourceLocationName", "Sem apontamento."),
                "Maquina":        o.get("SourceAssetName", "Sem apontamento."),
                "Status":         o.get("WOStatusName", "Sem apontamento."),
                "CriadoEm":       o.get("DateOriginated", "Sem apontamento."),
                "TrabalhoReq":    o.get("WorkRequested", "Sem apontamento."),
                "UltimaModif":    o.get("LastModifiedOn", "Sem apontamento."),
            }
            for o in orders
            if status_filter in (o.get("WOStatusName") or "") and o.get("SourceAssetName")
        ]

        if not filtered:
            return [{
                "IdOrdem": "Sem informacao.",
                "CriadaPor": "Sem informacao.",
                "NomeCriador": "Sem informacao.",
                "Cidade": "Sem informacao.",
                "Motivo": "Sem informacao.",
                "Problema": "Sem informacao.",
                "Categoria": "Sem informacao.",
                "Setor": "Sem informacao.",
                "Maquina": "Sem informacao.",
                "Status": "Sem informacao.",
                "CriadoEm": "Sem informacao.",
                "TrabalhoReq": "Sem informacao.",
                "UltimaModif": "Sem informacao.",
            }]

        return filtered

    def fetch_new_requests(self, city: str = "Petropolis", status_filter: str = "Completed"):
        token = self._get_token("login")
        start_date = self.get_current_date() + "06:00:00"
        end_date = self.date_formatted()

        orders = self._search_info(token, city, start_date, end_date)
        return self._filter(orders, status_filter)


if __name__ == "__main__":
    client = DudeConnectionBase()
    resultados = client.fetch_new_requests()
    for ordem in resultados:
        s = (
            f"–– Ordem de Serviço ––\n"
            f"ID:           {ordem['IdOrdem']}\n"
            f"Criada por:   {ordem['CriadaPor']} ({ordem['NomeCriador']})\n"
            f"Cidade:       {ordem['Cidade']}\n"
            f"Motivo:       {ordem['Motivo']}\n"
            f"Problema:     {ordem.get('Problema') or '—'}\n"
            f"Categoria:    {ordem['Categoria']}\n"
            f"Setor:        {ordem['Setor']}\n"
            f"Máquina:      {ordem['Maquina']}\n"
            f"Status:       {ordem['Status']}\n"
            f"Criado em:    {ordem['CriadoEm']}\n"
            f"Requisição:   {ordem['TrabalhoReq'].strip()}\n"
            f"Última modif: {ordem['UltimaModif']}\n"
        )
        print(s)
