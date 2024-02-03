class Helper:
    @staticmethod
    def set_table_headers(table_widget, headers):
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)