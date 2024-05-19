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
                hora TEXT,
                servico TEXT,                        
                id TEXT                        
            )
        """)
        self.conexao.commit()                                  # Comita as alterações no banco de dados.

    def inserir_dados(self, nome, telefone, data, hora, servico, id):
        self.cursor.execute("INSERT INTO agenda (nome, telefone, data, hora, servico, id) VALUES (?, ?, ?, ?, ?, ?)", (nome, telefone, data, hora, servico, id))  # Insere dados na tabela 'agenda'.
        self.conexao.commit()                                  # Comita a transação para salvar os dados inseridos.

    def excluir_dados(self, id):
        self.cursor.execute("DELETE FROM agenda WHERE id = ?", (id,))
        self.conexao.commit()

    def atualizar_dados(self, nome, telefone, data, hora, servico, id):
        self.cursor.execute("UPDATE agenda SET nome = ?, telefone = ?, data = ?, hora = ?, servico = ? WHERE id = ?", (nome, telefone, data, hora, servico, id))
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
        self.dataEntry = DateEntry(self, width=10, background='blue', foreground='white', borderwidth=2, locale='pt_BR', date_pattern='dd/MM/yyyy', firstweekday='sunday', showweeknumbers=False)
        self.dataEntry.grid(row=3, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Hora:").grid(row=4, column=0, padx=20, pady=10)
        self.horaEntry = ctk.CTkComboBox(self, values=["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"])
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
        self.id = id  # Recebe o ID como parâmetro
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

        ctk.CTkButton(self, text="Excluir", command=self.confirmar_exclusao).grid(row=2, column=1, padx=20, pady=20)

    def confirmar_exclusao(self):
        id = self.idEntry.get()
        ConfirmarExclusao(self.db_manager, id).mainloop()  # Passa o ID para a janela de confirmação de exclusão

class AtualizarAgendamento(ctk.CTk):
    def __init__(self, db_manager, id):
        super().__init__()
        self.db_manager = db_manager
        self.id = id
        self.title("Atualizar Agendamento")
        self.geometry("600x400")

        ctk.CTkLabel(self, text="Atualizar Agendamento", font=("Arial", 20)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        agendamentos = self.db_manager.buscar_agendamentos_por_id(id)
        if agendamentos:
            agendamento = agendamentos[0]  # Assume-se que só haverá um agendamento por ID

            ctk.CTkLabel(self, text="Nome:").grid(row=1, column=0, padx=20, pady=10)
            self.nomeEntry = ctk.CTkEntry(self)
            self.nomeEntry.insert(0, agendamento[0])  # Preenche com o valor existente
            self.nomeEntry.grid(row=1, column=1, padx=20, pady=10)

            ctk.CTkLabel(self, text="Telefone:").grid(row=2, column=0, padx=20, pady=10)
            self.telefoneEntry = ctk.CTkEntry(self)
            self.telefoneEntry.insert(0, agendamento[1])
            self.telefoneEntry.grid(row=2, column=1, padx=20, pady=10)

            ctk.CTkLabel(self, text="Data:").grid(row=3, column=0, padx=20, pady=10)
            self.dataEntry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, locale='pt_BR', date_pattern='dd/MM/yyyy', firstweekday='sunday', showweeknumbers=False)
            self.dataEntry.set_date(agendamento[2])
            self.dataEntry.grid(row=3, column=1, padx=20, pady=10)

            ctk.CTkLabel(self, text="Hora:").grid(row=4, column=0, padx=20, pady=10)
            self.horaEntry = ctk.CTkEntry(self)
            self.horaEntry.insert(0, agendamento[3])
            self.horaEntry.grid(row=4, column=1, padx=20, pady=10)

            ctk.CTkLabel(self, text="Serviço:").grid(row=5, column=0, padx=20, pady=10)
            self.servicoEntry = ctk.CTkComboBox(self, values=["Corte de Cabelo", "Manicure", "Pedicure", "Depilação", "Maquiagem"])
            self.servicoEntry.set(agendamento[4])
            self.servicoEntry.grid(row=5, column=1, padx=20, pady=10)

            ctk.CTkButton(self, text="Salvar", command=self.salvar_dados_atualizados).grid(row=6, column=1, padx=20, pady=20)

    def salvar_dados_atualizados(self):
        # Coleta os valores dos campos de entrada
        nome = self.nomeEntry.get()
        telefone = self.telefoneEntry.get()
        data = self.dataEntry.get()
        hora = self.horaEntry.get()
        servico = self.servicoEntry.get()
        
        # Chama a função de atualização de dados do gerenciador do banco de dados
        self.db_manager.atualizar_dados(nome, telefone, data, hora, servico, self.id)
        self.after(100, self.destroy)                                         # Fecha a janela.

class SelecionarAgendamentoParaAtualizar(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.title("Selecionar Agendamento para Atualizar")
        self.geometry("600x400")

        ctk.CTkLabel(self, text="Selecionar Agendamento para Atualizar", font=("Arial", 20)).pack(pady=20)

        ctk.CTkLabel(self, text="ID do Agendamento:").pack(pady=10)
        self.idEntry = ctk.CTkEntry(self)
        self.idEntry.pack(pady=10)

        ctk.CTkButton(self, text="Selecionar", command=self.selecionar_agendamento).pack(pady=20)

    def selecionar_agendamento(self):
        id = self.idEntry.get()
        AtualizarAgendamento(self.db_manager, id).mainloop()  # Passa o ID para a janela de atualização de agendamento

class ConsultarAgendamentos(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.title("Consultar Agendamentos")
        self.geometry("700x400")

        ctk.CTkLabel(self, text="Consultar Agendamentos", font=("Arial", 20)).pack(pady=20)
        
        ctk.CTkLabel(self, text="Data:").pack(pady=10)
        self.dataEntry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, locale='pt_BR', date_pattern='dd/MM/yyyy', firstweekday='sunday', showweeknumbers=False)
        self.dataEntry.pack(pady=10)
        
        ctk.CTkButton(self, text="Buscar", command=self.buscar_agendamentos).pack(pady=20)

        self.listaAgendamentos = Listbox(self) # Cria uma lista para exibir os agendamentos
        self.listaAgendamentos.pack(padx=20, pady=20, fill="both", expand=True)
        
    def buscar_agendamentos(self):
        data_selecionada = self.dataEntry.get()
        agendamentos = self.db_manager.buscar_agendamentos_por_data(data_selecionada)
        self.listaAgendamentos.delete(0, END)  # Limpa a lista antes de adicionar novos itens

        if agendamentos:
            for agendamento in agendamentos:
                agendamento_texto = f"Hora: {agendamento[0]} - Nome: {agendamento[1]} - Serviço: {agendamento[2]} - ID: {agendamento[3]}"
                self.listaAgendamentos.insert(END, agendamento_texto)
        else:
            self.listaAgendamentos.insert(END, "Nenhum agendamento encontrado para a data selecionada.")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()

        self.title("Barber's")
        self.geometry("600x400")

        ctk.CTkLabel(self, text="Barber's", font=("Arial", 20)).pack(pady=20)

        ctk.CTkButton(self, text="Novo Agendamento", command=self.abrir_novo_agendamento).pack(pady=10)
        ctk.CTkButton(self, text="Excluir Agendamento", command=self.abrir_excluir_agendamento).pack(pady=10)
        ctk.CTkButton(self, text="Atualizar Agendamento", command=self.abrir_selecionar_agendamento_para_atualizar).pack(pady=10)
        ctk.CTkButton(self, text="Consultar Agendamentos", command=self.abrir_consultar_agendamentos).pack(pady=10)

    def abrir_novo_agendamento(self):
        NovoAgendamento(self.db_manager).mainloop()

    def abrir_excluir_agendamento(self):
        ExcluirAgendamento(self.db_manager).mainloop()

    def abrir_selecionar_agendamento_para_atualizar(self):
        SelecionarAgendamentoParaAtualizar(self.db_manager).mainloop()

    def abrir_consultar_agendamentos(self):
        ConsultarAgendamentos(self.db_manager).mainloop()

if __name__ == "__main__":
    app = App()
    app.mainloop()