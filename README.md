# Projet de Web Scraping : Comparaison des Prix d'iPhone
 
Ce projet a pour but de comparer les prix des iPhones sur deux plateformes en ligne, Certideal et Mobileshop. Il utilise `Scrapy` pour le scraping des sites web et `Docker` pour la conteneurisation. Le système est constitué de trois conteneurs principaux :
 
- **db**: Une base de données MySQL.
- **scraper**: S'occupe du scraping des données sur les sites web mentionnés.
- **Flask**: Gère l'interface web où les données récupérées sont affichées.

## Projet en local

Pour cloner le projet sur votre ordinateur, allez dans votre terminal et saissisez la commande :

```
git clone https://gitlab.com/ariel-gasyd-anifath/webscraping.git
``` 

## Problème de connexion  MySQL

Si vous rencontrez un problème de connexion avec le serveur mysql, allez dans le dossier `db`, supprimer le dossier `db_dir` .

## Configuration du Réseau
 
Un réseau nommé `webscraping_scrapy_mysql_net` a été créé pour faciliter la communication entre les conteneurs.
 
## Exécution du Projet
 
Pour démarrer le projet, utilisez la commande suivante :
 
```
docker-compose build
``` 
Ensuite, saisissez la commande suivante pour lancer tous les conteneurs en mode détaché puis attendez 30 secondes :

```
docker-compose up -d 
```

 
## Connexion à MySQL
 
Pour vous connecter au conteneur MySQL, exécutez :
 
```
docker run -it --network=webscraping_scrapy_mysql_net mysql mysql -uroot -proot -hdb
```
 
Une fois connecté, sélectionnez la base de données avec la commande :
 
```
use testdb;
```
 
Pour afficher le contenu de la table `prices`, tapez :
 
```
select * from prices;
```
 
## Accès à l'Interface Web
 
Pour accéder à l'interface web, ouvrez le navigateur de votre choix et visitez :
 
`localhost:8080`
 
