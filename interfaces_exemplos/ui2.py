import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading


class GraphQLClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GraphQL Client")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Variáveis de configuração
        self.orgid = tk.StringVar()
        self.token = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        # ===== BARRA SUPERIOR (orgid + token) =====
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Org ID:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(top_frame, textvariable=self.orgid, width=25).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(top_frame, text="Token:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(top_frame, textvariable=self.token, width=50, show="*").pack(side=tk.LEFT, padx=(0, 10))

        # Botões de ação
        ttk.Button(top_frame, text="Introspect", command=self._run_introspect).pack(side=tk.LEFT, padx=4)
        ttk.Button(top_frame, text="Executar Query", command=self._run_query).pack(side=tk.LEFT, padx=4)
        ttk.Button(top_frame, text="Limpar", command=self._clear_all).pack(side=tk.LEFT, padx=4)

        # Toggle para mostrar/ocultar token
        self.show_token_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_frame, text="Mostrar token", variable=self.show_token_var,
                        command=self._toggle_token_visibility).pack(side=tk.LEFT, padx=10)

        # ===== ÁREA PRINCIPAL: 3 COLUNAS =====
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Coluna Esquerda - Introspecção
        left_frame = ttk.LabelFrame(paned, text="Schema (Introspecção)", padding=5)
        self.introspection_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE,
                                                            font=("Consolas", 10))
        self.introspection_text.pack(fill=tk.BOTH, expand=True)
        paned.add(left_frame, weight=1)

        # Coluna Central - Editor de Queries
        middle_frame = ttk.LabelFrame(paned, text="Query / Mutation", padding=5)
        self.query_text = scrolledtext.ScrolledText(middle_frame, wrap=tk.NONE,
                                                    font=("Consolas", 11))
        self.query_text.pack(fill=tk.BOTH, expand=True)
        # Query de exemplo
        self.query_text.insert("1.0", '{\n  __typename\n}\n')
        paned.add(middle_frame, weight=1)

        # Coluna Direita - Resultados
        right_frame = ttk.LabelFrame(paned, text="Resultado", padding=5)
        self.result_text = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE,
                                                     font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        paned.add(right_frame, weight=1)

        # ===== BARRA DE STATUS =====
        self.status_var = tk.StringVar(value="Pronto.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W, padding=4)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Atalhos de teclado
        self.root.bind("<Control-Return>", lambda e: self._run_query())
        self.root.bind("<Control-i>", lambda e: self._run_introspect())

    def _toggle_token_visibility(self):
        # Encontra o Entry do token e alterna a exibição
        for child in self.root.winfo_children()[0].winfo_children():
            if isinstance(child, ttk.Entry) and child.cget("show") in ("*", ""):
                child.config(show="" if self.show_token_var.get() else "*")
                break

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _clear_all(self):
        self.introspection_text.delete("1.0", tk.END)
        self.query_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self._set_status("Tudo limpo.")

    # -------------------------------------------------------------
    # Integração com seu backend GraphQL
    # Substitua os métodos abaixo pelas chamadas reais do seu software
    # -------------------------------------------------------------
    def _get_graphql_client(self):
        """
        TODO: Retorne aqui a instância do seu cliente GraphQL configurada
        com self.orgid.get() e self.token.get().
        Exemplo:
            from meu_modulo import GraphQLClient
            return GraphQLClient(org_id=self.orgid.get(), token=self.token.get())
        """
        return None

    def _run_introspect(self):
        orgid = self.orgid.get().strip()
        token = self.token.get().strip()
        if not orgid or not token:
            messagebox.showwarning("Atenção", "Preencha Org ID e Token antes de introspectar.")
            return

        def worker():
            try:
                self._set_status("Executando introspecção...")
                client = self._get_graphql_client()

                # TODO: substitua pela chamada real de introspecção
                # schema = client.introspect()
                # Exemplo simulado:
                schema = {
                    "__schema": {
                        "queryType": {"name": "Query"},
                        "types": [
                            {"name": "Query", "kind": "OBJECT"},
                            {"name": "User", "kind": "OBJECT"},
                        ]
                    }
                }

                formatted = json.dumps(schema, indent=2, ensure_ascii=False)
                self.root.after(0, self._update_introspection, formatted)
                self.root.after(0, self._set_status, "Introspecção concluída.")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Erro", f"Falha na introspecção:\n{e}")
                self.root.after(0, self._set_status, "Erro na introspecção.")

        threading.Thread(target=worker, daemon=True).start()

    def _run_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Atenção", "Escreva uma query antes de executar.")
            return

        orgid = self.orgid.get().strip()
        token = self.token.get().strip()
        if not orgid or not token:
            messagebox.showwarning("Atenção", "Preencha Org ID e Token.")
            return

        def worker():
            try:
                self._set_status("Executando query...")
                client = self._get_graphql_client()

                # TODO: substitua pela chamada real
                # result = client.execute(query)
                # Exemplo simulado:
                result = {"data": {"__typename": "Query"}}

                formatted = json.dumps(result, indent=2, ensure_ascii=False)
                self.root.after(0, self._update_result, formatted)
                self.root.after(0, self._set_status, "Query executada com sucesso.")
            except Exception as e:
                self.root.after(0, self._update_result, f"ERRO:\n{e}")
                self.root.after(0, self._set_status, "Erro na execução.")

        threading.Thread(target=worker, daemon=True).start()

    def _update_introspection(self, text):
        self.introspection_text.delete("1.0", tk.END)
        self.introspection_text.insert("1.0", text)

    def _update_result(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphQLClientApp(root)
    root.mainloop()