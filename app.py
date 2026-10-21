import sqlite3
from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

app = Flask(__name__)
DB_NAME = "taskflow.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela de Projetos/Tarefas com chave primária e relacionamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'PENDENTE',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- API REST ENDPOINTS (Consumidos por frontends, apps móveis ou Postman) ---

# 1. READ: Listar todas as tarefas (com suporte a filtro por status)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if status:
        cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY id DESC", (status.upper(),))
    else:
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "category": r[3],
            "status": r[4],
            "created_at": r[5]
        })
    return jsonify({"total": len(tasks), "data": tasks}), 200


# 2. CREATE: Cadastrar nova tarefa com suporte a Formulário HTML e JSON
@app.route('/api/tasks', methods=['POST'])
def create_task():
    # Tenta obter dados JSON; se for envio de formulário web, usa request.form
    data = request.get_json(silent=True) or request.form
    
    title = data.get('title')
    category = data.get('category', 'Geral')
    description = data.get('description', '')

    if not title:
        return jsonify({"error": "O campo 'title' é obrigatório!"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, category, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, description, category, created_at))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    # Se a requisição veio do formulário HTML do navegador, redireciona de volta para a página inicial
    if request.form:
        from flask import redirect
        return redirect('/')

    return jsonify({"message": "Tarefa criada com sucesso!", "id": task_id}), 201




# 3. UPDATE: Atualizar status da tarefa (Regra de Negócio: Transição de Status)
@app.route('/api/tasks/<int:task_id>/status', methods=['PUT', 'POST'])
def update_task_status(task_id):
    data = request.get_json() or request.form
    new_status = data.get('status')

    valid_statuses = ['PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDO']
    if new_status not in valid_statuses:
        return jsonify({"error": f"Status inválido. Escolha entre: {valid_statuses}"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_affected == 0:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    return jsonify({"message": f"Status atualizado para {new_status}"}), 200

# 4. DELETE: Remover tarefa do banco
@app.route('/api/tasks/<int:task_id>', methods=['DELETE', 'POST'])
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_affected == 0:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    return jsonify({"message": "Tarefa removida com sucesso!"}), 200

# --- DASHBOARD VISUAL (Interface Web Simples) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>TaskFlow — Gestão de Tarefas</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        h1 { color: #38bdf8; border-bottom: 2px solid #1e293b; padding-bottom: 10px; }
        .card { background: #1e293b; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #38bdf8; }
        .form-group { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input, select, button { padding: 10px; margin: 5px 0; border-radius: 4px; border: none; }
        input, select { width: 95%; background: #0f172a; color: #fff; }
        button { background: #0284c7; color: white; cursor: pointer; font-weight: bold; width: 100%; }
        button:hover { background: #0369a1; }
        .badge { font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 12px; }
        .PENDENTE { background: #eab308; color: #000; }
        .EM_ANDAMENTO { background: #3b82f6; color: #fff; }
        .CONCLUIDO { background: #22c55e; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 TaskFlow API & Dashboard</h1>
        
        <div class="form-group">
            <h3>Cadastrar Nova Demandas / Tarefa</h3>
            <form action="/api/tasks" method="POST">
                <input type="text" name="title" placeholder="Título da tarefa (ex: Criar Stored Procedure em C#)" required><br>
                <input type="text" name="category" placeholder="Categoria (ex: Backend, SQL, Testes)"><br>
                <input type="text" name="description" placeholder="Descrição da demanda"><br>
                <button type="submit">Adicionar Tarefa (POST)</button>
            </form>
        </div>

        <h2>Tarefas Registradas no Banco (SQLite)</h2>
        {% for t in tasks %}
        <div class="card">
            <span class="badge {{ t.status }}">{{ t.status }}</span> | <strong>{{ t.category }}</strong>
            <h3>{{ t.title }}</h3>
            <p>{{ t.description }}</p>
            <small>Criado em: {{ t.created_at }}</small>
        </div>
        {% else %}
        <p>Nenhuma tarefa cadastrada no banco.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [{"id": r[0], "title": r[1], "description": r[2], "category": r[3], "status": r[4], "created_at": r[5]} for r in rows]
    return render_template_string(HTML_TEMPLATE, tasks=tasks)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
