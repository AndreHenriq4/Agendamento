import random
import sqlite3
import customtkinter as ctk
from tkcalendar import Calendar, DateEntry
from tkinter import END, Listbox

class DatabaseManager:
    def __init__(self):
        self.db_path = 'agendamento.db'          # Define o caminho para o arquivo do banco de dados.
        self.conexao = sqlite3.connect(self.db_path)  # Estabelece a conexão com o banco de dados.
        self.cursor = self.conexao.cursor()      # Cria um cursor para executar operações de banco de dados.
        self.setup_database()                    # Chama o método para configurar a tabela do banco de dados.

    def setup_database(self):
        self.cursor.execute("""                
            CREATE TABLE IF NOT EXISTS agenda (   
                nome TEXT,                       
                telefone TEXT,                    
                data TEXT,                        
                hora TEXT
                servico TEXT                        
            )
        """)

        self.cursor.execute("PRAGMA table_info(agenda)")  # Recupera informações sobre as colunas da tabela 'agenda'.
        columns = [info[1] for info in self.cursor.fetchall()]  # Extrai os nomes das colunas da resposta.
        if 'id' not in columns:                          # Verifica se a coluna 'servico' não está presente.
            self.cursor.execute("ALTER TABLE agenda ADD COLUMN id TEXT")  # Adiciona a coluna 'servico' se necessário.
        self.conexao.commit()                                  # Comita as alterações no banco de dados.

    def inserir_dados(self, nome, telefone, data, hora, servico, id):
        self.cursor.execute("INSERT INTO agenda (nome, telefone, data, hora, servico, id) VALUES (?, ?, ?, ?, ?, ?)", (nome, telefone, data, hora, servico, id))  # Insere dados na tabela 'agenda'.
        self.conexao.commit()                                  # Comita a transação para salvar os dados inseridos.

    def excluir_dados(self, id):
        self.cursor.execute("DELETE FROM agenda WHERE id = ?", (id,))
        self.conexao.commit()

    def atualizar_dados(self, nome, telefone, data, hora, servico, id):
        self.cursor.execute("UPDATE agenda SET nome = ?, telefone = ?, data = ?, hora = ?, servico = ?  where id = ?", (nome, telefone, data, hora, servico, id))
        self.conexao.commit()

    def buscar_agendamentos_por_id(self, id):
        self.cursor.execute("SELECT nome, telefone, data, hora, servico, id FROM agenda WHERE id = ?", (id,))
        return self.cursor.fetchall()

    def buscar_agendamentos_por_data(self, data_selecionada):
        self.cursor.execute("SELECT hora, nome, servico, id FROM agenda WHERE data = ?", (data_selecionada,))  # Busca agendamentos por data.
        return self.cursor.fetchall()                           # Retorna os resultados da consulta.

    def __del__(self):
        self.conexao.close()                                   # Fecha a conexão com o banco de dados ao destruir a instância.

