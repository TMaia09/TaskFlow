# 📋 TaskFlow — RESTful API & Task Management Service

Serviço backend desenvolvido em Python com arquitetura RESTful para gestão e acompanhamento de tarefas/demandas de software, com suporte a persistência em banco de dados relacional (SQLite3).

## 🛠️ Tecnologias & Conceitos Aplicados
- **Backend & Rotas HTTP:** Flask (Endpoints GET, POST, PUT, DELETE).
- **Banco de Dados Relacional:** SQLite3 com queries estruturadas, manipulação de dados e ordenação de registos.
- **Arquitetura API REST:** Retorno no padrão JSON, manipulação de Status Codes HTTP (200, 201, 400, 404) e validação de payloads.
- **Desenvolvimento Multiplataforma:** Compatível com execução nativa em Linux, Windows e Android (Termux).

## 📌 Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/tasks` | Lista todas as tarefas cadastradas (com filtro opcional por `status`). |
| `POST` | `/api/tasks` | Cadastra uma nova tarefa no banco de dados. |
| `PUT` | `/api/tasks/<id>/status` | Atualiza a etapa/status de uma tarefa existente. |
| `DELETE` | `/api/tasks/<id>` | Remove uma tarefa da base de dados. |

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/TMaia09/TaskFlow.git](https://github.com/TMaia09/TaskFlow.git)
   cd TaskFlow
