

from pathlib import Path

import pandas as pd
import customtkinter as ctk
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results" / "eda"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"



ctk.set_appearance_mode("dark")

COLOR_BACKGROUND = "#0F172A"
COLOR_CARD = "#1E293B"
COLOR_CARD_ALT = "#172033"
COLOR_ACCENT_BLUE = "#2563EB"
COLOR_ACCENT_GREEN = "#10B981"
COLOR_TEXT = "#E2E8F0"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_ERROR = "#EF4444"
COLOR_BORDER = "#334155"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 15, "bold")
FONT_NORMAL = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 11)



def load_csv(filename: str) -> pd.DataFrame | None:
    """
    Charge un fichier CSV depuis results/eda/tables.

    Retourne None si le fichier est absent, vide ou illisible.
    """
    filepath = TABLES_DIR / filename

    if not filepath.exists():
        print(f"⚠ Fichier CSV absent : {filepath}")
        return None

    try:
        dataframe = pd.read_csv(filepath, encoding="utf-8-sig")

        if dataframe.empty:
            print(f"⚠ Fichier CSV vide : {filepath}")
            return None

        return dataframe

    except Exception as exception:
        print(f"⚠ Impossible de lire le fichier '{filepath}' : {exception}")
        return None


def load_text(filename: str) -> str | None:
    """
    Charge un fichier texte depuis results/eda/reports.
    """
    filepath = REPORTS_DIR / filename

    if not filepath.exists():
        print(f"⚠ Fichier texte absent : {filepath}")
        return None

    try:
        return filepath.read_text(encoding="utf-8")

    except Exception as exception:
        print(f"⚠ Impossible de lire le fichier '{filepath}' : {exception}")
        return None


def display_dataframe(
    parent,
    dataframe: pd.DataFrame | None,
    height: int = 420
):
    """
    Affiche un DataFrame dans un tableau avec défilement horizontal
    et vertical.

    CustomTkinter ne prenant pas en charge orientation="both",
    cette fonction utilise un CTkFrame contenant un Canvas Tkinter
    et deux Scrollbar Tkinter.
    """
    import tkinter as tk

    container = ctk.CTkFrame(
        parent,
        fg_color=COLOR_CARD,
        corner_radius=12
    )
    container.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    if dataframe is None or dataframe.empty:
        ctk.CTkLabel(
            container,
            text=(
                "Résultat EDA non disponible.\n"
                "Veuillez d'abord exécuter l'analyse EDA."
            ),
            font=FONT_NORMAL,
            text_color=COLOR_ERROR,
            justify="center"
        ).pack(expand=True, pady=40)

        return container

    # Évite les index incohérents sans modifier le DataFrame d'origine.
    dataframe = dataframe.reset_index(drop=True)

    table_wrapper = ctk.CTkFrame(
        container,
        fg_color=COLOR_CARD_ALT,
        corner_radius=8
    )
    table_wrapper.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    table_wrapper.grid_rowconfigure(0, weight=1)
    table_wrapper.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(
        table_wrapper,
        background=COLOR_CARD_ALT,
        highlightthickness=0,
        height=height
    )
    canvas.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    vertical_scrollbar = tk.Scrollbar(
        table_wrapper,
        orient="vertical",
        command=canvas.yview
    )
    vertical_scrollbar.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    horizontal_scrollbar = tk.Scrollbar(
        table_wrapper,
        orient="horizontal",
        command=canvas.xview
    )
    horizontal_scrollbar.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    canvas.configure(
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    table_frame = ctk.CTkFrame(
        canvas,
        fg_color=COLOR_CARD_ALT,
        corner_radius=0
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=table_frame,
        anchor="nw"
    )

    column_width = 160

    for column_index in range(len(dataframe.columns)):
        table_frame.grid_columnconfigure(
            column_index,
            minsize=column_width,
            weight=0
        )

    # En-têtes
    for column_index, column_name in enumerate(dataframe.columns):
        header_cell = ctk.CTkFrame(
            table_frame,
            fg_color=COLOR_CARD,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER
        )
        header_cell.grid(
            row=0,
            column=column_index,
            sticky="nsew"
        )

        ctk.CTkLabel(
            header_cell,
            text=str(column_name),
            font=FONT_SUBTITLE,
            text_color=COLOR_ACCENT_BLUE,
            width=column_width,
            anchor="w"
        ).pack(
            fill="both",
            padx=8,
            pady=7
        )

    # Données
    for row_index, row_values in enumerate(
        dataframe.itertuples(index=False, name=None),
        start=1
    ):
        row_color = (
            COLOR_CARD
            if row_index % 2 == 0
            else COLOR_CARD_ALT
        )

        for column_index, value in enumerate(row_values):
            if pd.isna(value):
                displayed_value = ""
            else:
                displayed_value = str(value)

            cell = ctk.CTkFrame(
                table_frame,
                fg_color=row_color,
                corner_radius=0,
                border_width=1,
                border_color=COLOR_BORDER
            )
            cell.grid(
                row=row_index,
                column=column_index,
                sticky="nsew"
            )

            ctk.CTkLabel(
                cell,
                text=displayed_value,
                font=FONT_NORMAL,
                text_color=COLOR_TEXT,
                width=column_width,
                anchor="w"
            ).pack(
                fill="both",
                padx=8,
                pady=5
            )

    def update_scroll_region(_event=None):
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    def resize_table_window(event):
        """
        Étend le tableau jusqu'à la largeur visible lorsque son contenu
        est plus étroit que le canvas, sans supprimer le défilement
        horizontal lorsqu'il est plus large.
        """
        requested_width = table_frame.winfo_reqwidth()
        canvas.itemconfigure(
            canvas_window,
            width=max(event.width, requested_width)
        )

    table_frame.bind(
        "<Configure>",
        update_scroll_region
    )
    canvas.bind(
        "<Configure>",
        resize_table_window
    )

    def on_mousewheel(event):
        canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    def on_shift_mousewheel(event):
        canvas.xview_scroll(
            int(-event.delta / 120),
            "units"
        )

    def bind_mousewheel(_event=None):
        canvas.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )
        canvas.bind_all(
            "<Shift-MouseWheel>",
            on_shift_mousewheel
        )

    def unbind_mousewheel(_event=None):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")

    canvas.bind(
        "<Enter>",
        bind_mousewheel
    )
    canvas.bind(
        "<Leave>",
        unbind_mousewheel
    )

    update_scroll_region()

    return container



