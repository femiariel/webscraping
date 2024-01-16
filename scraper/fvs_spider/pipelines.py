import MySQLdb.cursors
import pandas as pd
from twisted.enterprise import adbapi
from pydispatch import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
import logging
from fvs_spider import settings
from time import sleep

class FvSSpiderPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)
 
    def __init__(self, stats):
        self.stats = stats
        self.dbpool = None
        self._connect_to_database()
 
    def _connect_to_database(self):
        retries = 0
        max_retries = 5  # Nombre maximal de tentatives de reconnexion
        delay = 5  # Délai en secondes entre les tentatives
 
        while retries < max_retries:
            try:
                self.dbpool = adbapi.ConnectionPool('MySQLdb',
                    host=settings.MYSQL_HOST,
                    user=settings.MYSQL_USER,
                    passwd=settings.MYSQL_PASS,
                    db=settings.MYSQL_DB,
                    charset='utf8',
                    use_unicode=True,
                    cursorclass=MySQLdb.cursors.DictCursor
                )
                return  # Connexion réussie, sortez de la boucle
            except Exception as e:
                retries += 1
                logging.error(f"Tentative de connexion {retries}/{max_retries} échouée: {e}")
                time.sleep(delay)
 
        if retries == max_retries:
            logging.error("Échec de toutes les tentatives de connexion à la base de données.")
            # Gérer l'échec ici (par exemple, en arrêtant le spider ou en levant une exception)
           
 
    def open_spider(self, spider):
        # Initialiser une liste vide pour stocker les données des articles
        self.items = []

    def spider_closed(self, spider):
        # À la fin du spider, convertir la liste des articles en DataFrame
        df = pd.DataFrame(self.items)
        # Afficher la DataFrame
        print(df[['seller', 'product_url']])
        self.dbpool.close()
        # Vous pouvez aussi sauvegarder la DataFrame dans un fichier si nécessaire
        # df.to_csv('output.csv', index=False)

    def process_item(self, item, spider):
        
        # Supprimez l'espace insécable, le symbole euro, et remplacez la virgule par un point.
        price_str = item['price']
        if isinstance(price_str, list):
            price_str = price_str[0]  # Si la liste est vide, cela lèvera une erreur.
        price_str = price_str.replace('€', '').replace('\xa0', '').replace(',', '.').strip()

        # Supprimez tous les espaces restants et convertissez en float.
        try:
            item['price'] = float(price_str)
        except ValueError as e:
            # Gérez l'erreur ou imprimez un message pour déboguer
            spider.logger.error(f"Erreur de conversion: {e}, Valeur de l'item: {price_str}")
            item['price'] = None  # ou une autre valeur par défaut si nécessaire


                    # Répétez le processus pour d'autres champs si nécessaire
        if 'old_price' in item and isinstance(item['old_price'], list):  # Adaptez le nom du champ si nécessaire
            item['old_price'] = item['old_price'][0] if item['old_price'] else None
            item['old_price'] = float(item['old_price'].replace('\xa0€', '').replace(',', '.').strip()) if item['old_price'] else None
        
        item['title'] = item['title'].replace('\n', ' ').replace('\t', ' ').strip()
        self.items.append(item)
        query = self.dbpool.runInteraction(self._insert_record, item)
        query.addErrback(self._handle_error)
        return item

    def _insert_record(self, tx, item):
        # Ajoutez ici les champs correspondants à votre item
        fields = ['title', 'price','image_url','product_url','seller']
        # ... dans votre méthode _insert_record ...
        values = [str(item.get(field)) for field in fields]
        # Prenez le premier élément de chaque liste
        values = ['"'+value+'"' for value in values]  # Assurez-vous que les valeurs sont des chaînes
        result = tx.execute(
            """ INSERT IGNORE INTO prices ({}) VALUES ({}) """\
            .format(','.join(fields), ','.join(values))
        )
        # print("MYSQL: ", result)
        if result > 0:
            self.stats.inc_value('database/items_added')
   
    def _handle_error(self, e):
        logging.error(e)