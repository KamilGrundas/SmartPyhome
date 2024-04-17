import pickle


def add_port_to_file(filename, port):
    with open(filename, 'ab') as file:  # 'ab' for append in binary mode
        pickle.dump([port], file)  # Zapisuje port jako listę, aby utrzymać spójność danych


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
    # Usuwamy port, zakładając, że ports jest prostą listą liczb całkowitych
    ports = [port for port in ports if port != port_to_remove]
    with open(filename, 'wb') as file:
        pickle.dump(ports, file)  # Zapisujemy zaktualizowaną listę portów