class NovoAgendamento(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()                                       # Inicializa a classe pai ctk.CTk.
        self.db_manager = db_manager                             # Armazena a referência para o gerenciador do banco de dados.
        self.title("Novo Agendamento")                           # Define o título da janela.
        self.geometry("600x400")                                 # Define o tamanho da janela.

        # Criação e posicionamento de widgets como labels, entradas de texto e botões
        ctk.CTkLabel(self, text="Novo Agendamento", font=("Arial", 20)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        ctk.CTkLabel(self, text="Nome:").grid(row=1, column=0, padx=20, pady=10)
        self.nomeEntry = ctk.CTkEntry(self)
        self.nomeEntry.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Telefone:").grid(row=2, column=0, padx=20, pady=10)
        self.telefoneEntry = ctk.CTkEntry(self)
        self.telefoneEntry.grid(row=2, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Data:").grid(row=3, column=0, padx=20, pady=10)
        self.dataEntry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, locale='pt_BR', date_pattern='dd/MM/yyyy', firstweekday='sunday', showweeknumbers=False)
        self.dataEntry.grid(row=3, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Hora:").grid(row=4, column=0, padx=20, pady=10)
        self.horaEntry = ctk.CTkEntry(self)
        self.horaEntry.grid(row=4, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Serviço:").grid(row=5, column=0, padx=20, pady=10)
        self.servicoEntry = ctk.CTkComboBox(self, values=["Corte de Cabelo", "Manicure", "Pedicure", "Depilação", "Maquiagem"])
        self.servicoEntry.grid(row=5, column=1, padx=20, pady=10)

        ctk.CTkButton(self, text="Salvar", command=self.salvar_dados).grid(row=6, column=1, padx=20, pady=20)

    def salvar_dados(self):
        # Coleta os valores dos campos de entrada
        nome = self.nomeEntry.get()
        telefone = self.telefoneEntry.get()
        data = self.dataEntry.get()
        hora = self.horaEntry.get()
        servico = self.servicoEntry.get()
        
        # Chama a função de inserção de dados do gerenciador do banco de dados
        id = random.randint(1, 1000)                            # Gera um ID aleatório para o agendamento.
        self.db_manager.inserir_dados(nome, telefone, data, hora, servico, id)
        self.after(100, self.destroy)                                         # Fecha a janela.

    def fechar_janela(self):
        self.after(100, self.destroy)                                         # Função para fechar a janela.

class ConfirmarExclusao(ctk.CTk):
    def __init__(self, db_manager, id):
        super().__init__()
        self.db_manager = db_manager
        self.id = id  # Recebe o ID como parâmetr
        self.title("Excluir Agendamento")
        self.geometry("700x400")

        self.listaAgendamentos = ctk.CTkLabel(self, text="?", font=("Arial", 20))

        agendamentos = self.db_manager.buscar_agendamentos_por_id(id)
        if agendamentos:
            agendamento = agendamentos[0]  # Assume-se que só haverá um agendamento por ID

            self.nomeLabel = ctk.CTkLabel(self, text=f"Nome: {agendamento[0]}")
            self.nomeLabel.pack(pady=2)

            self.telefoneLabel = ctk.CTkLabel(self, text=f"Telefone: {agendamento[1]}")
            self.telefoneLabel.pack(pady=2)

            self.dataLabel = ctk.CTkLabel(self, text=f"Data: {agendamento[2]}")
            self.dataLabel.pack(pady=2)

            self.horaLabel = ctk.CTkLabel(self, text=f"Hora: {agendamento[3]}")
            self.horaLabel.pack(pady=2)

            self.servicoLabel = ctk.CTkLabel(self, text=f"Serviço: {agendamento[4]}")
            self.servicoLabel.pack(pady=2)

            self.idLabel = ctk.CTkLabel(self, text=f"ID: {agendamento[5]}")
            self.idLabel.pack(pady=2)          

        ctk.CTkLabel(self, text=f"Confirma exclusão do agendamento?").pack(pady=20)
        ctk.CTkButton(self, text="Excluir", command=self.excluir_agendamento).pack()
        ctk.CTkButton(self, text="Cancelar", command= self.cancelar_exclusao).pack(pady=10)    

    def cancelar_exclusao(self):
        self.after(100, self.destroy)

    def excluir_agendamento(self):
        self.db_manager.excluir_dados(self.id)
        print("Agendamento excluído.")
        self.after(100, self.destroy)  # Fecha a janela 

class ExcluirAgendamento(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()                                       # Inicializa a classe pai ctk.CTk.
        self.db_manager = db_manager                             # Armazena a referência para o gerenciador do banco de dados.
        self.title("Excluir Agendamento")                        # Define o título da janela.
        self.geometry("600x400")                                 # Define o tamanho da janela.

        # Criação e posicionamento de widgets como labels, entradas de texto e botões
        ctk.CTkLabel(self, text="Excluir Agendamento", font=("Arial", 20)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        ctk.CTkLabel(self, text="ID do Agendamento:").grid(row=1, column=0, padx=20, pady=10)
        self.idEntry = ctk.CTkEntry(self)
        self.idEntry.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkButton(self, text="Seguir", command=self.abrir_confirmar_exclusao).grid(row=2, column=1, padx=20, pady=20)
        ctk.CTkButton(self, text="Cancelar", command=self.fechar_janela).grid(row=3, column=1, padx=20)

    def fechar_janela(self):
        self.after(100, self.destroy)                                         # Função para fechar a janela.

    def coletaId(self):
        id = self.idEntry.get()
        return id

    def excluir_agendamento(self):
        # Chama a função de exclusão de dados do gerenciador do banco de dados
        id = self.idEntry.get()
        self.db_manager.excluir_dados(id)
        self.after(100, self.destroy)                                         # Fecha a janela.

    def abrir_confirmar_exclusao(self):
        id = self.idEntry.get()  # Coleta o ID
        agendamentos = self.db_manager.buscar_agendamentos_por_id(id)
        if agendamentos:  # Certifique-se de que o ID não está vazio
            confirmar = ConfirmarExclusao(self.db_manager, id)  # Passa o ID para a classe de confirmação
            confirmar.mainloop()
        else:
            #caso não encontre o ID
            ctk.CTkLabel(self, text="ID não encontrado").grid(row=4, column=1, padx=20, pady=10)

class JanelaAgendamentos(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()                                       # Inicializa a classe pai ctk.CTk.
        self.db_manager = db_manager                             # Armazena a referência para o gerenciador do banco de dados.
        self.title("Agendamentos")                               # Define o título da janela.
        self.geometry("1200x800")                                # Define o tamanho da janela.

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Criação e posicionamento de widgets como calendário, lista de agendamentos e botões
        self.calendario = Calendar(self, selectmode='day', year=2024, month=5, day=1, date_pattern='dd/MM/yyyy', locale='pt_BR', firstweekday="sunday", showweeknumbers=False) 
        self.calendario.grid(row=0, column=1, padx=50, pady=50, sticky="ne")
        self.calendario.bind("<<CalendarSelected>>", self.carregar_agendamentos)

        self.listaAgendamentos = Listbox(self, height=50, width=130)
        self.listaAgendamentos.grid(row=0, column=0, padx=10, pady=10)
        
        ctk.CTkButton(self, text="Novo Agendamento", command=self.abrir_novo_agendamento).grid(row=0, column=1, padx=0, pady=250, sticky="n")
        ctk.CTkButton(self, text="Excluir Agendamento", command=self.abrir_excluir_agendamento).grid(row=0, column=1, padx=0, pady=280, sticky="n")
        ctk.CTkButton(self, text="Atualizar Agendamento", command=self.abrir_atualizar_agendamento).grid(row=0, column=1, padx=0, pady=310, sticky="n")

    def abrir_novo_agendamento(self):
        novo = NovoAgendamento(self.db_manager)   # Cria e exibe a janela de novo agendamento.
        novo.mainloop()                           # Inicia o loop da janela de novo agendamento.

    def abrir_excluir_agendamento(self):
        exclui = ExcluirAgendamento(self.db_manager)  # Cria e exibe a janela de exclusão de agendamento.
        exclui.mainloop()                             # Inicia o loop da janela de exclusão de agendamento.

    def abrir_atualizar_agendamento(self):
        atualiza = atualizarAgendamento(self.db_manager)
        atualiza.mainloop()

    def carregar_agendamentos(self, event):
        # Coleta a data selecionada no calendário e atualiza a lista de agendamentos
        data_selecionada = self.calendario.get_date()
        self.listaAgendamentos.delete(0, END)    # Limpa a lista de agendamentos.
        for agendamento in self.db_manager.buscar_agendamentos_por_data(data_selecionada):
            self.listaAgendamentos.insert(END, f"{agendamento[0]} - {agendamento[1]} - {agendamento[2]} - [{agendamento[3]}]")  # Adiciona agendamentos à lista.

class AtualizarAgendamento(ctk.CTk):
    def __init__(self, db_manager, agendamento):
        super().__init__()
        self.db_manager = db_manager
        self.agendamento = agendamento
        self.title("Atualizar Agendamento")
        self.geometry("600x400")

        ctk.CTkLabel(self, text="Atualizar Agendamento", font=("Arial", 20)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        ctk.CTkLabel(self, text="Nome:").grid(row=1, column=0, padx=20, pady=10)
        self.nomeEntry = ctk.CTkEntry(self)
        self.nomeEntry.grid(row=1, column=1, padx=20, pady=10)
        self.nomeEntry.insert(0, agendamento[0])

        ctk.CTkLabel(self, text="Telefone:").grid(row=2, column=0, padx=20, pady=10)
        self.telefoneEntry = ctk.CTkEntry(self)
        self.telefoneEntry.grid(row=2, column=1, padx=20, pady=10)
        self.telefoneEntry.insert(0, agendamento[1])

        ctk.CTkLabel(self, text="Data:").grid(row=3, column=0, padx=20, pady=10)
        self.dataEntry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.dataEntry.grid(row=3, column=1, padx=20, pady=10)
        self.dataEntry.insert(0, agendamento[2])

        ctk.CTkLabel(self, text="Hora:").grid(row=4, column=0, padx=20, pady=10)
        self.horaEntry = ctk.CTkEntry(self)
        self.horaEntry.grid(row=4, column=1, padx=20, pady=10)
        self.horaEntry.insert(0, agendamento[3])

        ctk.CTkLabel(self, text="Serviço:").grid(row=5, column=0, padx=20, pady=10)
        self.servicoEntry = ctk.CTkComboBox(self, values=["Corte de Cabelo", "Manicure", "Pedicure", "Depilação", "Maquiagem"])
        self.servicoEntry.grid(row=5, column=1, padx=20, pady=10)
        self.servicoEntry.insert(0, agendamento[4])

        ctk.CTkButton(self,  text="Salvar", command=self.atualizar_dados).grid(row=6, column=1, padx=20, pady=20)
        ctk.CTkButton(self, text="Cancelar", command=self.fechar_janela).grid(row=7, column=1, padx=20)
        
        self.id = agendamento[5]

class atualizarAgendamento(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.title("Atualizar Agendamento")
        self.geometry("600x400")

        ctk.CTkLabel(self, text="Atualizar Agendamento", font=("Arial", 20)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        ctk.CTkLabel(self, text="ID do Agendamento:").grid(row=1, column=0, padx=20, pady=10)
        self.idEntry = ctk.CTkEntry(self)
        self.idEntry.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkButton(self, text="Buscar", command=self.buscar_agendamento).grid(row=2, column=1, padx=20, pady=20)
        ctk.CTkButton(self, text="Cancelar", command=self.fechar_janela).grid(row=3, column=1, padx=20)

    def fechar_janela(self):
        self.after(100, self.destroy)

    def buscar_agendamento(self):
        id = self.idEntry.get()
        agendamentos = self.db_manager.buscar_agendamentos_por_id(id)
        if agendamentos:
            agendamento = agendamentos[0]
            self.nomeLabel = ctk.CTkLabel(self, text=f"Nome: {agendamento[0]}")
            self.nomeLabel.grid(row=1, column=2, padx=20, pady=10)

            self.telefoneLabel = ctk.CTkLabel(self, text=f"Telefone: {agendamento[1]}")
            self.telefoneLabel.grid(row=2, column=2, padx=20, pady=10)

            self.dataLabel = ctk.CTkLabel(self, text=f"Data: {agendamento[2]}")
            self.dataLabel.grid(row=3, column=2, padx=20, pady=10)

            self.horaLabel = ctk.CTkLabel(self, text=f"Hora: {agendamento[3]}")
            self.horaLabel.grid(row=4, column=2, padx=20, pady=10)

            self.servicoLabel = ctk.CTkLabel(self, text=f"Serviço: {agendamento[4]}")
            self.servicoLabel.grid(row=5, column=2, padx=20, pady=10)

            self.idLabel = ctk.CTkLabel(self, text=f"ID: {agendamento[5]}")
            self.idLabel.grid(row=6, column=2, padx=20, pady=10)

            ctk.CTkButton(self, text="Atualizar", command=self.atualizar_agendamento).grid(row=4, column=1, padx=20, pady=20)
        else:
            ctk.CTkLabel(self, text="ID não encontrado").grid(row=4, column=1, padx=20, pady=10)


# Execução do programa
if __name__ == "__main__":
    db_manager = DatabaseManager()              # Cria uma instância do gerenciador de banco de dados.
    app = JanelaAgendamentos(db_manager)        # Cria a janela principal de agendamentos.
    app.mainloop()                              # Inicia o loop principal da aplicação.