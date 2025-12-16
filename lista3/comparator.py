def compare_files(file1, file2):
    """Porównuje zawartość dwóch plików."""
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            content1 = f1.read()
            content2 = f2.read()

        if content1 == content2:
            print("Pliki mają taką samą zawartość.")
        else:
            print("Pliki różnią się zawartością.")

    except FileNotFoundError as e:
        print(f"Błąd: nie znaleziono pliku - {e.filename}")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Porównaj zawartość dwóch plików.")
    parser.add_argument("file1", help="Ścieżka do pierwszego pliku")
    parser.add_argument("file2", help="Ścieżka do drugiego pliku")
    args = parser.parse_args()

    compare_files(args.file1, args.file2)
