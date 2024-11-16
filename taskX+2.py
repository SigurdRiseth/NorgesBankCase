import json
import ipaddress
import logging

class Node:
    """
    En klasse som representerer en node i en graf.

    Attributter:
        navn (str): Navnet på noden. Dette kan være en tom streng "", "S", eller "R".
        unikID (int): En unik identifikator for noden.
        naboer (list): En liste med int-verdi som representerer UnikID-ene til naboene til noden.
        samlepost (str): En spesifikk verdi som kan være en IP-adresse med subnett, et tall, eller et CIDR.
        kant (list): En liste med vekter som representerer kantene mellom denne noden og dens naboer. Vektene er initialisert til 0.
    """

    def __init__(self, navn, unikID, naboer, samlepost):
        """
        Initialiserer en Node-instans. Alle kanter blir intialisert til verdien 0 (null).

        Args:
            navn (str): Navnet på noden.
            unikID (int): Unik identifikator for noden.
            naboer (list): En liste over naboenes UnikID-er som denne noden har forbindelser til.
            samlepost (str): En spesifikk verdi knyttet til noden (kan være IP, CIDR eller tall).
        """
        self.navn = navn
        self.unikID = unikID
        self.naboer = [int(n) for n in naboer]  # Konverter naboer til int
        self.samlepost = samlepost
        self.kant = [0] * len(naboer)  # Default kantvekt er 0
    
    def __repr__(self):
        return f"Node({self.navn}, {self.unikID}, {self.naboer}, {self.samlepost})"
    
def lese_nodefil(filnavn):
    noder = []
    with open(filnavn, 'r') as f:
        data = json.load(f)
        for node_data in data:
            node = Node(node_data['Navn'], node_data['UnikID'], node_data['Naboer'], node_data['Samlepost'])
            noder.append(node)
    return noder

def er_gyldig_sti(sti, noder):
    # Validering av stien ifølge reglene
    pass

def finn_alle_stier(noder):
    # Her ville jeg implementert BFS for å finne korteste sti
    pass

def main():
    noder = lese_nodefil('nodefil.json')
    
    # Finn alle gyldige stier
    stier = finn_alle_stier(noder)
    
    # Sorter stiene etter vekt
    stier.sort(key=lambda x: (x[1], x[0]))  # Sorter etter vekt og så sti
    
    for sti in stier:
        print(sti)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename='taskX+2.log', 
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info('Started')
    main()
    logger.info('Finished')