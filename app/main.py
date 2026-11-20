
import customtkinter as ctk

from eda_view import EDAView
from statistical_view import StatisticalView


class NetworkIDSApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Network Intrusion Detection System")
        self.geometry("1200x750")
        self.minsize(900, 600)

        # Dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==============================
        # SIDEBAR
        # ==============================
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_rowconfigure(5, weight=1)

        # Project title
        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="🛡 NETWORK IDS",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        self.title_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(30, 10)
        )

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="NSL-KDD Data Mining",
            font=ctk.CTkFont(size=13)
        )
        self.subtitle_label.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 30)
        )

        # EDA button
        self.eda_button = ctk.CTkButton(
            self.sidebar,
            text="📊  EDA Analysis",
            height=45,
            command=self.show_eda
        )
        self.eda_button.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # Statistics button
        self.statistics_button = ctk.CTkButton(
            self.sidebar,
            text="📈  Statistical Analysis",
            height=45,
            command=self.show_statistics
        )
        self.statistics_button.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # ==============================
        # MAIN CONTENT
        # ==============================
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Create pages
        self.eda_view = EDAView(self.content)
        self.statistics_view = StatisticalView(self.content)

        # Show EDA first
        self.show_eda()

    def show_eda(self):
        """Display the EDA page."""
        self.statistics_view.grid_forget()

        self.eda_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def show_statistics(self):
        """Display the Statistical Analysis page."""
        self.eda_view.grid_forget()

        self.statistics_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


if __name__ == "__main__":
    app = NetworkIDSApp()
    app.mainloop()
