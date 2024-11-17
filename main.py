from utilities.finder import Finder

if __name__ == "__main__":
    pdf_path = "sensible_assets/pdf_test.pdf"
    finder = Finder()
    finder.find_rectangle(pdf_path=pdf_path)
