"""

import sys
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel, QInputDialog, QFormLayout, QSpinBox, QMessageBox, QTextEdit, QAbstractItemView
from PySide6.QtGui import QShortcut, QKeySequence

class DiamondTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_file = './main.dat'
        self.data = self.load_data()
        self.init_ui()

    def load_data(self):
        if os.path.isfile(self.data_file):
            with open(self.data_file, 'rb') as file:
                return pickle.load(file)
        else:
            return {}



    def init_ui(self):
        self.setWindowTitle('ダイヤ獲得数まとめ')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['年月日', 'ダイヤ総獲得数'])
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree.itemSelectionChanged.connect(self.display_event_details)
        left_layout.addWidget(self.tree)

        self.update_tree()

        button_layout = QHBoxLayout()
        add_year_button = QPushButton('年を追加')
        add_year_button.clicked.connect(self.add_year)
        button_layout.addWidget(add_year_button)

        add_month_button = QPushButton('月を追加')
        add_month_button.clicked.connect(self.add_month)
        button_layout.addWidget(add_month_button)

        add_day_button = QPushButton('日を追加')
        add_day_button.clicked.connect(self.add_day)
        button_layout.addWidget(add_day_button)

        add_event_button = QPushButton('イベントを追加')
        add_event_button.clicked.connect(self.add_event)
        button_layout.addWidget(add_event_button)

        delete_button = QPushButton('削除')
        delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(delete_button)

        # Add buttons for monthly and weekly totals
        monthly_totals_button = QPushButton('月間総計')
        monthly_totals_button.clicked.connect(self.display_monthly_totals)
        button_layout.addWidget(monthly_totals_button)

        weekly_totals_button = QPushButton('週間総計')
        weekly_totals_button.clicked.connect(self.display_weekly_totals)
        button_layout.addWidget(weekly_totals_button)

        custom_totals_button = QPushButton('期間総計')
        custom_totals_button.clicked.connect(self.display_custom_totals)
        button_layout.addWidget(custom_totals_button)

        left_layout.addLayout(button_layout)

        # Right side layout for event details
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.event_details = QTextEdit()
        self.event_details.setReadOnly(True)
        right_layout.addWidget(self.event_details)

        # キーボードショートカットでズームイン・ズームアウトを設定
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)

        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)

    def zoom_in(self):
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)

    def zoom_out(self):
        font = self.font()
        font.setPointSize(font.pointSize() - 1)
        self.setFont(font)



    def add_year(self):
        year, ok = QInputDialog.getText(self, '年を追加', '年を入力(例, 2024):')
        if ok and year:
            if year not in self.data:
                self.data[year] = {}
                self.save_data()
                self.update_tree()

    def add_month(self):
        selected_item = self.tree.currentItem()
        if selected_item and selected_item.parent() is None:  # Year selected
            year = selected_item.text(0)
            month, ok = QInputDialog.getText(self, '月を追加', '月を入力 (例, 07):')
            if ok and month:
                if month not in self.data[year]:
                    self.data[year][month] = {}
                    self.save_data()
                    self.update_tree()

    def add_day(self):
        selected_item = self.tree.currentItem()
        if selected_item and selected_item.parent() is not None and selected_item.parent().parent() is None:  # Month selected
            year = selected_item.parent().text(0)
            month = selected_item.text(0)
            days, ok = QInputDialog.getText(self, '日を追加', '日を入力 (例, 1 または 1-30):')
            if ok and days:
                if '-' in days:
                    start_day, end_day = map(int, days.split('-'))
                    for day in range(start_day, end_day + 1):
                        day_str = str(day)
                        if day_str not in self.data[year][month]:
                            self.data[year][month][day_str] = {'total': 0, 'events': []}
                else:
                    if days not in self.data[year][month]:
                        self.data[year][month][days] = {'total': 0, 'events': []}
                self.save_data()
                self.update_tree()
                # 月の選択を復元
                for i in range(self.tree.topLevelItemCount()):
                    year_item = self.tree.topLevelItem(i)
                    if year_item.text(0) == year:
                        for j in range(year_item.childCount()):
                            month_item = year_item.child(j)
                            if month_item.text(0) == month:
                                self.tree.setCurrentItem(month_item)
                                break

    def add_event(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            description, ok = QInputDialog.getText(self, 'イベントを追加', 'イベント詳細を入力:')
            if ok and description:
                diamonds, ok = QInputDialog.getInt(self, 'ダイヤ獲得数を追加', 'ダイヤの数を入力:')
                if ok:
                    selected_item_texts = [(item.parent().parent().text(0), item.parent().text(0), item.text(0)) for item in selected_items]
                    for selected_item in selected_items:
                        if selected_item.parent() is not None and selected_item.parent().parent() is not None:  # Day selected
                            year = selected_item.parent().parent().text(0)
                            month = selected_item.parent().text(0)
                            day = selected_item.text(0)
                            if day not in self.data[year][month]:
                                self.data[year][month][day] = {'total': 0, 'events': []}
                            event = {'description': description, 'diamonds': diamonds}
                            self.data[year][month][day]['events'].append(event)
                            self.data[year][month][day]['total'] += diamonds
                    self.save_data()
                    self.update_tree()
                    # 選択状態を復元
                    for year, month, day in selected_item_texts:
                        for i in range(self.tree.topLevelItemCount()):
                            year_item = self.tree.topLevelItem(i)
                            if year_item.text(0) == year:
                                for j in range(year_item.childCount()):
                                    month_item = year_item.child(j)
                                    if month_item.text(0) == month:
                                        for k in range(month_item.childCount()):
                                            day_item = month_item.child(k)
                                            if day_item.text(0) == day:
                                                day_item.setSelected(True)
                                                break


    def save_data(self):
        # 年間のダイヤ獲得数を更新
        for year, months in self.data.items():
            year_total = sum(month['total'] for month in months.values() if isinstance(month, dict) and 'total' in month)
            self.data[year]['total'] = year_total

        with open(self.data_file, 'wb') as file:
            pickle.dump(self.data, file)

    def update_tree(self):
        # 保存する展開状態
        expanded_items = set()
        def save_expanded_state(item):
            if item.isExpanded():
                expanded_items.add((item.text(0), item.parent().text(0) if item.parent() else None))
            for i in range(item.childCount()):
                save_expanded_state(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            save_expanded_state(self.tree.topLevelItem(i))

        self.tree.clear()
        for year, months in sorted(self.data.items(), key=lambda x: int(x[0])):
            year_total = 0
            year_item = QTreeWidgetItem([year, '0'])
            self.tree.addTopLevelItem(year_item)
            for month, days in sorted(months.items(), key=lambda x: int(x[0]) if x[0] != 'total' else float('inf')):
                if month == 'total':
                    continue
                month_total = sum(day['total'] for day in days.values() if 'total' in day)
                year_total += month_total
                month_item = QTreeWidgetItem([month, str(month_total)])
                year_item.addChild(month_item)
                for day, details in sorted(days.items(), key=lambda x: int(x[0])):
                    day_item = QTreeWidgetItem([day, str(details['total'])])
                    month_item.addChild(day_item)
                    for event in details['events']:
                        event_item = QTreeWidgetItem([event['description'], str(event['diamonds'])])
                        day_item.addChild(event_item)
            year_item.setText(1, str(year_total))

        # 復元する展開状態
        def restore_expanded_state(item):
            if (item.text(0), item.parent().text(0) if item.parent() else None) in expanded_items:
                item.setExpanded(True)
            for i in range(item.childCount()):
                restore_expanded_state(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            restore_expanded_state(self.tree.topLevelItem(i))


    def delete_item(self):
        selected_item = self.tree.currentItem()
        if selected_item:
            parent = selected_item.parent()
            if parent is None:  # Year selected
                year = selected_item.text(0)
                del self.data[year]
            elif parent.parent() is None:  # Month selected
                year = parent.text(0)
                month = selected_item.text(0)
                del self.data[year][month]
            elif parent.parent().parent() is None:  # Day selected
                year = parent.parent().text(0)
                month = parent.text(0)
                day = selected_item.text(0)
                del self.data[year][month][day]
            else:  # Event selected
                year = parent.parent().parent().text(0)
                month = parent.parent().text(0)
                day = parent.text(0)
                event_description = selected_item.text(0)
                events = self.data[year][month][day]['events']
                for event in events:
                    if event['description'] == event_description:
                        self.data[year][month][day]['total'] -= event['diamonds']
                        events.remove(event)
                        break
                # 他のイベントが残っている場合は日を削除しない
                if not events:
                    self.data[year][month][day]['events'] = []
                    self.data[year][month][day]['total'] = 0

        self.save_data()
        self.update_tree()

    def delete_items(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        for selected_item in selected_items:
            parent = selected_item.parent()
            if parent is None:  # Year selected
                year = selected_item.text(0)
                del self.data[year]
            elif parent.parent() is None:  # Month selected
                year = parent.text(0)
                month = selected_item.text(0)
                del self.data[year][month]
            elif parent.parent().parent() is None:  # Day selected
                year = parent.parent().text(0)
                month = parent.text(0)
                day = selected_item.text(0)
                del self.data[year][month][day]
            else:  # Event selected
                year = parent.parent().parent().text(0)
                month = parent.parent().text(0)
                day = parent.text(0)
                event_description = selected_item.text(0)
                events = self.data[year][month][day]['events']
                for event in events:
                    if event['description'] == event_description:
                        self.data[year][month][day]['total'] -= event['diamonds']
                        events.remove(event)
                        break
                # 他のイベントが残っている場合は日を削除しない
                if not events:
                    del self.data[year][month][day]

        self.save_data()
        self.update_tree()


    def display_event_details(self):
        selected_item = self.tree.currentItem()
        if selected_item:
            parent = selected_item.parent()
            if parent and parent.parent() and parent.parent().parent() is None:  # Day selected
                year = parent.parent().text(0)
                month = parent.text(0)
                day = selected_item.text(0)
            elif parent and parent.parent() and parent.parent().parent():  # Event selected
                year = parent.parent().parent().text(0)
                month = parent.parent().text(0)
                day = parent.text(0)
            else:
                self.event_details.clear()
                return

            events = self.data[year][month][day]['events']
            event_details_text = "\n\n".join([f"詳細: {event['description']}\nダイヤ: {event['diamonds']}個" for event in events])
            self.event_details.setText(event_details_text)
        else:
            self.event_details.clear()

    def display_monthly_totals(self):
        year, ok = QInputDialog.getText(self, '年を入力', '年を入力してください (例: 2024):')
        if not ok or not year:
            return

        month, ok = QInputDialog.getText(self, '月を入力', '対象の月を入力してください (例: 07):')
        if not ok or not month:
            return

        if year not in self.data or month not in self.data[year]:
            QMessageBox.warning(self, 'データなし', f'{year}年{month}月のデータは存在しません。')
            return

        monthly_totals = {'total': 0, 'events': {}}
        for day, details in self.data[year][month].items():
            monthly_totals['total'] += details['total']
            for event in details['events']:
                if event['description'] not in monthly_totals['events']:
                    monthly_totals['events'][event['description']] = 0
                monthly_totals['events'][event['description']] += event['diamonds']

        result_text = f"{year}年{month}月の総計:\n"
        result_text += f"総計: {monthly_totals['total']} 個\n"
        for event, total in monthly_totals['events'].items():
            result_text += f"  {event}: {total} 個\n"

        self.event_details.setText(result_text)
        self.plot_event_totals({f"{year}-{month}": monthly_totals})

    def display_weekly_totals(self):
        week_start_str, ok = QInputDialog.getText(self, '週の数え始め', '数え開始日を入力(YYYY-MM-DD):')
        if not ok or not week_start_str:
            return

        try:
            week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, '無効な日付です', 'YYYY-MM-DDの形式で日付を入力してください。')
            return

        week_end = week_start + timedelta(days=6)
        weekly_totals = {'total': 0, 'events': {}}

        for year, months in self.data.items():
            for month, days in months.items():
                if month == 'total':
                    continue
                for day, details in days.items():
                    date_str = f"{year}-{month}-{day}"
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        continue
                    if week_start <= date_obj <= week_end:
                        weekly_totals['total'] += details['total']
                        for event in details['events']:
                            if event['description'] not in weekly_totals['events']:
                                weekly_totals['events'][event['description']] = 0
                            weekly_totals['events'][event['description']] += event['diamonds']

        result_text = f"{week_start_str} から {week_end.strftime('%Y-%m-%d')} までの週間総計:\n"
        result_text += f"総計: {weekly_totals['total']} 個\n"
        for event, total in weekly_totals['events'].items():
            result_text += f"  {event}: {total} 個\n"

        self.event_details.setText(result_text)
        self.plot_event_totals({f"{week_start_str} - {week_end.strftime('%Y-%m-%d')}": weekly_totals})


    def display_custom_totals(self):
        start_date_str, ok = QInputDialog.getText(self, '開始日を入力', '開始日を入力してください (YYYY-MM-DD):')
        if not ok or not start_date_str:
            return

        end_date_str, ok = QInputDialog.getText(self, '終了日を入力', '終了日を入力してください (YYYY-MM-DD):')
        if not ok or not end_date_str:
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, '無効な日付です', 'YYYY-MM-DDの形式で日付を入力してください。')
            return

        if start_date > end_date:
            QMessageBox.warning(self, '無効な期間', '開始日は終了日より前でなければなりません。')
            return

        custom_totals = {'total': 0, 'events': {}}

        for year, months in self.data.items():
            for month, days in months.items():
                if month == 'total':
                    continue
                for day, details in days.items():
                    date_str = f"{year}-{month}-{day}"
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        continue
                    if start_date <= date_obj <= end_date:
                        custom_totals['total'] += details['total']
                        for event in details['events']:
                            if event['description'] not in custom_totals['events']:
                                custom_totals['events'][event['description']] = 0
                            custom_totals['events'][event['description']] += event['diamonds']

        result_text = f"{start_date_str} から {end_date_str} までの総計:\n"
        result_text += f"総計: {custom_totals['total']} 個\n"
        for event, total in custom_totals['events'].items():
            result_text += f"  {event}: {total} 個\n"

        self.event_details.setText(result_text)
        self.plot_event_totals({f"{start_date_str} - {end_date_str}": custom_totals})


    def plot_event_totals(self, totals):
        events = {}
        for period, data in totals.items():
            for event, total in data['events'].items():
                if event not in events:
                    events[event] = 0
                events[event] += total

        event_names = list(events.keys())
        event_totals = list(events.values())

        # ログスケールを使用するかどうかを決定
        use_log_scale = max(event_totals) / min(event_totals) > 1000

        font_path = 'C:/Windows/Fonts/msgothic.ttc'  # WindowsのMSゴシックフォントのパス
        font_prop = fm.FontProperties(fname=font_path)

        plt.figure(figsize=(12, 6))
        bars = plt.bar(event_names, event_totals, color='skyblue')

        # ログスケールを使用する場合
        if use_log_scale:
            plt.yscale('log')
            plt.ylabel('ダイヤ獲得数 (対数スケール)', fontproperties=font_prop)
        else:
            plt.ylabel('ダイヤ獲得数', fontproperties=font_prop)

        plt.xlabel('イベント', fontproperties=font_prop)
        plt.title('イベントごとのダイヤ獲得数', fontproperties=font_prop)
        plt.xticks(rotation=45, ha='right', fontproperties=font_prop)

        # 数が非常に大きい場合、途中の値を省略して表示
        for bar in bars:
            height = bar.get_height()
            if use_log_scale and height > 1000:
                plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0e}', ha='center', va='bottom', fontproperties=font_prop)
            else:
                plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom', fontproperties=font_prop)

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DiamondTracker()
    window.show()
    sys.exit(app.exec())
"""