def display_image(parent, filename: str, max_width: int = 900, max_height: int = 520):
    """
    Affiche une image PNG depuis results/eda/figures.

    L'image est redimensionnée en conservant ses proportions.
    Une référence à CTkImage est conservée pour éviter le garbage collection.
    """
    filepath = FIGURES_DIR / filename

    container = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=12)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    if not filepath.exists():
        ctk.CTkLabel(
            container,
            text=f"Figure non disponible :\n{filepath.name}\n\n"
                 "Veuillez d'abord exécuter l'analyse EDA.",
            font=FONT_NORMAL,
            text_color=COLOR_ERROR,
            justify="center"
        ).pack(expand=True, pady=40)

        return container

    try:
        image = Image.open(filepath)
        image_width, image_height = image.size

        scale = min(
            max_width / image_width,
            max_height / image_height,
            1.0
        )

        display_width = max(1, int(image_width * scale))
        display_height = max(1, int(image_height * scale))

        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(display_width, display_height)
        )

        # Référence conservée pour éviter la destruction par le garbage collector
        container._ctk_image_reference = ctk_image

        ctk.CTkLabel(
            container,
            text="",
            image=ctk_image
        ).pack(expand=True, pady=10)

        ctk.CTkLabel(
            container,
            text=filepath.name,
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 10))

    except Exception as exception:
        ctk.CTkLabel(
            container,
            text=f"Impossible d'afficher l'image :\n{filepath.name}\n\n{exception}",
            font=FONT_NORMAL,
            text_color=COLOR_ERROR,
            justify="center"
        ).pack(expand=True, pady=40)

    return container


