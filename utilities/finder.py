from pdf2image import convert_from_path
import os
from PIL import Image
import numpy as np
from datetime import datetime


class Finder:
    
    def find_rectangle(self, pdf_path: str, overlay_image: str) -> None:
        bottom_right_image_path = "sensible_assets/outputs/output" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "bottom_right.png"
        final_image_path = "sensible_assets/outputs/output" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "final.png"

        binary_matrices = self.__pdf_to_binary_matrix(pdf_path)
        print("The image was converted to binary")

        interest_region = self.__find_largest_rectangle(binary_matrices[0])
        print(f"The rectangle was found with coordinates {interest_region}")

        self.__save_bottom_right_of_pdf(pdf_path, bottom_right_image_path)
        print(f"The right bottom path was saved as png with the name {bottom_right_image_path}")

        # self.__crop_rectangle(bottom_right_image_path,  final_image_path, interest_region)
        # print(f"The rectangle was croped with the name {final_image_path}")

        self.__paste_image_on_image(bottom_right_image_path, overlay_image, interest_region, final_image_path)

    def __save_bottom_right_of_pdf(self, pdf_path: str, output_path: str) -> None:
        """
        Decupează și salvează partea din dreapta jos a unui PDF cu o singură pagină.

        :param pdf_path: Calea către fișierul PDF.
        :param output_path: Calea unde se va salva imaginea decupată.
        """
        # Convertim pagina PDF la imagine
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if not images:
            raise ValueError("PDF-ul nu a putut fi convertit în imagine.")
        
        img = images[0]  # Preluăm imaginea primei și singurei pagini
        width, height = img.size  # Dimensiunile imaginii

        # Coordonatele pentru partea din dreapta jos
        region = (width // 2, height // 2, width, height)  # (left, upper, right, lower)

        # Decupăm regiunea
        cropped_img = img.crop(region)

        # Salvăm imaginea decupată
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cropped_img.save(output_path)
        print(f"Partea din dreapta jos a fost salvată la {output_path}")


    def __pdf_to_binary_matrix(self, pdf_path: str, dpi: int = 200, threshold: int = 128) -> list:
        """
        Return a binary matrix with 1 - black pixel, 0 - while pixel for the bottom right corner of the pdf
        """
        pages = convert_from_path(pdf_path, dpi=dpi)
        binary_matrices: list = []

        for page in pages:
            width, height = page.size
            right_bottom_region = page.crop((width // 2, height // 2, width, height))
            grayscale_image = right_bottom_region.convert("L")
            binary_image = np.array(grayscale_image) < threshold
            binary_matrix = binary_image.astype(int)
            binary_matrices.append(binary_matrix)

        return binary_matrices


    def __find_largest_rectangle(self, binary_matrix: list) -> tuple:
        rows, cols = binary_matrix.shape
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        max_rectangle = (0, 0, 0, 0)  # top_left_y, top_left_x, bottom_right_y, bottom_right_x
        max_area = 0

        def can_move(x, y):
            """Verifică dacă ne putem deplasa la poziția dată."""
            return 0 <= x < rows and 0 <= y < cols and binary_matrix[x][y] == 1 and not visited[x][y]

        def explore_rectangle(start_x, start_y):
            """Explorează dreptunghiul pornind de la o poziție."""
            visited[start_x][start_y] = True
            top, left, bottom, right = start_x, start_y, start_x, start_y

            # Mergem în sus până nu mai putem
            x, y = start_x, start_y
            while can_move(x - 1, y):
                x -= 1
                visited[x][y] = True
                top = x

            # Mergem în stânga până nu mai putem
            x, y = top, start_y
            while can_move(x, y - 1):
                y -= 1
                visited[x][y] = True
                left = y

            # Mergem în dreapta până nu mai putem
            x, y = top, start_y
            while can_move(x, y + 1):
                y += 1
                visited[x][y] = True
                right = y

            # Mergem în jos până nu mai putem
            x, y = top, right
            while can_move(x + 1, y):
                x += 1
                visited[x][y] = True
                bottom = x

            # Returnăm coordonatele dreptunghiului
            return top, left, bottom, right

        # Analizăm matricea de jos în sus
        for row in reversed(range(rows)):
            for col in range(cols):
                if binary_matrix[row][col] == 1 and not visited[row][col]:
                    top, left, bottom, right = explore_rectangle(row, col)
                    area = (bottom - top + 1) * (right - left + 1)
                    if area > max_area:
                        max_area = area
                        max_rectangle = (top, left, bottom, right)

        return max_rectangle
    

    def __highlight_largest_rectangle(self, binary_matrix: list, filename: str) -> None:
        top_left_y, top_left_x, bottom_right_y, bottom_right_x = self.__find_largest_rectangle(binary_matrix)
        height, width = binary_matrix.shape
        color_image = Image.new("RGB", (width, height), (255, 255, 255))

        # Colorează doar cel mai mare dreptunghi în roșu
        for y in range(height):
            for x in range(width):
                if top_left_y <= y <= bottom_right_y and top_left_x <= x <= bottom_right_x:
                    color_image.putpixel((x, y), (255, 0, 0))  # roșu
                elif binary_matrix[y, x] == 1:
                    color_image.putpixel((x, y), (0, 0, 0))  # negru pentru alte valori de 1
                else:
                    color_image.putpixel((x, y), (255, 255, 255))  # alb

        color_image.save(filename)


    def __crop_rectangle(self, image_path: str, output_path: str, rectangle: tuple) -> None:
        """
        Decupează o regiune dreptunghiulară din imagine și o salvează într-un fișier.

        :param image_path: Calea către imaginea originală.
        :param output_path: Calea unde se va salva imaginea decupată.
        :param rectangle: Tuple cu coordonatele dreptunghiului (top, left, bottom, right).
        """
        # Deschidem imaginea
        with Image.open(image_path) as img:
            # Coordonatele dreptunghiului
            top, left, bottom, right = rectangle

            # Decupăm regiunea
            cropped_img = img.crop((left, top, right + 1, bottom + 1))  # PIL folosește (left, upper, right, lower)

            # Salvăm imaginea decupată
            cropped_img.save(output_path)

            print(f"Imaginea decupată a fost salvată la {output_path}")


    def __paste_image_on_image(self, base_image_path: str, overlay_image_path: str, position: tuple, output_path: str)-> None:
        """
        Plasează o imagine (overlay) pe o altă imagine (bază) la coordonatele specificate.

        :param base_image_path: Calea către imaginea de bază.
        :param overlay_image_path: Calea către imaginea ce va fi suprapusă.
        :param position: Coordonatele unde se plasează (x, y) în imaginea de bază.
        :param output_path: Calea unde se salvează rezultatul.
        """
            # Deschidem imaginea de bază
        base_image = Image.open(base_image_path).convert("RGBA")

        # Deschidem imaginea ce va fi suprapusă
        overlay_image = Image.open(overlay_image_path).convert("RGBA")

        # Obținem dimensiunile imaginii de suprapus
        overlay_width, overlay_height = overlay_image.size

        # Verificăm dacă imaginea de suprapus depășește dimensiunile imaginii de bază
        base_width, base_height = base_image.size
        if position[0] + overlay_width > base_width or position[1] + overlay_height > base_height:
            raise ValueError("Imaginea suprapusă depășește dimensiunile imaginii de bază.")

        # Plasăm imaginea suprapusă peste cea de bază
        base_image.paste(overlay_image, position, overlay_image)

        # Salvăm imaginea rezultată
        base_image.save(output_path)
        print(f"Imaginea a fost salvată la {output_path}")