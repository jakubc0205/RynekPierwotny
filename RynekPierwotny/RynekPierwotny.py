""" 
This script perform the following operations: 
1) Loads the report and prints the first 10 rows 
2) Creates a small subreport with the information about the average price of a squere meter of a flat for a given investition 
3) Looks for the coordinates of an objects and append this piece of information to the script 
4) Creates a database and a report with the sales report for each month
"""
import argparse
import pathlib
import sqlite3
from tkinter import filedialog as fd
from typing import List

import numpy as np
import openpyxl
import pandas as pd
import xlsxwriter
from geopy.geocoders import GoogleV3


def localisation(adres: str = None) -> tuple:
    """
    Gets the longitude and latitude of the given address using Google Maps, if the action cannot be performed
    return None
    TODO : You need to possess your own GOOGLE API key in order to use this function.
    For more information please navigate to the website:
    https://developers.google.com/maps/documentation/geocoding?hl=pl
    Parameters:
        adres (str): String representing the location for example "Marszałkowska 10 Warszawa"
    Returns:
        coordinates (tuple): Latitude and longitude of the given address
        None (NoneType) : Nothing is returned once the address cannot be found
    """
    try:
        geolocator = GoogleV3(api_key="PLACE HERE YOUR GOOGLE API KEY")
        location = geolocator.geocode(f"""{adres}""")
        coordinates = (round(location.latitude, 2), round(location.longitude, 2))
        return coordinates
    except:
        return None


