"""Cipher Toolkit - a small Tkinter front end for the ciphers in ciphers/.

Run with:  python cipher_gui.py

Nothing here knows about Caesar specifically. The picker, the parameter
boxes and the extra buttons are all built from ciphers.REGISTRY, so adding a
new algorithm never means editing this file.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import ciphers

PAD = 8


class CipherApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.grid(row=0, column=0, sticky="nsew")

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)  # input pane grows
        self.rowconfigure(5, weight=2)  # output pane grows more

        self.param_entries = {}
        self.current = ciphers.REGISTRY[0]

        self._build_picker()
        self._build_params()
        self._build_input()
        self._build_buttons()
        self._build_output()
        self._build_status()

        self.on_cipher_change()

    # ---------- layout ----------

    def _build_picker(self):
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Cipher:").grid(row=0, column=0, padx=(0, PAD))

        self.cipher_var = tk.StringVar(value=self.current.name)
        picker = ttk.Combobox(
            frame,
            textvariable=self.cipher_var,
            values=ciphers.names(),
            state="readonly",
            width=24,
        )
        picker.grid(row=0, column=1, sticky="w")
        picker.bind("<<ComboboxSelected>>", self.on_cipher_change)

        self.description = ttk.Label(frame, text="", foreground="#555")
        self.description.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _build_params(self):
        self.params_frame = ttk.Frame(self)
        self.params_frame.grid(row=1, column=0, sticky="ew", pady=(PAD, 0))

    def _build_input(self):
        box = ttk.LabelFrame(self, text="Input", padding=6)
        box.grid(row=3, column=0, sticky="nsew", pady=(PAD, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)

        self.input_text = ScrolledText(box, height=6, wrap="word", font="TkFixedFont")
        self.input_text.grid(row=0, column=0, sticky="nsew")
        self.input_text.bind("<Control-Return>", lambda _e: self.run_encrypt())

    def _build_buttons(self):
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=4, column=0, sticky="ew", pady=(PAD, 0))

    def _build_output(self):
        box = ttk.LabelFrame(self, text="Output", padding=6)
        box.grid(row=5, column=0, sticky="nsew", pady=(PAD, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)

        self.output_text = ScrolledText(
            box, height=10, wrap="word", font="TkFixedFont", state="disabled"
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

    def _build_status(self):
        self.status_var = tk.StringVar(value="Ready.")
        self.status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        self.status.grid(row=6, column=0, sticky="ew", pady=(6, 0))

    # ---------- reacting to the cipher choice ----------

    def on_cipher_change(self, _event=None):
        self.current = ciphers.get(self.cipher_var.get())
        self.description.config(text=self.current.description)
        self._rebuild_params()
        self._rebuild_buttons()
        self.set_output("")
        self.set_status(f"{self.current.name} selected.")

    def _rebuild_params(self):
        for child in self.params_frame.winfo_children():
            child.destroy()
        self.param_entries.clear()

        for column, param in enumerate(self.current.params):
            cell = ttk.Frame(self.params_frame)
            cell.grid(row=0, column=column, sticky="w", padx=(0, 16))

            ttk.Label(cell, text=param.label + ":").grid(row=0, column=0, padx=(0, 6))
            var = tk.StringVar(value=param.default)
            entry = ttk.Entry(cell, textvariable=var, width=14)
            entry.grid(row=0, column=1)
            entry.bind("<Return>", lambda _e: self.run_encrypt())
            self.param_entries[param.key] = var

    def _rebuild_buttons(self):
        for child in self.button_frame.winfo_children():
            child.destroy()

        column = 0

        def add(text, command, style=None):
            nonlocal column
            button = ttk.Button(self.button_frame, text=text, command=command)
            if style:
                button.config(style=style)
            button.grid(row=0, column=column, padx=(0, 6))
            column += 1

        add("Encrypt", self.run_encrypt, "Accent.TButton")
        add("Decrypt", self.run_decrypt)
        for action in self.current.extra_actions:
            add(
                action.label,
                lambda a=action: self.run(
                    a.run, a_label=a.label, use_params=a.uses_params
                ),
            )

        self.button_frame.columnconfigure(column, weight=1)  # spacer
        column += 1
        add("Copy output", self.copy_output)
        add("Clear", self.clear_all)

    # ---------- running a cipher ----------

    def run_encrypt(self):
        self.run(self.current.encrypt, a_label="Encrypted")

    def run_decrypt(self):
        self.run(self.current.decrypt, a_label="Decrypted")

    def run(self, action, a_label="Done", use_params=True):
        text = self.input_text.get("1.0", "end-1c")

        if self.current.validate:
            problem = self.current.validate(text)
            if problem:
                self.fail(problem)
                return

        params = {}
        if use_params:
            try:
                params = self.current.coerce_params(
                    {key: var.get() for key, var in self.param_entries.items()}
                )
            except ValueError as exc:
                self.fail(str(exc))
                return

        try:
            result = action(text, params)
        except Exception as exc:  # a cipher module misbehaving shouldn't kill the app
            self.fail(f"{self.current.name} raised {type(exc).__name__}: {exc}")
            return

        self.set_output(result)
        self.set_status(f"{a_label} with {self.current.name}.")

    # ---------- little helpers ----------

    def set_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def set_status(self, message):
        self.status.config(foreground="#333")
        self.status_var.set(message)

    def fail(self, message):
        self.set_output("")
        self.status.config(foreground="#b00020")
        self.status_var.set(message)

    def copy_output(self):
        text = self.output_text.get("1.0", "end-1c")
        if not text:
            self.fail("Nothing to copy yet.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status("Output copied to clipboard.")

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.set_output("")
        self.set_status("Cleared.")


def main():
    root = tk.Tk()
    root.title("Cipher Toolkit")
    root.geometry("720x600")
    root.minsize(520, 460)

    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass

    if not ciphers.REGISTRY:
        messagebox.showerror(
            "Cipher Toolkit",
            "No ciphers were found in the ciphers/ folder.\n\n"
            "Each cipher module needs a module-level CIPHER object.",
        )
        root.destroy()
        return

    app = CipherApp(root)

    if ciphers.LOAD_ERRORS:
        app.fail(f"{len(ciphers.LOAD_ERRORS)} cipher module(s) failed to load.")
        messagebox.showwarning(
            "Some ciphers didn't load",
            "These modules were skipped:\n\n" + "\n".join(ciphers.LOAD_ERRORS),
        )

    root.mainloop()


if __name__ == "__main__":
    main()