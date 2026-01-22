"""
Camera Spoofer - Aplicativo Principal
Interface gráfica para renomear câmeras virtuais com nomes de câmeras reais.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional

from admin_utils import is_admin, ensure_admin_or_exit
from camera_utils import (
    get_all_cameras, 
    rename_camera_in_registry, 
    restore_camera_name,
    get_backed_up_cameras
)
from real_cameras import (
    get_all_real_camera_names, 
    get_real_cameras_by_brand,
    is_virtual_camera,
    get_suggested_name
)


# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CameraSpoofApp(ctk.CTk):
    """Aplicativo principal para renomear câmeras virtuais."""
    
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("📷 Camera Spoofer")
        self.geometry("780x920")
        self.minsize(750, 850)
        
        # Dados
        self.cameras = []
        self.selected_camera = None
        
        # Paleta de cores premium (roxo/ciano gradiente)
        self.colors = {
            'bg': '#0f0f1a',           # Fundo muito escuro
            'card': '#1a1a2e',          # Cards
            'card_hover': '#252542',    # Card hover
            'accent': '#6366f1',        # Roxo vibrante (indigo)
            'accent_light': '#818cf8',  # Roxo claro
            'success': '#10b981',       # Verde esmeralda
            'success_hover': '#059669', # Verde escuro
            'warning': '#f59e0b',       # Âmbar
            'danger': '#ef4444',        # Vermelho
            'text': '#f8fafc',          # Texto branco
            'text_muted': '#94a3b8',    # Texto cinza
            'border': '#334155',        # Bordas
            'gradient_start': '#6366f1', # Roxo
            'gradient_end': '#06b6d4',   # Ciano
        }
        
        self.configure(fg_color=self.colors['bg'])
        
        # Cria interface
        self._create_widgets()
        
        # Carrega câmeras
        self.after(100, self._load_cameras_async)
    
    def _create_widgets(self):
        """Cria todos os widgets da interface."""
        
        # Container principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header com visual premium
        title_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=20, border_width=1, border_color=self.colors['border'])
        title_frame.pack(fill="x", pady=(0, 12))
        
        # Container interno do header
        header_inner = ctk.CTkFrame(title_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=15)
        
        # Título principal com estilo
        title_label = ctk.CTkLabel(
            header_inner,
            text="🎭 Camera Spoofer",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.pack()
        
        # Linha decorativa (simula gradiente)
        accent_line = ctk.CTkFrame(header_inner, fg_color=self.colors['accent'], height=3, corner_radius=2)
        accent_line.pack(fill="x", pady=(8, 8), padx=100)
        
        subtitle = ctk.CTkLabel(
            header_inner,
            text="Gerencie os nomes das suas câmeras com facilidade",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_muted']
        )
        subtitle.pack()
        
        # Status de admin
        admin_status = "✅ Administrador" if is_admin() else "⚠️ Sem privilégios de Admin"
        admin_color = self.colors['success'] if is_admin() else self.colors['warning']
        
        self.admin_label = ctk.CTkLabel(
            header_inner,
            text=admin_status,
            font=ctk.CTkFont(size=12),
            text_color=admin_color
        )
        self.admin_label.pack(pady=(8, 0))
        
        # Seção de câmeras detectadas
        cameras_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=16, border_width=1, border_color=self.colors['border'])
        cameras_frame.pack(fill="both", expand=True, pady=(0, 12))
        
        cameras_label = ctk.CTkLabel(
            cameras_frame,
            text="Câmeras Detectadas",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors['text']
        )
        cameras_label.pack(pady=(12, 8), padx=15, anchor="w")
        
        # Lista de câmeras com visual melhorado
        self.cameras_listbox = ctk.CTkScrollableFrame(
            cameras_frame,
            height=160,
            fg_color=self.colors['bg'],
            corner_radius=12
        )
        self.cameras_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        
        # Botão de atualizar com estilo
        refresh_btn = ctk.CTkButton(
            cameras_frame,
            text="↻  Atualizar Lista",
            command=self._load_cameras_async,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_light'],
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.pack(pady=(0, 10))
        
        # Seção de renomeação
        rename_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=16, border_width=1, border_color=self.colors['border'])
        rename_frame.pack(fill="x", pady=(0, 12))
        
        rename_label = ctk.CTkLabel(
            rename_frame,
            text="📝  Renomear Câmera",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors['text']
        )
        rename_label.pack(pady=(12, 8), padx=15, anchor="w")
        
        # Dropdown para novo nome
        new_name_frame = ctk.CTkFrame(rename_frame, fg_color="transparent")
        new_name_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        new_name_label = ctk.CTkLabel(
            new_name_frame,
            text="Selecione um nome de câmera real:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_muted']
        )
        new_name_label.pack(anchor="w", pady=(0, 4))
        
        # Combobox com nomes de câmeras reais
        self.real_camera_var = ctk.StringVar(value=get_suggested_name())
        self.real_camera_combo = ctk.CTkComboBox(
            new_name_frame,
            values=get_all_real_camera_names(),
            variable=self.real_camera_var,
            width=400,
            height=38,
            corner_radius=10,
            fg_color=self.colors['bg'],
            border_color=self.colors['border'],
            button_color=self.colors['accent'],
            button_hover_color=self.colors['accent_light'],
            dropdown_fg_color=self.colors['card'],
            dropdown_hover_color=self.colors['accent'],
            font=ctk.CTkFont(size=13)
        )
        self.real_camera_combo.pack(fill="x", pady=(0, 10))
        
        # Card para opção de nome personalizado
        custom_card = ctk.CTkFrame(new_name_frame, fg_color=self.colors['bg'], corner_radius=10)
        custom_card.pack(fill="x", pady=(0, 5))
        
        custom_inner = ctk.CTkFrame(custom_card, fg_color="transparent")
        custom_inner.pack(fill="x", padx=12, pady=10)
        
        # Checkbox para usar nome personalizado
        self.use_custom_var = ctk.BooleanVar(value=False)
        self.custom_check = ctk.CTkCheckBox(
            custom_inner,
            text="  Usar nome personalizado",
            variable=self.use_custom_var,
            command=self._toggle_custom_name,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_light'],
            border_color=self.colors['border'],
            checkmark_color=self.colors['text']
        )
        self.custom_check.pack(anchor="w", pady=(0, 8))
        
        # Campo de entrada para nome personalizado
        self.custom_name_var = ctk.StringVar(value="")
        self.custom_name_entry = ctk.CTkEntry(
            custom_inner,
            textvariable=self.custom_name_var,
            placeholder_text="Digite qualquer nome aqui...",
            height=38,
            corner_radius=10,
            fg_color=self.colors['card'],
            border_color=self.colors['border'],
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.custom_name_entry.pack(fill="x")
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(rename_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=15)
        
        self.rename_btn = ctk.CTkButton(
            buttons_frame,
            text="✔  Renomear Selecionada",
            command=self._rename_camera,
            fg_color=self.colors['success'],
            hover_color=self.colors['success_hover'],
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled"
        )
        self.rename_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
        
        self.restore_btn = ctk.CTkButton(
            buttons_frame,
            text="↩  Restaurar Original",
            command=self._restore_camera,
            fg_color="transparent",
            hover_color=self.colors['card_hover'],
            border_width=2,
            border_color=self.colors['accent'],
            text_color=self.colors['accent_light'],
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled"
        )
        self.restore_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))
        
        # Status bar
        self.status_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        self.status_frame.pack(fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="💡 Selecione uma câmera para renomear",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_muted']
        )
        self.status_label.pack(pady=8)
    
    def _load_cameras_async(self):
        """Carrega câmeras em thread separada."""
        # Mostra status de carregando na barra de status
        self._update_status("🔍 Buscando câmeras...", "info")
        
        # Limpa a lista atual
        for widget in self.cameras_listbox.winfo_children():
            widget.destroy()
        
        # Adiciona label de carregando na lista
        loading = ctk.CTkLabel(
            self.cameras_listbox,
            text="⏳ Carregando...",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        loading.pack(pady=30)
        
        def load():
            self.cameras = get_all_cameras()
            try:
                self.after(0, self._update_cameras_list)
            except Exception:
                pass
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _update_cameras_list(self):
        """Atualiza a lista de câmeras na interface."""
        # Limpa lista anterior (incluindo o loading)
        for widget in self.cameras_listbox.winfo_children():
            widget.destroy()
        
        if not self.cameras:
            no_cameras_label = ctk.CTkLabel(
                self.cameras_listbox,
                text="❌ Nenhuma câmera encontrada\n\n💡 Dica: Abra o OBS e clique em\n'Ferramentas → Iniciar Câmera Virtual'",
                font=ctk.CTkFont(size=14),
                text_color="#888888",
                justify="center"
            )
            no_cameras_label.pack(pady=30)
            self._update_status("Nenhuma câmera detectada no sistema", "warning")
            return
        
        # Adiciona cada câmera
        for i, camera in enumerate(self.cameras):
            self._create_camera_item(camera, i)
        
        # Verifica backups e habilita botão de restaurar
        self._check_and_enable_restore()
        
        self._update_status(f"✅ {len(self.cameras)} câmeras encontradas - Clique em 'Selecionar' para renomear", "success")
    
    def _create_camera_item(self, camera: dict, index: int):
        """Cria um item de câmera na lista."""
        item_frame = ctk.CTkFrame(
            self.cameras_listbox,
            fg_color=self.colors['card'],
            corner_radius=10,
            border_width=1,
            border_color=self.colors['border']
        )
        item_frame.pack(fill="x", pady=4, padx=2)
        
        # Frame interno
        inner_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=12, pady=10)
        
        # Nome da câmera
        name_label = ctk.CTkLabel(
            inner_frame,
            text=camera['name'],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors['text']
        )
        name_label.pack(side="left")
        
        # Botão de selecionar com estilo premium
        select_btn = ctk.CTkButton(
            inner_frame,
            text="Selecionar",
            width=100,
            height=32,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_light'],
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda c=camera: self._select_camera(c)
        )
        select_btn.pack(side="right")
    
    def _select_camera(self, camera: dict):
        """Seleciona uma câmera para renomeação."""
        self.selected_camera = camera
        self.rename_btn.configure(state="normal")
        self._update_status(f"📷 Selecionada: {camera['name']}", "info")
    
    def _rename_camera(self):
        """Renomeia a câmera selecionada."""
        if not self.selected_camera:
            messagebox.showwarning("Aviso", "Selecione uma câmera primeiro!")
            return
        
        # Obtém o nome (personalizado ou da lista)
        if self.use_custom_var.get():
            new_name = self.custom_name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Aviso", "Digite um nome personalizado!")
                return
        else:
            new_name = self.real_camera_var.get()
            if not new_name:
                messagebox.showwarning("Aviso", "Escolha um nome de câmera!")
                return
        
        old_name = self.selected_camera['name']
        
        # Confirmação
        if not messagebox.askyesno(
            "Confirmar Renomeação",
            f"Renomear:\n\n'{old_name}'\n\npara:\n\n'{new_name}'\n\n"
            "Um backup será criado automaticamente."
        ):
            return
        
        self._update_status("⏳ Renomeando câmera...", "info")
        self.update()
        
        success, message = rename_camera_in_registry(old_name, new_name)
        
        if success:
            self._update_status(f"✅ {message}", "success")
            messagebox.showinfo("Sucesso", message + "\n\nReinicie os aplicativos para ver a mudança.")
            self._load_cameras_async()
        else:
            self._update_status(f"❌ {message}", "error")
            messagebox.showerror("Erro", message)
    
    def _restore_camera(self):
        """Restaura o nome original de uma câmera."""
        backed_up = get_backed_up_cameras()
        
        if not backed_up:
            messagebox.showinfo("Info", "Nenhum backup encontrado.")
            return
        
        # Mostra lista de backups para restaurar
        restore_window = ctk.CTkToplevel(self)
        restore_window.title("Restaurar Câmera")
        restore_window.geometry("400x300")
        restore_window.configure(fg_color=self.colors['bg'])
        restore_window.transient(self)
        restore_window.grab_set()
        
        label = ctk.CTkLabel(
            restore_window,
            text="Selecione uma câmera para restaurar:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=15)
        
        listbox = ctk.CTkScrollableFrame(
            restore_window,
            fg_color=self.colors['card'],
            corner_radius=10
        )
        listbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for camera_name in backed_up:
            btn = ctk.CTkButton(
                listbox,
                text=camera_name,
                fg_color=self.colors['accent'],
                hover_color="#1a4a7a",
                command=lambda n=camera_name, w=restore_window: self._do_restore(n, w)
            )
            btn.pack(fill="x", pady=3)
    
    def _do_restore(self, camera_name: str, window):
        """Executa a restauração de uma câmera."""
        window.destroy()
        
        self._update_status("⏳ Restaurando nome original...", "info")
        self.update()
        
        success, message = restore_camera_name(camera_name)
        
        if success:
            self._update_status(f"✅ {message}", "success")
            messagebox.showinfo("Sucesso", message)
            self._load_cameras_async()
        else:
            self._update_status(f"❌ {message}", "error")
            messagebox.showerror("Erro", message)
    
    def _update_status(self, message: str, status_type: str = "info"):
        """Atualiza a barra de status."""
        colors = {
            "info": "#888888",
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['danger']
        }
        self.status_label.configure(text=message, text_color=colors.get(status_type, "#888888"))
    
    def _toggle_custom_name(self):
        """Alterna entre modo preset e modo personalizado."""
        if self.use_custom_var.get():
            self.custom_name_entry.configure(state="normal")
            self.real_camera_combo.configure(state="disabled")
        else:
            self.custom_name_entry.configure(state="disabled")
            self.real_camera_combo.configure(state="normal")
    
    def _check_and_enable_restore(self):
        """Verifica se existem backups e habilita o botão de restaurar."""
        backed_up = get_backed_up_cameras()
        if backed_up:
            self.restore_btn.configure(state="normal")
        else:
            self.restore_btn.configure(state="disabled")


def main():
    """Função principal."""
    # Verifica privilégios de admin
    if not is_admin():
        # Mostra aviso mas permite continuar
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askyesno(
            "Privilégios de Administrador",
            "Este programa funciona melhor com privilégios de administrador.\n\n"
            "Deseja executar como administrador?\n\n"
            "(Clique 'Não' para continuar sem admin - funcionalidade limitada)"
        )
        root.destroy()
        
        if result:
            ensure_admin_or_exit()
    
    # Inicia aplicativo
    app = CameraSpoofApp()
    app.mainloop()


if __name__ == "__main__":
    main()