### ASSIGNMENT NR1
class Raport:
    @staticmethod
    def zad_1(file_path: pathlib.Path = None) -> pd.DataFrame:
        """
        The function gets the path to the excel file and returns it as the pandas DataFrame.
        Parameters:
            file_path (pathlib.Path): The path to the file, if not provided, a user will be asked for it.
        Returns:
            raport (pd.DataFrame): Raport given in a pandas DataFrame object.
        """
        file_path = file_path if file_path is not None else fd.askopenfilename()
        try:
            raport = pd.read_excel(file_path)
        except:
            raise Exception(
                """Cannot load the Excel file, please make sure that you gave the right path and the structure of it is proper"""
            )
        print(raport.head(10))
        return raport

    ### ASSIGNMENT NR2
    # Getting offer id and its price, droping empty record since not relevant to the average
    @staticmethod
    def zad_2(raport: pd.DataFrame = None) -> pd.DataFrame:
        """
        The function takes a report and reporoces it in order to pull information about the average price for
        a flat in each investition.
        Parameters:
            raport: pd.DataFrame: DataFrame containing the information about flats.
        Returns:
            raport_avg_square_meter (pd.DataFrame): a refashioned raport with the insight of the average price for
            a squere meter per investition.
        """
        raport_avg_square_meter = raport[["offer_id", "cena_m2"]] 
        #Getting rid of null values since not relvent for this purpose.
        raport_avg_square_meter = raport_avg_square_meter.dropna()
        raport_avg_square_meter = (
            raport_avg_square_meter.groupby(["offer_id"])
            .mean()
            .rename(columns={"cena_m2": "avg_price_square_meter_per_invest"})
        )
        raport_avg_square_meter[
            "avg_price_square_meter_per_invest"
        ] = raport_avg_square_meter["avg_price_square_meter_per_invest"].apply(
            lambda x: round(x)
        )
        print(raport_avg_square_meter.head())
        return raport_avg_square_meter

    ## ASSIGNMENT NR3

    @staticmethod
    def zad_3(raport: pd.DataFrame = None) -> None:
        """
        The function takes a report and adds the column "wspolrzedne" indicating the latitude and the longiture of the
        given place.
        Parameters:
            raport: pd.DataFrame: DataFrame containing the information about flats.
        Returns:
            None (NoneType): The function itself does not return anything, but saves an excel file on a drive.
        """  
        '''NOTE: In the following example I created a new column in order to make the address fully precise 
        and minimalise the risk of giving the location from some other city. For example 
        the result of the query for "Ul. Armii Krajowej 94" will highely likely point to Katowice.  
        '''
        raport["full_address"] = raport["lokalizacja"] + " Warszawa"
        #raport["wspolrzedne"] = raport["lokalizacja"].apply(localisation) 
        raport = raport.drop(['full_address'], axis=1)
        return print(raport.head())

    ### ASSIGNMENT NR4
    @staticmethod
    def zad_4(raport: pd.DataFrame = None) -> pd.DataFrame:
        """
        The function takes a report, cuts a slice from it and based on the piece create a table in SQL containing
        information about the sales for each month which is than added to an Excel raport and saved on a drive.
        Parameters:
            raport: pd.DataFrame: DataFrame containing the information about flats.
        Returns:
            raport_avg_square_meter (pd.DataFrame): a refashioned raport with the insight of the average price for
            a squere meter per investition.
        """
        sprzedaz_miesieczna_db = raport[["data_sprzedazy", "property_id"]] 
        #Getting rid of null values since not relvent for this purpose.
        sprzedaz_miesieczna_db = sprzedaz_miesieczna_db.dropna()
        try:
            conn = sqlite3.connect("RynekPierwotny.db")
        except:
            print("Cannot establish the connection")
        sprzedaz_miesieczna_db.to_sql(
            "sprzedaz_miesieczna_db", conn, if_exists="replace"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sprzedaz_miesieczna as
            SELECT strftime('%m %Y', data_sprzedazy) AS "Month" ,count(property_id) as "liczba"  from sprzedaz_miesieczna_db
            group by 1
            order by data_sprzedazy asc;
            """
        )
        cursor = conn.execute(
            """
            SELECT Month,liczba from sprzedaz_miesieczna order by strftime("%m-%Y",Month) ASC;
            """
        )
        raport_sprzedaz_miesieczna = pd.DataFrame(
            cursor.fetchall(),
            columns=[description[0] for description in cursor.description],
        )
        conn.close()
        raport_sprzedaz_miesieczna.to_excel("Raport.xlsx", engine="xlsxwriter")
 
def __main():  
    parser = argparse.ArgumentParser(description='''The tool can take a raport and reprocess it in order to fulfill some 
usefull information''')
    parser.add_argument("--raport", 
                        help = "Takes the report and return specific information", 
                        action="store_true", 
                        ) 
    parser.add_argument("--location",   
                    nargs='+',    
                    help = "Gives a longitude and a latitude for a given adress for example: Marszałkowska 10 Warszawa", 
                    )   
    
    args = parser.parse_args() 
    raport = args.raport 
    location = args.location 
    if raport: 
        raport = Raport.zad_1()
        Raport.zad_2(raport)
        Raport.zad_3(raport)
        Raport.zad_4(raport)     
    elif location: 
        return print(localisation(args.location))   

if __name__ == '__main__': 
    __main()    


# Here you can execute the script:
# raport = Raport.zad_1()
# Raport.zad_2(raport)
# Raport.zad_3(raport)
# Raport.zad_4(raport)
### ASSIGNMENT NR5
""" 
    W celu opytmalizacji przechowywania baz danych możliwe do przeprowadzenia jest 
kilka procedur.    
    W przypadku znaczących problemów z dostępnoscią pamięci pierwszym krokiem może być  
oczywiście zinwentaryzowanie baz danych i rozważnie usunięcia niepotrzebnych kolumn/tabel, tudzież 
wierszy zawierających rekordy stare, które nie są i nie będą już używane do jakiejkolwiek 
rzetelnej analizy.  
    Dobrym pomysłem jest implementacja indeksowania, wprowadzone w poprawny sposób 
pozwala na znaczące zmniejszenie czasu egzekucji zapytań. 
W wielu przypadkach jedynym indeksem  
w bazie danych jest klucz główny, wówczas w przypadku wyszukiwania konkretnej wartości w klauzuli WHERE 
musi zostać wykonany pełny skan tabeli. Jeżeli zatem często tworzymy zapytanie, w którym odwołujemy się do kolumny 
zawierającej informacje na przykłąd o dacie :  

Select liczba from sprzedaz_miesieczna where strftime('%m %Y', data_sprzedazy) = '01-2020'; 

Można rozważyć implementacje indeksowania, wówczas ułatwimy zadanie 
silnikowi bazy danych, który w tym przypadku znacznie szybciej znajdzie pożądany  
przez nas wynik. Dobrym pomysłem jest zatem stosowanie 
indeksów w przypadku kolumn często występujących w klauzuli WHERE,GROUP BY,ORDER BY, 
a także te, z których często wyciągane są zagregowane dane: MIN,MAX etc. Indeksowanie kolumn 
w tabelach, które czesto podlegają łączeniu również może pomóc w optymalizacji czasu egzekucji zapytania.  
Należy jednak pamiętać, że większa ilość indeksów nie przekłada sie z automatu na lepszą wydajność,  
będzie ona szczególnie pomocna w przypadku dużych tabel i jeżeli indeksowanie zostanie ograniczone 
do niezbędnego minimum, w przeciwnym przypadku możemy jedynie niepotrzebnie zapchać swoją bazę 
dodatkowymi informacjami i wydłużyć czas potrzebny na otrzymanie wyniku.
    Chcąc upłynnić proces egzekucji zapytań warto przyjrzeć się ich strukturze.  
Warto zastanowić się nad ograniczniem ilości zwracanych kolumn do minimum, a także tam gdzie to możliwe  
unikać stosowanie podzapytań i skorelowanych podzapytań. Przykładowo skorelowane podzapytanie : 
  
"Select imie, dzial, pensja,  
(select sum(pensja) from pracownicy p1  
where p1.id = p2.id group by dzial) 
from pracownicy p2"  

Będzie musiało zostać wykonane dla każdego rekordu w tabeli, a zatem za każdym razem 
będziemy musieli wczytać tabele od nowa. 
W tym przypadku spore korzyści w czasie egzekucji  
można osiągnąć stosująć klauzule over(): 

"select imie, dzial, pensja, 
sum(pensja) over(partition by dzial) 
from pracownicy"

    W niektórych przypadkach pomocne okazać się może tworzenie kolumn lub tabel 
agregujących. Przykładowo korzystając często ze średniej wartości wszystkich mieszkań  
w Warszawie potencjalnym rozwiązaniem przyspieszającym czas otrzymania wyniku byłoby  
utworzenie tabeli/kolumny agregującej zawierającej tą informację, pomimo tego, że teoretycznie 
wartość tą można otrzymywać również wyciągająć za każdym razem średnią z kolumny z ceną.  
Należy jednak brać pod uwagę, że w pojęciu ogólnym należy unikać powtarzania się zapisów w 
bazach danych, rozwiąznie to należy stosować jedynie w szczególnych przypadkach.
    Warto również przyjrzeć się typom danych, które przypisaliśmy naszym kolumnom w tabelach. 
Odpowiednia deklaracja tychże pozwala zaoszczędzić sporo pamięci, a co za tym idzie znacząco przyspieszyć 
proces wyciągania dancych.  
    Baczną uwagę należy również przywiązać do kolejności kolumn w tabelach. Odpowiednie sortowanie 
powinno w miarę możliwości naśladować podany schemat: 
1) Klucz główny 
2) Klucz obcy 
3) Kolumny często pojawiające sie w klauzuli WHERE 
4) Kolumny często poddawane aktualizacji 
5) Kolumny typu NULL (od używanych najczęściej do używanch rzadziej).
"""
