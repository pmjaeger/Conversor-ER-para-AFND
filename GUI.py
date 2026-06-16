from tkinter import Tk, Label, Entry, Button, Frame, messagebox
import automata.fa.nfa as nfa
import os
import tempfile
import shutil


class ConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title('Conversor ER -> AFND')

        frm = Frame(master)
        frm.pack(padx=10, pady=10)

        Label(frm, text='Expressão regular:').pack(anchor='w')
        self.entry = Entry(frm, width=60)
        self.entry.pack(pady=5)

        Button(frm, text='Gerar Autômato',
               command=self.on_generate).pack(pady=10)

    def on_generate(self):
        regex = self.entry.get().strip()
        if not regex:
            messagebox.showwarning('Aviso', 'Digite uma expressão regular.')
            return

        try:
            input_symbols = {ch for ch in regex if ch not in '()*|.'}
            builder = nfa.parse_regex(regex, input_symbols)

            # Convert builder to NFA object
            my_nfa = nfa.NFA(
                states=set(builder._transitions.keys()),
                input_symbols=input_symbols,
                transitions=builder._transitions,
                initial_state=builder._initial_state,
                final_states=builder._final_states
            )

            tmp_dir = tempfile.mkdtemp(prefix='afnd_')
            output_path = os.path.join(tmp_dir, 'afnd.png')
            my_nfa.show_diagram(path=output_path)

            if os.path.exists(output_path):
                try:
                    if os.name == 'nt':
                        os.startfile(output_path)
                    else:
                        opener = shutil.which(
                            'xdg-open') or shutil.which('open')
                        if opener:
                            os.system(f'"{opener}" "{output_path}"')
                        else:
                            messagebox.showinfo(
                                'Aviso', f'Arquivo gerado em:\n{output_path}')
                except Exception:
                    messagebox.showinfo(
                        'Aviso', f'Arquivo gerado em:\n{output_path}')
            else:
                messagebox.showerror(
                    'Erro', 'Não foi possível gerar o arquivo de diagrama.')
        except Exception as e:
            messagebox.showerror('Erro', f'Erro: {e}')


def main():
    root = Tk()
    root.geometry('400x150')
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
