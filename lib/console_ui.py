import npyscreen


class ConsoleUI(npyscreen.NPSApp):

    def __init__(self, console_model):
        super().__init__()

        # The form where our widgets will be
        self.form = None

        # Refresh the screen as often as possible
        self.keypress_timeout_default = 1

        # The widgets drawn on the terminal
        self.alert_status_widget = None
        self.stats_widget = None
        self.alert_history_widget = None

        # THe model to fetch our state from
        self.console_model = console_model

    def while_waiting(self):
        # Status update
        new_status_value, color = self.console_model.get_alert_status_message()

        if new_status_value != self.alert_status_widget.value:
            self.alert_status_widget.entry_widget.color = color
            self.alert_status_widget.value = new_status_value
            self.alert_status_widget.display()

        # Last updated update
        new_lats_updated_value = self.console_model.get_last_updated_message()

        if new_lats_updated_value != self.last_updated_widget.value:
            self.last_updated_widget.value = new_lats_updated_value
            self.last_updated_widget.display()

        # Stats update
        new_stats_value = self.console_model.get_stats_messages()

        if new_stats_value != self.stats_widget.value:
            self.stats_widget.values = new_stats_value
            self.stats_widget.display()

        # Alerts update
        new_alert_history_value = self.console_model.get_alert_history_messages()

        if new_alert_history_value != self.alert_history_widget.value:
            self.alert_history_widget.values = new_alert_history_value
            self.alert_history_widget.display()

    def main(self):
        self.form = npyscreen.FormBaseNew(parentApp=self, name="HTTP Log Monitoring")

        # Alert status widget
        self.alert_status_widget = self.form.add(npyscreen.TitleText,
                                                 name="Alert Status",
                                                 max_height=3,
                                                 editable=False)

        # Last updated widget
        self.last_updated_widget = self.form.add(npyscreen.TitleText,
                                                 name="Last update",
                                                 max_height=3,
                                                 editable=False)

        # Stats widget
        self.stats_widget = self.form.add(npyscreen.BoxTitle,
                                          name="Statistics",
                                          max_width=50,
                                          relx=2,
                                          rely=5)

        self.stats_widget.entry_widget.scroll_exit = True

        # Alert history widget
        self.alert_history_widget = self.form.add(npyscreen.BoxTitle,
                                                  name="Alert History",
                                                  max_width=66,
                                                  relx=52,
                                                  rely=5)

        self.alert_history_widget.entry_widget.scroll_exit = True

        # Render the form
        self.form.edit()