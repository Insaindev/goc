# GOC (General objects categorization)

# github url: 
## git hub git clone https://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@github.com/Insaindev/goc.git

# odkaz na yolo3.weight => https://drive.google.com/file/d/1QGHp37BvVqN_7zGodf1m1RC_teJ1qEW2/view?usp=share_link

# Moduly

## source_connector
### Bude spajat zdroj obrazu s databazou pre ukladanie frameov do temp tabulky z ktorej bude pokracovat proces analyzy obrazu
* Mosquitto => klient so zdrojom obrazu preposle potrebne metadata priamo do mqtt konektora ktory metadata spracuje a ulozi do databazy => **mosquitto_connector.py**
* Preposlanie metadata priamo do databazy => **db_connector.py**
* Citanie framov priamo zo zdroja (video nahravka) => **live_connector.py**

## database_connector
### bude vytahovat nespracovane zaznamy (processed_flag = false)

## Object classificator
*Samostatna trieda (proces) kde vstup je uz frame a dalsie potrebne metadata a vystup je zoznam classifikacii*

## Vyhladavanie zaznamov
*Modul pre vyhladavanie zaznamov pouzitim filtrov ako napriklad rozsah casu a datumu, konkretna kamera, konkretny typ objektu*