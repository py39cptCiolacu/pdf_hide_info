from utilities.finder import Finder

if __name__ == "__main__":
    pdf_path = "sensible_assets/pdf_test_2.pdf"
    overlay_image_path = "sensible_assets/template_1.png"
    finder = Finder()
    finder.find_rectangle(pdf_path=pdf_path, overlay_image=overlay_image_path)
