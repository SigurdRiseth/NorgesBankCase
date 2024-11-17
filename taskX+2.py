import json
import ipaddress
import logging

class Node:
    """
    Representerer en node i en graf.

    Attributter:
        navn (str): Navnet på noden, som kan være en tom streng "", "S", eller "R".
        unikID (int): En unik identifikator for noden.
        naboer (list[int]): Liste over UnikID-ene til naboene til noden.
        samlepost (str): En spesifikk verdi (IP-adresse med subnett, et tall, eller et CIDR).
        kant (list[int]): Liste med vekter for kantene mellom denne noden og dens naboer.
    """

    def __init__(self, navn, unikID, naboer, samlepost):
        """
        Initialiserer en Node-instans.

        Args:
            navn (str): Navnet på noden.
            unikID (int): Unik identifikator for noden.
            naboer (list): Liste over naboenes UnikID-er.
            samlepost (str): Verdi tilknyttet noden (IP, CIDR, eller tall).
        """
        self.navn = navn
        self.unikID = unikID
        self.naboer = [int(n) for n in naboer]
        self.samlepost = samlepost
        self.kant = [0] * len(naboer)  # Default kantvekt er 0
    
    def __repr__(self):
        """
        Returnerer en lesbar strengrepresentasjon av noden.
        """
        return f"Node({self.navn}, {self.unikID}, {self.naboer}, {self.samlepost})"
    
def lese_nodefil(filnavn):
    """
    Leser noder fra en JSON-fil og oppretter Node-objekter.

    Args:
        filnavn (str): Filnavnet som inneholder JSON-data.

    Returns:
        list[Node]: Liste med Node-objekter.
    """
    noder = []
    with open(filnavn, 'r') as f:
        data = json.load(f)
        for node_data in data:
            node = Node(node_data['Navn'], node_data['UnikID'], node_data['Naboer'], node_data['Samlepost'])
            noder.append(node)
    return noder

def er_gyldig_sti(sti, noder):
    """
    Sjekker om en sti er gyldig basert på spesifikke regler.

    Args:
        sti (list[int]): Liste med UnikID-er som representerer stien.
        noder (list[Node]): Liste med alle Node-objekter.

    Returns:
        bool: True hvis stien er gyldig, ellers False.
    """
    # 1. Ingen noder kan besøkes to ganger i samme sti.
    if len(sti) != len(set(sti)):
        return False
    
    # 2. Stier må starte og slutte i en ""-node, og ikke være innom andre ""-noder.
    start_node = next(node for node in noder if node.unikID == sti[0])
    slutt_node = next(node for node in noder if node.unikID == sti[-1])
    if start_node.navn != "" or slutt_node.navn != "":
        return False
    
    for node_id in sti[1:-1]:  # Sjekk de midterste nodene
        mid_node = next(node for node in noder if node.unikID == node_id)
        if mid_node.navn == "":
            return False
    
    # 3. ""- og "R"-noder sin CIDR-range kan ikke overlappe.
    def cidr_overlap(cidr1, cidr2):
        # Eksempelimplementasjon av CIDR-sjekk (bruk bibliotek hvis tilgjengelig)
        import ipaddress
        return ipaddress.ip_network(cidr1).overlaps(ipaddress.ip_network(cidr2))
    
    for node_id in sti:
        current_node = next(node for node in noder if node.unikID == node_id)
        if current_node.navn == "":
            for node_id2 in sti:
                other_node = next(node for node in noder if node.unikID == node_id2)
                if other_node.navn == "R" and cidr_overlap(current_node.samlepost, other_node.samlepost):
                    return False
    
    # 4. "S"- til "S"-node stier må ha samme samlepost.
    s_nodes = [node for node in noder if node.navn == "S" and node.unikID in sti]
    if len(s_nodes) > 1:
        samleposter = {node.samlepost for node in s_nodes}
        if len(samleposter) > 1:
            return False
    
    return True

def finn_alle_stier(noder):
    """
    Finner alle gyldige stier i grafen.

    Args:
        noder (list[Node]): Liste over alle Node-objekter.

    Returns:
        list[list[int]]: Liste av gyldige stier, hvor hver sti er en liste med UnikID-er.
    """

    def finn_stier_fra_node(aktiv_sti, besøkte):
        """
        Utforsker stier fra en gitt node rekursivt.

        Args:
            aktiv_sti (list[int]): Gjeldende sti som utforskes.
            besøkte (set[int]): Sett med noder som allerede er besøkt.
        """
        # Hent siste node i stien
        siste_node = next(node for node in noder if node.unikID == aktiv_sti[-1])
        
        # Hvis stien ender i en "", vurder den som komplett
        if siste_node.navn == "" and len(aktiv_sti) > 1:
            if er_gyldig_sti(aktiv_sti, noder):
                stier.append(list(aktiv_sti))
            return
        
        # Utforsk naboer rekursivt (med backtracking)
        for nabo_id in siste_node.naboer:
            if nabo_id not in besøkte:
                aktiv_sti.append(nabo_id)
                besøkte.add(nabo_id)
                finn_stier_fra_node(aktiv_sti, besøkte)
                aktiv_sti.pop()
                besøkte.remove(nabo_id)

    stier = []
    for node in noder:
        if node.navn == "":
            finn_stier_fra_node([node.unikID], {node.unikID})
    
    return stier

def nodefil_ugyldig(noder):
    """
    Sjekker om nodene inneholder noen av følgende feil:
    1. To ""-noder er naboer.
    2. En node har seg selv som nabo.
    3. "S"-node har Samlepost-verdi utenfor 2-4096.
    """
    for node in noder:
        # Sjekk 2: En node har seg selv som nabo
        if node.unikID in node.naboer:
            logger.error(f"Node {node.unikID} har seg selv som nabo.")
            return True

        # Sjekk 3: "S"-node med Samlepost utenfor området 2-4096
        if node.navn == "S":
            if (int(node.samlepost) < 2 or int(node.samlepost) > 4096):
                logger.error(f"S-node {node.unikID} har en ugyldig Samlepost-verdi: {node.samlepost}.")
                return True

    # Sjekk 1: To ""-noder som er naboer
    for node in noder:
        if node.navn == "":
            for nabo_id in node.naboer:
                nabo_node = next((n for n in noder if n.unikID == nabo_id), None)
                if nabo_node and nabo_node.navn == "":
                    logger.error(f'""-noder {node.unikID} og {nabo_node.unikID} er naboer.')
                    return True

    return False

def main():
    """
    Leser noder fra en JSON-fil, finner gyldige stier, og logger resultatene.
    """
    try:
        logger.info("Leser nodefil...")
        noder = lese_nodefil('nodefil.json')
        if nodefil_ugyldig(noder):
            logger.error("Nodefilen er ugyldig. Avslutter programmet.")
            return
        logger.info("Nodefil lastet inn.")

        logger.info("Finner alle gyldige stier...")
        stier = finn_alle_stier(noder)
        logger.info(f"Antall gyldige stier funnet: {len(stier)}")

        if len(stier) > 0:
            for sti in stier:
                print(sti)
        else:
            logger.warning("Ingen stier ble funnet i grafen.")

    except Exception as e:
        logger.error(f"En feil oppstod: {e}")

if __name__ == "__main__":
    """
    Konfigurerer logging og starter hovedprogrammet.
    """
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