
from pathlib import Path
import json

import pandas as pd
import customtkinter as ctk

from PIL import Image


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATISTICS_DIR = PROJECT_ROOT / "results" / "statistique"
FIGURES_DIR = STATISTICS_DIR / "figures"
TABLES_DIR = STATISTICS_DIR / "tables"

REPORT_PATH = STATISTICS_DIR / "rapport_statistique.json"


class StatisticalView(ctk.CTkScrollableFrame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        # ====================================================
        # PAGE TITLE
        # ====================================================

        title = ctk.CTkLabel(
            self,
            text="📈 Statistical Analysis",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=0, column=0, pady=(20, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Statistical tests and significance analysis",
            font=ctk.CTkFont(size=15)
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        # ====================================================
        # CHECK RESULTS FOLDER
        # ====================================================

        if not STATISTICS_DIR.exists():
            self.show_message(
                row=2,
                message=(
                    "Statistical results folder not found.\n\n"
                    f"Expected path:\n{STATISTICS_DIR}"
                )
            )
            return

        # ====================================================
        # STATISTICAL TESTS
        # ====================================================

        self.create_test_section(
            row=2,
            title="Chi-Square Test (χ²)",
            keywords=["chi2", "chi_square", "chi-square"],
            null_hypothesis=(
                "H₀: Protocol type and label are independent."
            ),
            alternative_hypothesis=(
                "H₁: Protocol type and label are associated."
            )
        )

        self.create_test_section(
            row=3,
            title="ANOVA Test",
            keywords=["anova"],
            null_hypothesis=(
                "H₀: The means of all groups are equal."
            ),
            alternative_hypothesis=(
                "H₁: At least one group has a different mean."
            )
        )

        self.create_test_section(
            row=4,
            title="Levene Test",
            keywords=["levene"],
            null_hypothesis=(
                "H₀: The variances of the groups are equal."
            ),
            alternative_hypothesis=(
                "H₁: At least one group has a different variance."
            )
        )

        self.create_test_section(
            row=5,
            title="Kruskal-Wallis Test",
            keywords=["kruskal"],
            null_hypothesis=(
                "H₀: The groups have the same distribution."
            ),
            alternative_hypothesis=(
                "H₁: At least one group has a different distribution."
            )
        )

        # ====================================================
        # STATISTICAL TABLES
        # ====================================================

        self.create_tables_section(row=6)

        # ====================================================
        # FIGURES
        # ====================================================

        self.create_figures_section(row=7)

        # ====================================================
        # JSON REPORT
        # ====================================================

        self.create_json_report(row=8)


    # ========================================================
    # MESSAGE
    # ========================================================

    def show_message(self, row, message):

        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=15),
            justify="center"
        )

        label.grid(
            row=row,
            column=0,
            padx=20,
            pady=30
        )


    # ========================================================
    # TEST SECTION
    # ========================================================

    def create_test_section(
        self,
        row,
        title,
        keywords,
        null_hypothesis,
        alternative_hypothesis
    ):

        card = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=12
        )

        card.grid_columnconfigure(0, weight=1)

        # Test title
        test_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=22, weight="bold")
        )

        test_title.grid(
            row=0,
            column=0,
            pady=(20, 15)
        )

        # Hypotheses
        hypotheses = ctk.CTkLabel(
            card,
            text=(
                f"{null_hypothesis}\n\n"
                f"{alternative_hypothesis}"
            ),
            justify="left",
            font=ctk.CTkFont(size=14)
        )

        hypotheses.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="w"
        )

        # Search for matching CSV files
        matching_files = []

        if TABLES_DIR.exists():

            for csv_path in sorted(TABLES_DIR.glob("*.csv")):

                filename_lower = csv_path.name.lower()

                if any(keyword in filename_lower for keyword in keywords):
                    matching_files.append(csv_path)

        # Display matching CSV files
        if matching_files:

            current_row = 2

            for csv_path in matching_files:

                self.display_csv(
                    parent=card,
                    csv_path=csv_path,
                    row=current_row
                )

                current_row += 1

        else:

            message = ctk.CTkLabel(
                card,
                text=(
                    "No CSV result found for this test.\n\n"
                    f"Folder searched:\n{TABLES_DIR}"
                ),
                font=ctk.CTkFont(size=14)
            )

            message.grid(
                row=2,
                column=0,
                padx=25,
                pady=25
            )


    # ========================================================
    # DISPLAY CSV
    # ========================================================

    def display_csv(self, parent, csv_path, row):

        try:

            df = pd.read_csv(csv_path)

            # CSV title
            title = ctk.CTkLabel(
                parent,
                text=f"📄 {csv_path.name}",
                font=ctk.CTkFont(size=16, weight="bold")
            )

            title.grid(
                row=row,
                column=0,
                padx=20,
                pady=(15, 5),
                sticky="w"
            )

            # CSV data
            results_text = df.to_string(index=False)

            textbox = ctk.CTkTextbox(
                parent,
                height=180,
                font=ctk.CTkFont(size=13),
                wrap="none"
            )

            textbox.grid(
                row=row + 1,
                column=0,
                padx=20,
                pady=(5, 20),
                sticky="ew"
            )

            textbox.insert("1.0", results_text)
            textbox.configure(state="disabled")

        except Exception as error:

            error_label = ctk.CTkLabel(
                parent,
                text=f"Error reading {csv_path.name}:\n{error}",
                font=ctk.CTkFont(size=13)
            )

            error_label.grid(
                row=row,
                column=0,
                padx=20,
                pady=20
            )


    # ========================================================
    # ALL CSV TABLES
    # ========================================================

    def create_tables_section(self, row):

        card = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="📋 Statistical Tables",
            font=ctk.CTkFont(size=22, weight="bold")
        )

        title.grid(
            row=0,
            column=0,
            pady=20
        )

        if not TABLES_DIR.exists():

            self.show_message_in_card(
                card,
                "Tables folder not found.",
                row=1
            )
            return

        csv_files = sorted(TABLES_DIR.glob("*.csv"))

        if not csv_files:

            self.show_message_in_card(
                card,
                "No CSV tables found.",
                row=1
            )
            return

        current_row = 1

        for csv_path in csv_files:

            self.display_csv(
                parent=card,
                csv_path=csv_path,
                row=current_row
            )

            current_row += 2


    # ========================================================
    # FIGURES
    # ========================================================

    def create_figures_section(self, row):

        card = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="📊 Statistical Visualizations",
            font=ctk.CTkFont(size=22, weight="bold")
        )

        title.grid(
            row=0,
            column=0,
            pady=20
        )

        if not FIGURES_DIR.exists():

            self.show_message_in_card(
                card,
                "Figures folder not found.",
                row=1
            )
            return

        image_files = sorted(
            FIGURES_DIR.glob("*.png")
        )

        if not image_files:

            self.show_message_in_card(
                card,
                "No PNG figures found.",
                row=1
            )
            return

        current_row = 1

        for image_path in image_files:

            self.display_figure(
                parent=card,
                image_path=image_path,
                row=current_row
            )

            current_row += 2


    # ========================================================
    # DISPLAY FIGURE
    # ========================================================

    def display_figure(self, parent, image_path, row):

        try:

            image = Image.open(image_path)

            # Resize for interface
            max_width = 850
            max_height = 500

            image.thumbnail(
                (max_width, max_height),
                Image.Resampling.LANCZOS
            )

            ctk_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )

            # Figure title
            title = ctk.CTkLabel(
                parent,
                text=image_path.stem.replace("_", " ").title(),
                font=ctk.CTkFont(size=17, weight="bold")
            )

            title.grid(
                row=row,
                column=0,
                pady=(20, 10)
            )

            # Figure
            image_label = ctk.CTkLabel(
                parent,
                text="",
                image=ctk_image
            )

            image_label.grid(
                row=row + 1,
                column=0,
                padx=15,
                pady=(0, 20)
            )

            # Keep image reference
            image_label.image = ctk_image

        except Exception as error:

            error_label = ctk.CTkLabel(
                parent,
                text=f"Error loading figure {image_path.name}:\n{error}"
            )

            error_label.grid(
                row=row,
                column=0,
                pady=15
            )


    # ========================================================
    # JSON REPORT
    # ========================================================

    def create_json_report(self, row):

        card = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="📝 Statistical Report",
            font=ctk.CTkFont(size=22, weight="bold")
        )

        title.grid(
            row=0,
            column=0,
            pady=20
        )

        if not REPORT_PATH.exists():

            self.show_message_in_card(
                card,
                "JSON statistical report not found.",
                row=1
            )
            return

        try:

            with open(
                REPORT_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                report = json.load(file)

            report_text = json.dumps(
                report,
                indent=4,
                ensure_ascii=False
            )

            textbox = ctk.CTkTextbox(
                card,
                height=300,
                font=ctk.CTkFont(size=13)
            )

            textbox.grid(
                row=1,
                column=0,
                padx=20,
                pady=(5, 20),
                sticky="ew"
            )

            textbox.insert("1.0", report_text)
            textbox.configure(state="disabled")

        except Exception as error:

            self.show_message_in_card(
                card,
                f"Error reading JSON report:\n{error}",
                row=1
            )


    # ========================================================
    # MESSAGE INSIDE CARD
    # ========================================================

    def show_message_in_card(self, card, message, row):

        label = ctk.CTkLabel(
            card,
            text=message,
            font=ctk.CTkFont(size=14),
            justify="center"
        )

        label.grid(
            row=row,
            column=0,
            padx=20,
            pady=30
        )
