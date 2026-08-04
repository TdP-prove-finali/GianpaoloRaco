import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self._page = page
        self._page.title = "Consulente Virtuale per il Mercato Calcistico"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.scroll = ft.ScrollMode.AUTO
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None

        # ---------------- Tab 1: Analisi Rosa ----------------
        self.dd_club = None
        self.btn_analizza_rosa = None
        self.txt_analisi_rosa = None

        # ---------------- Tab 2: Obiettivi Campagna ----------------
        self.tf_budget = None
        self.cb_ruolo_portiere = None
        self.cb_ruolo_difensore = None
        self.cb_ruolo_centrocampista = None
        self.cb_ruolo_attaccante = None
        self.tf_eta_min = None
        self.tf_eta_max = None
        self.dd_campionato_provenienza = None
        self.btn_imposta_obiettivi = None

        # ---------------- Tab 3: Giocatori Sottovalutati ----------------
        self.dd_ruolo_sottovalutati = None
        self.tf_prezzo_min = None
        self.tf_prezzo_max = None
        self.btn_cerca_sottovalutati = None
        self.txt_sottovalutati_result = None

        # ---------------- Tab 4: Sostituti Simili ----------------
        self.dd_giocatore = None
        self.tf_valore_max_sostituto = None
        self.sl_soglia_similarita = None
        self.btn_trova_sostituti = None
        self.txt_sostituti_result = None

        # ---------------- Tab 5: Piano di Mercato ----------------
        self.dd_club_piano = None
        self.tf_max_acquisti = None
        self.btn_genera_piano = None
        self.btn_confronta_scenari = None
        self.txt_piano_result = None

    def load_interface(self):
        title = ft.Text("Consulente Virtuale per il Mercato Calcistico", color="blue", size=24)
        self._page.controls.append(title)

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
            tabs=[
                self._build_tab_analisi_rosa(),
                self._build_tab_obiettivi_campagna(),
                self._build_tab_sottovalutati(),
                self._build_tab_sostituti_simili(),
                self._build_tab_piano_mercato(),
            ],
        )
        self._page.controls.append(tabs)
        self._page.update()

    def _build_tab_analisi_rosa(self):
        self.dd_club = ft.Dropdown(label="Club", width=300)
        self._controller.fillDDClub(self.dd_club)
        self.btn_analizza_rosa = ft.ElevatedButton(
            text="Analizza Rosa", on_click=self._controller.handleAnalizzaRosa, width=250)

        self.txt_analisi_rosa = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=350)

        content = ft.Column([
            ft.Row([self.dd_club, self.btn_analizza_rosa], alignment=ft.MainAxisAlignment.CENTER),
            self.txt_analisi_rosa,
        ])
        return ft.Tab(text="Analisi Rosa", content=content)

    def _build_tab_obiettivi_campagna(self):
        self.tf_budget = ft.TextField(label="Budget disponibile (€)", width=250, keyboard_type=ft.KeyboardType.NUMBER)

        self.cb_ruolo_portiere = ft.Checkbox(label="Portiere")
        self.cb_ruolo_difensore = ft.Checkbox(label="Difensore")
        self.cb_ruolo_centrocampista = ft.Checkbox(label="Centrocampista")
        self.cb_ruolo_attaccante = ft.Checkbox(label="Attaccante")

        self.tf_eta_min = ft.TextField(label="Età minima", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.tf_eta_max = ft.TextField(label="Età massima", width=120, keyboard_type=ft.KeyboardType.NUMBER)

        self.dd_campionato_provenienza = ft.Dropdown(label="Campionato di provenienza", width=300)
        self._controller.fillDDCampionato(self.dd_campionato_provenienza)

        self.btn_imposta_obiettivi = ft.ElevatedButton(
            text="Imposta Obiettivi Campagna", on_click=self._controller.handleImpostaObiettivi, width=250)

        content = ft.Column([
            ft.Row([self.tf_budget], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Ruoli da rafforzare"),
            ft.Row([self.cb_ruolo_portiere, self.cb_ruolo_difensore,
                    self.cb_ruolo_centrocampista, self.cb_ruolo_attaccante],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.tf_eta_min, self.tf_eta_max], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.dd_campionato_provenienza], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_imposta_obiettivi], alignment=ft.MainAxisAlignment.CENTER),
        ])
        return ft.Tab(text="Obiettivi Campagna", content=content)

    def _build_tab_sottovalutati(self):
        self.dd_ruolo_sottovalutati = ft.Dropdown(label="Ruolo", width=250)
        self._controller.fillDDRuolo(self.dd_ruolo_sottovalutati)

        self.tf_prezzo_min = ft.TextField(label="Prezzo minimo (€)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.tf_prezzo_max = ft.TextField(label="Prezzo massimo (€)", width=180, keyboard_type=ft.KeyboardType.NUMBER)

        self.btn_cerca_sottovalutati = ft.ElevatedButton(
            text="Cerca Sottovalutati", on_click=self._controller.handleCercaSottovalutati, width=250)

        self.txt_sottovalutati_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=350)

        content = ft.Column([
            ft.Row([self.dd_ruolo_sottovalutati, self.tf_prezzo_min, self.tf_prezzo_max],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_cerca_sottovalutati], alignment=ft.MainAxisAlignment.CENTER),
            self.txt_sottovalutati_result,
        ])
        return ft.Tab(text="Giocatori Sottovalutati", content=content)

    def _build_tab_sostituti_simili(self):
        self.dd_giocatore = ft.Dropdown(label="Giocatore", width=300)
        self._controller.fillDDGiocatore(self.dd_giocatore)

        self.tf_valore_max_sostituto = ft.TextField(
            label="Valore massimo sostituto (€)", width=220, keyboard_type=ft.KeyboardType.NUMBER)

        self.txt_soglia_similarita_value = ft.Text(value="0.50", width=50)
        self.sl_soglia_similarita = ft.Slider(
            min=0, max=1, divisions=20, value=0.5, width=300,
            on_change=self._handle_soglia_similarita_change)

        self.btn_trova_sostituti = ft.ElevatedButton(
            text="Trova Sostituti", on_click=self._controller.handleTrovaSostituti, width=250)

        self.txt_sostituti_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=350)

        content = ft.Column([
            ft.Row([self.dd_giocatore, self.tf_valore_max_sostituto], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text("Soglia di similarità"), self.sl_soglia_similarita, self.txt_soglia_similarita_value],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_trova_sostituti], alignment=ft.MainAxisAlignment.CENTER),
            self.txt_sostituti_result,
        ])
        return ft.Tab(text="Sostituti Simili", content=content)

    def _build_tab_piano_mercato(self):
        self.dd_club_piano = ft.Dropdown(label="Club", width=300)
        self._controller.fillDDClub(self.dd_club_piano)

        self.tf_max_acquisti = ft.TextField(
            label="Numero massimo acquisti", width=220, keyboard_type=ft.KeyboardType.NUMBER)

        self.btn_genera_piano = ft.ElevatedButton(
            text="Genera Piano Ottimale", on_click=self._controller.handleGeneraPiano, width=250)
        self.btn_confronta_scenari = ft.ElevatedButton(
            text="Confronta Scenari", on_click=self._controller.handleConfrontaScenari, width=250)

        self.txt_piano_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=350)

        content = ft.Column([
            ft.Row([self.dd_club_piano, self.tf_max_acquisti], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_genera_piano, self.btn_confronta_scenari], alignment=ft.MainAxisAlignment.CENTER),
            self.txt_piano_result,
        ])
        return ft.Tab(text="Piano di Mercato", content=content)

    def _handle_soglia_similarita_change(self, e):
        self.txt_soglia_similarita_value.value = f"{float(e.control.value):.2f}"
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()
