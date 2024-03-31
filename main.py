import customtkinter
import tkinter as tk
import tkinter.messagebox as messagebox

class PlannerApp():
    def __init__(self, master):
        root = customtkinter.CTk()

        self.master = master
        self.master.title("Планирование")

        self.canvas = customtkinter.CTkCanvas(self.master, bg="bisque", highlightthickness=0)
        self.canvas.pack(fill=customtkinter.BOTH, expand=True)

        self.draw_grid()  # Начальное создание сетки

        # Создаем фрейм для кнопок
        self.button_frame = customtkinter.CTkFrame(self.master)
        self.button_frame.pack(side=customtkinter.BOTTOM, fill=customtkinter.X)

        # Создаем кнопку для добавления текста
        self.add_text_button = customtkinter.CTkButton(self.button_frame, text="Добавить текст", command=self.add_text)
        self.add_text_button.pack(side=customtkinter.LEFT, padx=10, pady=10)

        # Создаем кнопку для выбора фигур
        self.shape_var = tk.StringVar(self.button_frame)
        self.shape_var.set("Прямоугольник")  # Значение по умолчанию
        self.shape_menu = customtkinter.CTkOptionMenu(self.button_frame, variable=self.shape_var, values=["Прямоугольник", "Квадрат"])
        self.shape_menu.pack(side=tk.LEFT, padx=10, pady=10)

        # Создаем кнопку для создания фигуры на холсте
        self.create_shape_button = customtkinter.CTkButton(self.button_frame, text="Создать фигуру на холсте", command=self.create_shape)
        self.create_shape_button.pack(side=tk.LEFT, padx=10, pady=10)

        #Создаем кнопку для выбора стрелки
        self.arrow_var = tk.StringVar(self.button_frame)
        self.arrow_var.set('Вниз') # Значение по умолчанию
        self.arrow_menu = customtkinter.CTkOptionMenu(self.button_frame, variable=self.arrow_var, values=['Вниз', 'Вверх', 'Направо', 'Налево'])
        self.arrow_menu.pack(side=tk.LEFT, padx=10, pady=10)

        # Создаем кнопку для добавления стрелочки
        self.add_arrow_button = customtkinter.CTkButton(self.button_frame, text="Добавить стрелку",
                                                        command=self.add_arrow)
        self.add_arrow_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Привязываем обновление сетки к событию изменения размеров окна
        self.master.bind("<Configure>", self.on_window_resize)

        # Создаем контекстное меню для текста
        self.context_menu_text = tk.Menu(self.master, tearoff=0)
        self.context_menu_text.add_command(label="Изменить", command=self.edit_text)
        self.context_menu_text.add_command(label='Удалить', command=self.delete_selected_text)

        # Создаем контекстное меню для фигуры
        self.context_menu_shape = tk.Menu(self.master, tearoff=0)
        self.context_menu_shape.add_command(label='Удалить', command=self.delete_selected_shape)

        # Создаем контекстное меню для стрелочки
        self.context_menu_arrow = tk.Menu(self.master, tearoff=0)
        self.context_menu_arrow.add_command(label='Удалить', command=self.delete_selected_arrow)

        # Создаем кнопку для очистки холста
        self.clear_canvas_button = customtkinter.CTkButton(self.button_frame, text="Очистить холст",
                                                           command=self.clear_canvas)
        self.clear_canvas_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Идентификаторы текстового и фигурного объектов для редактирования и перемещения
        self.selected_object = None
        self.start_x = None
        self.start_y = None
        self.ctrl_pressed = False

        # Привязываем события нажатия и отпускания клавиши CTRL
        self.master.bind("<Control_L>", self.on_ctrl_press)
        self.master.bind("<Control_R>", self.on_ctrl_press)
        self.master.bind("<KeyRelease-Control_L>", self.on_ctrl_release)
        self.master.bind("<KeyRelease-Control_R>", self.on_ctrl_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Bind mouse wheel event to canvas

    def delete_selected_text(self):
        # Удаляем выбранный текстовый объект
        if self.selected_text is not None:
            self.canvas.delete(self.selected_text)

    def clear_canvas(self):
        # Отображаем диалоговое окно с вопросом о подтверждении
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить холст?")
        if confirm:
            # Удаляем все объекты с холста, кроме точек сетки
            for item in self.canvas.find_all():
                if self.canvas.gettags(item) != ("grid",):  # Проверяем теги объекта
                    self.canvas.delete(item)

    def on_ctrl_press(self, event):
        # Обработка нажатия клавиши CTRL
        self.ctrl_pressed = True

    def on_ctrl_release(self, event):
        # Обработка отпускания клавиши CTRL
        self.ctrl_pressed = False

    def delete_selected_shape(self):
        # Удаляем выбранный фигурный объект
        if self.selected_shape is not None:
            self.canvas.delete(self.selected_shape)

    def show_context_menu_shape(self, event, shape_id):
        # Показываем контекстное меню на позиции щелчка
        self.context_menu_shape.post(event.x_root, event.y_root)
        # Сохраняем идентификатор фигуры для последующего использования
        self.selected_shape = shape_id

    def on_shape_scroll(self, event, shape_id):
        if self.ctrl_pressed:
            if event.delta > 0:
                self.canvas.scale(shape_id, event.x, event.y, 1.1, 1.1)
            elif event.delta < 0:
                self.canvas.scale(shape_id, event.x, event.y, 0.9, 0.9)

    def on_shape_click(self, event, shape_id):
        # Запоминаем начальные координаты объекта фигуры и выделенный объект
        self.selected_object = shape_id
        self.start_x = event.x
        self.start_y = event.y
        # Привязываем событие перемещения фигуры к холсту
        self.canvas.bind("<B1-Motion>", self.on_shape_drag)

    def create_shape(self):
        selected_shape = self.shape_var.get()
        if selected_shape == "Прямоугольник":
            shape_id = self.canvas.create_rectangle(50, 50, 320, 180, fill="white", outline='black', stipple="gray50")
        elif selected_shape == "Квадрат":
            shape_id = self.canvas.create_rectangle(50, 50, 150, 150, fill="white", stipple="gray50")
        # Привязываем обработчики событий к фигуре
        self.canvas.tag_bind(shape_id, "<ButtonPress-1>",
                             lambda event, shape_id=shape_id: self.on_shape_click(event, shape_id))
        self.canvas.tag_bind(shape_id, "<B1-Motion>",
                             lambda event, shape_id=shape_id: self.on_shape_drag(event, shape_id))
        self.canvas.tag_bind(shape_id, "<Button-3>",
                             lambda event, shape_id=shape_id: self.show_context_menu_shape(event, shape_id))
        # Перемещаем текстовый объект на передний план после создания фигуры
        self.canvas.tag_raise("text")  # Поднять все объекты с тегом "text" на передний план

    def on_shape_drag(self, event):
        # Если нет выделенного объекта, выходим
        if self.selected_object is None:
            return
        # Вычисляем разницу в позиции мыши с последнего события
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        # Перемещаем объект фигуры на вычисленную разницу
        self.canvas.move(self.selected_object, delta_x, delta_y)
        # Обновляем начальные координаты для следующего события перетаскивания
        self.start_x, self.start_y = event.x, event.y

    def on_mouse_wheel(self, event):
        if self.ctrl_pressed:
            x, y = event.x, event.y
            overlapping_items = self.canvas.find_overlapping(x, y, x, y)
            if overlapping_items:
                selected_item = overlapping_items[-1]
                if self.canvas.type(selected_item) in ["oval", "rectangle"]:
                    self.on_shape_scroll(event, selected_item)
                elif self.canvas.type(selected_item) == "text":
                    self.on_text_scroll(event, selected_item)
                elif self.canvas.type(selected_item) == "line":
                    self.on_arrow_scale(event, selected_item)

    def draw_grid(self):
        self.canvas.delete("grid")  # Удаление предыдущей сетки
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # Создаем сетку из серых точек с очень низкой прозрачностью
        for x in range(0, w, 20):
            for y in range(0, h, 20):
                point = self.canvas.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#888888", outline="#888888",
                                                stipple="gray12", tags="grid")
                self.canvas.tag_lower(point)  # Помещаем точку сетки позади других объектов

    def on_window_resize(self, event):
        self.draw_grid()  # Обновляем сетку при изменении размеров окна

    def add_text(self):
        # Добавляем текст на холст
        text_id = self.canvas.create_text(100, 100, text="Новый текст", font=("Arial", 12, "bold"), fill="black",
                                          tags="text")
        # Перемещаем текстовый объект на передний план
        self.canvas.tag_raise(text_id)
        # Привязываем контекстное меню к тексту
        self.canvas.tag_bind(text_id, "<Button-3>",
                             lambda event, text_id=text_id: self.show_context_menu_text(event, text_id))
        # Привязываем события перемещения текста к холсту
        self.canvas.tag_bind(text_id, "<ButtonPress-1>", self.on_text_click)
        self.canvas.tag_bind(text_id, "<B1-Motion>", self.on_text_drag)
    def on_text_click(self, event):
        # Запоминаем начальные координаты объекта текста
        self.selected_object = self.canvas.find_closest(event.x, event.y)[0]
        self.start_x = event.x
        self.start_y = event.y

    def on_text_drag(self, event):
        # Если нет выделенного текстового объекта, выходим
        if self.selected_object is None:
            return
        # Вычисляем разницу в позиции мыши с последнего события
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        # Перемещаем объект текста на вычисленную разницу
        self.canvas.move(self.selected_object, delta_x, delta_y)
        # Обновляем начальные координаты для следующего события перетаскивания
        self.start_x, self.start_y = event.x, event.y

    def on_text_scroll(self, event, text_id):
        # Обработка прокрутки колесика мыши для изменения размера текста
        current_font = self.canvas.itemcget(text_id, "font")
        # Получаем текущий размер шрифта
        font_size = int(current_font.split()[1])
        # Определяем направление прокрутки
        if event.delta > 0:
            # Увеличиваем размер шрифта
            font_size += 1
        elif event.delta < 0:
            # Уменьшаем размер шрифта (с учетом минимального значения)
            font_size = max(1, font_size - 1)
        # Создаем новый шрифт с обновленным размером
        new_font = (current_font.split()[0], font_size)
        # Применяем новый шрифт к тексту
        self.canvas.itemconfig(text_id, font=new_font)

    def show_context_menu_text(self, event, text_id):
        # Показываем контекстное меню на позиции щелчка
        self.context_menu_text.post(event.x_root, event.y_root)
        # Сохраняем идентификатор текста для последующего использования
        self.selected_text = text_id

    def edit_text(self):
        # Проверяем, является ли выбранный объект текстовым объектом
        if self.canvas.type(self.selected_object) == "text":
            # Получаем текущий текст
            current_text = self.canvas.itemcget(self.selected_object, "text")
            # Создаем текстовый виджет для редактирования текста
            self.text_edit_widget = tk.Entry(self.canvas, font=("Arial", 12, "bold"), bg="bisque", bd=0)
            self.text_edit_widget.insert(0, current_text)
            bbox = self.canvas.bbox(self.selected_object)
            self.text_edit_widget.place(x=bbox[0], y=bbox[1])
            self.text_edit_widget.focus_set()  # Устанавливаем фокус на текстовый виджет
            # Привязываем событие нажатия Enter для сохранения изменений
            self.text_edit_widget.bind("<Return>", self.save_text_changes)
        else:
            # Если выбранный объект не текст, выведите сообщение об ошибке или выполните другие действия
            print("Этот объект не является текстом и не может быть изменен.")

    def save_text_changes(self, event):
        new_text = self.text_edit_widget.get()
        # Обновляем текст объекта на холсте
        self.canvas.itemconfig(self.selected_object, text=new_text)
        # Удаляем текстовый виджет
        self.text_edit_widget.destroy()
        self.text_edit_widget = None

    def add_arrow(self):
        # Получаем выбранное значение из self.arrow_var
        selected_arrow = self.arrow_var.get()

        # Определяем координаты начала и конца стрелки в зависимости от выбранной стрелки
        if selected_arrow == 'Вниз':
            start_x, start_y = 100, 100
            end_x, end_y = 100, 200
        elif selected_arrow == 'Вверх':
            start_x, start_y = 100, 200
            end_x, end_y = 100, 100
        elif selected_arrow == 'Направо':
            start_x, start_y = 100, 100
            end_x, end_y = 200, 100
        elif selected_arrow == 'Налево':
            start_x, start_y = 200, 100
            end_x, end_y = 100, 100

        # Создаем стрелку на холсте
        arrow_id = self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST, fill="black", width=2)

        # Привязываем события перемещения стрелки к холсту
        self.canvas.tag_bind(arrow_id, "<ButtonPress-1>", self.on_arrow_click)
        self.canvas.tag_bind(arrow_id, "<B1-Motion>", self.on_arrow_drag)

        # Привязываем контекстное меню к стрелке
        self.bind_arrow_context_menu(arrow_id)

    def bind_arrow_context_menu(self, arrow_id):
        # Привязываем контекстное меню к стрелке
        self.canvas.tag_bind(arrow_id, "<Button-3>",
                             lambda event, arrow_id=arrow_id: self.show_context_menu_arrow(event, arrow_id))

    def on_arrow_click(self, event):
        # Запоминаем начальные координаты объекта стрелки
        self.selected_object = self.canvas.find_closest(event.x, event.y)[0]
        self.start_x = event.x
        self.start_y = event.y

    def on_arrow_drag(self, event):
        # Если нет выделенного объекта или это не стрелка, выходим
        if self.selected_object is None or self.canvas.type(self.selected_object) != "line":
            return
        # Вычисляем разницу в позиции мыши с последнего события
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        # Перемещаем наконечник стрелки на вычисленную разницу
        self.canvas.move(self.selected_object, delta_x, delta_y)
        # Обновляем начальные координаты для следующего события перетаскивания
        self.start_x, self.start_y = event.x, event.y

    def on_arrow_release(self, event):
        # Если нет выделенного объекта или это не стрелка, выходим
        if self.selected_object is None or self.canvas.type(self.selected_object) != "line":
            return
        # Удаляем привязку события перемещения наконечника
        self.canvas.unbind("<B1-Motion>")

    def show_context_menu_arrow(self, event, arrow_id):
        # Показываем контекстное меню на позиции щелчка
        self.context_menu_arrow.post(event.x_root, event.y_root)
        # Сохраняем идентификатор фигуры для последующего использования
        self.selected_arrow = arrow_id

    def delete_selected_arrow(self):
        # Удаляем выбранный фигурный объект
        if self.selected_arrow is not None:
            self.canvas.delete(self.selected_arrow)

    def on_arrow_scale(self, event, arrow_id):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale(arrow_id, event.x, event.y, scale_factor, scale_factor)


def main():
    root = customtkinter.CTk()
    root.geometry("1000x500")  # Устанавливаем начальный размер окна
    app = PlannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()