def display_report(parent, filename: str = "eda_summary.txt"):
    """
    Affiche le contenu d'un rapport texte dans une zone scrollable.
    """
    container = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=12)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    report_text = load_text(filename)

    if report_text is None:
        ctk.CTkLabel(
            container,
            text="Rapport EDA non disponible.\nVeuillez d'abord exécuter l'analyse EDA.",
            font=FONT_NORMAL,
            text_color=COLOR_ERROR,
            justify="center"
        ).pack(expand=True, pady=40)

        return container

    textbox = ctk.CTkTextbox(
        container,
        font=FONT_MONO,
        fg_color=COLOR_CARD_ALT,
        text_color=COLOR_TEXT,
        wrap="word"
    )
    textbox.pack(fill="both", expand=True, padx=10, pady=10)
    textbox.insert("0.0", report_text)
    textbox.configure(state="disabled")

    return container


# ---------------------------------------------------------------------------
# Classe principale
# ---------------------------------------------------------------------------

class EDAViewer(ctk.CTkFrame):
    """
    Interface d'affichage des résultats EDA.

    Cette classe ne calcule aucune statistique.
    Elle lit uniquement les fichiers générés par le notebook EDA.
    """

    PAGES = [
        "EDA Overview",
        "Data Quality",
        "Statistics",
        "Target Analysis",
        "Categorical Analysis",
        "Numeric Distributions",
        "Correlation Analysis",
        "Class Patterns",
        "Outliers",
        "EDA Report"
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLOR_BACKGROUND, **kwargs)

        self.current_page = "EDA Overview"
        self.page_frames = {}

        self._build_layout()
        self.show_page("EDA Overview")

    # -----------------------------------------------------------------------
    # Construction de l'interface
    # -----------------------------------------------------------------------

    def _build_layout(self):
        """
        Construit la barre latérale et la zone principale.
        """
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        """
        Construit le menu de navigation.
        """
        sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=COLOR_CARD
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(len(self.PAGES), weight=1)

        ctk.CTkLabel(
            sidebar,
            text="NETWORK IDS",
            font=FONT_TITLE,
            text_color=COLOR_ACCENT_BLUE
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            sidebar,
            text="EDA Results Viewer",
            font=FONT_NORMAL,
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 25))

        for page_name in self.PAGES:
            button = ctk.CTkButton(
                sidebar,
                text=page_name,
                font=FONT_NORMAL,
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLOR_CARD_ALT,
                text_color=COLOR_TEXT,
                anchor="w",
                command=lambda name=page_name: self.show_page(name)
            )
            button.pack(fill="x", padx=15, pady=4)

        refresh_button = ctk.CTkButton(
            sidebar,
            text="🔄 Refresh Results",
            font=FONT_NORMAL,
            height=42,
            corner_radius=8,
            fg_color=COLOR_ACCENT_GREEN,
            hover_color="#059669",
            text_color="#04150F",
            command=self.refresh_results
        )
        refresh_button.pack(side="bottom", fill="x", padx=15, pady=20)

    def _build_main_area(self):
        """
        Construit la zone principale d'affichage.
        """
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")

        self.header_frame = ctk.CTkFrame(
            self.main_area,
            height=70,
            fg_color=COLOR_CARD,
            corner_radius=0
        )
        self.header_frame.pack(fill="x")

        self.page_title = ctk.CTkLabel(
            self.header_frame,
            text="EDA Overview",
            font=FONT_TITLE,
            text_color=COLOR_TEXT
        )
        self.page_title.pack(side="left", padx=25, pady=18)

        self.content_area = ctk.CTkFrame(
            self.main_area,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0
        )
        self.content_area.pack(fill="both", expand=True)

    # -----------------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------------

    def show_page(self, page_name: str):
        """
        Affiche une page EDA et recharge uniquement son contenu.
        """
        if page_name not in self.PAGES:
            return

        self.current_page = page_name
        self.page_title.configure(text=page_name)

        # Suppression de l'ancienne page
        for widget in self.content_area.winfo_children():
            widget.destroy()

        page_builders = {
            "EDA Overview": self._build_overview_page,
            "Data Quality": self._build_data_quality_page,
            "Statistics": self._build_statistics_page,
            "Target Analysis": self._build_target_analysis_page,
            "Categorical Analysis": self._build_categorical_analysis_page,
            "Numeric Distributions": self._build_numeric_distributions_page,
            "Correlation Analysis": self._build_correlation_page,
            "Class Patterns": self._build_class_patterns_page,
            "Outliers": self._build_outliers_page,
            "EDA Report": self._build_report_page
        }

        builder = page_builders.get(page_name)

        if builder:
            builder()

    def refresh_results(self):
        """
        Recharge uniquement la page actuellement affichée.

        Cette fonction :
        - ne recalcule pas l'EDA ;
        - ne modifie pas les fichiers de résultats ;
        - relit uniquement les fichiers présents dans results/eda/.
        """
        self.show_page(self.current_page)

    # -----------------------------------------------------------------------
    # Pages
    # -----------------------------------------------------------------------

    def _add_section_title(self, parent, text: str):
        """
        Ajoute un titre de section.
        """
        ctk.CTkLabel(
            parent,
            text=text,
            font=FONT_SUBTITLE,
            text_color=COLOR_ACCENT_GREEN,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(15, 5))

    def _build_overview_page(self):
        """
        Page : EDA Overview.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        dataset_shape = load_csv("dataset_shape.csv")
        missing_values = load_csv("missing_values.csv")
        duplicates_report = load_csv("duplicates_report.csv")
        data_types = load_csv("data_types.csv")
        target_distribution = load_csv("target_distribution.csv")

        cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        cards_frame.pack(fill="x", padx=15, pady=15)

        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def get_shape_value(keyword):
            if dataset_shape is None:
                return "N/A"

            filtered = dataset_shape[
                dataset_shape["element"].str.contains(keyword, case=False, na=False)
            ]

            if filtered.empty:
                return "N/A"

            return str(filtered.iloc[0]["valeur"])

        def get_missing_total():
            if missing_values is None:
                return "N/A"

            if "valeurs_manquantes" in missing_values.columns:
                return str(int(missing_values["valeurs_manquantes"].sum()))

            return "N/A"

        def get_duplicates_total():
            if duplicates_report is None:
                return "N/A"

            filtered = duplicates_report[
                duplicates_report["indicateur"].str.contains(
                    "nombre_de_doublons", case=False, na=False
                )
            ]

            if filtered.empty:
                return "N/A"

            return str(filtered.iloc[0]["valeur"])

        def get_class_count():
            if target_distribution is None:
                return "N/A"

            return str(len(target_distribution))

        def get_numeric_count():
            if data_types is None:
                return "N/A"

            numeric_types = ["int64", "float64", "int32", "float32"]
            return str(data_types["type"].isin(numeric_types).sum())

        def get_categorical_count():
            if data_types is None:
                return "N/A"

            categorical_types = ["object", "category", "bool"]
            return str(data_types["type"].isin(categorical_types).sum())

        cards = [
            ("Lignes", get_shape_value("ligne"), COLOR_ACCENT_BLUE),
            ("Colonnes", get_shape_value("colonnes"), COLOR_ACCENT_GREEN),
            ("Valeurs manquantes", get_missing_total(), COLOR_ACCENT_BLUE),
            ("Doublons", get_duplicates_total(), COLOR_ACCENT_GREEN),
            ("Variables numériques", get_numeric_count(), COLOR_ACCENT_BLUE),
            ("Variables catégorielles", get_categorical_count(), COLOR_ACCENT_GREEN),
            ("Classes cibles", get_class_count(), COLOR_ACCENT_BLUE)
        ]

        for index, (title, value, color) in enumerate(cards):
            row = index // 4
            column = index % 4

            card = ctk.CTkFrame(
                cards_frame,
                fg_color=COLOR_CARD,
                corner_radius=12,
                border_width=1,
                border_color=COLOR_BORDER
            )
            card.grid(
                row=row,
                column=column,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED
            ).pack(pady=(15, 5))

            ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 24, "bold"),
                text_color=color
            ).pack(pady=(0, 15))

        if target_distribution is not None:
            self._add_section_title(page, "Distribution de la variable cible")
            display_dataframe(page, target_distribution)

        if missing_values is not None:
            self._add_section_title(page, "Valeurs manquantes par colonne")
            display_dataframe(page, missing_values)

    def _build_data_quality_page(self):
        """
        Page : Data Quality.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        files = [
            ("Dimensions du dataset", "dataset_shape.csv"),
            ("Valeurs manquantes", "missing_values.csv"),
            ("Doublons", "duplicates_report.csv"),
            ("Types de données", "data_types.csv")
        ]

        for title, filename in files:
            self._add_section_title(page, title)
            display_dataframe(page, load_csv(filename))

    def _build_statistics_page(self):
        """
        Page : Statistics.
        """
        page = ctk.CTkFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        selector_frame = ctk.CTkFrame(
            page,
            fg_color=COLOR_CARD,
            corner_radius=12
        )
        selector_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            selector_frame,
            text="Sélectionner un tableau statistique :",
            font=FONT_NORMAL,
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=15)

        table_selector = ctk.CTkOptionMenu(
            selector_frame,
            values=[
                "descriptive_statistics.csv",
                "numeric_summary.csv",
                "categorical_summary.csv"
            ],
            font=FONT_NORMAL,
            fg_color=COLOR_CARD_ALT,
            button_color=COLOR_ACCENT_BLUE,
            button_hover_color="#1D4ED8",
            command=lambda filename: self._show_selected_statistics(
                page, filename
            )
        )
        table_selector.pack(side="left", padx=15, pady=10)

        self.statistics_container = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )
        self.statistics_container.pack(fill="both", expand=True)

        self._show_selected_statistics(
            page,
            "descriptive_statistics.csv"
        )

    def _show_selected_statistics(self, page, filename: str):
        """
        Affiche le tableau statistique sélectionné.
        """
        for widget in self.statistics_container.winfo_children():
            widget.destroy()

        dataframe = load_csv(filename)

        if dataframe is not None:
            dataframe = dataframe.reset_index(drop=True)

        display_dataframe(self.statistics_container, dataframe)

    def _build_target_analysis_page(self):
        """
        Page : Target Analysis.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        self._add_section_title(page, "Distribution de la variable cible")
        display_dataframe(page, load_csv("target_distribution.csv"))

        self._add_section_title(page, "Graphique en barres")
        display_image(page, "target_distribution_bar.png")

        self._add_section_title(page, "Répartition des classes")
        display_image(page, "target_distribution_pie.png")

    def _build_categorical_analysis_page(self):
        """
        Page : Categorical Analysis.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        categorical_tables = [
            ("Protocoles", "protocol_type_frequency.csv"),
            ("Services", "service_frequency.csv"),
            ("Flags", "flag_frequency.csv")
        ]

        categorical_images = [
            ("Fréquence des protocoles", "protocol_type_frequency.png"),
            ("Top 15 services", "service_top15_frequency.png"),
            ("Fréquence des flags", "flag_frequency.png")
        ]

        for title, filename in categorical_tables:
            self._add_section_title(page, title)
            display_dataframe(page, load_csv(filename))

        for title, filename in categorical_images:
            self._add_section_title(page, title)
            display_image(page, filename)

    def _build_numeric_distributions_page(self):
        """
        Page : Numeric Distributions.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        images = [
            "numeric_distributions.png",
            "duration_distribution.png",
            "duration_log_distribution.png",
            "src_bytes_distribution.png",
            "src_bytes_log_distribution.png",
            "dst_bytes_distribution.png",
            "dst_bytes_log_distribution.png"
        ]

        for filename in images:
            display_image(page, filename)

    def _build_correlation_page(self):
        """
        Page : Correlation Analysis.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        self._add_section_title(page, "Corrélations fortes")
        display_dataframe(page, load_csv("strong_correlations.csv"))

        self._add_section_title(page, "Matrice de corrélation")
        display_image(page, "correlation_heatmap.png")

    def _build_class_patterns_page(self):
        """
        Page : Class Patterns.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        self._add_section_title(page, "Patterns numériques par classe")
        display_dataframe(page, load_csv("class_patterns.csv"))

        self._add_section_title(page, "Moyennes par classe")
        display_image(page, "numeric_features_by_class.png")

        self._add_section_title(page, "Comparaison des classes")
        display_image(page, "class_comparison_boxplots.png")

    def _build_outliers_page(self):
        """
        Page : Outliers.
        """
        page = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        self._add_section_title(page, "Rapport des outliers IQR")
        display_dataframe(page, load_csv("outliers_report.csv"))

        self._add_section_title(page, "Boxplots des outliers")
        display_image(page, "outliers_boxplots.png")

    def _build_report_page(self):
        """
        Page : EDA Report.
        """
        page = ctk.CTkFrame(
            self.content_area,
            fg_color=COLOR_BACKGROUND
        )
        page.pack(fill="both", expand=True)

        display_report(page, "eda_summary.txt")