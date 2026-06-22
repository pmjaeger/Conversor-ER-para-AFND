from tkinter import Tk, Label, Entry, Button, Frame, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y, BOTH, LEFT, filedialog
from PIL import Image, ImageTk
from Conversor import ConversorThompson
import os
import shutil  # Importado para copiar o arquivo gerado com facilidade


class ConverterGUI:

    def __init__(self, master):
        self.master = master
        master.title("Conversor ER → AFND (Thompson)")
        master.geometry("1000x750")
        master.resizable(False, False)

        # Cores personalizadas
        self.cor_fundo = "#f0f4f8"
        self.cor_primaria = "#2c3e50"
        self.cor_secundaria = "#3498db"
        self.cor_sucesso = "#27ae60"
        self.cor_aviso = "#e74c3c"

        # Variável para armazenar a referência da imagem
        self.photo_image = None
        self.caminho_atual_png = "afnd.png"  # Mantém o rastro do arquivo gerado

        master.configure(bg=self.cor_fundo)

        # ========== TÍTULO ==========
        titulo = Label(
            master,
            text="Conversor de Expressão Regular para AFND",
            font=("Arial", 14, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        )
        titulo.pack(pady=8)

        # ========== SEÇÃO DE ENTRADA ==========
        entrada_frame = Frame(master, bg=self.cor_fundo)
        entrada_frame.pack(padx=20, pady=5, fill="x")

        Label(
            entrada_frame,
            text="📝 Expressão Regular:",
            font=("Arial", 11, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        ).pack(anchor="w", pady=(0, 5))

        self.entry = Entry(
            entrada_frame,
            width=60,
            font=("Arial", 11),
            border=2,
            relief="solid"
        )
        self.entry.pack(pady=5, ipady=8)

        # ========== EXEMPLOS ==========
        exemplo_frame = Frame(master, bg=self.cor_fundo)
        exemplo_frame.pack(padx=20, pady=5, fill="x")

        Label(
            exemplo_frame,
            text="💡 Exemplos:",
            font=("Arial", 9, "italic"),
            bg=self.cor_fundo,
            fg="#7f8c8d"
        ).pack(anchor="w")

        Label(
            exemplo_frame,
            text="ℹ️ Operadores: | (união), * (estrela), + (mais de 1), ? (opcional), ( ) (agrupamento), ε (epsilon)",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#555",
            justify="left",
            padx=10,
            pady=5,
            relief="solid",
            border=1
        ).pack(anchor="w", fill="x", pady=(0, 5))

        exemplos_text = "a  |  (a|b)* |  a+b+  |  (a|b)?c+  |  a(a|b)*b"
        Label(
            exemplo_frame,
            text=exemplos_text,
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#34495e",
            padx=10,
            pady=5,
            relief="solid",
            border=1
        ).pack(anchor="w", fill="x", pady=5)

        # ========== BOTÃO GERAR ==========
        botao_frame = Frame(master, bg=self.cor_fundo)
        botao_frame.pack(pady=5)

        btn_gerar = Button(
            botao_frame,
            text="🚀 Gerar AFND",
            command=self.on_generate,
            font=("Arial", 11, "bold"),
            bg=self.cor_secundaria,
            fg="white",
            padx=30,
            pady=10,
            border=0,
            cursor="hand2",
            activebackground="#2980b9",
            activeforeground="white"
        )
        btn_gerar.pack(side=LEFT, padx=5)

        btn_limpar = Button(
            botao_frame,
            text="🗑️ Limpar",
            command=self.on_clear,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=10,
            border=0,
            cursor="hand2",
            activebackground="#7f8c8d"
        )
        btn_limpar.pack(side=LEFT, padx=5)

        # ========== LOG/RESULTADO ==========
        log_frame = Frame(master, bg=self.cor_fundo)
        log_frame.pack(padx=20, pady=5, fill="x")

        Label(
            log_frame,
            text="📋 Status:",
            font=("Arial", 10, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        ).pack(anchor="w", pady=(0, 3))

        # Frame com scrollbar para log
        log_inner = Frame(log_frame, bg="white", relief="solid", border=1)
        log_inner.pack(fill="x")

        scrollbar = Scrollbar(log_inner, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log_text = Text(
            log_inner,
            height=3,
            width=60,
            font=("Courier", 9),
            wrap="word",
            bg="white",
            fg="#2c3e50",
            yscrollcommand=scrollbar.set,
            border=0,
            padx=10,
            pady=10
        )
        self.log_text.pack(side=LEFT, fill=BOTH, expand=False)
        scrollbar.config(command=self.log_text.yview)

        # Mensagem inicial
        self.add_log(
            "✅ Sistema pronto! Digite uma expressão regular acima.", "info")

        # ========== VISUALIZADOR DE IMAGEM ==========
        imagem_frame = Frame(master, bg=self.cor_fundo)
        imagem_frame.pack(padx=20, pady=5, fill=BOTH, expand=True)

        Label(
            imagem_frame,
            text="🖼️ Visualização do AFND:",
            font=("Arial", 10, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        ).pack(anchor="w", pady=(0, 5))

        # Frame com borda para a imagem
        imagem_inner = Frame(imagem_frame, bg="white",
                             relief="solid", border=1)
        imagem_inner.pack(fill=BOTH, expand=True)

        self.imagem_label = Label(
            imagem_inner,
            bg="white",
            text="Nenhum AFND gerado ainda",
            font=("Arial", 10, "italic"),
            fg="#999"
        )
        self.imagem_label.pack(fill=BOTH, expand=True)

        # ========== RODAPÉ (INSTRUÇÕES E BOTÃO SALVAR) ==========
        instr_frame = Frame(master, bg="#ecf0f1")
        instr_frame.pack(padx=20, pady=5, fill="x")

        # Texto descritivo alinhado à esquerda
        Label(
            instr_frame,
            text="ℹ️ Operadores: | (união), * (estrela), + (mais de 1), ? (opcional), ( ) (agrupamento), ε (epsilon)",
            font=("Arial", 8),
            bg="#ecf0f1",
            fg="#555",
            justify="left"
        ).pack(side=LEFT, padx=10, pady=8)

        # NOVO: Botão de Salvar Imagem alinhado no canto inferior direito
        self.btn_salvar = Button(
            instr_frame,
            text="💾 Salvar Imagem",
            command=self.on_save_image,
            font=("Arial", 9, "bold"),
            bg=self.cor_sucesso,
            fg="white",
            padx=15,
            pady=4,
            border=0,
            cursor="hand2",
            activebackground="#219150",
            activeforeground="white",
            state="disabled"  # Começa desativado até que uma imagem exista
        )
        self.btn_salvar.pack(side=RIGHT, padx=10, pady=5)

    def on_generate(self):
        regex = self.entry.get().strip()

        if not regex:
            self.add_log("❌ Erro: Digite uma expressão regular!", "erro")
            messagebox.showwarning(
                "⚠️ Aviso",
                "Por favor, digite uma expressão regular."
            )
            return

        self.add_log(f"⏳ Processando: {regex}...", "info")
        self.master.update()

        try:
            conversor = ConversorThompson(regex)
            afnd = conversor.converter()

            output_path = self.caminho_atual_png
            afnd.show_diagram(path=output_path)

            if os.path.exists(output_path):
                self.exibir_imagem(output_path)
                # Ativa o botão ao gerar com sucesso
                self.btn_salvar.config(state="normal")

            self.add_log(f"✅ Sucesso! AFND gerado para: {regex}", "sucesso")
            messagebox.showinfo(
                "🎉 Sucesso",
                "AFND gerado com sucesso!"
            )

        except Exception as e:
            erro_msg = str(e)
            self.add_log(f"❌ Erro: {erro_msg}", "erro")
            messagebox.showerror(
                "⚠️ Erro na Conversão",
                f"Erro ao processar a expressão:\n\n{erro_msg}"
            )

    def exibir_imagem(self, caminho_imagem):
        """Carrega e exibe a imagem PNG na interface."""
        try:
            # Abre a imagem
            img = Image.open(caminho_imagem)

            # Redimensiona para caber na área disponível (mantém proporção)
            max_width = 950
            max_height = 600

            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Converte para PhotoImage do tkinter
            self.photo_image = ImageTk.PhotoImage(img)

            # Exibe na label
            self.imagem_label.config(image=self.photo_image, text="")
        except Exception as e:
            self.add_log(
                f"⚠️ Aviso: Não foi possível exibir a imagem: {str(e)}", "aviso")

    def on_save_image(self):
        """Abre uma caixa de diálogo para salvar a imagem gerada em um local escolhido."""
        if not os.path.exists(self.caminho_atual_png):
            messagebox.showerror(
                "❌ Erro", "Nenhuma imagem encontrada para salvar.")
            return

        # Abre o explorador de arquivos para escolher o destino
        caminho_destino = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagens PNG", "*.png"), ("Todos os arquivos", "*.*")],
            title="Salvar Imagem do AFND como..."
        )

        if caminho_destino:
            try:
                # Copia o arquivo temporário gerado para o local escolhido pelo usuário
                shutil.copy(self.caminho_atual_png, caminho_destino)
                self.add_log(
                    f"💾 Imagem salva com sucesso em: {caminho_destino}", "sucesso")
                messagebox.showinfo("💾 Salvo", "Imagem salva com sucesso!")
            except Exception as e:
                self.add_log(f"❌ Erro ao salvar imagem: {str(e)}", "erro")
                messagebox.showerror(
                    "⚠️ Erro", f"Não foi possível salvar a imagem:\n{str(e)}")

    def on_clear(self):
        self.entry.delete(0, "end")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="normal")
        self.imagem_label.config(image="", text="Nenhum AFND gerado ainda")
        self.photo_image = None
        self.btn_salvar.config(state="disabled")  # Desativa o botão de salvar
        self.add_log("🧹 Campo limpo!", "info")
        self.entry.focus()

    def add_log(self, mensagem, tipo="info"):
        self.log_text.config(state="normal")

        # Cores para diferentes tipos de mensagem
        cores = {
            "info": "#3498db",
            "sucesso": "#27ae60",
            "erro": "#e74c3c",
            "aviso": "#f39c12"
        }

        self.log_text.insert("end", mensagem + "\n")

        # Colore a última linha
        ultima_linha = int(self.log_text.index("end").split(".")[0]) - 1
        self.log_text.tag_add(
            f"cor_{tipo}", f"{ultima_linha}.0", f"{ultima_linha}.end")
        self.log_text.tag_config(
            f"cor_{tipo}", foreground=cores.get(tipo, "#2c3e50"))

        self.log_text.see("end")
        self.log_text.config(state="disabled")


def main():
    root = Tk()
    ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
