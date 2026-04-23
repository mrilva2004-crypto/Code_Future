import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        
        self.books = []
        self.load_data()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_frame()
        self.create_button_frame()
        
        self.refresh_table()
    
    def create_input_frame(self):
        """Форма для ввода данных"""
        input_frame = LabelFrame(self.root, text="Добавление новой книги", padx=10, pady=10)
        input_frame.pack(fill=X, padx=10, pady=5)
        
        # Поля ввода
        labels = ["Название книги:", "Автор:", "Жанр:", "Количество страниц:"]
        self.entries = {}
        
        for i, label in enumerate(labels):
            Label(input_frame, text=label).grid(row=i, column=0, sticky=W, padx=5, pady=5)
            entry = Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry
        
        # Кнопка добавления
        self.add_button = Button(input_frame, text="Добавить книгу", command=self.add_book, 
                                  bg="green", fg="white", font=("Arial", 10, "bold"))
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_filter_frame(self):
        """Фильтрация"""
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill=X, padx=10, pady=5)
        
        # Фильтр по жанру
        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по страницам
        Label(filter_frame, text="Страниц больше чем:").grid(row=0, column=2, padx=5, pady=5)
        self.pages_filter = Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопка применения фильтра
        self.filter_button = Button(filter_frame, text="Применить фильтр", command=self.apply_filter,
                                     bg="blue", fg="white")
        self.filter_button.grid(row=0, column=4, padx=10, pady=5)
        
        # Кнопка сброса фильтра
        self.reset_button = Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                     bg="orange", fg="white")
        self.reset_button.grid(row=0, column=5, padx=10, pady=5)
    
    def create_tree_frame(self):
        """Таблица с книгами"""
        tree_frame = Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Создание таблицы
        columns = ("ID", "Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")
        
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=120)
        self.tree.column("Страницы", width=100)
        
        # Скроллбар
        scrollbar = Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def create_button_frame(self):
        """Кнопки управления"""
        button_frame = Frame(self.root)
        button_frame.pack(fill=X, padx=10, pady=5)
        
        self.save_button = Button(button_frame, text="Сохранить в JSON", command=self.save_data,
                                   bg="purple", fg="white")
        self.save_button.pack(side=LEFT, padx=5)
        
        self.delete_button = Button(button_frame, text="Удалить выбранную", command=self.delete_book,
                                     bg="red", fg="white")
        self.delete_button.pack(side=LEFT, padx=5)
    
    def validate_input(self, title, author, genre, pages):
        """Проверка корректности ввода"""
        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Поля 'Название', 'Автор' и 'Жанр' не могут быть пустыми!")
            return False
        
        try:
            pages_int = int(pages)
            if pages_int <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return False
        
        return True
    
    def add_book(self):
        """Добавление книги"""
        title = self.entries["Название книги:"].get().strip()
        author = self.entries["Автор:"].get().strip()
        genre = self.entries["Жанр:"].get().strip()
        pages = self.entries["Количество страниц:"].get().strip()
        
        if self.validate_input(title, author, genre, pages):
            book = {
                "id": len(self.books) + 1,
                "title": title,
                "author": author,
                "genre": genre,
                "pages": int(pages)
            }
            self.books.append(book)
            self.clear_inputs()
            self.refresh_table()
            messagebox.showinfo("Успех", f"Книга '{title}' успешно добавлена!")
    
    def clear_inputs(self):
        """Очистка полей ввода"""
        for entry in self.entries.values():
            entry.delete(0, END)
    
    def refresh_table(self, filtered_books=None):
        """Обновление таблицы"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        books_to_show = filtered_books if filtered_books is not None else self.books
        
        for book in books_to_show:
            self.tree.insert("", END, values=(book["id"], book["title"], book["author"], 
                                              book["genre"], book["pages"]))
    
    def apply_filter(self):
        """Применение фильтрации"""
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter = self.pages_filter.get().strip()
        
        filtered = self.books.copy()
        
        # Фильтр по жанру
        if genre_filter:
            filtered = [book for book in filtered if genre_filter in book["genre"].lower()]
        
        # Фильтр по страницам
        if pages_filter:
            try:
                pages_num = int(pages_filter)
                filtered = [book for book in filtered if book["pages"] > pages_num]
            except ValueError:
                messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
                return
        
        if not filtered:
            messagebox.showinfo("Результат", "Книги, соответствующие фильтру, не найдены.")
        
        self.refresh_table(filtered)
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.genre_filter.delete(0, END)
        self.pages_filter.delete(0, END)
        self.refresh_table()
        messagebox.showinfo("Фильтр", "Фильтр сброшен. Показаны все книги.")
    
    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите книгу для удаления!")
            return
        
        # Получаем ID книги
        item = self.tree.item(selected[0])
        book_id = item["values"][0]
        
        # Удаляем книгу
        self.books = [book for book in self.books if book["id"] != book_id]
        
        # Перенумерация ID
        for i, book in enumerate(self.books, 1):
            book["id"] = i
        
        self.refresh_table()
        messagebox.showinfo("Успех", "Книга успешно удалена!")
    
    def save_data(self):
        """Сохранение в JSON"""
        try:
            with open("books.json", "w", encoding="utf-8") as file:
                json.dump(self.books, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные успешно сохранены в books.json!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка из JSON"""
        if os.path.exists("books.json"):
            try:
                with open("books.json", "r", encoding="utf-8") as file:
                    self.books = json.load(file)
            except:
                self.books = []
        else:
            self.books = []

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()
