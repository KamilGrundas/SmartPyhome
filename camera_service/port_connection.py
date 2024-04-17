import pickle


def add_port_to_file(filename, port):
    ports = read_ports_from_file(filename)  # Odczytujemy aktualną listę portów
    ports.append(port)  # Dodajemy nowy port do listy
    with open(filename, 'wb') as file:  # Otwieramy plik w trybie zapisu binarnego, który czyści poprzednią zawartość
        pickle.dump(ports, file)  # Zapisujemy zaktualizowaną listę portów


# Przykład użycia


def clear_ports_file(filename):
    with open(filename, 'wb') as file:  # 'wb' - write binary mode, clears the file
        pass  # Simply opening in write mode truncates the file


def read_ports_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            ports = pickle.load(file)
    except FileNotFoundError:
        ports = []  # Jeśli plik nie istnieje, zwracamy pustą listę
    except EOFError:
        ports = []  # Jeśli plik jest pusty, zwracamy pustą listę
    return ports


def remove_specific_port(filename, port_to_remove):
    ports = read_ports_from_file(filename)
    ports = [port for port in ports if port != port_to_remove]  # Usuwamy określony port
    with open(filename, 'wb') as file:
        pickle.dump(ports, file)  # Zapisujemy listę bez usuniętego portu
