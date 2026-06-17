from tkinter import Tk, Label, Entry, Button, Frame, messagebox
from Conversor import ConversorThompson
import os
import shutil


class ConverterGUI:

    def __init__(self, master):
        self.master = master
        master.title("Conversor ER → AFND (Thompson)")

        frm = Frame(master)
        frm.pack(padx=10, pady=10)

        Label(frm, text="Expressão Regular:").pack(anchor="w")

        self.entry = Entry(frm, width=50)
        self.entry.pack(pady=5)

        Button(
            frm,
            text="Gerar AFND",
            command=self.on_generate
        ).pack(pady=10)

    def on_generate(self):

        regex = self.entry.get().strip()

        if not regex:
            messagebox.showwarning(
                "Aviso",
                "Digite uma expressão regular."
            )
            return

        try:
            conversor = ConversorThompson(regex)

            afnd = conversor.converter()

            output_path = "afnd.png"

            afnd.show_diagram(path=output_path)

            if os.path.exists(output_path):

                try:

                    if os.name == "nt":
                        os.startfile(output_path)

                    else:
                        opener = shutil.which(
                            "xdg-open"
                        ) or shutil.which(
                            "open"
                        )

                        if opener:
                            os.system(
                                f'"{opener}" "{output_path}"'
                            )

                except Exception:
                    pass

            messagebox.showinfo(
                "Sucesso",
                "AFND gerado com sucesso!"
            )

        except Exception as e:

            messagebox.showerror(
                "Erro",
                str(e)
            )


def main():

    root = Tk()

    root.geometry("450x150")

    ConverterGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
