import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
# from fpdf import FPDF
import os

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCG Resizer")
        self.root.geometry("600x600")

        # Panel superior para configuración de tamaño
        self.top_panel = tk.Frame(self.root)
        self.top_panel.pack(fill=tk.X, padx=10, pady=5)

        # Campos para configuración de tamaño
        self.label_width = tk.Label(self.top_panel, text="Ancho (mm):")
        self.label_width.grid(row=0, column=0, padx=5)
        self.entry_width = tk.Entry(self.top_panel)
        self.entry_width.grid(row=0, column=1, padx=5)

        self.label_height = tk.Label(self.top_panel, text="Alto (mm):")
        self.label_height.grid(row=0, column=2, padx=5)
        self.entry_height = tk.Entry(self.top_panel)
        self.entry_height.grid(row=0, column=3, padx=5)
        
        self.label_dpi = tk.Label(self.top_panel, text="DPI:")
        self.label_dpi.grid(row=0, column=4, padx=5)
        self.dpi_entry = tk.Entry(self.top_panel)
        self.dpi_entry.grid(row=0, column=5, padx=5)
        self.dpi_entry.insert(0, "96")  # Valor por defecto

        # Panel para configuración de recorte
        self.crop_panel = tk.Frame(self.root)
        self.crop_panel.pack(fill=tk.X, padx=10, pady=5)

        # Campo para la cantidad de margen a recortar
        self.label_crop = tk.Label(self.crop_panel, text="Margen a recortar (pixeles):")
        self.label_crop.grid(row=0, column=0, padx=5)
        self.entry_crop = tk.Entry(self.crop_panel)
        self.entry_crop.insert(0, "0")  # Valor predeterminado es 0
        self.entry_crop.grid(row=0, column=1, padx=5)

        # Botones
        self.btn_open = tk.Button(self.root, text="Abrir Imágenes", command=self.open_images)
        self.btn_open.pack(pady=10)

        self.btn_resize = tk.Button(self.root, text="Redimensionar y Guardar en Carpeta", command=self.resize_images)
        self.btn_resize.pack(pady=10)
        
        # Botón para recortar y generar PDF
        # self.btn_crop_pdf = tk.Button(self.root, text="Recortar y Generar PDF", command=self.crop_and_generate_pdf)
        # self.btn_crop_pdf.pack(pady=10)

        # Contenedor de las imágenes y entradas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable Canvas
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Variable para almacenar las imágenes y entradas
        self.images = []
        self.image_widgets = []

    def open_images(self):
        # Abre un cuadro de diálogo para seleccionar varias imágenes
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_paths:
            return
        try:
            # Carga todas las imágenes seleccionadas y obtiene DPI si está disponible
            for file_path in file_paths:
                img = Image.open(file_path)
                dpi = img.info.get("dpi", (300, 300))[0]  # Extrae DPI o usa 300 como valor predeterminado
                self.images.append((img, dpi))
            self.display_images()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron abrir las imágenes: {e}")

    def display_images(self):
        # Limpia la vista previa antes de agregar nuevas imágenes
        for widget in self.image_widgets:
            widget.destroy()
        self.image_widgets = []  # Reinicia la lista de widgets

        # Obtiene el tamaño de la ventana
        window_width = self.root.winfo_width()
        thumbnail_width = int(window_width * 0.1)  # Tamaño reducido de la imagen (10% del tamaño de la ventana)

        # Muestra cada imagen en el canvas con un campo de entrada para las copias
        for i, (image, dpi) in enumerate(self.images):
            # Redimensiona la imagen para la vista previa
            thumbnail = image.resize((thumbnail_width, int(thumbnail_width * image.height / image.width)), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(thumbnail)

            # Crea un contenedor para la imagen y su entrada
            frame = tk.Frame(self.canvas)
            frame.pack(pady=5, padx=10)

            # Imagen
            img_label = tk.Label(frame, image=img_tk)
            img_label.image = img_tk  # Mantiene una referencia para evitar que la imagen se elimine
            img_label.pack(side=tk.LEFT)

            # Campo para la cantidad de copias
            entry = tk.Entry(frame)
            entry.insert(0, "1")  # Valor predeterminado es 1
            entry.pack(side=tk.LEFT, padx=10)

            # Añadir al canvas
            self.canvas.create_window(0, len(self.image_widgets) * 100, window=frame, anchor="nw")
            self.image_widgets.append(frame)  # Ahora solo almacenamos los frames, no las tuplas

        # Ajusta el tamaño del canvas para que sea scrollable
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def resize_images(self):
        if not self.images:
            messagebox.showwarning("Advertencia", "Primero debes cargar imágenes.")
            return

        # Obtiene los valores de ancho, alto y margen desde la interfaz
        width_mm = self.entry_width.get()
        height_mm = self.entry_height.get()
        crop_margin = self.entry_crop.get()

        try:
            # Convertir los valores a enteros
            crop_margin = int(crop_margin)
            if crop_margin < 0:
                raise ValueError("El margen de recorte no puede ser negativo.")
            
            if width_mm:
                width_mm = float(width_mm)
            else:
                width_mm = None

            if height_mm:
                height_mm = float(height_mm)
            else:
                height_mm = None

        except ValueError as e:
            messagebox.showerror("Error", f"Error en los valores ingresados: {e}")
            return

        # Solicita la carpeta de destino para guardar las imágenes redimensionadas
        save_directory = filedialog.askdirectory()
        if not save_directory:
            return

        try:
            for i, (image, dpi) in enumerate(self.images):
                # Encuentra la entrada para la cantidad de copias
                entry = self.image_widgets[i].winfo_children()[-1]  # El último widget en el frame es la entrada
                # Obtiene la cantidad de copias a guardar
                try:
                    copies = int(entry.get())
                    if copies <= 0:
                        raise ValueError("El número de copias debe ser mayor a 0.")
                except ValueError:
                    messagebox.showerror("Error", f"Por favor ingresa un número válido de copias para la imagen {i + 1}.")
                    return
                
                # Obtener el valor de DPI del campo de entrada
                try:
                    dpi = int(self.dpi_entry.get())
                    if dpi <= 0:
                        raise ValueError("El DPI debe ser mayor a 0.")
                except ValueError:
                    messagebox.showerror("Error", "Por favor ingresa un valor válido de DPI.")
                    return
                
                # Recorte de la imagen
                if crop_margin > 0:
                    width, height = image.size
                    left = crop_margin
                    top = crop_margin
                    right = width - crop_margin
                    bottom = height - crop_margin
                    image = image.crop((left, top, right, bottom))

                # Si el ancho o el alto se especificaron, calcular la nueva resolución usando el DPI de cada imagen
                if width_mm or height_mm:
                    width_pixels = width_mm * dpi / 25.4 if width_mm and width_mm > 0 else 0
                    height_pixels = height_mm * dpi / 25.4 if height_mm and height_mm > 0 else 0
                
                    # Si solo uno de los dos se especificó, calcular el otro proporcionalmente
                    if width_mm and not height_mm:
                        height_pixels = (image.height * width_pixels) / image.width
                    elif height_mm and not width_mm:
                        width_pixels = (image.width * height_pixels) / image.height
                
                    new_size = (int(width_pixels), int(height_pixels)) if width_pixels and height_pixels else image.size
                else:
                    # Si no se especifica ningún valor, no redimensionamos
                    new_size = image.size
                
                # Redimensiona la imagen
                resized_image = image.resize(new_size, Image.LANCZOS)
                
                # Guarda las imágenes
                for copy in range(copies):
                    output_path = os.path.join(save_directory, f"imagen_{i + 1}_copia_{copy + 1}.png")
                    resized_image.save(output_path)

            messagebox.showinfo("Éxito", "Las imágenes se han redimensionado y guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar las imágenes: {e}")
            
    # def crop_and_generate_pdf(self):
    #     # Solicita la carpeta de destino para guardar el PDF
    #     save_directory = filedialog.askdirectory()
    #     if not save_directory:
    #         return
    
    #     pdf = FPDF()
    #     pdf.set_auto_page_break(0)
    
    #     try:
    #         # Tamaño de la página A4 en píxeles a 96 DPI
    #         page_width = 210 * 96 / 25.4
    #         page_height = 297 * 96 / 25.4
    
    #         # Margen entre imágenes
    #         margin = 10
    
    #         # Posición inicial
    #         x, y = margin, margin
    
    #         # Añadir la primera página
    #         pdf.add_page()
    
    #         for i, (image, dpi) in enumerate(self.images):
    #             # Encuentra la entrada para la cantidad de copias
    #             entry = self.image_widgets[i].winfo_children()[-1]  # El último widget en el frame es la entrada
    #             # Obtiene la cantidad de copias a guardar
    #             try:
    #                 copies = int(entry.get())
    #                 if copies <= 0:
    #                     raise ValueError("El número de copias debe ser mayor a 0.")
    #             except ValueError:
    #                 messagebox.showerror("Error", f"Por favor ingresa un número válido de copias para la imagen {i + 1}.")
    #                 return
    
    #             for copy in range(copies):
    #                 # Recorte de la imagen
    #                 crop_margin = int(self.entry_crop.get())
    #                 if crop_margin > 0:
    #                     width, height = image.size
    #                     left = crop_margin
    #                     top = crop_margin
    #                     right = width - crop_margin
    #                     bottom = height - crop_margin
    
    #                     # Verificar que las coordenadas de recorte sean válidas
    #                     if left < right and top < bottom:
    #                         image = image.crop((left, top, right, bottom))
    #                     else:
    #                         messagebox.showerror("Error", f"Las coordenadas de recorte no son válidas: left={left}, right={right}, top={top}, bottom={bottom}")
    #                         return
    
    #                 # Convertir la imagen a RGB si es necesario
    #                 if image.mode != 'RGB':
    #                     image = image.convert('RGB')
    
    #                 # Redimensionar la imagen a 96 DPI
    #                 image = image.resize((int(image.width * 96 / dpi), int(image.height * 96 / dpi)), Image.LANCZOS)
    
    #                 # Guardar la imagen temporalmente
    #                 temp_image_path = os.path.join(save_directory, f"temp_image_{i}_copy_{copy}.jpg")
    #                 image.save(temp_image_path)
    
    #                 # Añadir la imagen al PDF
    #                 img_width, img_height = image.size
    #                 if x + img_width + margin > page_width:
    #                     x = margin
    #                     y += img_height + margin
    #                 if y + img_height + margin > page_height:
    #                     pdf.add_page()
    #                     x, y = margin, margin
    
    #                 pdf.image(temp_image_path, x=x * 25.4 / 96, y=y * 25.4 / 96, w=img_width * 25.4 / 96, h=img_height * 25.4 / 96)
    #                 x += img_width + margin
    
    #                 # Eliminar la imagen temporal
    #                 os.remove(temp_image_path)
    
    #         # Guardar el PDF
    #         pdf_output_path = os.path.join(save_directory, "output.pdf")
    #         pdf.output(pdf_output_path)
    
    #         messagebox.showinfo("Éxito", "El PDF se ha generado correctamente.")
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Ha ocurrido un error: {e}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()

