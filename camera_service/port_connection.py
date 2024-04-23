import pickle


def add_port_to_file(filename, port):
    ports = read_ports_from_file(filename)
    ports.append(port)
    with open(filename, 'wb') as file:
        pickle.dump(ports, file)




def clear_ports_file(filename):
    with open(filename, 'wb') as file:
        pass


def read_ports_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            ports = pickle.load(file)
    except FileNotFoundError:
        ports = []
    except EOFError:
        ports = []
    return ports


def remove_specific_port(filename, port_to_remove):
    ports = read_ports_from_file(filename)
    ports = [port for port in ports if port != port_to_remove]
    with open(filename, 'wb') as file:
        pickle.dump(ports, file)
